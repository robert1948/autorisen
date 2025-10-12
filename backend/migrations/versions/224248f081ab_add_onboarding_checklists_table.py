"""add onboarding checklists table

Revision ID: 224248f081ab
Revises: e73b9501791c
Create Date: 2025-10-12 04:45:00.000000

"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "224248f081ab"
down_revision: Union[str, None] = "e73b9501791c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "onboarding_checklists",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("thread_id", sa.String(length=36), nullable=False),
        sa.Column("tasks", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_unique_constraint(
        "uq_onboarding_checklists_user_thread",
        "onboarding_checklists",
        ["user_id", "thread_id"],
    )


def downgrade() -> None:
    op.drop_constraint("uq_onboarding_checklists_user_thread", "onboarding_checklists", type_="unique")
    op.drop_table("onboarding_checklists")
