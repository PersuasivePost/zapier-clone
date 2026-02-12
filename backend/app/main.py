from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from contextlib import asynccontextmanager

from app.core.database import get_db, test_connection
from app.core.config import get_settings
from app.api.auth import router as auth_router
from app.api.rest import router as rest_router
from app.integrations import register_all_integrations

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events."""
    # Startup
    print("🚀 Starting FlowForge backend...")
    await test_connection()
    
    # Register all integrations
    register_all_integrations()
    
    yield
    # Shutdown
    print("👋 Shutting down FlowForge backend...")


app = FastAPI(
    title="FlowForge",
    version="0.1.0",
    lifespan=lifespan
)

# Add Session middleware (required for OAuth)
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/api")
app.include_router(rest_router, prefix="/api")


@app.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    # Verify database connection
    result = await db.execute(text("SELECT 1"))
    
    # Verify all tables exist
    tables_query = await db.execute(
        text(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema = 'public'"
        )
    )
    tables = [row[0] for row in tables_query.fetchall()]

    return {
        "status": "healthy",
        "database": "connected",
        "tables": tables,
        "expected_tables": [
            "users",
            "connections", 
            "workflows",
            "workflow_steps",
            "workflow_runs",
            "step_runs",
        ],
    }