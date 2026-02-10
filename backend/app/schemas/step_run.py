import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from app.models.step_run import StepRunStatus


class StepRunResponse(BaseModel):
    id: uuid.UUID
    workflow_run_id: uuid.UUID
    workflow_step_id: Optional[uuid.UUID]
    step_order: int
    integration_id: str
    operation_id: str
    status: StepRunStatus
    input_data: Optional[dict]
    output_data: Optional[dict]
    error_message: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    duration_ms: Optional[int]

    model_config = {"from_attributes": True}