import os
from app.services.llm.base import LLMProvider, EmbeddingProvider
from app.services.llm.providers.openai_compatible import OpenAICompatibleProvider
from app.services.llm.providers.ollama_provider import OllamaProvider

class AIGateway:
    """
    Central router determining whether TARS communicates with an external provider
    or a separate local AI server (e.g., Ollama/vLLM) over the internal network.
    """
    
    @staticmethod
    def get_llm_provider() -> LLMProvider:
        provider_type = os.getenv("AI_PROVIDER_TYPE", "external").lower()
        
        if provider_type == "ollama":
            return OllamaProvider()
        # Fallback to external API (OpenAI/Anthropic compatible)
        return OpenAICompatibleProvider()
        
    @staticmethod
    def get_embedding_provider() -> EmbeddingProvider:
        # Stub for Phase 17+ (Qdrant/Vector support)
        raise NotImplementedError("Embedding provider routing not yet configured.")
