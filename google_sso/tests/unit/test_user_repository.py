"""Unit tests for UserRepository."""
import pytest

from app.db.repositories.user_repository import UserRepository


@pytest.mark.asyncio
async def test_get_or_create_creates_then_reuses(db_session):
    repo = UserRepository(db_session)
    user, created = await repo.get_or_create(google_id='g9', email='e@x.com', display_name='E', avatar_url=None)
    assert created is True
    same, created_again = await repo.get_or_create(google_id='g9', email='e@x.com', display_name='E', avatar_url=None)
    assert created_again is False
    assert same.id == user.id
