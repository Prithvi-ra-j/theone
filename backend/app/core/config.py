"""Configuration settings for the Dristhi application."""

import os
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, PostgresDsn, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    PROJECT_NAME: str = "Dristhi"
    VERSION: str = "0.1.0"
    DESCRIPTION: str = "AI-Powered Career & Life Improvement Platform"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"
    

    # Security
    SECRET_KEY: str = "your-super-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    JWT_ALGORITHM: str = "HS256"

    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8000",
    ]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        """Parse CORS origins from string or list."""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # Database
    DATABASE_URL: PostgresDsn = "postgresql://postgres:password@localhost:5432/dristhi"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 30
    DATABASE_POOL_TIMEOUT: int = 30

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_POOL_SIZE: int = 10

    # AI Services
    ENABLE_AI_FEATURES: bool = True  # Set to True to enable AI features
    LLM_PROVIDER: str = "api"  # or "api"
    # When True, force the AI service to use local fallback responses and
    # avoid any calls to external LLM providers. Useful for offline or
    # smoke-test scenarios where external auth is not available.
    AI_FORCE_FALLBACK: bool = False
    # When True, force the AI service to return local fallback responses and
    # avoid making any external network calls to LLM providers (useful for
    # offline development or when you don't want to configure API keys).
    # Development helpers
    # When True, will enable mock endpoints for frontend development.
    # Default to False so real routes are used unless developer explicitly enables mocks
    ENABLE_MOCK_ENDPOINTS: bool = False
    # When True, include a final compatibility catch-all that returns 501 for
    # unimplemented endpoints. Keep this off in production by default.
    ENABLE_COMPATIBILITY_STUBS: bool = False
    
   
    # LLM API settings - using environment variables for security
    API_LLM_API_KEY: str = os.getenv("API_LLM_API_KEY", "")
    API_LLM_BASE_URL: str = os.getenv("API_LLM_BASE_URL", "https://openrouter.ai/api/v1")
    API_LLM_MODEL: str = os.getenv("API_LLM_MODEL", "x-ai/grok-4-fast:free")

    # Gemini (Google) REST API settings (optional)
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_BASE_URL: str = "https://generativelanguage.googleapis.com/v1"
    GEMINI_MODEL: str = "models/text-bison-001"


    FAISS_INDEX_PATH: str = "./data/faiss_index"
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    LOG_FILE_PATH: str = "./logs/dristhi.log"

    class Config:
        """Pydantic config."""

        case_sensitive = True
        env_file = ".env"
        extra = "allow"   


# Create settings instance
settings = Settings()