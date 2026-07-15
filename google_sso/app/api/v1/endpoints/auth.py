"""Authentication endpoints implementing the Google SSO flow."""
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import safe_decode
from app.db.models.user import User
from app.db.repositories.auth_audit_repository import AuthAuditRepository
from app.db.repositories.token_denylist_repository import TokenDenylistRepository
from app.db.repositories.user_repository import UserRepository
from app.db.session import get_db
from app.middleware.auth_middleware import get_current_user
from app.schemas.token import LoginRedirect, MessageResponse, TokenResponse
from app.schemas.user import UserRead
from app.services.auth_service import AuthService
from app.services.google_oauth_service import GoogleOAuthError, GoogleOAuthService

router = APIRouter()

STATE_COOKIE = 'oauth_state'


def _build_service(db: AsyncSession) -> AuthService:
    return AuthService(
        users=UserRepository(db),
        audit=AuthAuditRepository(db),
        denylist=TokenDenylistRepository(db),
        google=GoogleOAuthService(),
    )


@router.get('/login/google', response_model=LoginRedirect)
async def login_google() -> LoginRedirect:
    google = GoogleOAuthService()
    state = google.generate_state()
    url = google.build_authorization_url(state)
    response = LoginRedirect(authorization_url=url, state=state)
    return response


@router.get('/callback/google', response_model=TokenResponse)
async def callback_google(
    request: Request,
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    ip = request.client.host if request.client else None
    ua = request.headers.get('user-agent')
    service = _build_service(db)
    cookie_state = request.cookies.get(STATE_COOKIE)
    if error:
        await service.record_failure(f'google_error:{error}', ip, ua)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Google authentication failed')
    if cookie_state is not None and state is not None and cookie_state != state:
        await service.record_failure('state_mismatch', ip, ua)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid state parameter')
    if not code:
        await service.record_failure('missing_code', ip, ua)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Authorization code is required')
    try:
        token, expires_in = await service.complete_login(code, ip, ua)
    except GoogleOAuthError:
        await service.record_failure('oauth_exchange_failed', ip, ua)
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail='Unable to authenticate with Google')
    return TokenResponse(access_token=token, expires_in=expires_in)


@router.post('/logout', response_model=MessageResponse)
async def logout(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    authorization = request.headers.get('authorization', '')
    token = authorization.split(' ', 1)[1] if ' ' in authorization else ''
    payload = safe_decode(token) or {}
    service = _build_service(db)
    await service.logout(
        jti=payload.get('jti', ''), user_id=current_user.id, exp=int(payload.get('exp', 0)),
        ip=request.client.host if request.client else None,
        user_agent=request.headers.get('user-agent'),
    )
    return MessageResponse(detail='Successfully logged out')


@router.get('/me', response_model=UserRead)
async def me(current_user: User = Depends(get_current_user)) -> User:
    return current_user
