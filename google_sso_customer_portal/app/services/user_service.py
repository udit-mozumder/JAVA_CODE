"""User persistence service (FR-4, FR-5)."""
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.user import User
from app.schemas.user import GoogleUserProfile


class UserService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_google_id(self, google_id: str) -> User | None:
        result = await self.db.execute(select(User).where(User.google_id == google_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_or_create(self, profile: GoogleUserProfile) -> tuple[User, bool]:
        """FR-4/FR-5: create on first login, otherwise return existing user.

        Returns (user, created).
        """
        user = await self.get_by_google_id(profile.google_id)
        if user is None:
            user = await self.get_by_email(profile.email)

        created = False
        if user is None:
            user = User(
                google_id=profile.google_id,
                email=profile.email,
                display_name=profile.display_name,
                avatar_url=profile.avatar_url,
            )
            self.db.add(user)
            created = True
        else:
            user.display_name = profile.display_name or user.display_name
            user.avatar_url = profile.avatar_url or user.avatar_url
            if not user.google_id:
                user.google_id = profile.google_id

        user.last_login_at = datetime.now(timezone.utc)
        await self.db.commit()
        await self.db.refresh(user)
        return user, created
