"""Dependency that authenticates requests via a Bearer JWT."""
from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import safe_decode
from app.db.models.user import User
from app.db.repositories.token_denylist_repository import TokenDenylistRepository
from app.db.repositories.user_repository import UserRepository
from app.db.session import get_db


async def get_current_user(
    authorization: str | None = Header(default=None),
    db: AsyncSession = Depends(get_db),
) -> User:
    if not authorization or not authorization.lower().startswith('bearer '):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Missing bearer token')
    token = authorization.split(' ', 1)[1]
    payload = safe_decode(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid or expired token')
    jti = payload.get('jti')
    denylist = TokenDenylistRepository(db)
    if jti and await denylist.is_denylisted(jti):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Token has been revoked')
    user = await UserRepository(db).get_by_id(payload.get('sub'))
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='User not found or inactive')
    return user
