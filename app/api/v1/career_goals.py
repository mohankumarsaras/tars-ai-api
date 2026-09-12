from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app import models, schemas
from app.database.database import get_db

router = APIRouter()

@router.get("/", response_model=List[schemas.CareerGoal])
def get_career_goals(user_id: int, db: Session = Depends(get_db)):
    return db.query(models.CareerGoal).filter(models.CareerGoal.user_id == user_id).all()

@router.post("/", response_model=schemas.CareerGoal)
def add_career_goal(goal_in: schemas.CareerGoalCreate, db: Session = Depends(get_db)):
    goal = models.CareerGoal(**goal_in.model_dump())
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return goal

@router.delete("/{item_id}")
def delete_career_goals(item_id: int, db: Session = Depends(get_db)):
    item = db.query(models.CareerGoal).filter(models.CareerGoal.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(item)
    db.commit()
    return {"status": "deleted"}
