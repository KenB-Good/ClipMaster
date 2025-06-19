
"""
Configuration settings for ClipMaster backend
"""
import os
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    """Application settings"""
    
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "ClipMaster"
    ALLOWED_HOSTS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # Database
    DATABASE_URL: str = Field(default="postgresql://clipmaster:clipmaster_password@localhost:5432/clipmaster")
    
    # Redis
    REDIS_URL: str = Field(default="redis://localhost:6379/0")
    CELERY_BROKER_URL: str = Field(default="redis://localhost:6379/0")
    CELERY_RESULT_BACKEND: str = Field(default="redis://localhost:6379/0")
    
    # File Storage
    UPLOAD_DIR: str = Field(default="/home/ubuntu/clipmaster/storage/uploads")
    CLIPS_DIR: str = Field(default="/home/ubuntu/clipmaster/storage/clips")
    TEMP_DIR: str = Field(default="/home/ubuntu/clipmaster/storage/temp")
    MAX_FILE_SIZE: int = Field(default=5 * 1024 * 1024 * 1024)  # 5GB
    
    # AI Models
    WHISPER_MODEL: str = Field(default="base")
    WHISPER_DEVICE: str = Field(default="cuda")
    ENABLE_GPU: bool = Field(default=True)
    
    # Twitch API
    TWITCH_CLIENT_ID: str = Field(default="")
    TWITCH_CLIENT_SECRET: str = Field(default="")
    TWITCH_REDIRECT_URI: str = Field(default="http://localhost:3000/twitch/callback")
    
    # Processing
    DEFAULT_CLIP_DURATION: int = Field(default=30)
    MIN_HIGHLIGHT_DURATION: int = Field(default=5)
    MAX_HIGHLIGHT_DURATION: int = Field(default=120)
    CONFIDENCE_THRESHOLD: float = Field(default=0.7)
    
    # Cleanup
    AUTO_CLEANUP_ENABLED: bool = Field(default=True)
    AUTO_CLEANUP_DAYS: int = Field(default=30)
    AUTO_CLEANUP_THRESHOLD: float = Field(default=0.8)  # 80% storage threshold
    
    # Security
    SECRET_KEY: str = Field(default="clipmaster-secret-key-please-change-in-production")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=60 * 24 * 8)  # 8 days
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO")
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create settings instance
settings = Settings()

# Ensure directories exist
for directory in [settings.UPLOAD_DIR, settings.CLIPS_DIR, settings.TEMP_DIR]:
    os.makedirs(directory, exist_ok=True)
