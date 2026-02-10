"""
A Connection = a user's authenticated link to an external service.

Example: 
  User "john@gmail.com" has:
    - Connection to Gmail (OAuth tokens stored)
    - Connection to Slack (webhook URL stored)  
    - Connection to OpenAI (API key stored)

credentials_encrypted stores DIFFERENT things depending on auth_type:
  - OAuth2: {"access_token": "...", "refresh_token": "...", "expires_at": 1234}
  - API Key: {"api_key": "sk-..."}
  - Webhook URL: {"webhook_url": "https://hooks.slack.com/..."}
  - Basic Auth: {"username": "...", "password": "..."}
"""

import uuid
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.models.base import Base, UUIDMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User


class ConnectionStatus(str, enum.Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    ERROR = "error"


class AuthType(str, enum.Enum):
    OAUTH2 = "oauth2"
    API_KEY = "api_key"
    WEBHOOK_URL = "webhook_url"
    BASIC_AUTH = "basic_auth"
    NONE = "none"


class Connection(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "connections"

    # ── Who owns this connection ─────────────────────────
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # ── Which integration this connects to ───────────────
    # This is a string ID like "gmail", "slack", "discord"
    # Maps to your integration definition files, NOT a DB table
    integration_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    # ── Display info ─────────────────────────────────────
    display_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        # e.g., "john@gmail.com" or "My Slack Workspace"
    )

    # ── Auth details ─────────────────────────────────────
    auth_type: Mapped[AuthType] = mapped_column(
        SQLEnum(AuthType),
        nullable=False,
    )

    # THIS IS THE MOST SENSITIVE FIELD IN YOUR ENTIRE DATABASE
    # Must be encrypted with Fernet/AES before storing
    # Contains: access_token, refresh_token, api_key, etc.
    credentials_encrypted: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    # ── Status tracking ──────────────────────────────────
    status: Mapped[ConnectionStatus] = mapped_column(
        SQLEnum(ConnectionStatus),
        default=ConnectionStatus.ACTIVE,
        nullable=False,
    )

    # ── Extra metadata (not sensitive) ───────────────────
    # e.g., {"account_email": "john@gmail.com", "workspace": "My Team"}
    metadata_: Mapped[Optional[dict]] = mapped_column(
        "metadata",
        JSONB,
        nullable=True,
        default=dict,
    )

    # ── OAuth specific fields ────────────────────────────
    token_expires_at: Mapped[Optional[int]] = mapped_column(
        nullable=True,
        # Unix timestamp when access_token expires
    )

    # ── Relationships ────────────────────────────────────
    user: Mapped["User"] = relationship(
        "User",
        back_populates="connections",
    )

    def __repr__(self) -> str:
        return f"<Connection {self.integration_id} - {self.display_name}>"