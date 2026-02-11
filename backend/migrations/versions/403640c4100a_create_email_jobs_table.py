"""create email_jobs table

Revision ID: 403640c4100a
Revises: b41f0b1a5b8e
Create Date: 2026-02-11 07:59:21.529849

"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '403640c4100a'
down_revision: Union[str, None] = 'b41f0b1a5b8e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "email_jobs" not in inspector.get_table_names():
        op.create_table(
            "email_jobs",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("job_type", sa.String(length=64), nullable=False),
            sa.Column("payload", sa.JSON(), nullable=False),
            sa.Column("status", sa.String(length=32), nullable=False),
            sa.Column(
                "attempts", sa.Integer(), nullable=False, server_default="0"
            ),
            sa.Column(
                "max_attempts", sa.Integer(), nullable=False, server_default="3"
            ),
            sa.Column(
                "run_after",
                sa.DateTime(timezone=True),
                nullable=False,
                server_default=sa.func.now(),
            ),
            sa.Column("last_error", sa.Text(), nullable=True),
            sa.Column("idempotency_key", sa.String(length=128), nullable=True),
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
        )
        op.create_index(
            "ix_email_jobs_status_run_after",
            "email_jobs",
            ["status", "run_after"],
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "email_jobs" in inspector.get_table_names():
        op.drop_index("ix_email_jobs_status_run_after", table_name="email_jobs")
        op.drop_table("email_jobs")
