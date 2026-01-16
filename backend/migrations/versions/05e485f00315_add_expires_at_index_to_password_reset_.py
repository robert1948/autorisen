"""add expires_at index to password_reset_tokens

Revision ID: 05e485f00315
Revises: c1e2d3f4g5h6
Create Date: 2026-01-16 02:43:16.476445

"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "05e485f00315"
down_revision: Union[str, None] = "c1e2d3f4g5h6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if not inspector.has_table("password_reset_tokens"):
        return

    existing_indexes = {
        ix["name"] for ix in inspector.get_indexes("password_reset_tokens")
    }
    if "ix_password_reset_tokens_expires_at" in existing_indexes:
        return

    op.create_index(
        "ix_password_reset_tokens_expires_at",
        "password_reset_tokens",
        ["expires_at"],
        unique=False,
    )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if not inspector.has_table("password_reset_tokens"):
        return

    existing_indexes = {
        ix["name"] for ix in inspector.get_indexes("password_reset_tokens")
    }
    if "ix_password_reset_tokens_expires_at" not in existing_indexes:
        return

    op.drop_index(
        "ix_password_reset_tokens_expires_at",
        table_name="password_reset_tokens",
    )
