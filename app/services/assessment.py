from sqlalchemy.orm import Session
from app import models
from app.services.llm.gateway import AIGateway
from app.services.evaluator import evaluate_skill
import json

class AssessmentEngine:
    def __init__(self, db: Session):
        self.db = db
        self.llm = AIGateway.get_llm_provider()

    def generate_assessment(self, skill_id: int, assessment_type: str) -> models.Assessment:
        skill = self.db.query(models.Skill).filter(models.Skill.id == skill_id).first()
        if not skill:
            return None
            
        system_msg = f"""You are TARS, creating a technical assessment for the skill: {skill.name}.
Assessment Type: {assessment_type}
Generate 3 challenging questions.
Format output strictly as JSON:
[
  {{"id": 1, "type": "free_text", "question": "..."}},
  {{"id": 2, "type": "free_text", "question": "..."}}
]"""
        
        prompt = f"Generate {assessment_type} questions for {skill.name}."
        response = self.llm.generate_response(prompt, system_message=system_msg)
        
        # Clean potential markdown
        content_json = response.replace('`json', '').replace('`', '').strip()
        
        assessment = models.Assessment(
            skill_id=skill_id,
            assessment_type=assessment_type,
            content=content_json
        )
        self.db.add(assessment)
        self.db.commit()
        self.db.refresh(assessment)
        return assessment

    def evaluate_attempt(self, user_id: int, attempt_id: int, user_responses_json: str) -> models.AssessmentAttempt:
        assessment = self.db.query(models.Assessment).filter(models.Assessment.id == attempt_id).first()
        if not assessment:
            return None
            
        system_msg = """You are TARS, evaluating a technical assessment.
You will receive the original questions and the user's answers.
Grade the attempt out of 100.
Provide constructive feedback.
Format output strictly as JSON:
{
  "score": 85,
  "feedback": "Good understanding of..."
}"""

        prompt = f"Questions:\n{assessment.content}\n\nUser Answers:\n{user_responses_json}"
        response = self.llm.generate_response(prompt, system_message=system_msg)
        
        try:
            clean_resp = response.replace('`json', '').replace('`', '').strip()
            data = json.loads(clean_resp)
            score = int(data.get("score", 0))
            feedback = data.get("feedback", "No feedback.")
        except:
            score = 0
            feedback = "Evaluation failed due to malformed LLM response."

        evidence_id = None
        if score >= 70:
            evidence = models.Evidence(
                user_id=user_id,
                description=f"Passed {assessment.assessment_type} assessment with score {score}/100",
                source_type="Assessment",
                url=None
            )
            self.db.add(evidence)
            self.db.commit()
            self.db.refresh(evidence)
            evidence_id = evidence.id
            
            # Trigger safe re-evaluation from Phase 7 engine
            evaluate_skill(assessment.skill_id, self.db)

        attempt = models.AssessmentAttempt(
            assessment_id=assessment.id,
            user_responses=user_responses_json,
            score=score,
            feedback=feedback,
            evidence_id=evidence_id
        )
        self.db.add(attempt)
        self.db.commit()
        self.db.refresh(attempt)
        
        return attempt
