"""
Add integrations tables: crm_leads and pos_orders
=================================================

Revision ID: add_integrations_tables
Revises: add_audit_logs_table
Create Date: 2025-09-06 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "add_integrations_tables"
down_revision = "add_audit_logs_table"
branch_labels = None
depends_on = None


def _uuid_type(bind):
    """Return a UUID-compatible type for the active dialect."""
    if bind.dialect.name == "postgresql":
        return postgresql.UUID(as_uuid=False)
    # Fallback for SQLite and others
    return sa.String(36)


def _json_type(bind):
    """Return a JSON-compatible type for the active dialect."""
    if bind.dialect.name == "postgresql":
        return postgresql.JSONB()
    # SQLite: store JSON as TEXT
    return sa.Text()


def upgrade() -> None:
    bind = op.get_bind()

    # crm_leads table
    op.create_table(
        "crm_leads",
        sa.Column("id", _uuid_type(bind), primary_key=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("phone", sa.String(length=50), nullable=True),
        sa.Column("source", sa.String(length=100), nullable=True),
        sa.Column(
            "status",
            sa.String(length=50),
            nullable=False,
            server_default=sa.text("'new'"),
        ),
        sa.Column("notes", sa.Text(), nullable=True),
        # attribute in ORM is lead_metadata; DB column is 'metadata'
        sa.Column("metadata", _json_type(bind), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
    )
    # Indexes for crm_leads
    op.create_index("ix_crm_leads_email", "crm_leads", ["email"], unique=False)
    op.create_index("ix_crm_leads_source", "crm_leads", ["source"], unique=False)
    op.create_index(
        "ix_crm_leads_created_at", "crm_leads", ["created_at"], unique=False
    )

    # pos_orders table
    op.create_table(
        "pos_orders",
        sa.Column("id", _uuid_type(bind), primary_key=True, nullable=False),
        sa.Column("customer_name", sa.String(length=255), nullable=True),
        sa.Column("item", sa.String(length=255), nullable=False),
        sa.Column(
            "quantity", sa.Integer(), nullable=False, server_default=sa.text("1")
        ),
        sa.Column(
            "total_cents", sa.Integer(), nullable=False, server_default=sa.text("0")
        ),
        sa.Column(
            "currency",
            sa.String(length=3),
            nullable=False,
            server_default=sa.text("'USD'"),
        ),
        sa.Column(
            "status",
            sa.String(length=50),
            nullable=False,
            server_default=sa.text("'pending'"),
        ),
        # attribute in ORM is order_metadata; DB column is 'metadata'
        sa.Column("metadata", _json_type(bind), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
    )
    # Indexes for pos_orders
    op.create_index(
        "ix_pos_orders_created_at", "pos_orders", ["created_at"], unique=False
    )


def downgrade() -> None:
    # Drop indexes then tables (order matters on some RDBMS)
    op.drop_index("ix_pos_orders_created_at", table_name="pos_orders")
    op.drop_table("pos_orders")

    op.drop_index("ix_crm_leads_created_at", table_name="crm_leads")
    op.drop_index("ix_crm_leads_source", table_name="crm_leads")
    op.drop_index("ix_crm_leads_email", table_name="crm_leads")
    op.drop_table("crm_leads")
