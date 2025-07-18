import os
from pydantic import BaseSettings
from typing import Optional, Dict, Any


class Settings(BaseSettings):
    """Application settings"""
    
    # API settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Green Certification"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "supersecretkey")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Database
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "green_certification")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    
    # Object Storage
    STORAGE_BUCKET: str = os.getenv("STORAGE_BUCKET", "green-certification")
    STORAGE_TYPE: str = os.getenv("STORAGE_TYPE", "local")  # local, s3, etc.
    
    # Gemma Model
    OLLAMA_API_URL: str = os.getenv("OLLAMA_API_URL", "http://localhost:11434/api")
    GEMMA_MODEL_NAME: str = os.getenv("GEMMA_MODEL_NAME", "gemma:3n")
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Cache
    REDIS_HOST: Optional[str] = os.getenv("REDIS_HOST")
    REDIS_PORT: Optional[int] = int(os.getenv("REDIS_PORT", "6379")) if os.getenv("REDIS_PORT") else None
    
    # File upload settings
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10 MB
    ALLOWED_IMAGE_TYPES: list = ["image/jpeg", "image/png", "image/tiff"]
    
    # Tree proximity settings
    DEFAULT_PROXIMITY_RADIUS: float = 5.0  # in meters
    
    # Geographic suitability settings
    GEO_DATA_PATH: str = os.getenv("GEO_DATA_PATH", "data/geo")
    
    # Scoring settings
    FRUIT_TREE_SCORE_BONUS: float = 2.0
    CROP_TREE_SCORE_NEUTRAL: float = 0.0
    OXYGEN_ABSORBING_PENALTY: float = -1.0
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()