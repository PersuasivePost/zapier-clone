"""
A Workflow = a "Zap". The core entity.

It has:
  - A trigger (always step_order=1)
  - One or more actions (step_order=2, 3, 4...)
  - Optional filters between steps

Status lifecycle:
  DRAFT → ACTIVE → PAUSED → ACTIVE → ...
                  → ERROR (auto-paused after repeated failures)
"""

import uuid
import secrets
from datetime import datetime
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import String, Text, Integer, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.models.base import Base, UUIDMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.workflow_step import WorkflowStep
    from app.models.workflow_run import WorkflowRun


class WorkflowStatus(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    ERROR = "error"


class Workflow(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "workflows"

    # ── Owner ────────────────────────────────────────────
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # ── Basic info ───────────────────────────────────────
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        default="Untitled Workflow",
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    # ── Status ───────────────────────────────────────────
    status: Mapped[WorkflowStatus] = mapped_column(
        SQLEnum(WorkflowStatus),
        default=WorkflowStatus.DRAFT,
        nullable=False,
        index=True,
    )

    # ── Webhook Configuration ────────────────────────────
    # Unique token for this workflow's webhook URL
    # URL will be: POST /api/webhooks/{webhook_token}
    # Generated automatically, user never sees the internal workflow ID
    webhook_token: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        index=True,
        default=lambda: secrets.token_urlsafe(32),
        nullable=False,
    )

    # ── Polling Configuration ────────────────────────────
    # How often to poll (in seconds). Only used for polling triggers.
    polling_interval: Mapped[int] = mapped_column(
        Integer,
        default=300,  # 5 minutes
        nullable=False,
    )
    last_polled_at: Mapped[Optional[datetime]] = mapped_column(
        nullable=True,
    )

    # ── Execution tracking ───────────────────────────────
    last_run_at: Mapped[Optional[datetime]] = mapped_column(
        nullable=True,
    )
    consecutive_failures: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    # ── Relationships ────────────────────────────────────
    user: Mapped["User"] = relationship(
        "User",
        back_populates="workflows",
    )
    steps: Mapped[List["WorkflowStep"]] = relationship(
        "WorkflowStep",
        back_populates="workflow",
        cascade="all, delete-orphan",
        order_by="WorkflowStep.step_order",
        lazy="selectin",
    )
    runs: Mapped[List["WorkflowRun"]] = relationship(
        "WorkflowRun",
        back_populates="workflow",
        cascade="all, delete-orphan",
        order_by="WorkflowRun.started_at.desc()",
        lazy="noload",  # Don't auto-load runs, could be thousands
    )

    def __repr__(self) -> str:
        return f"<Workflow {self.name} ({self.status})>"