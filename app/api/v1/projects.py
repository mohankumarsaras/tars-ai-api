from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app import models, schemas
from app.database.database import get_db

router = APIRouter()

@router.get("/", response_model=List[schemas.Project])
def get_projects(user_id: int, db: Session = Depends(get_db)):
    return db.query(models.Project).filter(models.Project.user_id == user_id).all()

@router.post("/", response_model=schemas.Project)
def add_project(project_in: schemas.ProjectCreate, db: Session = Depends(get_db)):
    proj_data = project_in.model_dump(exclude={'skill_ids'})
    proj = models.Project(**proj_data)
    if project_in.skill_ids:
        skills = db.query(models.Skill).filter(models.Skill.id.in_(project_in.skill_ids)).all()
        proj.skills = skills
    db.add(proj)
    db.commit()
    db.refresh(proj)
    return proj

@router.delete("/{item_id}")
def delete_projects(item_id: int, db: Session = Depends(get_db)):
    item = db.query(models.Project).filter(models.Project.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(item)
    db.commit()
    return {"status": "deleted"}
