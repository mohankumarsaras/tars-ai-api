from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database.database import get_db
from app import schemas, models
from app.services.intelligence import IntelligenceEngine

router = APIRouter()

@router.post("/analyze/{user_id}", response_model=schemas.CareerAnalysis)
def run_career_analysis(user_id: int, db: Session = Depends(get_db)):
    profile = db.query(models.UserProfile).filter(models.UserProfile.id == user_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="User not found")
        
    engine = IntelligenceEngine(db)
    return engine.analyze_career(user_id)

@router.get("/history/{user_id}", response_model=List[schemas.CareerAnalysis])
def get_analysis_history(user_id: int, db: Session = Depends(get_db)):
    return db.query(models.CareerAnalysis).filter(models.CareerAnalysis.user_id == user_id).all()
