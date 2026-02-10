import uuid
from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, Field

from app.models.connection import ConnectionStatus, AuthType


# ── Request Schemas ──────────────────────────────────────

class ConnectionCreate(BaseModel):
    integration_id: str = Field(..., example="gmail")
    display_name: str = Field(..., example="My Gmail Account")
    auth_type: AuthType
    credentials: dict = Field(
        ...,
        example={"api_key": "sk-xxxxx"},
        # This is the RAW credentials before encryption
        # Backend will encrypt before storing
    )
    metadata: Optional[dict] = None


class ConnectionUpdate(BaseModel):
    display_name: Optional[str] = None
    credentials: Optional[dict] = None
    # If user needs to update API key or reconnect


# ── Response Schemas ─────────────────────────────────────

class ConnectionResponse(BaseModel):
    id: uuid.UUID
    integration_id: str
    display_name: str
    auth_type: AuthType
    status: ConnectionStatus
    metadata: Optional[dict]
    token_expires_at: Optional[int]
    created_at: datetime
    updated_at: datetime

    # NOTICE: credentials_encrypted is NEVER returned
    # The client never sees stored credentials

    model_config = {"from_attributes": True}


class ConnectionListResponse(BaseModel):
    connections: list[ConnectionResponse]
    total: int