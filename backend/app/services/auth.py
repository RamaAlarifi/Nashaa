"""Authentication and password-reset services (US01, US02)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.core.security import (
    generate_token,
    hash_password,
    hash_token,
    verify_password,
)
from app.models.enums import ProfileVisibility, Role
from app.models.password_reset import PasswordReset
from app.models.profile import Profile
from app.models.session import Session as SessionModel
from app.models.user import User
from app.services.errors import (
    EmailAlreadyRegistered,
    InvalidCredentials,
    ResetTokenExpired,
    ResetTokenNotFound,
    ResetTokenUsed,
)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.execute(select(User).where(User.email == email.lower())).scalar_one_or_none()


def create_user(
    db: Session,
    *,
    email: str,
    password: str,
    role: Role,
    display_name: str,
) -> User:
    normalized_email = email.lower().strip()
    if get_user_by_email(db, normalized_email) is not None:
        raise EmailAlreadyRegistered("An account with this email already exists.")

    user = User(
        email=normalized_email,
        password_hash=hash_password(password),
        role=role,
    )
    profile = Profile(
        user=user,
        display_name=display_name,
        role_specific_info={},
        profile_visibility=ProfileVisibility.REGISTERED,
    )
    db.add(user)
    db.add(profile)
    db.commit()
    db.refresh(user)
    return user


def authenticate(db: Session, *, email: str, password: str) -> User:
    user = get_user_by_email(db, email)
    if user is None or not verify_password(password, user.password_hash):
        raise InvalidCredentials("Incorrect email or password.")
    return user


def create_session(db: Session, user: User) -> tuple[SessionModel, str]:
    """Create a new server-side session. Returns (session, plaintext_token)."""
    settings = get_settings()
    token = generate_token()
    session = SessionModel(
        user_id=user.id,
        token_hash=hash_token(token),
        expires_at=_utcnow() + timedelta(seconds=settings.session_expire_seconds),
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session, token


def delete_session_by_token(db: Session, token: str) -> bool:
    session = db.execute(
        select(SessionModel).where(SessionModel.token_hash == hash_token(token))
    ).scalar_one_or_none()
    if session is None:
        return False
    db.delete(session)
    db.commit()
    return True


def request_password_reset(db: Session, email: str) -> tuple[PasswordReset, str] | None:
    """Create a reset token. Returns None if the email is unknown so the API
    response does not leak which emails exist (US02 + privacy)."""
    user = get_user_by_email(db, email)
    if user is None:
        return None
    settings = get_settings()
    token = generate_token()
    reset = PasswordReset(
        user_id=user.id,
        token_hash=hash_token(token),
        expires_at=_utcnow() + timedelta(seconds=settings.reset_expire_seconds),
    )
    db.add(reset)
    db.commit()
    db.refresh(reset)
    return reset, token


def confirm_password_reset(db: Session, *, token: str, new_password: str) -> User:
    reset = db.execute(
        select(PasswordReset).where(PasswordReset.token_hash == hash_token(token)).with_for_update()
    ).scalar_one_or_none()
    if reset is None:
        raise ResetTokenNotFound("This reset link is invalid.")
    if reset.is_used:
        raise ResetTokenUsed("This reset link has already been used.")
    if reset.is_expired:
        raise ResetTokenExpired("This reset link has expired. Request a new one.")

    user = reset.user
    user.password_hash = hash_password(new_password)
    reset.used_at = _utcnow()
    for other in db.execute(select(PasswordReset).where(PasswordReset.user_id == user.id, PasswordReset.used_at.is_(None))).scalars():
        other.used_at = reset.used_at
    # Invalidate all active sessions for this user after a password change.
    active_sessions = db.execute(
        select(SessionModel).where(SessionModel.user_id == user.id)
    ).scalars().all()
    for sess in active_sessions:
        db.delete(sess)
    db.commit()
    db.refresh(user)
    return user
