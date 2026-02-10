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