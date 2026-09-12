import os
import httpx
from app.services.llm.base import LLMProvider

class OpenAICompatibleProvider(LLMProvider):
    def __init__(self):
        self.api_key = os.getenv("LLM_API_KEY", "")
        self.base_url = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")
        self.model = os.getenv("LLM_MODEL", "gpt-4o-mini")

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

        with httpx.Client(timeout=120.0) as client:
            # Fallback mock for testing if no API key is provided
            if not self.api_key or self.api_key == "mock":
                return "Mocked External LLM Response based on Phase 8 constraints."
                
            response = client.post(f"{self.base_url}/chat/completions", headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
