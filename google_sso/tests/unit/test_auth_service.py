"""Unit tests for AuthService orchestration with a mocked Google service."""
import pytest

from app.db.models.auth_audit_log import AuthEventType
from app.db.repositories.auth_audit_repository import AuthAuditRepository
from app.db.repositories.token_denylist_repository import TokenDenylistRepository
from app.db.repositories.user_repository import UserRepository
from app.schemas.user import GoogleProfile
from app.services.auth_service import AuthService


class FakeGoogle:
    async def exchange_code(self, code):
        return {'access_token': 'tok'}

    async def fetch_userinfo(self, access_token):
        return GoogleProfile(google_id='g1', email='u@x.com', display_name='U', avatar_url=None)


@pytest.mark.asyncio
async def test_complete_login_issues_token_and_audits(db_session):
    service = AuthService(
        users=UserRepository(db_session),
        audit=AuthAuditRepository(db_session),
        denylist=TokenDenylistRepository(db_session),
        google=FakeGoogle(),
    )
    token, expires_in = await service.complete_login('code', '127.0.0.1', 'pytest')
    assert token
    assert expires_in > 0


@pytest.mark.asyncio
async def test_logout_denylists_jti(db_session):
    denylist = TokenDenylistRepository(db_session)
    service = AuthService(
        users=UserRepository(db_session),
        audit=AuthAuditRepository(db_session),
        denylist=denylist,
        google=FakeGoogle(),
    )
    await service.logout(jti='jti-1', user_id=None, exp=9999999999, ip='127.0.0.1', user_agent='pytest')
    assert await denylist.is_denylisted('jti-1') is True
