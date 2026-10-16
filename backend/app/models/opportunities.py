"""Sprint 2 opportunity, permission and investment records (US09–US16)."""
from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Numeric, String, Text, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPkMixin


class Challenge(Base, UUIDPkMixin, TimestampMixin):
    __tablename__ = "challenges"
    __table_args__ = (CheckConstraint("status IN ('draft','published','closed')"),)
    owner_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), index=True)
    idea_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("business_ideas.id", ondelete="RESTRICT"))
    title: Mapped[str] = mapped_column(String(200))
    problem: Mapped[str] = mapped_column(Text, default="")
    desired_outcome: Mapped[str] = mapped_column(Text, default="")
    required_skills: Mapped[list] = mapped_column(JSONB, default=list)
    industry: Mapped[str] = mapped_column(String(120), default="")
    location: Mapped[str] = mapped_column(String(120), default="")
    timeline: Mapped[str] = mapped_column(String(200), default="")
    compensation: Mapped[str] = mapped_column(String(200), default="")
    status: Mapped[str] = mapped_column(String(32), default="draft", index=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class VerificationRequest(Base, UUIDPkMixin, TimestampMixin):
    __tablename__ = "verification_requests"
    __table_args__ = (
        CheckConstraint("status IN ('pending','approved','rejected')"),
        Index("uq_verification_pending", "user_id", unique=True, postgresql_where=text("status = 'pending'")),
    )
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), index=True)
    information: Mapped[str] = mapped_column(Text)
    reference: Mapped[str] = mapped_column(String(500), default="")
    status: Mapped[str] = mapped_column(String(32), default="pending")
    reviewer_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"))
    decision_reason: Mapped[str] = mapped_column(Text, default="")
    decided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class Proposal(Base, UUIDPkMixin, TimestampMixin):
    __tablename__ = "proposals"
    __table_args__ = (UniqueConstraint("challenge_id", "innovator_id"), CheckConstraint("cost IS NULL OR cost >= 0"), CheckConstraint("status IN ('submitted','selected','not_selected')"))
    challenge_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("challenges.id"), index=True)
    innovator_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), index=True)
    approach: Mapped[str] = mapped_column(Text)
    deliverables: Mapped[str] = mapped_column(Text)
    timeline: Mapped[str] = mapped_column(String(200))
    cost: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    status: Mapped[str] = mapped_column(String(32), default="submitted")


class Collaboration(Base, UUIDPkMixin, TimestampMixin):
    __tablename__ = "collaborations"
    challenge_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("challenges.id"), unique=True)
    selected_proposal_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("proposals.id"), unique=True)


class ContactRequest(Base, UUIDPkMixin, TimestampMixin):
    __tablename__ = "contact_requests"
    __table_args__ = (CheckConstraint("status IN ('pending','accepted','rejected','revoked')"), CheckConstraint("sender_id <> recipient_id"), CheckConstraint("(idea_id IS NULL) <> (challenge_id IS NULL)", name="ck_contact_context"))
    sender_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), index=True)
    recipient_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), index=True)
    idea_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("business_ideas.id", ondelete="RESTRICT"))
    challenge_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("challenges.id"))
    status: Mapped[str] = mapped_column(String(32), default="pending")


class Conversation(Base, UUIDPkMixin, TimestampMixin):
    __tablename__ = "conversations"
    __table_args__ = (
        CheckConstraint("(idea_id IS NULL) <> (challenge_id IS NULL)"),
        CheckConstraint("owner_id <> counterpart_id"),
        Index("uq_conversation_idea", "owner_id", "counterpart_id", "idea_id", unique=True, postgresql_where=text("idea_id IS NOT NULL")),
        Index("uq_conversation_challenge", "owner_id", "counterpart_id", "challenge_id", unique=True, postgresql_where=text("challenge_id IS NOT NULL")),
    )
    owner_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), index=True)
    counterpart_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), index=True)
    idea_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("business_ideas.id", ondelete="RESTRICT"))
    challenge_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("challenges.id"))
    current_contact_request_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("contact_requests.id"))


class Message(Base, UUIDPkMixin, TimestampMixin):
    __tablename__ = "messages"
    conversation_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("conversations.id"), index=True)
    sender_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    body: Mapped[str] = mapped_column(Text)


class InvestorPreference(Base, UUIDPkMixin, TimestampMixin):
    __tablename__ = "investor_preferences"
    __table_args__ = (CheckConstraint("min_funding >= 0 AND max_funding >= min_funding"),)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), unique=True)
    industries: Mapped[list] = mapped_column(JSONB, default=list)
    stages: Mapped[list] = mapped_column(JSONB, default=list)
    locations: Mapped[list] = mapped_column(JSONB, default=list)
    min_funding: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    max_funding: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)


class InvestmentHistory(Base, UUIDPkMixin, TimestampMixin):
    __tablename__ = "investment_history"
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), index=True)
    project_name: Mapped[str] = mapped_column(String(200))
    industry: Mapped[str] = mapped_column(String(120))
    stage: Mapped[str] = mapped_column(String(32))
    source: Mapped[str] = mapped_column(String(500))


class ProjectFundingRequirement(Base, UUIDPkMixin, TimestampMixin):
    __tablename__ = "project_funding_requirements"
    __table_args__ = (CheckConstraint("amount >= 0"),)
    idea_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("business_ideas.id", ondelete="CASCADE"), unique=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    currency: Mapped[str] = mapped_column(String(3), default="SAR")


class AssessmentShare(Base, UUIDPkMixin, TimestampMixin):
    __tablename__ = "assessment_shares"
    __table_args__ = (UniqueConstraint("assessment_id", "investor_id"),)
    assessment_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("assessments.id", ondelete="RESTRICT"), index=True)
    investor_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), index=True)
    owner_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
