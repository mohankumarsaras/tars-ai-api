from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app import models, schemas
from app.database.database import get_db
from app.services.search import get_search_provider

router = APIRouter()

@router.get("/", response_model=List[schemas.KnowledgeRecord])
def get_knowledge_records(
    user_id: int, 
    category: Optional[str] = None,
    source_type: Optional[str] = None,
    verification_status: Optional[str] = None,
    tags: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.KnowledgeRecord).filter(models.KnowledgeRecord.user_id == user_id)
    if category:
        query = query.filter(models.KnowledgeRecord.category == category)
    if source_type:
        query = query.filter(models.KnowledgeRecord.source_type == source_type)
    if verification_status:
        query = query.filter(models.KnowledgeRecord.verification_status == verification_status)
    if tags:
        query = query.filter(models.KnowledgeRecord.tags.like(f"%{tags}%"))
        
    return query.all()

@router.post("/", response_model=schemas.KnowledgeRecord)
def create_knowledge_record(record_in: schemas.KnowledgeRecordCreate, db: Session = Depends(get_db)):
    if record_in.source_type and record_in.source_type.lower() == "ai" and record_in.verification_status == "VERIFIED":
        record_in.verification_status = "NEEDS_REVIEW"
        
    record = models.KnowledgeRecord(**record_in.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    
    provider = get_search_provider(db)
    provider.index(
        entity_id=record.id,
        entity_type="Knowledge",
        title=record.title,
        content=record.content,
        verification_status=record.verification_status,
        source=record.source
    )
    db.commit()
    return record

@router.put("/{item_id}", response_model=schemas.KnowledgeRecord)
def update_knowledge_record(item_id: int, record_in: schemas.KnowledgeRecordUpdate, db: Session = Depends(get_db)):
    record = db.query(models.KnowledgeRecord).filter(models.KnowledgeRecord.id == item_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
        
    update_data = record_in.model_dump(exclude_unset=True)
    
    # AI restriction on update
    is_ai = update_data.get("source_type", record.source_type)
    if is_ai and is_ai.lower() == "ai" and update_data.get("verification_status") == "VERIFIED":
        raise HTTPException(status_code=400, detail="AI-generated content cannot be manually set to VERIFIED. Must be verified through another process.")
        
    for key, value in update_data.items():
        setattr(record, key, value)
        
    db.commit()
    db.refresh(record)
    
    provider = get_search_provider(db)
    provider.index(
        entity_id=record.id,
        entity_type="Knowledge",
        title=record.title,
        content=record.content,
        verification_status=record.verification_status,
        source=record.source
    )
    db.commit()
    return record

@router.delete("/{item_id}")
def delete_knowledge_record(item_id: int, db: Session = Depends(get_db)):
    record = db.query(models.KnowledgeRecord).filter(models.KnowledgeRecord.id == item_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    provider = get_search_provider(db)
    provider.delete(entity_id=item_id, entity_type="Knowledge")
    
    db.delete(record)
    db.commit()
    return {"status": "deleted"}

@router.get("/profile", response_model=schemas.UserProfile)
def get_knowledge_profile(db: Session = Depends(get_db)):
    # Get the default single user profile for personal knowledge
    profile = db.query(models.UserProfile).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile

@router.get("/skills", response_model=List[schemas.Skill])
def get_knowledge_skills(db: Session = Depends(get_db)):
    return db.query(models.Skill).all()

@router.get("/career", response_model=List[schemas.CareerExperience])
def get_knowledge_career(db: Session = Depends(get_db)):
    return db.query(models.CareerExperience).all()

@router.get("/education", response_model=List[schemas.Education])
def get_knowledge_education(db: Session = Depends(get_db)):
    return db.query(models.Education).all()

@router.get("/certifications", response_model=List[schemas.Certification])
def get_knowledge_certifications(db: Session = Depends(get_db)):
    return db.query(models.Certification).all()

@router.get("/evidence", response_model=List[schemas.Evidence])
def get_knowledge_evidence(db: Session = Depends(get_db)):
    return db.query(models.Evidence).all()
