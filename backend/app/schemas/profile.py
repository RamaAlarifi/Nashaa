"""Profile schemas (US03)."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.enums import ProfileVisibility
from app.schemas import ORM_CONFIG


class ProfileOut(BaseModel):
    model_config = ORM_CONFIG

    user_id: UUID
    display_name: str
    location: str
    short_description: str
    role_specific_info: dict[str, Any]
    profile_visibility: ProfileVisibility
    created_at: datetime
    updated_at: datetime


class ProfileUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    @model_validator(mode="before")
    @classmethod
    def reject_nulls(cls, values):
        if isinstance(values, dict) and any(v is None for v in values.values()):
            raise ValueError("Fields cannot be null. Use an empty string to clear optional text.")
        return values

    # Role is intentionally NOT included: a user cannot change their role
    # through an ordinary profile update (US03 completion check).
    display_name: str | None = Field(default=None, min_length=1, max_length=120)
    location: str | None = Field(default=None, max_length=120)
    short_description: str | None = None
    role_specific_info: dict[str, Any] | None = None
    profile_visibility: ProfileVisibility | None = None
