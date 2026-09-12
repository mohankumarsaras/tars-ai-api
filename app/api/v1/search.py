from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.database.database import get_db
from app.services.search import get_search_provider

router = APIRouter()

@router.get("/")
def search(query: str = Query(..., min_length=1), limit: int = 10, db: Session = Depends(get_db)):
    provider = get_search_provider(db)
    results = provider.search(query, limit=limit)
    return results
