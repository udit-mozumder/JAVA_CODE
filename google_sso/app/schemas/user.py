"""Pydantic schemas for User resources."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class GoogleProfile(BaseModel):
    google_id: str
    email: EmailStr
    display_name: str | None = None
    avatar_url: str | None = None


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    google_id: str
    email: EmailStr
    display_name: str | None = None
    avatar_url: str | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
