import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

from app.models.workflow import WorkflowStatus
from app.schemas.workflow_step import (
    WorkflowStepCreate,
    WorkflowStepResponse,
)


# ── Request Schemas ──────────────────────────────────────

class WorkflowCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    polling_interval: int = Field(default=300, ge=60, le=86400)
    # Steps can be added during creation or later
    steps: Optional[List[WorkflowStepCreate]] = None


class WorkflowUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[WorkflowStatus] = None
    polling_interval: Optional[int] = Field(None, ge=60, le=86400)
    steps: Optional[List[WorkflowStepCreate]] = None
    # When steps are provided, it REPLACES all existing steps
    # (simpler than individual step CRUD for a 2-week project)


# ── Response Schemas ─────────────────────────────────────

class WorkflowResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: Optional[str]
    status: WorkflowStatus
    webhook_token: str
    webhook_url: Optional[str] = None  # Computed field
    polling_interval: int
    last_polled_at: Optional[datetime]
    last_run_at: Optional[datetime]
    consecutive_failures: int
    steps: List[WorkflowStepResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class WorkflowListResponse(BaseModel):
    workflows: list[WorkflowResponse]
    total: int


class WorkflowSummary(BaseModel):
    """Lighter version for dashboard listing."""
    id: uuid.UUID
    name: str
    status: WorkflowStatus
    last_run_at: Optional[datetime]
    consecutive_failures: int
    step_count: int = 0
    trigger_integration: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}