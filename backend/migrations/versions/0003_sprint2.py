"""Sprint 2 opportunities, verification, messaging and explicit sharing.

Upgrade preserves all Sprint 1 data. Back up before applying; downgrade removes
Sprint 2 records and therefore requires a deliberate data-retention decision.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0003_sprint2"
down_revision = "0002_sprint1_only"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("users", sa.Column("verification_status", sa.String(32), nullable=False, server_default="unverified"))
    op.create_check_constraint("ck_user_verification", "users", "verification_status IN ('unverified','pending','approved','rejected')")
    op.add_column("profiles", sa.Column("contact_preference", sa.String(32), nullable=False, server_default="contact_request"))
    op.create_check_constraint("ck_profile_contact", "profiles", "contact_preference IN ('open','contact_request','closed')")
    # Frozen Sprint 2 schema.
    op.create_table('investment_history',
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('project_name', sa.String(length=200), nullable=False),
    sa.Column('industry', sa.String(length=120), nullable=False),
    sa.Column('stage', sa.String(length=32), nullable=False),
    sa.Column('source', sa.String(length=500), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_investment_history_user_id'), 'investment_history', ['user_id'], unique=False)
    op.create_table('investor_preferences',
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('industries', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('stages', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('locations', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('min_funding', sa.Numeric(precision=14, scale=2), nullable=False),
    sa.Column('max_funding', sa.Numeric(precision=14, scale=2), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint('min_funding >= 0 AND max_funding >= min_funding'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_id')
    )
    op.create_table('verification_requests',
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('information', sa.Text(), nullable=False),
    sa.Column('reference', sa.String(length=500), nullable=False),
    sa.Column('status', sa.String(length=32), nullable=False),
    sa.Column('reviewer_id', sa.UUID(), nullable=True),
    sa.Column('decision_reason', sa.Text(), nullable=False),
    sa.Column('decided_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint("status IN ('pending','approved','rejected')"),
    sa.ForeignKeyConstraint(['reviewer_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_verification_requests_user_id'), 'verification_requests', ['user_id'], unique=False)
    op.create_index('uq_verification_pending', 'verification_requests', ['user_id'], unique=True, postgresql_where=sa.text("status = 'pending'"))
    op.create_table('challenges',
    sa.Column('owner_id', sa.UUID(), nullable=False),
    sa.Column('idea_id', sa.UUID(), nullable=True),
    sa.Column('title', sa.String(length=200), nullable=False),
    sa.Column('problem', sa.Text(), nullable=False),
    sa.Column('desired_outcome', sa.Text(), nullable=False),
    sa.Column('required_skills', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('industry', sa.String(length=120), nullable=False),
    sa.Column('location', sa.String(length=120), nullable=False),
    sa.Column('timeline', sa.String(length=200), nullable=False),
    sa.Column('compensation', sa.String(length=200), nullable=False),
    sa.Column('status', sa.String(length=32), nullable=False),
    sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint("status IN ('draft','published','closed')"),
    sa.ForeignKeyConstraint(['idea_id'], ['business_ideas.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_challenges_owner_id'), 'challenges', ['owner_id'], unique=False)
    op.create_index(op.f('ix_challenges_status'), 'challenges', ['status'], unique=False)
    op.create_table('project_funding_requirements',
    sa.Column('idea_id', sa.UUID(), nullable=False),
    sa.Column('amount', sa.Numeric(precision=14, scale=2), nullable=False),
    sa.Column('currency', sa.String(length=3), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint('amount >= 0'),
    sa.ForeignKeyConstraint(['idea_id'], ['business_ideas.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('idea_id')
    )
    op.create_table('assessment_shares',
    sa.Column('assessment_id', sa.UUID(), nullable=False),
    sa.Column('investor_id', sa.UUID(), nullable=False),
    sa.Column('owner_id', sa.UUID(), nullable=False),
    sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['assessment_id'], ['assessments.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['investor_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('assessment_id', 'investor_id')
    )
    op.create_index(op.f('ix_assessment_shares_assessment_id'), 'assessment_shares', ['assessment_id'], unique=False)
    op.create_index(op.f('ix_assessment_shares_investor_id'), 'assessment_shares', ['investor_id'], unique=False)
    op.create_table('contact_requests',
    sa.Column('sender_id', sa.UUID(), nullable=False),
    sa.Column('recipient_id', sa.UUID(), nullable=False),
    sa.Column('idea_id', sa.UUID(), nullable=True),
    sa.Column('challenge_id', sa.UUID(), nullable=True),
    sa.Column('status', sa.String(length=32), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint("status IN ('pending','accepted','rejected','revoked')"),
    sa.CheckConstraint('sender_id <> recipient_id'),
    sa.ForeignKeyConstraint(['challenge_id'], ['challenges.id'], ),
    sa.ForeignKeyConstraint(['idea_id'], ['business_ideas.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['recipient_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['sender_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_contact_requests_recipient_id'), 'contact_requests', ['recipient_id'], unique=False)
    op.create_index(op.f('ix_contact_requests_sender_id'), 'contact_requests', ['sender_id'], unique=False)
    op.create_table('proposals',
    sa.Column('challenge_id', sa.UUID(), nullable=False),
    sa.Column('innovator_id', sa.UUID(), nullable=False),
    sa.Column('approach', sa.Text(), nullable=False),
    sa.Column('deliverables', sa.Text(), nullable=False),
    sa.Column('timeline', sa.String(length=200), nullable=False),
    sa.Column('cost', sa.Numeric(precision=14, scale=2), nullable=True),
    sa.Column('status', sa.String(length=32), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint("status IN ('submitted','selected','not_selected')"),
    sa.CheckConstraint('cost IS NULL OR cost >= 0'),
    sa.ForeignKeyConstraint(['challenge_id'], ['challenges.id'], ),
    sa.ForeignKeyConstraint(['innovator_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('challenge_id', 'innovator_id')
    )
    op.create_index(op.f('ix_proposals_challenge_id'), 'proposals', ['challenge_id'], unique=False)
    op.create_index(op.f('ix_proposals_innovator_id'), 'proposals', ['innovator_id'], unique=False)
    op.create_table('collaborations',
    sa.Column('challenge_id', sa.UUID(), nullable=False),
    sa.Column('selected_proposal_id', sa.UUID(), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['challenge_id'], ['challenges.id'], ),
    sa.ForeignKeyConstraint(['selected_proposal_id'], ['proposals.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('challenge_id'),
    sa.UniqueConstraint('selected_proposal_id')
    )
    op.create_table('conversations',
    sa.Column('owner_id', sa.UUID(), nullable=False),
    sa.Column('counterpart_id', sa.UUID(), nullable=False),
    sa.Column('idea_id', sa.UUID(), nullable=True),
    sa.Column('challenge_id', sa.UUID(), nullable=True),
    sa.Column('current_contact_request_id', sa.UUID(), nullable=True),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint('(idea_id IS NULL) <> (challenge_id IS NULL)'),
    sa.CheckConstraint('owner_id <> counterpart_id'),
    sa.ForeignKeyConstraint(['challenge_id'], ['challenges.id'], ),
    sa.ForeignKeyConstraint(['counterpart_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['current_contact_request_id'], ['contact_requests.id'], ),
    sa.ForeignKeyConstraint(['idea_id'], ['business_ideas.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_conversations_counterpart_id'), 'conversations', ['counterpart_id'], unique=False)
    op.create_index(op.f('ix_conversations_owner_id'), 'conversations', ['owner_id'], unique=False)
    op.create_index('uq_conversation_challenge', 'conversations', ['owner_id', 'counterpart_id', 'challenge_id'], unique=True, postgresql_where=sa.text('challenge_id IS NOT NULL'))
    op.create_index('uq_conversation_idea', 'conversations', ['owner_id', 'counterpart_id', 'idea_id'], unique=True, postgresql_where=sa.text('idea_id IS NOT NULL'))
    op.create_table('messages',
    sa.Column('conversation_id', sa.UUID(), nullable=False),
    sa.Column('sender_id', sa.UUID(), nullable=False),
    sa.Column('body', sa.Text(), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ),
    sa.ForeignKeyConstraint(['sender_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_messages_conversation_id'), 'messages', ['conversation_id'], unique=False)


def downgrade():
    op.drop_table("messages")
    op.drop_table("conversations")
    op.drop_table("collaborations")
    op.drop_table("proposals")
    op.drop_table("contact_requests")
    op.drop_table("assessment_shares")
    op.drop_table("project_funding_requirements")
    op.drop_table("challenges")
    op.drop_table("verification_requests")
    op.drop_table("investor_preferences")
    op.drop_table("investment_history")
    op.drop_constraint("ck_profile_contact", "profiles", type_="check")
    op.drop_column("profiles", "contact_preference")
    op.drop_constraint("ck_user_verification", "users", type_="check")
    op.drop_column("users", "verification_status")
