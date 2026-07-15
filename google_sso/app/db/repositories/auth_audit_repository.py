"""Data-access layer for authentication audit logs."""
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.auth_audit_log import AuthAuditLog, AuthEventType


class AuthAuditRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def record(self, *, event_type: AuthEventType, user_id: str | None = None,
                     ip_address: str | None = None, user_agent: str | None = None,
                     failure_reason: str | None = None) -> AuthAuditLog:
        entry = AuthAuditLog(
            event_type=event_type, user_id=user_id, ip_address=ip_address,
            user_agent=user_agent, failure_reason=failure_reason,
        )
        self.session.add(entry)
        await self.session.commit()
        await self.session.refresh(entry)
        return entry
