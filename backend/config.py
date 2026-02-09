from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    OPENAI_API_KEY: str
    MODEL: str = "gpt-4o-mini"
    
    class Config:
        env_file = str(Path(__file__).parent.parent / ".env")
        env_file_encoding = 'utf-8'
        extra = 'ignore'  # Ignore extra fields from .env

settings = Settings()
