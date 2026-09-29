"""Remove unused verification and messaging preferences; retain Sprint 1 data.

Back up before upgrading. Downgrade restores column structure and defaults;
restore the pre-upgrade backup to recover original removed values.
"""
from alembic import op
import sqlalchemy as sa

revision = "0002_sprint1_only"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column("users", "verification_status")
    op.drop_column("profiles", "contact_preference")
    # SQLAlchemy's VARCHAR enums store member NAMES, not enum values.
    for table, column, default in [
        ("users", "role", "BUSINESS_OWNER"),
        ("users", "account_status", "ACTIVE"),
        ("profiles", "profile_visibility", "REGISTERED"),
        ("business_ideas", "business_stage", "IDEA"),
        ("business_ideas", "visibility", "PRIVATE"),
        ("assessments", "generation_status", "PENDING"),
    ]:
        op.alter_column(table, column, server_default=default)


def downgrade():
    op.add_column("users", sa.Column("verification_status", sa.String(32), nullable=False, server_default="UNVERIFIED"))
    op.add_column("profiles", sa.Column("contact_preference", sa.String(32), nullable=False, server_default="CONTACT_REQUEST"))
