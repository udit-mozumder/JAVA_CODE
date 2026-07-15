"""Orchestrates authentication: OAuth callback, JWT issuance and logout."""
from datetime import datetime, timezone

from app.core.security import create_access_token
from app.core.config import settings
from app.db.models.auth_audit_log import AuthEventType
from app.db.repositories.auth_audit_repository import AuthAuditRepository
from app.db.repositories.token_denylist_repository import TokenDenylistRepository
from app.db.repositories.user_repository import UserRepository
from app.schemas.user import GoogleProfile
from app.services.google_oauth_service import GoogleOAuthService


class AuthService:
    def __init__(self, users: UserRepository, audit: AuthAuditRepository,
                 denylist: TokenDenylistRepository, google: GoogleOAuthService) -> None:
        self.users = users
        self.audit = audit
        self.denylist = denylist
        self.google = google

    async def complete_login(self, code: str, ip: str | None, user_agent: str | None) -> tuple[str, int]:
        tokens = await self.google.exchange_code(code)
        profile: GoogleProfile = await self.google.fetch_userinfo(tokens['access_token'])
        user, _ = await self.users.get_or_create(
            google_id=profile.google_id, email=profile.email,
            display_name=profile.display_name, avatar_url=profile.avatar_url,
        )
        token, _jti = create_access_token(subject=user.id, extra={'email': user.email})
        await self.audit.record(event_type=AuthEventType.LOGIN_SUCCESS, user_id=user.id,
                                ip_address=ip, user_agent=user_agent)
        return token, settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60

    async def record_failure(self, reason: str, ip: str | None, user_agent: str | None) -> None:
        await self.audit.record(event_type=AuthEventType.LOGIN_FAILURE, ip_address=ip,
                                user_agent=user_agent, failure_reason=reason)

    async def logout(self, *, jti: str, user_id: str | None, exp: int,
                     ip: str | None, user_agent: str | None) -> None:
        expires_at = datetime.fromtimestamp(exp, tz=timezone.utc)
        await self.denylist.add(jti=jti, user_id=user_id, expires_at=expires_at)
        await self.audit.record(event_type=AuthEventType.LOGOUT, user_id=user_id,
                                ip_address=ip, user_agent=user_agent)
