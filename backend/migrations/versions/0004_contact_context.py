"""Enforce a single opportunity context for contact requests."""
from alembic import op

revision = "0004_contact_context"
down_revision = "0003_sprint2"
branch_labels = None
depends_on = None


def upgrade():
    op.create_check_constraint("ck_contact_context", "contact_requests", "(idea_id IS NULL) <> (challenge_id IS NULL)")


def downgrade():
    op.drop_constraint("ck_contact_context", "contact_requests", type_="check")
