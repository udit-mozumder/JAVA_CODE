"""Pydantic schemas for the User entity."""
import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr


class GoogleUserProfile(BaseModel):
    """Profile returned by Google's userinfo endpoint (FR-3)."""

    google_id: str
    email: EmailStr
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    google_id: str
    email: EmailStr
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: bool
    created_at: datetime
    last_login_at: Optional[datetime] = None
