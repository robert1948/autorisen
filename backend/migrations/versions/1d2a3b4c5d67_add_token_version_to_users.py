"""add token_version column to users

Revision ID: 1d2a3b4c5d67
Revises: f5b3c9e5a4c2
Create Date: 2025-10-13 08:10:00

"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "1d2a3b4c5d67"
down_revision: Union[str, None] = "f5b3c9e5a4c2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    dialect = bind.dialect.name if bind else None

    op.add_column(
        "users",
        sa.Column("token_version", sa.Integer(), nullable=False, server_default="1"),
    )
    if dialect != "sqlite":
        # Drop the server_default now that existing rows have 1
        op.alter_column("users", "token_version", server_default=None)


def downgrade() -> None:
    op.drop_column("users", "token_version")
