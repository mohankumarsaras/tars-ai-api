from app.services.llm.external_provider import ExternalLLMProvider
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
        try:
            results = self.search_provider.search(question, limit=5)
        except Exception as e:
            print(f"Search provider failed (FTS5 missing?): {e}")
            results = []
        
        context_lines = []
        for res in results:
            context_lines.append(f"Source [{res['category']}]: {res['result']} - {res.get('snippet', '')}")
            
        if not context_lines:
            return "No specific personal data found in the knowledge base."
        return "\n".join(context_lines)
        
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

        prompt = f"User Intent: {intent}\n\nContext from Knowledge Base:\n{context}\n\nUser Question: {question}"
        
        return self.llm.generate_response(prompt, system_message=system_msg)
