from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from app.database.database import get_db
from app import schemas, models
from app.services.learning import LearningEngine

router = APIRouter()

class IngestRequest(BaseModel):
    user_id: int
    content: str
    source: str

class CompleteRequest(BaseModel):
    attempt_id: int

@router.post("/ingest")
def ingest_knowledge(req: IngestRequest, db: Session = Depends(get_db)):
    engine = LearningEngine(db)
    kr = engine.ingest_and_classify(req.user_id, req.content, req.source)
    return {"message": "Ingested", "knowledge_id": kr.id, "type": kr.knowledge_type, "status": kr.verification_status}

@router.get("/queue/{user_id}", response_model=List[schemas.LearningActivity])
def get_pending_activities(user_id: int, db: Session = Depends(get_db)):
    return db.query(models.LearningActivity).filter(
        models.LearningActivity.user_id == user_id, 
        models.LearningActivity.status == "PENDING_ASSESSMENT"
    ).all()

@router.post("/complete/{activity_id}", response_model=schemas.LearningHistory)
def complete_learning_activity(activity_id: int, req: CompleteRequest, db: Session = Depends(get_db)):
    engine = LearningEngine(db)
    history = engine.complete_activity(activity_id, req.attempt_id)
    if not history:
        raise HTTPException(status_code=404, detail="Activity not found")
    return history
