"""enhance flow run state fields

Revision ID: 3d1a7b7b4c1c
Revises: 224248f081ab
Create Date: 2025-10-12 05:30:00.000000

"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "3d1a7b7b4c1c"
down_revision: Union[str, None] = "224248f081ab"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("flow_runs", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "status",
                sa.String(length=20),
                nullable=False,
                server_default="pending",
            )
        )
        batch_op.add_column(
            sa.Column(
                "attempt",
                sa.Integer(),
                nullable=False,
                server_default="0",
            )
        )
        batch_op.add_column(
            sa.Column(
                "max_attempts",
                sa.Integer(),
                nullable=False,
                server_default="3",
            )
        )
        batch_op.add_column(
            sa.Column("idempotency_key", sa.String(length=128), nullable=True)
        )
        batch_op.add_column(sa.Column("error_message", sa.Text(), nullable=True))
        batch_op.add_column(
            sa.Column("started_at", sa.DateTime(timezone=True), nullable=True)
        )
        batch_op.add_column(
            sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True)
        )
        batch_op.create_unique_constraint(
            "uq_flow_runs_user_idempotency", ["user_id", "idempotency_key"]
        )
        batch_op.create_index("ix_flow_runs_status", ["status"])

    # Backfill existing rows to reflect succeeded runs.
    op.execute(
        """
        UPDATE flow_runs
        SET status = 'succeeded',
            attempt = CASE WHEN attempt = 0 THEN 1 ELSE attempt END,
            max_attempts = CASE WHEN max_attempts IS NULL OR max_attempts = 0 THEN 1 ELSE max_attempts END,
            started_at = COALESCE(started_at, created_at),
            completed_at = COALESCE(completed_at, created_at)
        """
    )


def downgrade() -> None:
    with op.batch_alter_table("flow_runs", schema=None) as batch_op:
        batch_op.drop_index("ix_flow_runs_status")
        batch_op.drop_constraint("uq_flow_runs_user_idempotency", type_="unique")
        batch_op.drop_column("completed_at")
        batch_op.drop_column("started_at")
        batch_op.drop_column("error_message")
        batch_op.drop_column("idempotency_key")
        batch_op.drop_column("max_attempts")
        batch_op.drop_column("attempt")
        batch_op.drop_column("status")
