import os
import httpx
from app.services.llm.base import LLMProvider

class OllamaProvider(LLMProvider):
    def __init__(self):
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/api")
        self.model = os.getenv("LLM_MODEL", "llama3")

    def generate_response(self, prompt: str, system_message: str = None) -> str:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "system": system_message if system_message else "",
            "stream": False,
            "options": {
                "temperature": 0.2
            }
        }

        with httpx.Client(timeout=120.0) as client:
            if self.base_url == "mock":
                return "Mocked Local Inference Response."
            
            response = client.post(f"{self.base_url}/generate", json=payload)
            response.raise_for_status()
            data = response.json()
            return data["response"]
