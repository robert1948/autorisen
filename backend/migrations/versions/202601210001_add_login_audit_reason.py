"""add_login_audit_reason

Revision ID: 202601210001
Revises: 4d7f2a9c1b23, c1e2d3f4g5h6
Create Date: 2026-01-21 00:01:00.000000

"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "202601210001"
down_revision: Union[str, None] = ("4d7f2a9c1b23", "c1e2d3f4g5h6")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "login_audits",
        sa.Column("reason", sa.String(length=64), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("login_audits", "reason")
