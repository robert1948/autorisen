"""Align subscription plan_id values: starter→free, growth→pro

Revision ID: 20260219_plan_align
Revises: 20260214_subscriptions
Create Date: 2026-02-19 10:00:00.000000
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op

revision: str = "20260219_plan_align"
down_revision: Union[str, None] = "20260214_subscriptions"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Update existing rows
    op.execute("UPDATE subscriptions SET plan_id = 'free' WHERE plan_id = 'starter'")
    op.execute("UPDATE subscriptions SET plan_id = 'pro' WHERE plan_id = 'growth'")

    # Drop old constraint, add new one
    op.drop_constraint("subscription_plan_check", "subscriptions", type_="check")
    op.create_check_constraint(
        "subscription_plan_check",
        "subscriptions",
        "plan_id IN ('free', 'pro', 'enterprise')",
    )

    # Update default
    op.alter_column(
        "subscriptions",
        "plan_id",
        server_default="free",
    )


def downgrade() -> None:
    op.execute("UPDATE subscriptions SET plan_id = 'starter' WHERE plan_id = 'free'")
    op.execute("UPDATE subscriptions SET plan_id = 'growth' WHERE plan_id = 'pro'")

    op.drop_constraint("subscription_plan_check", "subscriptions", type_="check")
    op.create_check_constraint(
        "subscription_plan_check",
        "subscriptions",
        "plan_id IN ('starter', 'growth', 'enterprise')",
    )

    op.alter_column(
        "subscriptions",
        "plan_id",
        server_default="starter",
    )
