"""add onboarding checklists table

Revision ID: 224248f081ab
Revises: e73b9501791c
Create Date: 2025-10-12 04:45:00.000000

"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = "224248f081ab"
down_revision: Union[str, None] = "e73b9501791c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _table_exists(inspector: sa.Inspector, table_name: str) -> bool:
    return table_name in inspector.get_table_names()


def _unique_exists(inspector: sa.Inspector, table_name: str, constraint_name: str) -> bool:
    return any(uc["name"] == constraint_name for uc in inspector.get_unique_constraints(table_name))


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    table_name = "onboarding_checklists"
    unique_name = "uq_onboarding_checklists_user_thread"

    if not _table_exists(inspector, table_name):
        op.create_table(
            table_name,
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("user_id", sa.String(length=36), nullable=False),
            sa.Column("thread_id", sa.String(length=36), nullable=False),
            sa.Column("tasks", sa.JSON(), nullable=False, server_default="{}"),
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=True),
                server_default=sa.func.now(),
                nullable=False,
            ),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("user_id", "thread_id", name=unique_name),
        )
        inspector = sa.inspect(bind)
    elif not _unique_exists(inspector, table_name, unique_name) and bind.dialect.name != "sqlite":
        op.create_unique_constraint(unique_name, table_name, ["user_id", "thread_id"])


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    table_name = "onboarding_checklists"

    if _table_exists(inspector, table_name):
        op.drop_table(table_name)
