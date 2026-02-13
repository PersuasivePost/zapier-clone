import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.auth import get_current_user
from app.schemas.workflow import (
    WorkflowCreate,
    WorkflowUpdate,
    WorkflowResponse,
)
from app.services.workflow_service import (
    create_workflow,
    get_workflows,
    get_workflow,
    update_workflow,
    delete_workflow,
    toggle_workflow,
)

router = APIRouter(prefix="/workflows", tags=["Workflows"])


@router.post("/", response_model=WorkflowResponse)
async def api_create_workflow(
    body: WorkflowCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    try:
        wf = await create_workflow(db, uuid.UUID(user["id"]), body)
        return wf
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[WorkflowResponse])
async def api_list_workflows(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    wfs = await get_workflows(db, uuid.UUID(user["id"]))
    return wfs


@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def api_get_workflow(
    workflow_id: str,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    try:
        wf = await get_workflow(db, uuid.UUID(user["id"]), uuid.UUID(workflow_id))
        return wf
    except ValueError:
        raise HTTPException(status_code=404, detail="Workflow not found")


@router.put("/{workflow_id}", response_model=WorkflowResponse)
async def api_update_workflow(
    workflow_id: str,
    body: WorkflowUpdate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    try:
        wf = await update_workflow(db, uuid.UUID(user["id"]), uuid.UUID(workflow_id), body)
        return wf
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{workflow_id}")
async def api_delete_workflow(
    workflow_id: str,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    try:
        await delete_workflow(db, uuid.UUID(user["id"]), uuid.UUID(workflow_id))
        return {"deleted": True}
    except ValueError:
        raise HTTPException(status_code=404, detail="Workflow not found")


@router.post("/{workflow_id}/toggle", response_model=WorkflowResponse)
async def api_toggle_workflow(
    workflow_id: str,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    try:
        wf = await toggle_workflow(db, uuid.UUID(user["id"]), uuid.UUID(workflow_id))
        return wf
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
