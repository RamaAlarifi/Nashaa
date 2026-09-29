"""FastAPI dependencies: authentication and role-based access control.

Every protected action is checked by the server here, not only hidden on the
screen (project rule 1). A request without a valid session token is rejected
with 401; a session whose role is not allowed is rejected with 403.
"""

from __future__ import annotations

from collections.abc import Iterable

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.core.security import constant_time_eq, hash_token
from app.database import get_db
from app.models.enums import AccountStatus, Role
from app.models.session import Session as SessionModel
from app.models.user import User


def _extract_bearer_token(request: Request) -> str | None:
    header = request.headers.get("Authorization")
    if not header:
        return None
    parts = header.split(" ", 1)
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None
    token = parts[1].strip()
    return token or None


def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
) -> User:
    """Resolve the authenticated user from the Bearer token, or 401."""
    token = _extract_bearer_token(request)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication is required.",
        )

    token_hash = hash_token(token)
    session = db.execute(
        select(SessionModel).where(SessionModel.token_hash == token_hash)
    ).scalar_one_or_none()

    if session is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Your session is invalid. Please sign in again.",
        )
    if session.is_expired:
        db.delete(session)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Your session has expired. Please sign in again.",
        )

    user = session.user
    if user.account_status != AccountStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account is not active.",
        )
    return user


def require_role(*allowed: Role) -> type[User]:
    """Dependency factory: allow only the given roles, else 403."""

    def _checker(user: User = Depends(get_current_user)) -> User:
        if user.role not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action.",
            )
        return user

    return _checker


def require_business_owner(user: User = Depends(get_current_user)) -> User:
    if user.role != Role.BUSINESS_OWNER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only business owners can perform this action.",
        )
    return user
