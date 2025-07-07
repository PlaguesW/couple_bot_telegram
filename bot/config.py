import os
from pydantic import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Настройки бота"""
    
    # Telegram Bot API Token
    BOT_TOKEN: str
    
    # Backend API настройки
    API_BASE_URL: str = "http://localhost:8000"
    API_VERSION: str = "v1"
    
    # Настройки логирования
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "bot.log"
    
    # Админы бота
    ADMIN_IDS: List[int] = []
    
    REDIS_URL: str = "redis://localhost:6379"
    
    
    # Настройки для развертывания
    WEBHOOK_URL: str = ""
    WEBHOOK_PATH: str = "/webhook"
    WEBAPP_HOST: str = "0.0.0.0"
    WEBAPP_PORT: int = 8080
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
    
    @property
    def api_url(self) -> str:
        """Полный URL для API"""
        return f"{self.API_BASE_URL}/api/{self.API_VERSION}"


settings = Settings()