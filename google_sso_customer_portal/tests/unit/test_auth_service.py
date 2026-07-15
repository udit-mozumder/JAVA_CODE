"""Unit tests for AuthService (test_auth_service)."""
import pytest
from sqlalchemy import select

from app.core.security import decode_token
from app.db.models.auth_audit_log import AuthAuditLog, AuthEventType
from app.schemas.user import GoogleUserProfile
from app.services.auth_service import AuthService


@pytest.mark.asyncio
async def test_complete_google_login_issues_token_and_audits(db_session):
    svc = AuthService(db_session)
    profile = GoogleUserProfile(google_id="g-9", email="log@example.com", display_name="L")
    resp = await svc.complete_google_login(profile, ip_address="1.2.3.4", user_agent="pytest")

    payload = decode_token(resp.access_token)
    assert payload["email"] == "log@example.com"
    assert resp.user.email == "log@example.com"

    logs = (await db_session.execute(select(AuthAuditLog))).scalars().all()
    assert any(l.event_type == AuthEventType.LOGIN_SUCCESS for l in logs)


@pytest.mark.asyncio
async def test_logout_denylists_token(db_session):
    svc = AuthService(db_session)
    profile = GoogleUserProfile(google_id="g-10", email="out@example.com")
    resp = await svc.complete_google_login(profile)
    payload = decode_token(resp.access_token)

    await svc.logout(token=resp.access_token, jti=payload["jti"], user_id=resp.user.id)
    assert await svc.is_denylisted(payload["jti"]) is True
