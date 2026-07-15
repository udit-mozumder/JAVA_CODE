"""Auth context middleware and JWT bearer dependency."""
import uuid
from typing import Optional

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.core.security import JWTError, decode_token
from app.db.models.user import User
from app.db.session import get_db
from app.services.auth_service import AuthService
from app.utils.errors import AuthError

bearer_scheme = HTTPBearer(auto_error=False)


class AuthContextMiddleware(BaseHTTPMiddleware):
    """Attaches request-scoped context (client IP / user agent)."""

    async def dispatch(self, request: Request, call_next) -> Response:
        request.state.client_ip = request.client.host if request.client else None
        request.state.user_agent = request.headers.get("user-agent")
        return await call_next(request)


async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Validate the Bearer JWT, honouring the denylist (FR-8)."""
    if credentials is None:
        raise AuthError("Missing authentication credentials", status_code=401)

    token = credentials.credentials
    try:
        payload = decode_token(token)
    except JWTError:
        raise AuthError("Invalid or expired token", status_code=401)

    jti = payload.get("jti")
    sub = payload.get("sub")
    if not jti or not sub:
        raise AuthError("Malformed token", status_code=401)

    service = AuthService(db)
    if await service.is_denylisted(jti):
        raise AuthError("Token has been revoked", status_code=401)

    user = await service.get_user(uuid.UUID(sub))
    if user is None or not user.is_active:
        raise AuthError("User not found or inactive", status_code=401)

    request.state.jti = jti
    request.state.token = token
    return user
