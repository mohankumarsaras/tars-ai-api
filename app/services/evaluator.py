import json
from sqlalchemy.orm import Session
from app import models

# Base weights mapped to 100% total
WEIGHTS = {
    "hands_on": 0.25,
    "knowledge": 0.20,
    "architecture": 0.15,
    "troubleshooting": 0.15,
    "security": 0.10,
    "communication": 0.10,
    "cost_optimization": 0.05
}

def calculate_confidence(source_types: set) -> str:
    count = len(source_types)
    if count == 0:
        return "★☆☆☆☆ Claim only"
    elif count == 1:
        if list(source_types)[0] == "User notes":
            return "★☆☆☆☆ Claim only"
        return "★★☆☆☆ Limited"
    elif count == 2:
        return "★★★☆☆ Moderate"
    elif count >= 3 and count < 5:
        return "★★★★☆ Strong"
    else:
        return "★★★★★ Proven"

def evaluate_skill(skill_id: int, db: Session) -> models.SkillEvaluation:
    skill = db.query(models.Skill).filter(models.Skill.id == skill_id).first()
    if not skill:
        return None

    # We will simulate scoring logic based on source types.
    source_types = set()
    
    # Base scores
    scores = {
        "knowledge": 0,
        "hands_on": 0,
        "troubleshooting": 0,
        "architecture": 0,
        "security": 0,
        "cost_optimization": 0,
        "communication": 0
    }
    
    # Fetch all evidence tied to this skill. 
    # For a robust implementation, Evidence should map specifically to a skill.
    # In Phase 2, Evidence has user_id, but not directly linked to skill_id via foreign key explicitly in schema (except perhaps through related_skills string).
    # Since we need a concrete deterministic mapping, let's assume we query Evidence where related_skills contains the skill name, 
    # or we simulate mapping by just pulling evidence for the user.
    # For exactness here, we'll fetch Evidence by user_id and see if the skill name is in description or url.
    user_id = skill.category.user_id if skill.category else 1
    evidences = db.query(models.Evidence).filter(models.Evidence.user_id == user_id).all()
    
    relevant_evidences = []
    for ev in evidences:
        if skill.name.lower() in ev.description.lower():
            relevant_evidences.append(ev)
            if ev.source_type:
                source_types.add(ev.source_type)
                st = ev.source_type.lower()
                if st == "certification":
                    scores["knowledge"] = min(100, scores["knowledge"] + 40)
                    scores["architecture"] = min(100, scores["architecture"] + 20)
                elif st == "career experience":
                    scores["hands_on"] = min(100, scores["hands_on"] + 35)
                    scores["communication"] = min(100, scores["communication"] + 30)
                    scores["troubleshooting"] = min(100, scores["troubleshooting"] + 20)
                elif st == "project":
                    scores["hands_on"] = min(100, scores["hands_on"] + 40)
                    scores["architecture"] = min(100, scores["architecture"] + 30)
                    scores["security"] = min(100, scores["security"] + 15)
                elif st == "assessment":
                    scores["knowledge"] = min(100, scores["knowledge"] + 50)
                    scores["troubleshooting"] = min(100, scores["troubleshooting"] + 40)
                elif st == "practical exercise":
                    scores["hands_on"] = min(100, scores["hands_on"] + 20)
    
    # If the user self-declared familiarity, give a baseline
    if skill.familiarity:
        fam = skill.familiarity.lower()
        if fam in ["expert", "advanced"]:
            for k in scores: scores[k] = min(100, scores[k] + 20)
        elif fam in ["intermediate"]:
            for k in scores: scores[k] = min(100, scores[k] + 10)

    # Calculate overall
    overall = (
        scores["hands_on"] * WEIGHTS["hands_on"] +
        scores["knowledge"] * WEIGHTS["knowledge"] +
        scores["architecture"] * WEIGHTS["architecture"] +
        scores["troubleshooting"] * WEIGHTS["troubleshooting"] +
        scores["security"] * WEIGHTS["security"] +
        scores["communication"] * WEIGHTS["communication"] +
        scores["cost_optimization"] * WEIGHTS["cost_optimization"]
    )
    
    confidence = calculate_confidence(source_types)
    
    missing = []
    if scores["hands_on"] < 50: missing.append("Practical projects or career experience")
    if scores["troubleshooting"] < 50: missing.append("Assessment or incident response evidence")
    if scores["architecture"] < 50: missing.append("System design projects or certifications")
    if scores["security"] < 50: missing.append("Security-focused implementation details")
    if scores["cost_optimization"] < 50: missing.append("Cost savings achievements")
    
    # Avoid max() on empty sequence
    highest_area = "knowledge"
    if any(v > 0 for v in scores.values()):
        highest_area = [k for k, v in scores.items() if v == max(scores.values())][0]

    explanation = f"Score derived from {len(relevant_evidences)} evidence records across {len(source_types)} source types. Highest performing area is {highest_area}." if relevant_evidences else "No evidence provided. Score relies purely on declared familiarity."

    eval_record = db.query(models.SkillEvaluation).filter(models.SkillEvaluation.skill_id == skill_id).first()
    if not eval_record:
        eval_record = models.SkillEvaluation(skill_id=skill_id)
        db.add(eval_record)
        
    eval_record.overall_score = int(overall)
    eval_record.knowledge_score = scores["knowledge"]
    eval_record.hands_on_score = scores["hands_on"]
    eval_record.troubleshooting_score = scores["troubleshooting"]
    eval_record.architecture_score = scores["architecture"]
    eval_record.security_score = scores["security"]
    eval_record.cost_score = scores["cost_optimization"]
    eval_record.communication_score = scores["communication"]
    eval_record.confidence_level = confidence
    eval_record.missing_evidence = json.dumps(missing)
    eval_record.explanation = explanation
    
    db.commit()
    db.refresh(eval_record)
    return eval_record
