"""AI assessment model (US06, US07).

Each assessment attempt is its own row. The *latest successful* assessment is
the one displayed. On failure, the previous successful result is preserved
(rule: "If an AI request fails, do not delete the last successful result").
The ``idea_revision`` records which idea revision produced this assessment.
"""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import BigInteger, Enum, ForeignKey, Identity, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPkMixin
from app.models.enums import AssessmentStatus


class Assessment(Base, UUIDPkMixin, TimestampMixin):
    __tablename__ = "assessments"

    # Monotonic insertion order. Within a single database transaction now() is
    # constant, so created_at alone cannot order assessment attempts reliably
    # (e.g. two attempts in one request). This sequence advances per row.
    seq: Mapped[int] = mapped_column(
        BigInteger, Identity(always=False, cycle=False), nullable=False
    )

    idea_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("business_ideas.id", ondelete="CASCADE"), nullable=False, index=True
    )
    idea: Mapped["BusinessIdea"] = relationship(back_populates="assessments")  # type: ignore[name-defined]

    idea_revision: Mapped[int] = mapped_column(Integer, nullable=False)
    input_snapshot: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)

    # Required assessment content (US06).
    market_considerations: Mapped[str] = mapped_column(Text, nullable=False, default="")
    target_customer_analysis: Mapped[str] = mapped_column(Text, nullable=False, default="")
    competitor_considerations: Mapped[str] = mapped_column(Text, nullable=False, default="")
    indicative_costs: Mapped[str] = mapped_column(Text, nullable=False, default="")
    suggested_next_steps: Mapped[str] = mapped_column(Text, nullable=False, default="")
    assumptions: Mapped[str] = mapped_column(Text, nullable=False, default="")
    sources: Mapped[str] = mapped_column(Text, nullable=False, default="")

    generation_status: Mapped[AssessmentStatus] = mapped_column(
        Enum(AssessmentStatus, native_enum=False, length=32),
        nullable=False,
        default=AssessmentStatus.PENDING,
    )
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
