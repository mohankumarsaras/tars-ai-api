from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app import models, schemas
from app.database.database import get_db

router = APIRouter()

@router.get("/", response_model=List[schemas.CareerExperience])
def get_career(user_id: int, db: Session = Depends(get_db)):
    return db.query(models.CareerExperience).filter(models.CareerExperience.user_id == user_id).all()

@router.post("/", response_model=schemas.CareerExperience)
def add_career(career_in: schemas.CareerExperienceCreate, db: Session = Depends(get_db)):
    company_data = career_in.company.model_dump()
    company = db.query(models.Company).filter(models.Company.name == company_data['name']).first()
    if not company:
        company = models.Company(**company_data)
        db.add(company)
        db.commit()
        db.refresh(company)
        
    exp_data = career_in.model_dump(exclude={'company'})
    exp = models.CareerExperience(**exp_data, company_id=company.id)
    db.add(exp)
    db.commit()
    db.refresh(exp)
    return exp

@router.delete("/{item_id}")
def delete_career(item_id: int, db: Session = Depends(get_db)):
    item = db.query(models.CareerExperience).filter(models.CareerExperience.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(item)
    db.commit()
    return {"status": "deleted"}
