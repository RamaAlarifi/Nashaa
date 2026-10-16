"""Record assessment provenance without relabelling historic output as Gemini."""
from alembic import op
import sqlalchemy as sa
revision = "0006_assessment_provider"
down_revision = "0005_plan_industries"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("assessments",sa.Column("provider",sa.String(16),nullable=False,server_default="unknown"))
    op.execute("UPDATE assessments SET provider='mock' WHERE sources='No external sources used. This is a simulated assessment.'")


def downgrade():
    op.drop_column("assessments","provider")
