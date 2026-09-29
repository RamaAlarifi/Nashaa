"""User account model."""

from __future__ import annotations

from sqlalchemy import Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPkMixin
from app.models.enums import AccountStatus, Role


class User(Base, UUIDPkMixin, TimestampMixin):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    role: Mapped[Role] = mapped_column(
        Enum(Role, native_enum=False, length=32), nullable=False, default=Role.BUSINESS_OWNER
    )
    account_status: Mapped[AccountStatus] = mapped_column(
        Enum(AccountStatus, native_enum=False, length=32),
        nullable=False,
        default=AccountStatus.ACTIVE,
    )
    # Parent-side relationships. Targets are forward-referenced by string so the
    # models can be imported in any order without circular import errors.
    profile: Mapped["Profile"] = relationship(  # type: ignore[name-defined]
        back_populates="user", uselist=False, cascade="all, delete-orphan", lazy="selectin"
    )
    business_ideas: Mapped[list["BusinessIdea"]] = relationship(  # type: ignore[name-defined]
        back_populates="owner", cascade="all, delete-orphan", lazy="selectin"
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<User {self.email} ({self.role})>"
