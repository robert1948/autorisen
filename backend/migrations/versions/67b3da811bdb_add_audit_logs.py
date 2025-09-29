"""add audit_logs (manual)

Revision ID: 67b3da811bdb
Revises: d6ae4005f7e5
Create Date: 2025-09-28
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "67b3da811bdb"
down_revision = "d6ae4005f7e5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column("event", sa.String(length=120), nullable=False),
        sa.Column("actor", sa.String(length=120), nullable=True),
        sa.Column("level", sa.String(length=20), nullable=False, server_default=sa.text("'info'")),
        sa.Column("meta", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index("ix_audit_logs_event", "audit_logs", ["event"], unique=False)
    op.create_index("ix_audit_logs_actor", "audit_logs", ["actor"], unique=False)


def downgrade() -> None:
    # Be defensive — these no-op if they don't exist
    op.execute("DROP INDEX IF EXISTS public.ix_audit_logs_actor")
    op.execute("DROP INDEX IF EXISTS public.ix_audit_logs_event")
    op.drop_table("audit_logs")
