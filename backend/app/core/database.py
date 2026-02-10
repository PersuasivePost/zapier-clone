from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from .config import settings

# Use DATABASE_URL from environment (.env) when available, otherwise fall back to example DSN
DEFAULT_DATABASE_URL = "postgresql+asyncpg://user:pass@localhost/dbname"
DATABASE_URL = settings.database_url or DEFAULT_DATABASE_URL

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
