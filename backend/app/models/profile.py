"""User profile model (one-to-one with User)."""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPkMixin
from app.models.enums import ProfileVisibility


class Profile(Base, UUIDPkMixin, TimestampMixin):
    __tablename__ = "profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True
    )
    user: Mapped["User"] = relationship(back_populates="profile")  # type: ignore[name-defined]

    display_name: Mapped[str] = mapped_column(String(120), nullable=False)
    location: Mapped[str] = mapped_column(String(120), nullable=False, default="")
    short_description: Mapped[str] = mapped_column(Text, nullable=False, default="")

    # Flexible role-specific data (e.g. investor preferences, innovator skills).
    role_specific_info: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)

    profile_visibility: Mapped[ProfileVisibility] = mapped_column(
        Enum(ProfileVisibility, native_enum=False, length=32),
        nullable=False,
        default=ProfileVisibility.REGISTERED,
    )
