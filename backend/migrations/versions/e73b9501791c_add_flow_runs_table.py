"""add flow runs table

Revision ID: e73b9501791c
Revises: 1384297dc9c4
Create Date: 2025-10-12 04:25:00.000000

"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "e73b9501791c"
down_revision: Union[str, None] = "1384297dc9c4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "flow_runs",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=True),
        sa.Column("agent_id", sa.String(length=36), nullable=True),
        sa.Column("agent_version_id", sa.String(length=36), nullable=True),
        sa.Column("placement", sa.String(length=64), nullable=False),
        sa.Column("thread_id", sa.String(length=36), nullable=False),
        sa.Column("steps", sa.JSON(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_flow_runs_thread_id", "flow_runs", ["thread_id"], unique=False)
    op.create_index("ix_flow_runs_user_id", "flow_runs", ["user_id"], unique=False)
    op.create_index("ix_flow_runs_agent_id", "flow_runs", ["agent_id"], unique=False)
    op.create_index(
        "ix_flow_runs_agent_version_id", "flow_runs", ["agent_version_id"], unique=False
    )


def downgrade() -> None:
    op.drop_index("ix_flow_runs_agent_version_id", table_name="flow_runs")
    op.drop_index("ix_flow_runs_agent_id", table_name="flow_runs")
    op.drop_index("ix_flow_runs_user_id", table_name="flow_runs")
    op.drop_index("ix_flow_runs_thread_id", table_name="flow_runs")
    op.drop_table("flow_runs")
