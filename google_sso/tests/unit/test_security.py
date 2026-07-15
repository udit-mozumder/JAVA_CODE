"""Unit tests for JWT security helpers."""
from app.core.security import create_access_token, decode_token, safe_decode


def test_create_and_decode_token():
    token, jti = create_access_token('user-123', extra={'email': 'a@b.com'})
    payload = decode_token(token)
    assert payload['sub'] == 'user-123'
    assert payload['jti'] == jti
    assert payload['email'] == 'a@b.com'


def test_safe_decode_invalid_token():
    assert safe_decode('not-a-jwt') is None
