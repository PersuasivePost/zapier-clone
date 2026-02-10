import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

from app.models.workflow_run import RunStatus
from app.schemas.step_run import StepRunResponse


# ── Response Schemas ─────────────────────────────────────
# (Runs are created by the system, not by the user directly)

class WorkflowRunResponse(BaseModel):
    id: uuid.UUID
    workflow_id: uuid.UUID
    status: RunStatus
    trigger_data: Optional[dict]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    error_message: Optional[str]
    error_step_order: Optional[int]
    attempt_number: int
    step_runs: List[StepRunResponse] = []
    created_at: datetime

    # Computed
    duration_ms: Optional[int] = None

    model_config = {"from_attributes": True}


class WorkflowRunListResponse(BaseModel):
    runs: list[WorkflowRunResponse]
    total: int


class WorkflowRunSummary(BaseModel):
    """For the runs list view — lighter payload."""
    id: uuid.UUID
    status: RunStatus
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    error_message: Optional[str]
    attempt_number: int
    steps_total: int = 0
    steps_completed: int = 0

    model_config = {"from_attributes": True}