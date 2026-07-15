"""Data-access layer for User records."""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.user import User


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_google_id(self, google_id: str) -> User | None:
        result = await self.session.execute(select(User).where(User.google_id == google_id))
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: str) -> User | None:
        result = await self.session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def create(self, *, google_id: str, email: str, display_name: str | None, avatar_url: str | None) -> User:
        user = User(google_id=google_id, email=email, display_name=display_name, avatar_url=avatar_url)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def get_or_create(self, *, google_id: str, email: str, display_name: str | None, avatar_url: str | None) -> tuple[User, bool]:
        existing = await self.get_by_google_id(google_id)
        if existing:
            return existing, False
        created = await self.create(google_id=google_id, email=email, display_name=display_name, avatar_url=avatar_url)
        return created, True
