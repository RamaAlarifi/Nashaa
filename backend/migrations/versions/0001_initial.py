"""Initial Nashaa schema (Sprint 1).

Reproduces the tables that ``Base.metadata.create_all`` creates from the
models in ``app/models/``. Existing development databases created via
``create_all`` are compatible with this migration (the schema is identical);
the migration is the repeatable path for Docker and deployment
(Nashaa_Guide.md §25). Tests continue to use ``create_all`` directly.

Downgrading drops all Sprint 1 tables.

Revision ID: 0001_initial
Revises:
Create Date: 2026-01-01 00:00:00.000000
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy import Identity

from migrations.legacy_enums import (
    AccountStatus,
    AssessmentStatus,
    BusinessStage,
    ContactPreference,
    IdeaVisibility,
    ProfileVisibility,
    Role,
    VerificationStatus,
)

# revision identifiers, used by Alembic.
revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # users
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column(
            "role",
            sa.Enum(Role, native_enum=False, length=32),
            nullable=False,
            server_default=Role.BUSINESS_OWNER.value,
        ),
        sa.Column(
            "account_status",
            sa.Enum(AccountStatus, native_enum=False, length=32),
            nullable=False,
            server_default=AccountStatus.ACTIVE.value,
        ),
        sa.Column(
            "verification_status",
            sa.Enum(VerificationStatus, native_enum=False, length=32),
            nullable=False,
            server_default=VerificationStatus.UNVERIFIED.value,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )

    # profiles
    op.create_table(
        "profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("display_name", sa.String(120), nullable=False),
        sa.Column("location", sa.String(120), nullable=False, server_default=""),
        sa.Column("short_description", sa.Text, nullable=False, server_default=""),
        sa.Column(
            "role_specific_info",
            postgresql.JSONB,
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "contact_preference",
            sa.Enum(ContactPreference, native_enum=False, length=32),
            nullable=False,
            server_default=ContactPreference.CONTACT_REQUEST.value,
        ),
        sa.Column(
            "profile_visibility",
            sa.Enum(ProfileVisibility, native_enum=False, length=32),
            nullable=False,
            server_default=ProfileVisibility.REGISTERED.value,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("user_id", name="uq_profiles_user_id"),
    )
    op.create_index("ix_profiles_user_id", "profiles", ["user_id"])

    # sessions
    op.create_table(
        "sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("token_hash", sa.String(64), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("token_hash", name="uq_sessions_token_hash"),
    )
    op.create_index("ix_sessions_user_id", "sessions", ["user_id"])
    op.create_index("ix_sessions_token_hash", "sessions", ["token_hash"])

    # password_resets
    op.create_table(
        "password_resets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("token_hash", sa.String(64), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("token_hash", name="uq_password_resets_token_hash"),
    )
    op.create_index("ix_password_resets_user_id", "password_resets", ["user_id"])
    op.create_index("ix_password_resets_token_hash", "password_resets", ["token_hash"])

    # business_ideas
    op.create_table(
        "business_ideas",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "owner_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("problem", sa.Text, nullable=False, server_default=""),
        sa.Column("solution", sa.Text, nullable=False, server_default=""),
        sa.Column("industry", sa.String(120), nullable=False, server_default=""),
        sa.Column(
            "business_stage",
            sa.Enum(BusinessStage, native_enum=False, length=32),
            nullable=False,
            server_default=BusinessStage.IDEA.value,
        ),
        sa.Column("target_location", sa.String(120), nullable=False, server_default=""),
        sa.Column("intended_customers", sa.Text, nullable=False, server_default=""),
        sa.Column("budget", sa.String(120), nullable=False, server_default=""),
        sa.Column("current_challenges", sa.Text, nullable=False, server_default=""),
        sa.Column(
            "visibility",
            sa.Enum(IdeaVisibility, native_enum=False, length=32),
            nullable=False,
            server_default=IdeaVisibility.PRIVATE.value,
        ),
        sa.Column("revision_number", sa.Integer, nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_business_ideas_owner_id", "business_ideas", ["owner_id"])

    # assessments
    op.create_table(
        "assessments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        # Monotonic insertion order (matches the model's Identity column).
        sa.Column("seq", sa.BigInteger(), Identity(always=False, cycle=False), nullable=False),
        sa.Column(
            "idea_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("business_ideas.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("idea_revision", sa.Integer, nullable=False),
        sa.Column(
            "input_snapshot",
            postgresql.JSONB,
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column("market_considerations", sa.Text, nullable=False, server_default=""),
        sa.Column("target_customer_analysis", sa.Text, nullable=False, server_default=""),
        sa.Column("competitor_considerations", sa.Text, nullable=False, server_default=""),
        sa.Column("indicative_costs", sa.Text, nullable=False, server_default=""),
        sa.Column("suggested_next_steps", sa.Text, nullable=False, server_default=""),
        sa.Column("assumptions", sa.Text, nullable=False, server_default=""),
        sa.Column("sources", sa.Text, nullable=False, server_default=""),
        sa.Column(
            "generation_status",
            sa.Enum(AssessmentStatus, native_enum=False, length=32),
            nullable=False,
            server_default=AssessmentStatus.PENDING.value,
        ),
        sa.Column("error_message", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_assessments_idea_id", "assessments", ["idea_id"])


def downgrade() -> None:
    op.drop_table("assessments")
    op.drop_table("business_ideas")
    op.drop_table("password_resets")
    op.drop_table("sessions")
    op.drop_table("profiles")
    op.drop_table("users")
