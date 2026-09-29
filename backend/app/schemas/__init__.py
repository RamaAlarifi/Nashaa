"""Shared Pydantic schemas, helpers, and a prototype-friendly email type."""

from __future__ import annotations

from typing import Annotated

from email_validator import EmailNotValidError, validate_email
from pydantic import AfterValidator, BaseModel, ConfigDict


class MessageOut(BaseModel):
    message: str


class TokenOut(BaseModel):
    token: str
    token_type: str = "Bearer"


# Reusable config for ORM -> Pydantic conversion.
ORM_CONFIG = ConfigDict(from_attributes=True)


def _validate_email(value: str) -> str:
    """Validate an email's format without DNS / special-use-TLD deliverability
    checks. The prototype uses clearly fictional demo addresses (e.g. the
    ``.test`` TLD) which would otherwise be rejected by ``EmailStr``."""
    try:
        info = validate_email(value, check_deliverability=False)
    except EmailNotValidError as exc:
        raise ValueError(str(exc)) from exc
    return info.normalized


# Drop-in replacement for ``EmailStr`` with deliverability checks disabled.
SafeEmail = Annotated[str, AfterValidator(_validate_email)]
