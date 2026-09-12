from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app import models, schemas
from app.database.database import get_db
from app.services import evaluator

router = APIRouter()

@router.get("/", response_model=List[schemas.Skill])
def get_skills(db: Session = Depends(get_db)):
    return db.query(models.Skill).all()

@router.post("/", response_model=schemas.Skill)
def add_skill(skill_in: schemas.SkillCreate, db: Session = Depends(get_db)):
    skill = models.Skill(**skill_in.model_dump())
    db.add(skill)
    db.commit()
    db.refresh(skill)
    return skill

@router.delete("/{item_id}")
def delete_skills(item_id: int, db: Session = Depends(get_db)):
    item = db.query(models.Skill).filter(models.Skill.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(item)
    db.commit()
    return {"status": "deleted"}

@router.get("/{item_id}/evaluation", response_model=schemas.SkillEvaluation)
def get_skill_evaluation(item_id: int, db: Session = Depends(get_db)):
    eval_record = db.query(models.SkillEvaluation).filter(models.SkillEvaluation.skill_id == item_id).first()
    if not eval_record:
        # Evaluate on the fly if missing
        eval_record = evaluator.evaluate_skill(item_id, db)
        if not eval_record:
            raise HTTPException(status_code=404, detail="Skill not found")
    return eval_record

@router.post("/{item_id}/evaluate", response_model=schemas.SkillEvaluation)
def trigger_skill_evaluation(item_id: int, db: Session = Depends(get_db)):
    eval_record = evaluator.evaluate_skill(item_id, db)
    if not eval_record:
        raise HTTPException(status_code=404, detail="Skill not found")
    return eval_record
