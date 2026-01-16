"""merge alembic heads: email log + password reset index

Revision ID: 20260116_merge_email_log_and_password_reset_heads
Revises: 20260113_email_log_phase1, 20260116_backfill_password_reset_tokens_table
Create Date: 2026-01-16

"""

from __future__ import annotations

from typing import Sequence, Union


# revision identifiers, used by Alembic.
revision: str = "20260116_merge_email_log_and_password_reset_heads"
down_revision: Union[str, None] = (
    "20260113_email_log_phase1",
    "20260116_backfill_password_reset_tokens_table",
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
