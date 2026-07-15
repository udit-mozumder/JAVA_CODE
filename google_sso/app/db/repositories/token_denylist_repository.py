"""Data-access layer for the JWT denylist."""
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.token_denylist import TokenDenylist


class TokenDenylistRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, *, jti: str, user_id: str | None, expires_at: datetime) -> TokenDenylist:
        entry = TokenDenylist(jti=jti, user_id=user_id, expires_at=expires_at)
        self.session.add(entry)
        await self.session.commit()
        await self.session.refresh(entry)
        return entry

    async def is_denylisted(self, jti: str) -> bool:
        result = await self.session.execute(select(TokenDenylist).where(TokenDenylist.jti == jti))
        return result.scalar_one_or_none() is not None
