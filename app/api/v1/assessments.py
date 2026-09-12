from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from app.database.database import get_db
from app import schemas, models
from app.services.assessment import AssessmentEngine

router = APIRouter()

class GenerateRequest(BaseModel):
    skill_id: int
    assessment_type: str

class SubmitRequest(BaseModel):
    user_id: int
    user_responses: str  # JSON string

@router.post("/generate", response_model=schemas.Assessment)
def generate_assessment(req: GenerateRequest, db: Session = Depends(get_db)):
    engine = AssessmentEngine(db)
    assessment = engine.generate_assessment(req.skill_id, req.assessment_type)
    if not assessment:
        raise HTTPException(status_code=404, detail="Skill not found")
    return assessment

@router.post("/{assessment_id}/submit", response_model=schemas.AssessmentAttempt)
def submit_attempt(assessment_id: int, req: SubmitRequest, db: Session = Depends(get_db)):
    engine = AssessmentEngine(db)
    attempt = engine.evaluate_attempt(req.user_id, assessment_id, req.user_responses)
    if not attempt:
        raise HTTPException(status_code=404, detail="Assessment not found")
    return attempt
