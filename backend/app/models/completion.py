"""Sprint 3 records. Private discovery data always belongs to its creator."""
import uuid
from sqlalchemy import CheckConstraint, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base, UUIDPkMixin, TimestampMixin


class ProgressUpdate(Base, UUIDPkMixin, TimestampMixin):
    __tablename__ = "progress_updates"
    collaboration_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("collaborations.id"), index=True)
    author_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    body: Mapped[str] = mapped_column(Text)


class CustomerProfile(Base, UUIDPkMixin, TimestampMixin):
    __tablename__ = "customer_profiles"
    idea_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("business_ideas.id", ondelete="CASCADE"), unique=True)
    kind: Mapped[str] = mapped_column(String(16))
    details: Mapped[dict] = mapped_column(JSONB)
    idea_revision: Mapped[int] = mapped_column(Integer)
    provider: Mapped[str] = mapped_column(String(32))


class LeadSource(Base, UUIDPkMixin, TimestampMixin):
    __tablename__ = "lead_sources"
    owner_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), index=True)
    idea_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("business_ideas.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(500))
    filename: Mapped[str] = mapped_column(String(200))
    permission: Mapped[str] = mapped_column(String(100))
    fictional: Mapped[bool] = mapped_column(default=False)


class CompanyRecord(Base, UUIDPkMixin, TimestampMixin):
    __tablename__ = "company_records"
    __table_args__ = (UniqueConstraint("idea_id", "fingerprint"),)
    idea_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("business_ideas.id", ondelete="CASCADE"), index=True)
    source_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("lead_sources.id"))
    name: Mapped[str] = mapped_column(String(200))
    industry: Mapped[str] = mapped_column(String(120))
    location: Mapped[str] = mapped_column(String(120))
    website: Mapped[str] = mapped_column(String(500))
    business_need: Mapped[str] = mapped_column(Text)
    fingerprint: Mapped[str] = mapped_column(String(64))


class Lead(Base, UUIDPkMixin, TimestampMixin):
    __tablename__ = "leads"
    __table_args__ = (UniqueConstraint("owner_id", "idea_id", "kind", "reference_id"), CheckConstraint("kind IN ('customer','investor')"), CheckConstraint("status IN ('new','reviewing','contact_requested','contacted','interested','not_interested','follow_up_needed','closed')"))
    owner_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), index=True)
    idea_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("business_ideas.id", ondelete="RESTRICT"))
    kind: Mapped[str] = mapped_column(String(16))
    reference_id: Mapped[uuid.UUID] = mapped_column()
    snapshot: Mapped[dict] = mapped_column(JSONB)
    status: Mapped[str] = mapped_column(String(32), default="new")


class LeadNote(Base, UUIDPkMixin, TimestampMixin):
    __tablename__ = "lead_notes"
    lead_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("leads.id"), index=True)
    body: Mapped[str] = mapped_column(Text)


class OutreachDraft(Base, UUIDPkMixin, TimestampMixin):
    __tablename__ = "outreach_drafts"
    lead_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("leads.id"), unique=True)
    body: Mapped[str] = mapped_column(Text)
    provider: Mapped[str] = mapped_column(String(32))


class Rating(Base, UUIDPkMixin, TimestampMixin):
    __tablename__ = "ratings"
    __table_args__ = (UniqueConstraint("collaboration_id", "author_id"), CheckConstraint("score BETWEEN 1 AND 5"))
    collaboration_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("collaborations.id"), index=True)
    author_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    recipient_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), index=True)
    score: Mapped[int] = mapped_column(Integer)
    comment: Mapped[str] = mapped_column(Text)


class UserReport(Base, UUIDPkMixin, TimestampMixin):
    __tablename__ = "user_reports"
    reporter_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), index=True)
    target_type: Mapped[str] = mapped_column(String(32))
    target_id: Mapped[uuid.UUID] = mapped_column()
    category: Mapped[str] = mapped_column(String(32))
    description: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(16), default="open")
    decision: Mapped[str] = mapped_column(Text, default="")
    reviewer_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"))


class AdminAction(Base, UUIDPkMixin, TimestampMixin):
    __tablename__ = "admin_actions"
    actor_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), index=True)
    action: Mapped[str] = mapped_column(String(64))
    target_type: Mapped[str] = mapped_column(String(32))
    target_id: Mapped[uuid.UUID] = mapped_column()
    reason: Mapped[str] = mapped_column(Text)


class EvaluationSession(Base, UUIDPkMixin, TimestampMixin):
    __tablename__ = "evaluation_sessions"
    participant_code: Mapped[str] = mapped_column(String(80), unique=True)
    role: Mapped[str] = mapped_column(String(32))
    browser: Mapped[str] = mapped_column(String(120))
    observations: Mapped[dict] = mapped_column(JSONB)
