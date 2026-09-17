import os
import httpx
from app.config import settings
from app.services.llm.base import LLMProvider

class OllamaProvider(LLMProvider):
    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.model = getattr(settings, "OLLAMA_MODEL", settings.LLM_MODEL)
        self.api_key = "ollama"

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
            if self.base_url == "mock":
                return "Mocked Local Inference Response."
            
            try:
                response = client.post(f"{self.base_url}/chat/completions", headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    return f"FACTS: The Ollama model '{self.model}' was not found. Please wait for the download to finish."
                return f"FACTS: Ollama returned an error: {e}"
            except Exception as e:
                return f"FACTS: Failed to connect to Ollama. Error: {e}"
