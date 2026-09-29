"""Authentication-related schemas (US01, US02)."""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.models.enums import Role
from app.schemas import SafeEmail
from app.schemas.profile import ProfileOut
from app.schemas.user import UserOut


class RegisterIn(BaseModel):
    email: SafeEmail
    password: str = Field(min_length=8, max_length=128)
    role: Role = Role.BUSINESS_OWNER
    display_name: str = Field(min_length=1, max_length=120)


class LoginIn(BaseModel):
    email: SafeEmail
    password: str


class AuthOut(BaseModel):
    token: str
    token_type: str = "Bearer"
    user: UserOut
    profile: ProfileOut | None = None


class MeOut(BaseModel):
    user: UserOut
    profile: ProfileOut | None = None


class PasswordResetRequestIn(BaseModel):
    email: SafeEmail


class PasswordResetConfirmIn(BaseModel):
    token: str = Field(min_length=1)
    new_password: str = Field(min_length=8, max_length=128)


class PasswordResetRequestOut(BaseModel):
    message: str
    # Only populated in non-production environments so tests can use the token.
    # In production this token is delivered by email, never returned to the API
    # client.
    reset_token: str | None = None
