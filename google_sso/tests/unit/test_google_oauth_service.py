"""Unit tests for GoogleOAuthService with mocked HTTP."""
import httpx
import pytest

from app.services.google_oauth_service import GoogleOAuthError, GoogleOAuthService


def test_build_authorization_url_contains_state():
    svc = GoogleOAuthService()
    url = svc.build_authorization_url('xyz-state')
    assert 'state=xyz-state' in url
    assert 'response_type=code' in url


@pytest.mark.asyncio
async def test_fetch_userinfo_maps_profile():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={'id': 'g1', 'email': 'u@x.com', 'name': 'U', 'picture': 'http://a/av.png'})
    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport) as client:
        svc = GoogleOAuthService(client=client)
        profile = await svc.fetch_userinfo('access-token')
    assert profile.google_id == 'g1'
    assert profile.email == 'u@x.com'
    assert profile.display_name == 'U'


@pytest.mark.asyncio
async def test_exchange_code_raises_on_http_error():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(400, json={'error': 'invalid_grant'})
    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport) as client:
        svc = GoogleOAuthService(client=client)
        with pytest.raises(GoogleOAuthError):
            await svc.exchange_code('bad-code')
