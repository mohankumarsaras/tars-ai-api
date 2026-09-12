from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app import models, schemas
from app.database.database import get_db

router = APIRouter()

@router.get("/", response_model=List[schemas.Education])
def get_education(user_id: int, db: Session = Depends(get_db)):
    return db.query(models.Education).filter(models.Education.user_id == user_id).all()

@router.post("/", response_model=schemas.Education)
def add_education(edu_in: schemas.EducationCreate, db: Session = Depends(get_db)):
    edu = models.Education(**edu_in.model_dump())
    db.add(edu)
    db.commit()
    db.refresh(edu)
    return edu

@router.delete("/{item_id}")
def delete_education(item_id: int, db: Session = Depends(get_db)):
    item = db.query(models.Education).filter(models.Education.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(item)
    db.commit()
    return {"status": "deleted"}
