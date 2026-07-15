"""Authentication endpoints (SCRUM-5 APIs)."""
from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import verify_state
from app.db.models.auth_audit_log import AuthEventType
from app.db.models.user import User
from app.db.session import get_db
from app.middleware.auth_middleware import get_current_user
from app.schemas.auth import LogoutResponse
from app.schemas.user import UserRead
from app.services.auth_service import AuthService
from app.services.google_oauth_service import GoogleOAuthError, GoogleOAuthService
from app.utils.errors import AuthError

router = APIRouter()


@router.get("/login/google", summary="Initiate Google OAuth 2.0 login (FR-1)")
async def login_google() -> RedirectResponse:
    oauth = GoogleOAuthService()
    authorization_url, _state = oauth.build_authorization_url()
    return RedirectResponse(url=authorization_url, status_code=307)


@router.get("/callback/google", summary="Handle Google OAuth 2.0 callback (FR-2..FR-6)")
async def google_callback(
    request: Request,
    code: str | None = Query(default=None),
    state: str | None = Query(default=None),
    error: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
) -> RedirectResponse:
    service = AuthService(db)
    ip = getattr(request.state, "client_ip", None)
    ua = getattr(request.state, "user_agent", None)

    if error or not code:
        await service.record_event(
            AuthEventType.LOGIN_FAILURE, ip_address=ip, user_agent=ua,
            error_message=error or "missing authorization code",
        )
        raise AuthError(f"Google authentication failed: {error or 'missing code'}", 400)

    if not state or not verify_state(state):
        await service.record_event(
            AuthEventType.LOGIN_FAILURE, ip_address=ip, user_agent=ua,
            error_message="invalid state parameter",
        )
        raise AuthError("Invalid state parameter (possible CSRF)", 400)

    try:
        oauth = GoogleOAuthService()
        tokens = await oauth.exchange_code_for_token(code)
        profile = await oauth.fetch_user_profile(tokens["access_token"])
    except (GoogleOAuthError, KeyError) as exc:
        await service.record_event(
            AuthEventType.LOGIN_FAILURE, ip_address=ip, user_agent=ua,
            error_message=str(exc),
        )
        raise AuthError("Failed to authenticate with Google", 502)

    token_response = await service.complete_google_login(profile, ip_address=ip, user_agent=ua)

    redirect = RedirectResponse(
        url=f"{settings.FRONTEND_DASHBOARD_URL}?token={token_response.access_token}",
        status_code=307,
    )
    redirect.set_cookie(
        "access_token", token_response.access_token, httponly=True, secure=True, samesite="lax"
    )
    return redirect


@router.post("/logout", response_model=LogoutResponse, summary="Logout (FR-8)")
async def logout(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> LogoutResponse:
    service = AuthService(db)
    await service.logout(
        token=request.state.token,
        jti=request.state.jti,
        user_id=current_user.id,
        ip_address=getattr(request.state, "client_ip", None),
        user_agent=getattr(request.state, "user_agent", None),
    )
    return LogoutResponse()


@router.get("/me", response_model=UserRead, summary="Current user profile")
async def me(current_user: User = Depends(get_current_user)) -> UserRead:
    return UserRead.model_validate(current_user)
