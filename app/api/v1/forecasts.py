from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from app.database.database import get_db
from app import schemas, models
from app.services.forecasting import ForecastingEngine

router = APIRouter()

class ForecastRequest(BaseModel):
    user_id: int
    query: str

@router.post("/simulate", response_model=schemas.ForecastScenario)
def simulate_career_path(req: ForecastRequest, db: Session = Depends(get_db)):
    engine = ForecastingEngine(db)
    scenario = engine.generate_forecast(req.user_id, req.query)
    return scenario

@router.get("/history/{user_id}", response_model=List[schemas.ForecastScenario])
def get_forecast_history(user_id: int, db: Session = Depends(get_db)):
    return db.query(models.ForecastScenario).filter(models.ForecastScenario.user_id == user_id).all()
