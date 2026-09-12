from abc import ABC, abstractmethod

class LLMProvider(ABC):
    @abstractmethod
    def generate_response(self, prompt: str, system_message: str = None) -> str:
        pass

class EmbeddingProvider(ABC):
    @abstractmethod
    def generate_embeddings(self, text: str) -> list[float]:
        pass
