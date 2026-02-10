from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.core.database import get_db

app = FastAPI(title="FlowForge", version="0.1.0")


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