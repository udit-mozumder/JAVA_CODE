"""JWT creation/validation and CSRF state helpers (NFR-1, NFR-3)."""
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict

from itsdangerous import BadSignature, URLSafeTimedSerializer
from jose import JWTError, jwt

from app.core.config import settings


def _now() -> datetime:
    return datetime.now(timezone.utc)


def create_access_token(subject: str, extra_claims: Dict[str, Any] | None = None) -> tuple[str, str, int]:
    """Return (token, jti, expires_in_seconds)."""
    jti = str(uuid.uuid4())
    expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = _now() + expires_delta
    to_encode: Dict[str, Any] = {
        "sub": subject,
        "jti": jti,
        "type": "access",
        "iat": int(_now().timestamp()),
        "exp": expire,
    }
    if extra_claims:
        to_encode.update(extra_claims)
    token = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token, jti, int(expires_delta.total_seconds())


def create_refresh_token(subject: str) -> str:
    expire = _now() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {
        "sub": subject,
        "jti": str(uuid.uuid4()),
        "type": "refresh",
        "iat": int(_now().timestamp()),
        "exp": expire,
    }
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> Dict[str, Any]:
    """Decode and validate a JWT. Raises JWTError on failure."""
    return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])


def token_expiry(token: str) -> datetime:
    payload = decode_token(token)
    return datetime.fromtimestamp(payload["exp"], tz=timezone.utc)


_state_serializer = URLSafeTimedSerializer(settings.JWT_SECRET_KEY, salt="oauth-state")


def generate_state() -> str:
    """Generate a signed CSRF state parameter (NFR-1, ASSUMPTION-11)."""
    return _state_serializer.dumps(str(uuid.uuid4()))


def verify_state(state: str, max_age_seconds: int = 600) -> bool:
    try:
        _state_serializer.loads(state, max_age=max_age_seconds)
        return True
    except BadSignature:
        return False
    except Exception:
        return False


__all__ = [
    "create_access_token",
    "create_refresh_token",
    "decode_token",
    "token_expiry",
    "generate_state",
    "verify_state",
    "JWTError",
]
