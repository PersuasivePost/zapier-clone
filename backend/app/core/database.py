from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)
from urllib.parse import parse_qsl, urlencode

from app.core.config import get_settings

settings = get_settings()

# Ensure the URL uses an async driver. If the user supplied a sync URL
# (postgresql://...) convert it to the asyncpg form required by SQLAlchemy's
# asyncio extension (postgresql+asyncpg://...). This prevents the
# "loaded 'psycopg2' is not async" error.
raw_url = settings.DATABASE_URL
if raw_url.startswith("postgresql://") and "+asyncpg" not in raw_url:
    async_url = raw_url.replace("postgresql://", "postgresql+asyncpg://", 1)
else:
    async_url = raw_url

# Parse and remove query params that asyncpg.connect doesn't accept directly
# (for example `sslmode` and `channel_binding`). If sslmode is present,
# pass ssl=True via connect_args instead.
connect_args = {}
if "?" in async_url:
    base, qs = async_url.split("?", 1)
    params = dict(parse_qsl(qs))
    if "sslmode" in params:
        # Ask asyncpg to use SSL. For stricter setups, supply an SSLContext
        connect_args["ssl"] = True
        params.pop("sslmode", None)
    # Remove channel_binding if present; asyncpg doesn't accept it as kw
    params.pop("channel_binding", None)
    # Rebuild URL without removed params
    if params:
        async_url = f"{base}?{urlencode(params)}"
    else:
        async_url = base

engine = create_async_engine(
    async_url,
    echo=True,  # Turn off in production
    connect_args=connect_args or None,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()