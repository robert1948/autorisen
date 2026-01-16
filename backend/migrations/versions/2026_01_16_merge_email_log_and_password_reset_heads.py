"""merge alembic heads: email log + password reset index

Revision ID: 20260116_merge_email_pwreset
Revises: 20260113_email_log_phase1, 20260116_pwreset_backfill
Create Date: 2026-01-16

"""

from __future__ import annotations

from typing import Sequence, Union


# revision identifiers, used by Alembic.
revision: str = "20260116_merge_email_pwreset"
down_revision: Union[str, None] = (
    "20260113_email_log_phase1",
    "20260116_pwreset_backfill",
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
