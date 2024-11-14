from pydantic_settings import BaseSettings
from functools import lru_cache
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    database_url: str = os.getenv("DATABASE_URL")
    port: int = int(os.getenv("PORT", "8000"))
    env: str = os.getenv("ENV", "development")
    cors_origins: list = ["http://localhost:8000"]
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings()