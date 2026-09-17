import json
import hashlib
from datetime import datetime
from sqlalchemy.orm import Session
from app import models, schemas
import logging

logger = logging.getLogger(__name__)

class ImportService:
    def __init__(self, db: Session):
        self.db = db

    def calculate_hash(self, file_path: str) -> str:
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def process_import(self, file_path: str) -> dict:
        stats = {
            "records_created": 0,
            "records_updated": 0,
            "records_skipped": 0,
            "duplicates": 0,
            "validation_errors": 0,
            "review_required": 0,
            "status": "FAILED",
            "categories": {
                "profile": 0,
                "education": 0,
                "career": 0,
                "skills": 0,
                "certifications": 0,
                "evidence": 0
            }
        }
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            logger.error(f"Failed to read JSON: {e}")
            stats["validation_errors"] += 1
            return stats

        source_hash = self.calculate_hash(file_path)
        import_id = f"import_{datetime.utcnow().timestamp()}"
        
        # Check if already imported
        existing_log = self.db.query(models.ImportAuditLog).filter(models.ImportAuditLog.source_hash == source_hash).first()
        if existing_log:
            logger.info("This file has already been imported.")
            stats["duplicates"] = 1 # Mark as duplicate run
            stats["status"] = "SUCCESS"
            return stats

        # Default User Profile (Since TARS might be single-user, we assume a single profile for personal knowledge)
        user = self.db.query(models.UserProfile).first()
        if not user:
            user = models.UserProfile(first_name="Default", last_name="User", email="default@example.com")
            self.db.add(user)
            self.db.flush()
            stats["records_created"] += 1

        try:
            # 1. Profile
            profile_data = data.get("profile", {})
            if profile_data:
                user.display_name = profile_data.get("display_name")
                user.professional_identity = profile_data.get("professional_identity")
                self.db.add(user)
                stats["records_updated"] += 1
                stats["categories"]["profile"] += 1

            # 2. Education
            for ed in data.get("education", []):
                # Check for duplicates
                existing_ed = self.db.query(models.Education).filter(
                    models.Education.user_id == user.id,
                    models.Education.qualification == ed.get("qualification"),
                    models.Education.institution == ed.get("institution")
                ).first()
                if not existing_ed:
                    new_ed = models.Education(
                        user_id=user.id,
                        qualification=ed.get("qualification"),
                        institution=ed.get("institution") or "Unknown",
                        result=ed.get("result"),
                        year=ed.get("year"),
                        source=ed.get("source"),
                        confidence="PROVISIONAL"
                    )
                    self.db.add(new_ed)
                    stats["records_created"] += 1
                    stats["categories"]["education"] += 1
                else:
                    stats["duplicates"] += 1

            # 3. Career
            career_experiences = data.get("career", [])
            for ce in career_experiences:
                existing_ce = self.db.query(models.CareerExperience).filter(
                    models.CareerExperience.user_id == user.id,
                    models.CareerExperience.title == ce.get("role"),
                    models.CareerExperience.organization_name == ce.get("organization")
                ).first()
                
                # Assume default company for constraint if company is required
                company = self.db.query(models.Company).filter(models.Company.name == ce.get("organization")).first()
                if not company:
                    company = models.Company(name=ce.get("organization") or "Unknown")
                    self.db.add(company)
                    self.db.flush()

                if not existing_ce:
                    start_date_str = ce.get("period", "").split("-")[0].strip()
                    # simplistic date parsing for seed, can be improved
                    start_date = datetime.utcnow().date() 
                    
                    new_ce = models.CareerExperience(
                        user_id=user.id,
                        company_id=company.id,
                        title=ce.get("role"),
                        organization_name=ce.get("organization"),
                        domain=ce.get("domain"),
                        source=ce.get("source"),
                        confidence=ce.get("confidence"),
                        start_date=start_date
                    )
                    self.db.add(new_ce)
                    self.db.flush()
                    existing_ce = new_ce
                    stats["records_created"] += 1
                    stats["categories"]["career"] += 1
                else:
                    stats["duplicates"] += 1
                
                # Process Evidence from Career
                for ev_text in ce.get("evidence", []):
                    existing_ev = self.db.query(models.Evidence).filter(
                        models.Evidence.career_experience_id == existing_ce.id,
                        models.Evidence.description == ev_text
                    ).first()
                    if not existing_ev:
                        new_ev = models.Evidence(
                            user_id=user.id,
                            description=ev_text,
                            career_experience_id=existing_ce.id,
                            evidence_type="CAREER_EVIDENCE",
                            source=ce.get("source"),
                            confidence=ce.get("confidence")
                        )
                        self.db.add(new_ev)
                        stats["records_created"] += 1
                        stats["categories"]["evidence"] += 1
                    else:
                        stats["duplicates"] += 1

            # 4. Skills Documented
            skill_category = self.db.query(models.SkillCategory).filter(models.SkillCategory.name == "Documented Skills").first()
            if not skill_category:
                skill_category = models.SkillCategory(name="Documented Skills")
                self.db.add(skill_category)
                self.db.flush()

            for skill_name in data.get("skills_documented", []):
                existing_skill = self.db.query(models.Skill).filter(
                    models.Skill.name == skill_name
                ).first()
                if not existing_skill:
                    new_skill = models.Skill(
                        name=skill_name,
                        category_id=skill_category.id,
                        status="DOCUMENTED",
                        assessment_status="NOT_ASSESSED",
                        confidence="PROVISIONAL",
                        score=None
                    )
                    self.db.add(new_skill)
                    stats["records_created"] += 1
                    stats["categories"]["skills"] += 1
                else:
                    stats["duplicates"] += 1

            # 5. Certifications
            for cert in data.get("certifications_mentioned", []):
                existing_cert = self.db.query(models.Certification).filter(
                    models.Certification.user_id == user.id,
                    models.Certification.name == cert.get("name")
                ).first()
                if not existing_cert:
                    new_cert = models.Certification(
                        user_id=user.id,
                        name=cert.get("name"),
                        issuer="Unknown", # Requires issuer normally
                        code=cert.get("code"),
                        status="MENTIONED",
                        verification_status=cert.get("verification", "NEEDS_VERIFICATION")
                    )
                    self.db.add(new_cert)
                    stats["records_created"] += 1
                    stats["categories"]["certifications"] += 1
                else:
                    stats["duplicates"] += 1

            # Audit Log
            audit_log = models.ImportAuditLog(
                import_id=import_id,
                source_file=file_path,
                source_hash=source_hash,
                records_created=stats["records_created"],
                records_updated=stats["records_updated"],
                records_skipped=stats["records_skipped"],
                duplicates=stats["duplicates"],
                validation_errors=stats["validation_errors"],
                review_required=stats["review_required"]
            )
            self.db.add(audit_log)
            
            self.db.commit()
            stats["status"] = "SUCCESS"
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error during import: {e}")
            stats["validation_errors"] += 1
            stats["status"] = "FAILED"
            
        return stats
