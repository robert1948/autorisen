"""email_jobs_outbox

Revision ID: 5f20050b5a77
Revises: 202601210001
Create Date: 2026-01-22 07:48:56.573238

"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "5f20050b5a77"
down_revision: Union[str, None] = "202601210001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "email_jobs",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("job_type", sa.String(length=64), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column(
            "status",
            sa.String(length=16),
            nullable=False,
            server_default=sa.text("'queued'"),
        ),
        sa.Column(
            "attempts",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column(
            "max_attempts",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("8"),
        ),
        sa.Column(
            "run_after",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("idempotency_key", sa.String(length=128), nullable=False),
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
        sa.UniqueConstraint("idempotency_key", name="uq_email_jobs_idempotency_key"),
    )

    op.create_index(
        "ix_email_jobs_status_run_after",
        "email_jobs",
        ["status", "run_after"],
    )
    op.create_index("ix_email_jobs_job_type", "email_jobs", ["job_type"])


def downgrade() -> None:
    op.drop_index("ix_email_jobs_job_type", table_name="email_jobs")
    op.drop_index("ix_email_jobs_status_run_after", table_name="email_jobs")
    op.drop_table("email_jobs")
