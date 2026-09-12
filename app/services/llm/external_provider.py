import httpx
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
