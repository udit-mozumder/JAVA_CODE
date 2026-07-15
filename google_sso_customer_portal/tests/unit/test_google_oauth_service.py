"""Unit tests for GoogleOAuthService (test_google_oauth_service)."""
import httpx
import pytest

from app.core.config import settings
from app.services.google_oauth_service import GoogleOAuthError, GoogleOAuthService


def test_build_authorization_url():
    svc = GoogleOAuthService()
    url, state = svc.build_authorization_url()
    assert settings.GOOGLE_AUTH_URI in url
    assert "response_type=code" in url
    assert "scope=" in url
    assert state


@pytest.mark.asyncio
async def test_fetch_user_profile_success():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={
            "sub": "google-1", "email": "jane@example.com",
            "name": "Jane", "picture": "http://img/x.png",
        })

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport) as client:
        svc = GoogleOAuthService(client=client)
        profile = await svc.fetch_user_profile("token")
    assert profile.google_id == "google-1"
    assert profile.email == "jane@example.com"


@pytest.mark.asyncio
async def test_fetch_user_profile_failure():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(401, text="unauthorized")

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport) as client:
        svc = GoogleOAuthService(client=client)
        with pytest.raises(GoogleOAuthError):
            await svc.fetch_user_profile("bad-token")
