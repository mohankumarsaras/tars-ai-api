from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app import models, schemas
from app.database.database import get_db

router = APIRouter()

@router.get("/", response_model=List[schemas.Certification])
def get_certifications(user_id: int, db: Session = Depends(get_db)):
    return db.query(models.Certification).filter(models.Certification.user_id == user_id).all()

@router.post("/", response_model=schemas.Certification)
def add_certification(cert_in: schemas.CertificationCreate, db: Session = Depends(get_db)):
    cert = models.Certification(**cert_in.model_dump())
    db.add(cert)
    db.commit()
    db.refresh(cert)
    return cert

@router.delete("/{item_id}")
def delete_certification(item_id: int, db: Session = Depends(get_db)):
    item = db.query(models.Certification).filter(models.Certification.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(item)
    db.commit()
    return {"status": "deleted"}
