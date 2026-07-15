"""SQLAlchemy declarative base and metadata."""
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all ORM models."""


from app.db.models.user import User  # noqa: E402,F401
from app.db.models.auth_audit_log import AuthAuditLog  # noqa: E402,F401
from app.db.models.token_denylist import TokenDenylist  # noqa: E402,F401
