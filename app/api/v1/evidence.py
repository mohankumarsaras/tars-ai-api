from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app import models, schemas
from app.database.database import get_db

router = APIRouter()

@router.get("/", response_model=List[schemas.Evidence])
def get_evidence(user_id: int, db: Session = Depends(get_db)):
    return db.query(models.Evidence).filter(models.Evidence.user_id == user_id).all()

@router.post("/", response_model=schemas.Evidence)
def add_evidence(ev_in: schemas.EvidenceCreate, db: Session = Depends(get_db)):
    ev = models.Evidence(**ev_in.model_dump())
    db.add(ev)
    db.commit()
    db.refresh(ev)
    return ev

@router.delete("/{item_id}")
def delete_evidence(item_id: int, db: Session = Depends(get_db)):
    item = db.query(models.Evidence).filter(models.Evidence.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(item)
    db.commit()
    return {"status": "deleted"}
