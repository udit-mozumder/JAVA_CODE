"""Integration tests for the auth endpoints."""
import httpx
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.db.base import Base
from app.db.session import get_db
from main import app


@pytest_asyncio.fixture
async def client():
    engine = create_async_engine('sqlite+aiosqlite:///:memory:', future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async def _get_db():
        async with maker() as session:
            yield session

    app.dependency_overrides[get_db] = _get_db
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url='http://test') as c:
        yield c
    app.dependency_overrides.clear()
    await engine.dispose()


@pytest.mark.asyncio
async def test_login_google_returns_authorization_url(client):
    resp = await client.get('/api/v1/auth/login/google')
    assert resp.status_code == 200
    body = resp.json()
    assert 'authorization_url' in body
    assert body['state']


@pytest.mark.asyncio
async def test_callback_missing_code_returns_400(client):
    resp = await client.get('/api/v1/auth/callback/google')
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_me_requires_authentication(client):
    resp = await client.get('/api/v1/auth/me')
    assert resp.status_code == 401
