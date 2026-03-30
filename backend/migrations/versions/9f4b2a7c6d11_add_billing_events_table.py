"""Add billing_events audit table.

Revision ID: 9f4b2a7c6d11
Revises: 8c9d0e1f2a3b
Create Date: 2026-03-29 10:25:00
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = "9f4b2a7c6d11"
down_revision = "8c9d0e1f2a3b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    if inspector.has_table("billing_events"):
        return

    op.create_table(
        "billing_events",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("subscription_id", sa.String(length=36), nullable=False),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("detail", sa.Text(), nullable=True),
        sa.Column("invoice_id", sa.String(length=36), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_billing_events_user_id", "billing_events", ["user_id"], unique=False
    )
    op.create_index(
        "ix_billing_events_subscription_id",
        "billing_events",
        ["subscription_id"],
        unique=False,
    )
    op.create_index(
        "ix_billing_events_event_type", "billing_events", ["event_type"], unique=False
    )
    op.create_index(
        "ix_billing_events_sub_type",
        "billing_events",
        ["subscription_id", "event_type"],
        unique=False,
    )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    if not inspector.has_table("billing_events"):
        return

    op.drop_index("ix_billing_events_sub_type", table_name="billing_events")
    op.drop_index("ix_billing_events_event_type", table_name="billing_events")
    op.drop_index("ix_billing_events_subscription_id", table_name="billing_events")
    op.drop_index("ix_billing_events_user_id", table_name="billing_events")
    op.drop_table("billing_events")
