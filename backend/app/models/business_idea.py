"""Business idea model (US05, US08)."""

from __future__ import annotations

import uuid

from sqlalchemy import Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPkMixin
from app.models.enums import BusinessStage, IdeaVisibility


class BusinessIdea(Base, UUIDPkMixin, TimestampMixin):
    __tablename__ = "business_ideas"

    owner_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    owner: Mapped["User"] = relationship(back_populates="business_ideas")  # type: ignore[name-defined]

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    problem: Mapped[str] = mapped_column(Text, nullable=False, default="")
    solution: Mapped[str] = mapped_column(Text, nullable=False, default="")
    industry: Mapped[str] = mapped_column(String(120), nullable=False, default="")
    business_stage: Mapped[BusinessStage] = mapped_column(
        Enum(BusinessStage, native_enum=False, length=32),
        nullable=False,
        default=BusinessStage.IDEA,
    )
    target_location: Mapped[str] = mapped_column(String(120), nullable=False, default="")
    intended_customers: Mapped[str] = mapped_column(Text, nullable=False, default="")
    budget: Mapped[str] = mapped_column(String(120), nullable=False, default="")
    current_challenges: Mapped[str] = mapped_column(Text, nullable=False, default="")

    visibility: Mapped[IdeaVisibility] = mapped_column(
        Enum(IdeaVisibility, native_enum=False, length=32),
        nullable=False,
        default=IdeaVisibility.PRIVATE,
    )

    # Increments when assessment-related fields change (US05, US07).
    revision_number: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    assessments: Mapped[list["Assessment"]] = relationship(  # type: ignore[name-defined]
        back_populates="idea", cascade="all, delete-orphan", order_by="Assessment.seq.desc()"
    )
