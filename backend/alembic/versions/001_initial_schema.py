"""Initial schema

Revision ID: 001
Revises:
Create Date: 2026-03-13
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "tags",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False, unique=True),
        sa.Column("color", sa.String(7), nullable=False, server_default="#6B7280"),
    )
    op.create_index("ix_tags_name", "tags", ["name"])

    op.create_table(
        "contacts",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("first_name", sa.String(100), nullable=False),
        sa.Column("last_name", sa.String(100)),
        sa.Column("display_name", sa.String(200)),
        sa.Column("email", sa.String(255), unique=True),
        sa.Column("email_secondary", sa.String(255)),
        sa.Column("phone", sa.String(50)),
        sa.Column("phone_secondary", sa.String(50)),
        sa.Column("title", sa.String(100)),
        sa.Column("image_url", sa.Text),
        sa.Column("image_storage_path", sa.Text),
        sa.Column("linkedin_url", sa.Text),
        sa.Column("twitter_url", sa.Text),
        sa.Column("github_url", sa.Text),
        sa.Column("instagram_url", sa.Text),
        sa.Column("website_url", sa.Text),
        sa.Column("address_city", sa.String(100)),
        sa.Column("address_country", sa.String(100)),
        sa.Column("birthday", sa.Date),
        sa.Column("bio_notes", sa.Text),
        sa.Column("last_contacted_at", sa.TIMESTAMP(timezone=True)),
        sa.Column("contact_frequency_days", sa.Integer),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
        sa.Column("is_archived", sa.Boolean, nullable=False, server_default="false"),
    )
    op.create_index("ix_contacts_email", "contacts", ["email"])
    op.create_index("ix_contacts_last_contacted_at", "contacts", ["last_contacted_at"])
    op.create_index("ix_contacts_is_archived", "contacts", ["is_archived"])
    # Full-text search index
    op.execute(
        "ALTER TABLE contacts ADD COLUMN fts tsvector "
        "GENERATED ALWAYS AS ("
        "  to_tsvector('english', coalesce(first_name,'') || ' ' || coalesce(last_name,'') || ' ' || coalesce(email,'') || ' ' || coalesce(title,''))"
        ") STORED"
    )
    op.create_index("ix_contacts_fts", "contacts", ["fts"], postgresql_using="gin")

    op.create_table(
        "companies",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("website_url", sa.Text),
        sa.Column("linkedin_url", sa.Text),
        sa.Column("industry", sa.String(100)),
        sa.Column("size_range", sa.String(50)),
        sa.Column("description", sa.Text),
        sa.Column("logo_url", sa.Text),
        sa.Column("logo_storage_path", sa.Text),
        sa.Column("address_city", sa.String(100)),
        sa.Column("address_country", sa.String(100)),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
        sa.Column("is_archived", sa.Boolean, nullable=False, server_default="false"),
    )
    op.create_index("ix_companies_name", "companies", ["name"])
    op.create_index("ix_companies_is_archived", "companies", ["is_archived"])
    op.execute(
        "ALTER TABLE companies ADD COLUMN fts tsvector "
        "GENERATED ALWAYS AS ("
        "  to_tsvector('english', coalesce(name,'') || ' ' || coalesce(description,''))"
        ") STORED"
    )
    op.create_index("ix_companies_fts", "companies", ["fts"], postgresql_using="gin")

    op.create_table(
        "project_stages",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("order_index", sa.Integer, nullable=False, server_default="0"),
        sa.Column("color", sa.String(7), nullable=False, server_default="#6B7280"),
        sa.Column("is_terminal", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("is_default", sa.Boolean, nullable=False, server_default="false"),
    )

    op.create_table(
        "projects",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("stage_id", UUID(as_uuid=True), sa.ForeignKey("project_stages.id")),
        sa.Column("stage_updated_at", sa.TIMESTAMP(timezone=True)),
        sa.Column("value_estimate", sa.Numeric(12, 2)),
        sa.Column("currency", sa.String(3), nullable=False, server_default="USD"),
        sa.Column("close_date_target", sa.Date),
        sa.Column("close_date_actual", sa.Date),
        sa.Column("outcome", sa.String(50)),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
        sa.Column("is_archived", sa.Boolean, nullable=False, server_default="false"),
    )
    op.create_index("ix_projects_name", "projects", ["name"])
    op.create_index("ix_projects_is_archived", "projects", ["is_archived"])

    op.create_table(
        "interactions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("contact_id", UUID(as_uuid=True), sa.ForeignKey("contacts.id"), nullable=False),
        sa.Column("project_id", UUID(as_uuid=True), sa.ForeignKey("projects.id")),
        sa.Column("raw_content", sa.Text, nullable=False),
        sa.Column("interaction_type", sa.String(50), nullable=False, server_default="other"),
        sa.Column("interaction_date", sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
        sa.Column("direction", sa.String(10), nullable=False, server_default="mutual"),
        sa.Column("from_whom", sa.String(200)),
        sa.Column("ai_status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_interactions_contact_id", "interactions", ["contact_id"])
    op.create_index("ix_interactions_project_id", "interactions", ["project_id"])
    op.create_index("ix_interactions_interaction_date", "interactions", ["interaction_date"])

    op.create_table(
        "interaction_ai_summaries",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("interaction_id", UUID(as_uuid=True), sa.ForeignKey("interactions.id"), unique=True),
        sa.Column("summary", sa.Text),
        sa.Column("action_points", sa.Text),  # JSON
        sa.Column("follow_up_date", sa.Date),
        sa.Column("key_topics", sa.Text),  # JSON array
        sa.Column("sentiment", sa.String(20)),
        sa.Column("model_used", sa.String(50)),
        sa.Column("prompt_version", sa.Integer, nullable=False, server_default="1"),
        sa.Column("processed_at", sa.TIMESTAMP(timezone=True)),
        sa.Column("raw_response", sa.Text),
    )

    op.create_table(
        "reminders",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("contact_id", UUID(as_uuid=True), sa.ForeignKey("contacts.id")),
        sa.Column("project_id", UUID(as_uuid=True), sa.ForeignKey("projects.id")),
        sa.Column("interaction_id", UUID(as_uuid=True), sa.ForeignKey("interactions.id")),
        sa.Column("text", sa.Text, nullable=False),
        sa.Column("due_date", sa.Date),
        sa.Column("is_completed", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("completed_at", sa.TIMESTAMP(timezone=True)),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_reminders_contact_id", "reminders", ["contact_id"])
    op.create_index("ix_reminders_due_date", "reminders", ["due_date"])

    # Join tables
    op.create_table(
        "contact_companies",
        sa.Column("contact_id", UUID(as_uuid=True), sa.ForeignKey("contacts.id"), primary_key=True),
        sa.Column("company_id", UUID(as_uuid=True), sa.ForeignKey("companies.id"), primary_key=True),
        sa.Column("role", sa.String(100)),
        sa.Column("is_primary", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("started_at", sa.Date),
        sa.Column("ended_at", sa.Date),
    )

    op.create_table(
        "project_contacts",
        sa.Column("project_id", UUID(as_uuid=True), sa.ForeignKey("projects.id"), primary_key=True),
        sa.Column("contact_id", UUID(as_uuid=True), sa.ForeignKey("contacts.id"), primary_key=True),
        sa.Column("role", sa.String(100)),
    )

    op.create_table(
        "project_companies",
        sa.Column("project_id", UUID(as_uuid=True), sa.ForeignKey("projects.id"), primary_key=True),
        sa.Column("company_id", UUID(as_uuid=True), sa.ForeignKey("companies.id"), primary_key=True),
    )

    op.create_table(
        "contact_tags",
        sa.Column("contact_id", UUID(as_uuid=True), sa.ForeignKey("contacts.id"), primary_key=True),
        sa.Column("tag_id", UUID(as_uuid=True), sa.ForeignKey("tags.id"), primary_key=True),
    )

    op.create_table(
        "company_tags",
        sa.Column("company_id", UUID(as_uuid=True), sa.ForeignKey("companies.id"), primary_key=True),
        sa.Column("tag_id", UUID(as_uuid=True), sa.ForeignKey("tags.id"), primary_key=True),
    )

    op.create_table(
        "project_tags",
        sa.Column("project_id", UUID(as_uuid=True), sa.ForeignKey("projects.id"), primary_key=True),
        sa.Column("tag_id", UUID(as_uuid=True), sa.ForeignKey("tags.id"), primary_key=True),
    )

    op.create_table(
        "contact_merge_suggestions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("contact_a_id", UUID(as_uuid=True), sa.ForeignKey("contacts.id"), nullable=False),
        sa.Column("contact_b_id", UUID(as_uuid=True), sa.ForeignKey("contacts.id"), nullable=False),
        sa.Column("confidence_score", sa.Float, nullable=False, server_default="0.0"),
        sa.Column("reasons", sa.Text),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("resolved_at", sa.TIMESTAMP(timezone=True)),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_merge_suggestions_contact_a", "contact_merge_suggestions", ["contact_a_id"])
    op.create_index("ix_merge_suggestions_contact_b", "contact_merge_suggestions", ["contact_b_id"])

    # Seed default pipeline stages
    op.execute("""
        INSERT INTO project_stages (id, name, order_index, color, is_terminal, is_default) VALUES
        (gen_random_uuid(), 'Prospect',       1, '#6B7280', false, true),
        (gen_random_uuid(), 'Qualified',      2, '#3B82F6', false, false),
        (gen_random_uuid(), 'Proposal',       3, '#8B5CF6', false, false),
        (gen_random_uuid(), 'Negotiation',    4, '#F59E0B', false, false),
        (gen_random_uuid(), 'Verbal Commit',  5, '#10B981', false, false),
        (gen_random_uuid(), 'On Hold',        6, '#D97706', false, false),
        (gen_random_uuid(), 'Closed Won',     7, '#22C55E', true,  false),
        (gen_random_uuid(), 'Closed Lost',    8, '#EF4444', true,  false)
    """)


def downgrade():
    tables = [
        "contact_merge_suggestions", "project_tags", "company_tags", "contact_tags",
        "project_companies", "project_contacts", "contact_companies",
        "reminders", "interaction_ai_summaries", "interactions",
        "projects", "project_stages", "companies", "contacts", "tags",
    ]
    for t in tables:
        op.drop_table(t)
