"""Pydantic schemas for tokens and OAuth flows."""
from pydantic import BaseModel


class LoginRedirect(BaseModel):
    authorization_url: str
    state: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = 'bearer'
    expires_in: int


class MessageResponse(BaseModel):
    detail: str
