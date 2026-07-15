"""Authentication orchestration service (FR-6, FR-7, FR-8)."""
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, create_refresh_token, token_expiry
from app.db.models.auth_audit_log import AuthAuditLog, AuthEventType
from app.db.models.token_denylist import TokenDenylist
from app.db.models.user import User
from app.schemas.auth import TokenResponse
from app.schemas.user import GoogleUserProfile, UserRead
from app.services.google_oauth_service import GoogleOAuthService
from app.services.user_service import UserService
from app.utils.logger import get_logger

logger = get_logger(__name__)


class AuthService:
    def __init__(self, db: AsyncSession, oauth: GoogleOAuthService | None = None) -> None:
        self.db = db
        self.oauth = oauth or GoogleOAuthService()
        self.users = UserService(db)

    async def record_event(
        self,
        event_type: AuthEventType,
        user_id: uuid.UUID | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
        error_message: str | None = None,
    ) -> None:
        """FR-7/NFR-5: persist an authentication audit event."""
        log = AuthAuditLog(
            user_id=user_id,
            event_type=event_type,
            ip_address=ip_address,
            user_agent=user_agent,
            error_message=error_message,
        )
        self.db.add(log)
        await self.db.commit()
        logger.info(
            "auth_event",
            extra={"extra_fields": {
                "event_type": event_type.value,
                "user_id": str(user_id) if user_id else None,
                "ip_address": ip_address,
                "error_message": error_message,
            }},
        )

    async def complete_google_login(
        self,
        profile: GoogleUserProfile,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> TokenResponse:
        """FR-4/FR-5/FR-6: upsert user and issue JWTs."""
        user, _created = await self.users.get_or_create(profile)
        access_token, _jti, expires_in = create_access_token(
            subject=str(user.id), extra_claims={"email": user.email}
        )
        refresh_token = create_refresh_token(subject=str(user.id))
        await self.record_event(
            AuthEventType.LOGIN_SUCCESS,
            user_id=user.id,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=expires_in,
            user=UserRead.model_validate(user),
        )

    async def is_denylisted(self, jti: str) -> bool:
        result = await self.db.execute(
            select(TokenDenylist).where(TokenDenylist.jti == jti)
        )
        return result.scalar_one_or_none() is not None

    async def logout(
        self,
        token: str,
        jti: str,
        user_id: uuid.UUID | None,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> None:
        """FR-8: add token JTI to the denylist and audit the logout."""
        if not await self.is_denylisted(jti):
            entry = TokenDenylist(jti=jti, user_id=user_id, expires_at=token_expiry(token))
            self.db.add(entry)
            await self.db.commit()
        await self.record_event(
            AuthEventType.LOGOUT,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
        )

    async def get_user(self, user_id: uuid.UUID) -> User | None:
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()
