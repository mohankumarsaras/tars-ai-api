import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    LLM_API_KEY: str = "sk-mock"
    LLM_BASE_URL: str = "https://api.openai.com/v1"
    LLM_MODEL: str = "gpt-4o-mini"
    PROJECT_NAME: str = "TARS"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///../data/database/tars.db")
    
    class Config:
        env_file = ".env"

settings = Settings()
