import os
import httpx
from fastapi import APIRouter
from app.config import settings

router = APIRouter()

@router.get("/llm")
async def health_check_llm():
    provider = settings.LLM_PROVIDER.lower()
    
    if provider == "ollama":
        base_url = settings.OLLAMA_BASE_URL
        model = getattr(settings, "OLLAMA_MODEL", settings.LLM_MODEL)
        status = "Disconnected"
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{base_url}/models")
                if response.status_code == 200:
                    models = response.json().get("data", [])
                    model_exists = any(m.get("id") == model for m in models)
                    status = "Connected" if model_exists else "Model unavailable"
                else:
                    status = "Ollama is not running or the model is unavailable."
        except Exception:
            status = "Ollama is not running or the model is unavailable."

        return {
            "LLM Provider": "Ollama",
            "LLM Base URL": base_url,
            "LLM Model": model,
            "Ollama Status": status
        }
    
    return {
        "LLM Provider": provider,
        "LLM Base URL": os.getenv("LLM_BASE_URL"),
        "LLM Model": os.getenv("LLM_MODEL")
    }
