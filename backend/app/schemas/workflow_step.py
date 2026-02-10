import uuid
from typing import Optional, Any
from pydantic import BaseModel, Field

from app.models.workflow_step import StepType


# ── Request Schemas ──────────────────────────────────────

class WorkflowStepCreate(BaseModel):
    step_order: int = Field(..., ge=1)
    step_type: StepType
    integration_id: str = Field(..., example="gmail")
    operation_id: str = Field(..., example="send_email")
    connection_id: Optional[uuid.UUID] = None
    config: dict = Field(
        default_factory=dict,
        example={
            "to": "{{trigger.sender_email}}",
            "subject": "Re: {{trigger.subject}}",
            "body": "Got your message!",
        },
    )
    ui_metadata: Optional[dict] = Field(
        default_factory=dict,
        example={
            "position": {"x": 250, "y": 100},
            "label": "Send Reply Email",
        },
    )


class WorkflowStepUpdate(BaseModel):
    step_order: Optional[int] = None
    integration_id: Optional[str] = None
    operation_id: Optional[str] = None
    connection_id: Optional[uuid.UUID] = None
    config: Optional[dict] = None
    ui_metadata: Optional[dict] = None


# ── Response Schemas ─────────────────────────────────────

class WorkflowStepResponse(BaseModel):
    id: uuid.UUID
    workflow_id: uuid.UUID
    step_order: int
    step_type: StepType
    integration_id: str
    operation_id: str
    connection_id: Optional[uuid.UUID]
    config: dict
    ui_metadata: Optional[dict]

    model_config = {"from_attributes": True}