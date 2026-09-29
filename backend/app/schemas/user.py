"""User account schemas."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.enums import AccountStatus, Role, VerificationStatus
from app.schemas import ORM_CONFIG, SafeEmail


class UserOut(BaseModel):
    model_config = ORM_CONFIG

    id: UUID
    email: SafeEmail
    role: Role
    account_status: AccountStatus
    verification_status: VerificationStatus
    created_at: datetime
    updated_at: datetime
