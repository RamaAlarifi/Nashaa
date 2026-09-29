"""Auth endpoints: register, login, logout, me, password reset (US01, US02)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.config import get_settings
from app.core.deps import _extract_bearer_token, get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.auth import (
    AuthOut,
    LoginIn,
    MeOut,
    PasswordResetConfirmIn,
    PasswordResetRequestIn,
    PasswordResetRequestOut,
    RegisterIn,
)
from app.schemas.profile import ProfileOut
from app.schemas.user import UserOut
from app.services import auth as auth_service
from app.services.errors import (
    EmailAlreadyRegistered,
    InvalidCredentials,
    ResetTokenExpired,
    ResetTokenNotFound,
    ResetTokenUsed,
)

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _auth_out(user: User, token: str) -> AuthOut:
    return AuthOut(
        token=token,
        user=UserOut.model_validate(user),
        profile=ProfileOut.model_validate(user.profile) if user.profile else None,
    )


@router.post("/register", response_model=AuthOut, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterIn, db: Session = Depends(get_db)):
    try:
        user = auth_service.create_user(
            db,
            email=payload.email,
            password=payload.password,
            role=payload.role,
            display_name=payload.display_name,
        )
    except EmailAlreadyRegistered as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    _, token = auth_service.create_session(db, user)
    return _auth_out(user, token)


@router.post("/login", response_model=AuthOut)
def login(payload: LoginIn, db: Session = Depends(get_db)):
    try:
        user = auth_service.authenticate(db, email=payload.email, password=payload.password)
    except InvalidCredentials as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))
    _, token = auth_service.create_session(db, user)
    return _auth_out(user, token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    token = _extract_bearer_token(request)
    if token:
        auth_service.delete_session_by_token(db, token)
    return None


@router.get("/me", response_model=MeOut)
def me(user: User = Depends(get_current_user)):
    return MeOut(
        user=UserOut.model_validate(user),
        profile=ProfileOut.model_validate(user.profile) if user.profile else None,
    )


@router.post("/password-reset/request", response_model=PasswordResetRequestOut)
def request_password_reset(payload: PasswordResetRequestIn, db: Session = Depends(get_db)):
    # Always return success to avoid leaking which emails are registered.
    result = auth_service.request_password_reset(db, payload.email)
    message = "If an account exists for this email, a reset link has been sent."
    reset_token: str | None = None
    settings = get_settings()
    if settings.environment != "production" and result is not None:
        reset_token = result[1]
    return PasswordResetRequestOut(message=message, reset_token=reset_token)


@router.post("/password-reset/confirm")
def confirm_password_reset(payload: PasswordResetConfirmIn, db: Session = Depends(get_db)):
    try:
        auth_service.confirm_password_reset(
            db, token=payload.token, new_password=payload.new_password
        )
    except ResetTokenNotFound as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except ResetTokenUsed as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except ResetTokenExpired as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    return {"message": "Your password has been reset. You can sign in now."}
