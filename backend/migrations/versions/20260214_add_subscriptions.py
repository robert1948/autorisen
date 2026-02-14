"""Add subscriptions and enterprise_inquiries tables

Revision ID: 20260214_subscriptions
Revises: 20260214_dev_admin
Create Date: 2026-02-14 14:00:00.000000

"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260214_subscriptions"
down_revision: Union[str, None] = "20260214_dev_admin"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "subscriptions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column(
            "plan_id",
            sa.String(length=32),
            nullable=False,
            server_default="starter",
        ),
        sa.Column(
            "status",
            sa.String(length=32),
            nullable=False,
            server_default="active",
        ),
        sa.Column("current_period_start", sa.DateTime(timezone=True), nullable=True),
        sa.Column("current_period_end", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "cancel_at_period_end",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("payment_provider", sa.String(length=32), nullable=True),
        sa.Column(
            "provider_subscription_id", sa.String(length=255), nullable=True
        ),
        sa.Column("metadata_json", sa.JSON(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], ondelete="CASCADE"
        ),
        sa.UniqueConstraint("user_id"),
        sa.CheckConstraint(
            "plan_id IN ('starter', 'growth', 'enterprise')",
            name="subscription_plan_check",
        ),
        sa.CheckConstraint(
            "status IN ('active', 'cancelled', 'past_due', 'trialing', 'pending')",
            name="subscription_status_check",
        ),
    )
    op.create_index("ix_subscriptions_user_id", "subscriptions", ["user_id"])
    op.create_index(
        "ix_subscriptions_provider_sub_id",
        "subscriptions",
        ["provider_subscription_id"],
    )

    op.create_table(
        "enterprise_inquiries",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=True),
        sa.Column("company_name", sa.String(length=200), nullable=False),
        sa.Column("contact_email", sa.String(length=320), nullable=False),
        sa.Column("contact_name", sa.String(length=100), nullable=False),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column(
            "status",
            sa.String(length=32),
            nullable=False,
            server_default="new",
        ),
        sa.Column("responded_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], ondelete="SET NULL"
        ),
        sa.CheckConstraint(
            "status IN ('new', 'contacted', 'closed')",
            name="enterprise_inquiry_status_check",
        ),
    )
    op.create_index(
        "ix_enterprise_inquiries_user_id", "enterprise_inquiries", ["user_id"]
    )


def downgrade() -> None:
    op.drop_table("enterprise_inquiries")
    op.drop_table("subscriptions")
