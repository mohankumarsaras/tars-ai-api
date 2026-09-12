from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database.database import get_db
from app.services.llm.pipeline import ContextPipeline

router = APIRouter()

class ChatRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    response: str

@router.post("/ask", response_model=ChatResponse)
def ask_tars(request: ChatRequest, db: Session = Depends(get_db)):
    pipeline = ContextPipeline(db)
    answer = pipeline.execute(request.question)
    return {"response": answer}
