import uuid
from typing import List, TYPE_CHECKING
from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.connection import Connection
    from app.models.workflow import Workflow


class User(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "users"

    # ── Auth Fields ──────────────────────────────────────
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # ── Profile Fields ───────────────────────────────────
    full_name: Mapped[str] = mapped_column(
        String(255),
        nullable=True,
    )

    # ── Status ───────────────────────────────────────────
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    # ── Relationships ────────────────────────────────────
    connections: Mapped[List["Connection"]] = relationship(
        "Connection",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    workflows: Mapped[List["Workflow"]] = relationship(
        "Workflow",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<User {self.email}>"