"""Encapsulates all interaction with Google's OAuth 2.0 endpoints."""
import secrets
from urllib.parse import urlencode

import httpx

from app.core.config import settings
from app.schemas.user import GoogleProfile


class GoogleOAuthError(Exception):
    """Raised when a Google OAuth interaction fails."""


class GoogleOAuthService:
    def __init__(self, client: httpx.AsyncClient | None = None) -> None:
        self._client = client

    @staticmethod
    def generate_state() -> str:
        return secrets.token_urlsafe(32)

    def build_authorization_url(self, state: str) -> str:
        params = {
            'client_id': settings.GOOGLE_CLIENT_ID,
            'redirect_uri': settings.GOOGLE_REDIRECT_URI,
            'response_type': 'code',
            'scope': settings.GOOGLE_SCOPES,
            'state': state,
            'access_type': 'offline',
            'prompt': 'consent',
        }
        return f'{settings.GOOGLE_AUTH_URI}?{urlencode(params)}'

    async def _get_client(self) -> httpx.AsyncClient:
        return self._client or httpx.AsyncClient(timeout=10.0)

    async def exchange_code(self, code: str) -> dict:
        data = {
            'code': code,
            'client_id': settings.GOOGLE_CLIENT_ID,
            'client_secret': settings.GOOGLE_CLIENT_SECRET,
            'redirect_uri': settings.GOOGLE_REDIRECT_URI,
            'grant_type': 'authorization_code',
        }
        client = await self._get_client()
        try:
            resp = await client.post(settings.GOOGLE_TOKEN_URI, data=data)
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPError as exc:
            raise GoogleOAuthError('Failed to exchange authorization code') from exc
        finally:
            if self._client is None:
                await client.aclose()

    async def fetch_userinfo(self, access_token: str) -> GoogleProfile:
        client = await self._get_client()
        try:
            resp = await client.get(
                settings.GOOGLE_USERINFO_URI,
                headers={'Authorization': f'Bearer {access_token}'},
            )
            resp.raise_for_status()
            data = resp.json()
        except httpx.HTTPError as exc:
            raise GoogleOAuthError('Failed to retrieve user profile') from exc
        finally:
            if self._client is None:
                await client.aclose()
        return GoogleProfile(
            google_id=data['id'],
            email=data['email'],
            display_name=data.get('name'),
            avatar_url=data.get('picture'),
        )
