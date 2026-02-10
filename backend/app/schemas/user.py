import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


# ── Request Schemas (what comes IN from the client) ──────

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None


# ── Response Schemas (what goes OUT to the client) ───────

class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    full_name: Optional[str]
    is_active: bool
    is_verified: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse