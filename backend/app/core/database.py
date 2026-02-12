from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)
from sqlalchemy import text
from sqlalchemy.pool import NullPool
from urllib.parse import parse_qsl, urlencode
import ssl

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
ssl_context = None

if "?" in async_url:
    base, qs = async_url.split("?", 1)
    params = dict(parse_qsl(qs))
    
    # Handle SSL for Neon (required for Neon databases)
    if "sslmode" in params:
        sslmode = params.pop("sslmode")
        if sslmode in ("require", "verify-ca", "verify-full"):
            # Create SSL context for secure connections
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            connect_args["ssl"] = ssl_context
    
    # Remove channel_binding if present; asyncpg doesn't accept it as kw
    params.pop("channel_binding", None)
    
    # Rebuild URL without removed params
    if params:
        async_url = f"{base}?{urlencode(params)}"
    else:
        async_url = base
else:
    # If no sslmode in URL but using Neon, enable SSL by default
    if "neon.tech" in async_url or "neon.postgres" in async_url:
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        connect_args["ssl"] = ssl_context

# Add timeout and connection settings for Neon
connect_args["timeout"] = 30  # Connection timeout
connect_args["command_timeout"] = 30  # Command timeout
connect_args["server_settings"] = {
    "application_name": "flowforge_backend",
    "jit": "off",  # Disable JIT for better cold start performance
}

engine = create_async_engine(
    async_url,
    echo=True,  # Turn off in production
    connect_args=connect_args,
    pool_pre_ping=True,  # Verify connections before using
    pool_size=10,  # Increase pool size for Neon
    max_overflow=20,  # Allow more overflow connections
    pool_recycle=3600,  # Recycle connections every hour (Neon closes idle connections)
    pool_timeout=30,  # Timeout for getting connection from pool
    pool_use_lifo=True,  # Use LIFO for better connection reuse with Neon
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_db():
    """Dependency to get async database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


async def test_connection():
    """Test database connection - useful for startup checks."""
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(text("SELECT 1"))
            result.scalar()
            print("✅ Database connection successful!")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False