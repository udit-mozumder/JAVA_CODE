"""Pydantic schemas for authentication flows."""
from typing import Optional

from pydantic import BaseModel

from app.schemas.user import UserRead


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserRead


class LogoutResponse(BaseModel):
    detail: str = "Successfully logged out"


class ErrorResponse(BaseModel):
    """Structured error response (FR-9, AC-4)."""

    error: str
    detail: Optional[str] = None
