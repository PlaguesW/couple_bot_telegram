import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Telegram Bot
    BOT_TOKEN: str
    
    # Backend API
    API_BASE_URL: str = "http://localhost:8000"
    API_TIMEOUT: int = 30
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    # Redis (For future use)
    REDIS_URL: Optional[str] = None
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()