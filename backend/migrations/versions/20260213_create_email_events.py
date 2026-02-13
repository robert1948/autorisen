"""create email_events table

Revision ID: 20260213_email_events
Revises: 20260211_app_builds, 20260113_email_log_phase1
Create Date: 2026-02-13

Merges two heads and adds the missing email_events table.
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = "20260213_email_events"
down_revision: Union[str, Sequence[str]] = (
    "20260211_app_builds",
    "20260113_email_log_phase1",
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "email_events",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("to_email", sa.String(length=320), nullable=False),
        sa.Column("template", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index("ix_email_events_to_email", "email_events", ["to_email"])


def downgrade() -> None:
    op.drop_index("ix_email_events_to_email", table_name="email_events")
    op.drop_table("email_events")
