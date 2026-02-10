"""
A StepRun = the execution record for ONE step within ONE workflow run.

This is your OBSERVABILITY goldmine.
It records exactly what went in, what came out, and what happened.

The input_data and output_data fields are what enable the 
step-by-step debugging view that makes your portfolio shine.
"""

import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Text, Integer, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.models.base import Base, UUIDMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.workflow_run import WorkflowRun
    from app.models.workflow_step import WorkflowStep


class StepRunStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"    # Skipped because a prior filter said stop
    FILTERED = "filtered"  # This IS the filter step that said stop


class StepRun(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "step_runs"

    # ── Parent run ───────────────────────────────────────
    workflow_run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workflow_runs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # ── Which step definition this executed ──────────────
    workflow_step_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workflow_steps.id", ondelete="SET NULL"),
        nullable=True,
        # SET NULL because if step is deleted, we still want
        # historical run data
    )

    # ── Step position (denormalized for easy ordering) ───
    step_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    # ── Step identity (denormalized for history) ─────────
    # Even if the step definition changes later, 
    # we know what ran at this point in time
    integration_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    operation_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    # ── Execution status ─────────────────────────────────
    status: Mapped[StepRunStatus] = mapped_column(
        SQLEnum(StepRunStatus),
        default=StepRunStatus.PENDING,
        nullable=False,
    )

    # ── THE IMPORTANT FIELDS ─────────────────────────────

    # What data went INTO this step (after template resolution)
    # Example for "Send Email" step:
    # {"to": "john@gmail.com", "subject": "Hello", "body": "Hi there"}
    input_data: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
    )

    # What data came OUT of this step
    # Example for "Send Email" step:
    # {"message_id": "abc123", "status": "sent", "timestamp": "..."}
    output_data: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
    )

    # ── Error details ────────────────────────────────────
    error_message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    # ── Timing ───────────────────────────────────────────
    started_at: Mapped[Optional[datetime]] = mapped_column(
        nullable=True,
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        nullable=True,
    )

    # Duration in milliseconds (computed and stored for easy querying)
    duration_ms: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )

    # ── Relationships ────────────────────────────────────
    workflow_run: Mapped["WorkflowRun"] = relationship(
        "WorkflowRun",
        back_populates="step_runs",
    )
    workflow_step: Mapped[Optional["WorkflowStep"]] = relationship(
        "WorkflowStep",
    )

    def __repr__(self) -> str:
        return f"<StepRun #{self.step_order} {self.integration_id}.{self.operation_id} - {self.status}>"