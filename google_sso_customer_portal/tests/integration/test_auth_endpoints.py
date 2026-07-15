"""Integration tests for auth endpoints (test_auth_endpoints)."""
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.db.base import Base
from app.db.session import get_db
from main import app


@pytest_asyncio.fixture
async def client():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async def override_get_db():
        async with factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
    await engine.dispose()


@pytest.mark.asyncio
async def test_login_google_redirects(client):
    resp = await client.get("/api/v1/auth/login/google", follow_redirects=False)
    assert resp.status_code in (307, 302)
    assert "accounts.google.com" in resp.headers["location"]


@pytest.mark.asyncio
async def test_callback_invalid_state_returns_error(client):
    resp = await client.get(
        "/api/v1/auth/callback/google?code=abc&state=bad", follow_redirects=False
    )
    assert resp.status_code == 400
    assert resp.json()["error"] == "authentication_error"


@pytest.mark.asyncio
async def test_me_requires_auth(client):
    resp = await client.get("/api/v1/auth/me")
    assert resp.status_code == 401
