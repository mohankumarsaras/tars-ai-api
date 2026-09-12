from sqlalchemy.orm import Session
from app import models
from app.services.llm.gateway import AIGateway
import json
import datetime

class LearningEngine:
    def __init__(self, db: Session):
        self.db = db
        self.llm = AIGateway.get_llm_provider()

    def ingest_and_classify(self, user_id: int, content: str, source: str) -> models.KnowledgeRecord:
        system_msg = """You are the TARS Knowledge Classifier.
Analyze the incoming knowledge content.
Determine the strictly defined knowledge type from this exact list:
- AUTHORITATIVE KNOWLEDGE
- PERSONAL KNOWLEDGE
- EXPERIENCE
- AI-GENERATED KNOWLEDGE

Also determine the most relevant skill name this applies to.
Respond in JSON:
{
    "knowledge_type": "...",
    "skill_name": "..."
}"""
        response = self.llm.generate_response(content, system_message=system_msg)
        
        try:
            clean_resp = response.replace('`json', '').replace('`', '').strip()
            data = json.loads(clean_resp)
            k_type = data.get("knowledge_type", "PERSONAL KNOWLEDGE")
            skill_name = data.get("skill_name", "General Knowledge")
        except:
            k_type = "AI-GENERATED KNOWLEDGE" # Failsafe lock
            skill_name = "General Knowledge"
            
        verification = "NEEDS_REVIEW" if k_type == "AI-GENERATED KNOWLEDGE" else "UNVERIFIED"
        
        # Store knowledge
        kr = models.KnowledgeRecord(
            user_id=user_id,
            title=f"Ingested from {source}",
            content=content,
            knowledge_type=k_type,
            verification_status=verification
        )
        self.db.add(kr)
        self.db.commit()
        self.db.refresh(kr)
        
        # Find or create skill
        skill = self.db.query(models.Skill).filter(models.Skill.name == skill_name).first()
        if not skill:
            skill = models.Skill(name=skill_name, category_id=1) # Fallback to first category
            self.db.add(skill)
            self.db.commit()
            self.db.refresh(skill)
            
        # Trigger learning loop if allowed
        if verification != "NEEDS_REVIEW":
            self.trigger_learning_loop(user_id, kr.id, skill.id)
            
        return kr

    def trigger_learning_loop(self, user_id: int, knowledge_id: int, skill_id: int):
        activity = models.LearningActivity(
            user_id=user_id,
            knowledge_id=knowledge_id,
            skill_id=skill_id,
            status="PENDING_ASSESSMENT"
        )
        self.db.add(activity)
        self.db.commit()
        
    def complete_activity(self, activity_id: int, attempt_id: int):
        activity = self.db.query(models.LearningActivity).filter(models.LearningActivity.id == activity_id).first()
        if not activity:
            return None
            
        attempt = self.db.query(models.AssessmentAttempt).filter(models.AssessmentAttempt.id == attempt_id).first()
        
        delta = 0.0
        if attempt and attempt.passed:
            delta = 2.5 # Mock deterministic delta from passing assessment
            
        activity.status = "COMPLETED"
        
        history = models.LearningHistory(
            user_id=activity.user_id,
            activity_id=activity.id,
            assessment_id=attempt_id if attempt else None,
            skill_improvement_delta=delta,
            next_recommendation="Proceed to Advanced " + activity.skill.name if activity.skill else "Review fundamentals."
        )
        self.db.add(history)
        self.db.commit()
        self.db.refresh(history)
        return history
