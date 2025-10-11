"""Configuration settings for the Dristhi application."""

import os
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, AnyUrl, field_validator
from loguru import logger
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

    # Optional canonical frontend URL (set per-deployment in environment)
    # Use this to advertise or validate the expected frontend origin in logs
    # and health endpoints. Do not hard-code sensitive or preview URLs in
    # source control; set them via environment variables in your hosting
    # provider (Vercel / Render) instead.
    FRONTEND_URL: Optional[AnyHttpUrl] = None

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        """Parse CORS origins from string or list."""
        # Defensive parsing: env var may be provided as a comma-separated string,
        # may include the key name (e.g. "BACKEND_CORS_ORIGINS=..."), or be
        # wrapped in quotes. Normalize these cases to a clean list of origins.
        if isinstance(v, str):
            s = v.strip()
            # If the string looks like an env assignment, strip the prefix
            if "=" in s and not s.startswith("[") and not s.startswith("http"):
                # handle cases like 'BACKEND_CORS_ORIGINS=https://a,https://b'
                parts = s.split("=", 1)
                if len(parts) == 2 and parts[1].strip():
                    s = parts[1].strip()
            # Strip surrounding quotes if present
            if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
                s = s[1:-1]
            if s.startswith("["):
                # Let pydantic parse a JSON-style list
                return s
            # Split on commas and remove empty entries
            return [i.strip() for i in s.split(",") if i.strip()]
        elif isinstance(v, list):
            # Already a list; return as-is
            return v
        raise ValueError(v)

    # Database
    # Use AnyUrl to support both Postgres and SQLite URLs
    DATABASE_URL: AnyUrl = "sqlite:///./data/app.db"
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

    # Normalize DATABASE_URL: if env var is set but empty, fallback to default SQLite
    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def _default_db_if_empty(cls, v: Any) -> Any:
        if v is None:
            return "sqlite:///./data/app.db"
        if isinstance(v, str) and v.strip() == "":
            return "sqlite:///./data/app.db"
        return v

    def model_post_init(self, __context: Any) -> None:
        """Post-init hook to append FRONTEND_URL into CORS origins when set.

        This is a convenience: if a deployment sets FRONTEND_URL in the
        environment (for example, the public Vercel frontend URL), the
        value will be appended to BACKEND_CORS_ORIGINS so it will be
        accepted by the FastAPI CORS middleware without requiring manual
        duplication of the origin list in environment variables.
        """
        try:
            frontend = getattr(self, "FRONTEND_URL", None)
            if frontend:
                # Normalize existing BACKEND_CORS_ORIGINS entries (strip trailing
                # slashes) to avoid exact-match mismatches against the browser's
                # Origin header (which never includes a trailing slash).
                try:
                    normalized = [str(u).rstrip("/") for u in (self.BACKEND_CORS_ORIGINS or [])]
                    self.BACKEND_CORS_ORIGINS = normalized
                except Exception:
                    # Fall back to original if normalization fails
                    pass

                # Normalize FRONTEND_URL value and append if not present
                fr_str = str(frontend).rstrip("/")
                existing = {str(u).rstrip("/") for u in (self.BACKEND_CORS_ORIGINS or [])}
                if fr_str not in existing:
                    self.BACKEND_CORS_ORIGINS.append(fr_str)
                    logger.info("Configured FRONTEND_URL appended to BACKEND_CORS_ORIGINS: {}", fr_str)
                else:
                    logger.debug("FRONTEND_URL already present in BACKEND_CORS_ORIGINS: {}", fr_str)
        except Exception:
            # Defensive: do not break startup if post-init logic fails
            logger.exception("Error while appending FRONTEND_URL to BACKEND_CORS_ORIGINS")


# Create settings instance
settings = Settings()