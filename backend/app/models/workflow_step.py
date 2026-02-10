"""
A WorkflowStep = one node in the workflow.

step_order=1 is ALWAYS the trigger.
step_order=2+ are actions or filters.

The `config` JSONB field is WHERE THE MAGIC HAPPENS.
It stores the user's field mappings including template variables.

Example config for a "Send Email" action:
{
    "to": "{{trigger.sender_email}}",
    "subject": "Re: {{trigger.subject}}",
    "body": "Thanks for reaching out, {{trigger.sender_name}}!"
}

Example config for a "Filter" step:
{
    "field": "{{trigger.amount}}",
    "operator": "greater_than",
    "value": "100"
}

Example config for a "New Email" polling trigger:
{
    "label": "INBOX",
    "search_query": "is:unread"
}
"""

import uuid
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Integer, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.models.base import Base, UUIDMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.workflow import Workflow
    from app.models.connection import Connection


class StepType(str, enum.Enum):
    TRIGGER = "trigger"
    ACTION = "action"
    FILTER = "filter"
    DELAY = "delay"
    TRANSFORM = "transform"


class WorkflowStep(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "workflow_steps"

    # ── Parent workflow ──────────────────────────────────
    workflow_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workflows.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # ── Ordering ─────────────────────────────────────────
    # 1 = trigger, 2+ = actions/filters
    step_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    # ── Step classification ──────────────────────────────
    step_type: Mapped[StepType] = mapped_column(
        SQLEnum(StepType),
        nullable=False,
    )

    # ── Which integration + operation ────────────────────
    # integration_id: "gmail", "slack", "discord", "webhook"
    # operation_id: "new_email", "send_message", "add_row"
    # These map to your integration definition files
    integration_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    operation_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    # ── Which user connection to use for auth ────────────
    # Can be NULL for integrations that don't need auth
    # (e.g., generic webhook trigger, or Discord webhook action)
    connection_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("connections.id", ondelete="SET NULL"),
        nullable=True,
    )

    # ── Step configuration ───────────────────────────────
    # THE most important field. Contains:
    # - Field mappings with template variables
    # - Static configuration values
    # - Filter conditions
    # - Everything the step needs to execute
    config: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
    )

    # ── UI metadata ──────────────────────────────────────
    # Position on the canvas, custom label, etc.
    ui_metadata: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        default=dict,
        # e.g., {"position": {"x": 100, "y": 200}, "label": "Send Alert"}
    )

    # ── Relationships ────────────────────────────────────
    workflow: Mapped["Workflow"] = relationship(
        "Workflow",
        back_populates="steps",
    )
    connection: Mapped[Optional["Connection"]] = relationship(
        "Connection",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<WorkflowStep #{self.step_order} {self.integration_id}.{self.operation_id}>"