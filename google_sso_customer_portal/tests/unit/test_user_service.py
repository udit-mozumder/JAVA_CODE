"""Unit tests for UserService (test_user_service)."""
import pytest

from app.schemas.user import GoogleUserProfile
from app.services.user_service import UserService


@pytest.mark.asyncio
async def test_get_or_create_creates_new_user(db_session):
    svc = UserService(db_session)
    profile = GoogleUserProfile(
        google_id="g-1", email="new@example.com", display_name="New", avatar_url=None
    )
    user, created = await svc.get_or_create(profile)
    assert created is True
    assert user.email == "new@example.com"
    assert user.last_login_at is not None


@pytest.mark.asyncio
async def test_get_or_create_returns_existing(db_session):
    svc = UserService(db_session)
    profile = GoogleUserProfile(google_id="g-2", email="e@example.com", display_name="E")
    await svc.get_or_create(profile)
    user, created = await svc.get_or_create(profile)
    assert created is False
    assert user.google_id == "g-2"
