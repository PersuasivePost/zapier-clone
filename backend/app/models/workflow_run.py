"""
A WorkflowRun = one execution of a workflow.

Every time a trigger fires (webhook received, poll finds new data),
a WorkflowRun is created and the execution engine processes it.

Status lifecycle:
  PENDING → RUNNING → SUCCESS
                    → FAILED
                    → FILTERED (trigger fired but filter stopped it)
"""

import uuid
from datetime import datetime
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import String, Text, ForeignKey, Enum as SQLEnum, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.models.base import Base, UUIDMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.workflow import Workflow
    from app.models.step_run import StepRun


class RunStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    FILTERED = "filtered"  # Stopped by a filter step
    TIMED_OUT = "timed_out"
    CANCELLED = "cancelled"


class WorkflowRun(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "workflow_runs"

    # ── Parent workflow ──────────────────────────────────
    workflow_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workflows.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # ── Execution status ─────────────────────────────────
    status: Mapped[RunStatus] = mapped_column(
        SQLEnum(RunStatus),
        default=RunStatus.PENDING,
        nullable=False,
        index=True,
    )

    # ── Trigger data ─────────────────────────────────────
    # The raw data that triggered this run
    # For webhook: the incoming JSON payload
    # For polling: the new item found
    trigger_data: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
    )

    # ── Timing ───────────────────────────────────────────
    started_at: Mapped[Optional[datetime]] = mapped_column(
        nullable=True,
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        nullable=True,
    )

    # ── Error tracking ───────────────────────────────────
    error_message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    error_step_order: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        # Which step failed? Useful for UI highlighting
    )

    # ── Retry tracking ───────────────────────────────────
    attempt_number: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
    )

    # ── Relationships ────────────────────────────────────
    workflow: Mapped["Workflow"] = relationship(
        "Workflow",
        back_populates="runs",
    )
    step_runs: Mapped[List["StepRun"]] = relationship(
        "StepRun",
        back_populates="workflow_run",
        cascade="all, delete-orphan",
        order_by="StepRun.step_order",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<WorkflowRun {self.id} - {self.status}>"