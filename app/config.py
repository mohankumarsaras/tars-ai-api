import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    LLM_PROVIDER: str = "ollama"
    OLLAMA_BASE_URL: str = "http://ollama:11434/v1"
    OLLAMA_MODEL: str = "gpt-oss:20b"
    LLM_API_KEY: str = "ollama"
    LLM_BASE_URL: str = "https://api.openai.com/v1"
    LLM_MODEL: str = "gpt-oss:20b"
    PROJECT_NAME: str = "TARS"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///../data/database/tars.db")
    
    class Config:
        env_file = ".env"

settings = Settings()
