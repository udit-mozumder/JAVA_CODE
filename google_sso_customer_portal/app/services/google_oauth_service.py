"""Google OAuth 2.0 integration service (FR-1, FR-2, FR-3)."""
from urllib.parse import urlencode

import httpx

from app.core.config import settings
from app.core.security import generate_state
from app.schemas.user import GoogleUserProfile
from app.utils.logger import get_logger

logger = get_logger(__name__)


class GoogleOAuthError(Exception):
    """Raised when a Google OAuth operation fails."""


class GoogleOAuthService:
    def __init__(self, client: httpx.AsyncClient | None = None) -> None:
        self._client = client

    def build_authorization_url(self) -> tuple[str, str]:
        """FR-1: build the Google authorisation URL and CSRF state."""
        state = generate_state()
        params = {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "response_type": "code",
            "scope": " ".join(settings.GOOGLE_SCOPES),
            "state": state,
            "access_type": "offline",
            "prompt": "consent",
        }
        return f"{settings.GOOGLE_AUTH_URI}?{urlencode(params)}", state

    async def exchange_code_for_token(self, code: str) -> dict:
        """FR-2: exchange the authorisation code for tokens."""
        data = {
            "code": code,
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code",
        }
        client = self._client or httpx.AsyncClient(timeout=10.0)
        try:
            resp = await client.post(settings.GOOGLE_TOKEN_URI, data=data)
            if resp.status_code != 200:
                raise GoogleOAuthError(f"Token exchange failed: {resp.text}")
            return resp.json()
        finally:
            if self._client is None:
                await client.aclose()

    async def fetch_user_profile(self, access_token: str) -> GoogleUserProfile:
        """FR-3: retrieve the user profile from Google's userinfo endpoint."""
        client = self._client or httpx.AsyncClient(timeout=10.0)
        try:
            resp = await client.get(
                settings.GOOGLE_USERINFO_URI,
                headers={"Authorization": f"Bearer {access_token}"},
            )
            if resp.status_code != 200:
                raise GoogleOAuthError(f"Userinfo request failed: {resp.text}")
            data = resp.json()
        finally:
            if self._client is None:
                await client.aclose()

        if "sub" not in data or "email" not in data:
            raise GoogleOAuthError("Incomplete profile returned by Google")

        return GoogleUserProfile(
            google_id=data["sub"],
            email=data["email"],
            display_name=data.get("name"),
            avatar_url=data.get("picture"),
        )
