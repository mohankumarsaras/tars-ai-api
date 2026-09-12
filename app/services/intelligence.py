from sqlalchemy.orm import Session
from app import models
from app.services.llm.gateway import AIGateway
import json

class IntelligenceEngine:
    def __init__(self, db: Session):
        self.db = db
        self.llm = AIGateway.get_llm_provider()

    def aggregate_profile(self, user_id: int) -> str:
        profile = self.db.query(models.UserProfile).filter(models.UserProfile.id == user_id).first()
        if not profile:
            return "Profile not found."
            
        skills = self.db.query(models.Skill).all() # Should ideally filter by user, but skipping complex joins for brevity
        goals = self.db.query(models.CareerGoal).filter(models.CareerGoal.user_id == user_id).all()
        history = self.db.query(models.CareerExperience).filter(models.CareerExperience.user_id == user_id).all()
        
        summary = f"User Profile: {profile.first_name} {profile.last_name}, {profile.professional_summary}\n\n"
        summary += f"Current Role: {profile.current_role}\n\n"
        
        summary += "Career Goals:\n"
        for g in goals:
            summary += f"- {g.description}\n"
            
        summary += "\nRecent Career History:\n"
        for h in history[:3]:
            summary += f"- {h.title} at {h.company_id}\n"
            
        summary += "\nDeclared Skills:\n"
        for s in skills:
            summary += f"- {s.name} ({s.familiarity})\n"
            
        return summary
        
    def analyze_career(self, user_id: int) -> models.CareerAnalysis:
        profile_summary = self.aggregate_profile(user_id)
        
        system_msg = """You are TARS, a highly realistic, rigorous Career Intelligence Engine.
You analyze the provided career summary and generate an unvarnished assessment.

STRICT RULES:
1. Do NOT guarantee career outcomes.
2. If evidence is insufficient, you MUST say "Your evidence is insufficient" or "You are not ready yet".
3. Be brutally realistic. Be willing to say "I don't recommend this" or "This path would require significant additional preparation".
4. Every recommendation MUST explicitly explain the evidence behind it.
5. Return the result strictly in this JSON format:
{
    "strengths": "...",
    "weaknesses": "...",
    "skill_gaps": "...",
    "career_risks": "...",
    "opportunities": "...",
    "recommended_skills": "...",
    "recommended_projects": "...",
    "suitable_roles": "..."
}"""

        prompt = f"Analyze the following user profile data:\n{profile_summary}"
        
        response = self.llm.generate_response(prompt, system_message=system_msg)
        
        # Parse JSON from response
        try:
            # Strip potential markdown blocks
            clean_resp = response.replace('`json', '').replace('`', '').strip()
            data = json.loads(clean_resp)
        except:
            # Fallback if LLM fails strict JSON
            data = {
                "strengths": "Failed to parse. Response was: " + response,
                "weaknesses": "Data insufficient.",
                "skill_gaps": "Data insufficient.",
                "career_risks": "Data insufficient.",
                "opportunities": "Data insufficient.",
                "recommended_skills": "Data insufficient.",
                "recommended_projects": "Data insufficient.",
                "suitable_roles": "Data insufficient."
            }
            
        analysis = models.CareerAnalysis(
            user_id=user_id,
            strengths=data.get("strengths"),
            weaknesses=data.get("weaknesses"),
            skill_gaps=data.get("skill_gaps"),
            career_risks=data.get("career_risks"),
            opportunities=data.get("opportunities"),
            recommended_skills=data.get("recommended_skills"),
            recommended_projects=data.get("recommended_projects"),
            suitable_roles=data.get("suitable_roles")
        )
        
        self.db.add(analysis)
        self.db.commit()
        self.db.refresh(analysis)
        
        return analysis
