from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str
    DATABASE_URL_SYNC: Optional[str] = None

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Auth
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # Encryption for stored credentials
    ENCRYPTION_KEY: str

    # Celery / background
    CELERY_BROKER_URL: Optional[str] = None

    # Google OAuth
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/auth/google/callback"
    FRONTEND_URL: str = "http://localhost:5173"

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    s = Settings()
    # If sync DB URL wasn't provided explicitly, fall back to the async DATABASE_URL
    if not s.DATABASE_URL_SYNC:
        # If DATABASE_URL contains +asyncpg, prefer a sync variant; otherwise reuse it
        s.DATABASE_URL_SYNC = s.DATABASE_URL
    return s


# Create a global settings instance
settings = get_settings()

# Test user token (the one you've been using in test_e2e.py)
TEST_USER_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJmMDgxN2UxNi0wNTg3LTRjYWUtOWQwYy1jNTNmMGE3NDIzNDEiLCJleHAiOjE3NzEzMDczNzh9.BceSO7w5P-Cxg6oZ6b0ds4g0mFJGzJAJPUg7VbU-P0U"