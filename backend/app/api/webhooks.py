"""
Webhook receiver endpoint for triggering workflows.
"""

from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.workflow import Workflow, WorkflowStatus
from app.workers.tasks import execute_workflow

router = APIRouter(prefix="/api/webhooks", tags=["Webhooks"])


@router.post("/{webhook_token}")
async def receive_webhook(
    webhook_token: str,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Receive a webhook and trigger workflow execution.
    
    This is a PUBLIC endpoint (no authentication required).
    """
    # 1. Query workflow by webhook_token
    result = await db.execute(
        select(Workflow).where(Workflow.webhook_token == webhook_token)
    )
    workflow = result.scalar_one_or_none()
    
    # 2. Check if workflow exists
    if not workflow:
        raise HTTPException(status_code=404, detail="Webhook not found")
    
    # 3. Check if workflow is active
    if workflow.status != WorkflowStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Workflow is not active")
    
    # 4. Get request body as JSON (trigger data)
    trigger_data = await request.json()
    
    # 5. Send Celery task
    execute_workflow.delay(str(workflow.id), trigger_data)
    
    # 6. Return 200 OK immediately
    return {
        "status": "accepted",
        "message": "Workflow execution queued"
    }
