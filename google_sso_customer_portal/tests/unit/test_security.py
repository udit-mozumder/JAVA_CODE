"""Unit tests for JWT and CSRF state helpers (test_security)."""
from app.core.security import (
    create_access_token,
    decode_token,
    generate_state,
    verify_state,
)


def test_access_token_roundtrip():
    token, jti, expires_in = create_access_token("user-123", {"email": "a@b.com"})
    payload = decode_token(token)
    assert payload["sub"] == "user-123"
    assert payload["jti"] == jti
    assert payload["type"] == "access"
    assert payload["email"] == "a@b.com"
    assert expires_in > 0


def test_state_generation_and_verification():
    state = generate_state()
    assert verify_state(state) is True


def test_invalid_state_rejected():
    assert verify_state("tampered.state.value") is False
