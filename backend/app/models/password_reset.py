"""Password-reset token model.

A reset token is single-use and time-limited (US02). Only a SHA-256 hash is
stored. Once consumed, ``used_at`` is set and the token cannot be reused.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDPkMixin
from app.models.user import User


class PasswordReset(Base, UUIDPkMixin):
    __tablename__ = "password_resets"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user: Mapped[User] = relationship(lazy="selectin")

    token_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    @property
    def is_expired(self) -> bool:
        return datetime.now(self.expires_at.tzinfo) >= self.expires_at

    @property
    def is_used(self) -> bool:
        return self.used_at is not None
