"""Sprint 3 tracking, discovery, follow-up and administrative records."""
from alembic import op
import sqlalchemy as sa
revision = "0007_sprint3"
down_revision = "0006_assessment_provider"
branch_labels = None
depends_on = None

def upgrade():
    op.add_column("collaborations", sa.Column("status",sa.String(16),nullable=False,server_default="active"))
    op.add_column("collaborations", sa.Column("ready_at",sa.DateTime(timezone=True)))
    op.add_column("collaborations", sa.Column("completed_at",sa.DateTime(timezone=True)))
    op.create_check_constraint("ck_collaboration_status", "collaborations", "status IN ('active','ready','completed')")
    op.add_column("challenges", sa.Column("is_hidden",sa.Boolean(),nullable=False,server_default=sa.false()))
    op.add_column("business_ideas", sa.Column("is_hidden",sa.Boolean(),nullable=False,server_default=sa.false()))
    op.execute('\nCREATE TABLE progress_updates (\n\tcollaboration_id UUID NOT NULL, \n\tauthor_id UUID NOT NULL, \n\tbody TEXT NOT NULL, \n\tid UUID NOT NULL, \n\tcreated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, \n\tupdated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, \n\tPRIMARY KEY (id), \n\tFOREIGN KEY(collaboration_id) REFERENCES collaborations (id), \n\tFOREIGN KEY(author_id) REFERENCES users (id)\n)\n\n')
    op.execute('CREATE INDEX ix_progress_updates_collaboration_id ON progress_updates (collaboration_id)')
    op.execute('\nCREATE TABLE customer_profiles (\n\tidea_id UUID NOT NULL, \n\tkind VARCHAR(16) NOT NULL, \n\tdetails JSONB NOT NULL, \n\tidea_revision INTEGER NOT NULL, \n\tprovider VARCHAR(32) NOT NULL, \n\tid UUID NOT NULL, \n\tcreated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, \n\tupdated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, \n\tPRIMARY KEY (id), \n\tUNIQUE (idea_id), \n\tFOREIGN KEY(idea_id) REFERENCES business_ideas (id) ON DELETE CASCADE\n)\n\n')
    op.execute('\nCREATE TABLE lead_sources (\n\towner_id UUID NOT NULL, \n\tidea_id UUID NOT NULL, \n\tname VARCHAR(500) NOT NULL, \n\tfilename VARCHAR(200) NOT NULL, \n\tpermission VARCHAR(100) NOT NULL, \n\tfictional BOOLEAN NOT NULL, \n\tid UUID NOT NULL, \n\tcreated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, \n\tupdated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, \n\tPRIMARY KEY (id), \n\tFOREIGN KEY(owner_id) REFERENCES users (id), \n\tFOREIGN KEY(idea_id) REFERENCES business_ideas (id) ON DELETE CASCADE\n)\n\n')
    op.execute('CREATE INDEX ix_lead_sources_owner_id ON lead_sources (owner_id)')
    op.execute('\nCREATE TABLE company_records (\n\tidea_id UUID NOT NULL, \n\tsource_id UUID NOT NULL, \n\tname VARCHAR(200) NOT NULL, \n\tindustry VARCHAR(120) NOT NULL, \n\tlocation VARCHAR(120) NOT NULL, \n\twebsite VARCHAR(500) NOT NULL, \n\tbusiness_need TEXT NOT NULL, \n\tfingerprint VARCHAR(64) NOT NULL, \n\tid UUID NOT NULL, \n\tcreated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, \n\tupdated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, \n\tPRIMARY KEY (id), \n\tUNIQUE (idea_id, fingerprint), \n\tFOREIGN KEY(idea_id) REFERENCES business_ideas (id) ON DELETE CASCADE, \n\tFOREIGN KEY(source_id) REFERENCES lead_sources (id)\n)\n\n')
    op.execute('CREATE INDEX ix_company_records_idea_id ON company_records (idea_id)')
    op.execute("\nCREATE TABLE leads (\n\towner_id UUID NOT NULL, \n\tidea_id UUID NOT NULL, \n\tkind VARCHAR(16) NOT NULL, \n\treference_id UUID NOT NULL, \n\tsnapshot JSONB NOT NULL, \n\tstatus VARCHAR(32) NOT NULL, \n\tid UUID NOT NULL, \n\tcreated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, \n\tupdated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, \n\tPRIMARY KEY (id), \n\tUNIQUE (owner_id, idea_id, kind, reference_id), \n\tCHECK (kind IN ('customer','investor')), \n\tCHECK (status IN ('new','reviewing','contact_requested','contacted','interested','not_interested','follow_up_needed','closed')), \n\tFOREIGN KEY(owner_id) REFERENCES users (id), \n\tFOREIGN KEY(idea_id) REFERENCES business_ideas (id) ON DELETE RESTRICT\n)\n\n")
    op.execute('CREATE INDEX ix_leads_owner_id ON leads (owner_id)')
    op.execute('\nCREATE TABLE lead_notes (\n\tlead_id UUID NOT NULL, \n\tbody TEXT NOT NULL, \n\tid UUID NOT NULL, \n\tcreated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, \n\tupdated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, \n\tPRIMARY KEY (id), \n\tFOREIGN KEY(lead_id) REFERENCES leads (id)\n)\n\n')
    op.execute('CREATE INDEX ix_lead_notes_lead_id ON lead_notes (lead_id)')
    op.execute('\nCREATE TABLE outreach_drafts (\n\tlead_id UUID NOT NULL, \n\tbody TEXT NOT NULL, \n\tprovider VARCHAR(32) NOT NULL, \n\tid UUID NOT NULL, \n\tcreated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, \n\tupdated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, \n\tPRIMARY KEY (id), \n\tUNIQUE (lead_id), \n\tFOREIGN KEY(lead_id) REFERENCES leads (id)\n)\n\n')
    op.execute('\nCREATE TABLE ratings (\n\tcollaboration_id UUID NOT NULL, \n\tauthor_id UUID NOT NULL, \n\trecipient_id UUID NOT NULL, \n\tscore INTEGER NOT NULL, \n\tcomment TEXT NOT NULL, \n\tid UUID NOT NULL, \n\tcreated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, \n\tupdated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, \n\tPRIMARY KEY (id), \n\tUNIQUE (collaboration_id, author_id), \n\tCHECK (score BETWEEN 1 AND 5), \n\tFOREIGN KEY(collaboration_id) REFERENCES collaborations (id), \n\tFOREIGN KEY(author_id) REFERENCES users (id), \n\tFOREIGN KEY(recipient_id) REFERENCES users (id)\n)\n\n')
    op.execute('CREATE INDEX ix_ratings_collaboration_id ON ratings (collaboration_id)')
    op.execute('CREATE INDEX ix_ratings_recipient_id ON ratings (recipient_id)')
    op.execute('\nCREATE TABLE user_reports (\n\treporter_id UUID NOT NULL, \n\ttarget_type VARCHAR(32) NOT NULL, \n\ttarget_id UUID NOT NULL, \n\tcategory VARCHAR(32) NOT NULL, \n\tdescription TEXT NOT NULL, \n\tstatus VARCHAR(16) NOT NULL, \n\tdecision TEXT NOT NULL, \n\treviewer_id UUID, \n\tid UUID NOT NULL, \n\tcreated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, \n\tupdated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, \n\tPRIMARY KEY (id), \n\tFOREIGN KEY(reporter_id) REFERENCES users (id), \n\tFOREIGN KEY(reviewer_id) REFERENCES users (id)\n)\n\n')
    op.execute('CREATE INDEX ix_user_reports_reporter_id ON user_reports (reporter_id)')
    op.execute('\nCREATE TABLE admin_actions (\n\tactor_id UUID NOT NULL, \n\taction VARCHAR(64) NOT NULL, \n\ttarget_type VARCHAR(32) NOT NULL, \n\ttarget_id UUID NOT NULL, \n\treason TEXT NOT NULL, \n\tid UUID NOT NULL, \n\tcreated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, \n\tupdated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, \n\tPRIMARY KEY (id), \n\tFOREIGN KEY(actor_id) REFERENCES users (id)\n)\n\n')
    op.execute('CREATE INDEX ix_admin_actions_actor_id ON admin_actions (actor_id)')
    op.execute('\nCREATE TABLE evaluation_sessions (\n\tparticipant_code VARCHAR(80) NOT NULL, \n\trole VARCHAR(32) NOT NULL, \n\tbrowser VARCHAR(120) NOT NULL, \n\tobservations JSONB NOT NULL, \n\tid UUID NOT NULL, \n\tcreated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, \n\tupdated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, \n\tPRIMARY KEY (id), \n\tUNIQUE (participant_code)\n)\n\n')

def downgrade():
    op.drop_table('evaluation_sessions')
    op.drop_table('admin_actions')
    op.drop_table('user_reports')
    op.drop_table('ratings')
    op.drop_table('outreach_drafts')
    op.drop_table('lead_notes')
    op.drop_table('leads')
    op.drop_table('company_records')
    op.drop_table('lead_sources')
    op.drop_table('customer_profiles')
    op.drop_table('progress_updates')
    op.drop_column("business_ideas","is_hidden")
    op.drop_column("challenges","is_hidden")
    op.drop_constraint("ck_collaboration_status","collaborations",type_="check")
    op.drop_column("collaborations","completed_at")
    op.drop_column("collaborations","ready_at")
    op.drop_column("collaborations","status")
