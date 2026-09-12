import os

# Update config
config_path = r'e:\Dev\tars-ai\tars-ai-api\app\config.py'
with open(config_path, 'r') as f:
    config_content = f.read()

if 'LLM_API_KEY' not in config_content:
    config_content = config_content.replace(
        'class Settings(BaseSettings):',
        '''class Settings(BaseSettings):
    LLM_API_KEY: str = "sk-mock"
    LLM_BASE_URL: str = "https://api.openai.com/v1"
    LLM_MODEL: str = "gpt-4o-mini"'''
    )
    with open(config_path, 'w') as f:
        f.write(config_content)

# Update env example
env_example = r'e:\Dev\tars-ai\.env.example'
with open(env_example, 'a') as f:
    f.write('''
# LLM Configuration
LLM_API_KEY=your_api_key_here
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4o-mini
''')

# Create LLM Services
llm_dir = r'e:\Dev\tars-ai\tars-ai-api\app\services\llm'
os.makedirs(llm_dir, exist_ok=True)

with open(os.path.join(llm_dir, '__init__.py'), 'w') as f:
    f.write('from .base import LLMProvider\nfrom .external_provider import ExternalLLMProvider\n')

with open(os.path.join(llm_dir, 'base.py'), 'w') as f:
    f.write('''from abc import ABC, abstractmethod

class LLMProvider(ABC):
    @abstractmethod
    def generate_response(self, prompt: str, system_message: str = None) -> str:
        pass
''')

with open(os.path.join(llm_dir, 'external_provider.py'), 'w') as f:
    f.write('''import httpx
from .base import LLMProvider
from app.config import settings

class ExternalLLMProvider(LLMProvider):
    def __init__(self):
        self.api_key = settings.LLM_API_KEY
        self.base_url = settings.LLM_BASE_URL
        self.model = settings.LLM_MODEL

    def generate_response(self, prompt: str, system_message: str = None) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
            
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.2
        }
        
        try:
            # For phase 8 testing, if it's the mock key, we bypass network.
            if self.api_key == "sk-mock":
                return self._mock_response(prompt)
                
            with httpx.Client(timeout=30.0) as client:
                response = client.post(f"{self.base_url}/chat/completions", headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]
        except Exception as e:
            return f"FACTS: Failed to connect to LLM provider. Error: {str(e)}"
            
    def _mock_response(self, prompt: str) -> str:
        return """FACTS: You asked a question about career context.
EVIDENCE: The search provider returned records.
ANALYSIS: Based on the facts and evidence, this is a mock analysis.
OPINION: In my view, this looks good.
RECOMMENDATION: Replace sk-mock with a real key."""
''')

with open(os.path.join(llm_dir, 'pipeline.py'), 'w') as f:
    f.write('''from app.services.llm.external_provider import ExternalLLMProvider
from app.services.search import get_search_provider
from sqlalchemy.orm import Session
import json

class ContextPipeline:
    def __init__(self, db: Session):
        self.db = db
        self.llm = ExternalLLMProvider()
        self.search_provider = get_search_provider(db)
        
    def identify_intent(self, question: str) -> str:
        # Fast regex heuristic instead of burning a full LLM call
        q = question.lower()
        if any(w in q for w in ["history", "worked", "job", "career"]):
            return "CAREER_HISTORY"
        elif any(w in q for w in ["skill", "good at", "knowledge of", "rate"]):
            return "SKILL_ANALYSIS"
        elif any(w in q for w in ["recommend", "learn", "course"]):
            return "LEARNING_RECOMMENDATIONS"
        else:
            return "GENERAL_KNOWLEDGE"
            
    def build_context(self, intent: str, question: str) -> str:
        # Use SearchProvider to fetch exactly what is needed without dumping DB
        results = self.search_provider.search(question, limit=5)
        
        context_lines = []
        for res in results:
            context_lines.append(f"Source [{res['category']}]: {res['result']} - {res.get('snippet', '')}")
            
        if not context_lines:
            return "No specific personal data found in the knowledge base."
        return "\\n".join(context_lines)
        
    def execute(self, question: str) -> str:
        intent = self.identify_intent(question)
        context = self.build_context(intent, question)
        
        system_msg = """You are TARS, a Personal Career Intelligence System.
You MUST output your response strictly using these sections:
FACTS:
EVIDENCE:
ANALYSIS:
OPINION:
RECOMMENDATION:

Do not present opinions as facts. Rely primarily on the provided context."""

        prompt = f"User Intent: {intent}\\n\\nContext from Knowledge Base:\\n{context}\\n\\nUser Question: {question}"
        
        return self.llm.generate_response(prompt, system_message=system_msg)
''')

# Create API endpoint
api_path = r'e:\Dev\tars-ai\tars-ai-api\app\api\v1\chat.py'
with open(api_path, 'w') as f:
    f.write('''from fastapi import APIRouter, Depends, HTTPException
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
''')

# Wire router
router_path = r'e:\Dev\tars-ai\tars-ai-api\app\api\v1\router.py'
with open(router_path, 'r') as f:
    content = f.read()

if 'chat' not in content:
    content = content.replace(
        'from . import profile',
        'from . import profile, chat'
    )
    content += '\\napi_router.include_router(chat.router, prefix="/chat", tags=["chat"])'
    with open(router_path, 'w') as f:
        f.write(content)
        
print("Phase 8 setup complete.")
