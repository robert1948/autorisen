"""backfill password_reset_tokens table if missing

Revision ID: 20260116_backfill_password_reset_tokens_table
Revises: 05e485f00315
Create Date: 2026-01-16

Staging recovery helper:
Some environments may have an alembic_version consistent with later revisions
but still be missing the password_reset_tokens table. This migration creates the
table and expected indexes only if they do not already exist.

"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260116_backfill_password_reset_tokens_table"
down_revision: Union[str, None] = "05e485f00315"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not inspector.has_table("password_reset_tokens"):
        op.create_table(
            "password_reset_tokens",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("user_id", sa.String(length=36), nullable=False),
            sa.Column("token_hash", sa.String(length=255), nullable=False),
            sa.Column(
                "purpose",
                sa.String(length=32),
                nullable=False,
                server_default="password_reset",
            ),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                nullable=False,
                server_default=sa.func.now(),
            ),
            sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint(
                "token_hash", name="uq_password_reset_tokens_token_hash"
            ),
        )

    # Create expected indexes if missing.
    inspector = sa.inspect(bind)
    if not inspector.has_table("password_reset_tokens"):
        return

    existing_indexes = {ix["name"] for ix in inspector.get_indexes("password_reset_tokens")}

    if "ix_password_reset_tokens_user_id" not in existing_indexes:
        op.create_index(
            "ix_password_reset_tokens_user_id",
            "password_reset_tokens",
            ["user_id"],
            unique=False,
        )

    if "ix_password_reset_tokens_expires_at" not in existing_indexes:
        op.create_index(
            "ix_password_reset_tokens_expires_at",
            "password_reset_tokens",
            ["expires_at"],
            unique=False,
        )


def downgrade() -> None:
    # Not safely reversible: this may have been a no-op in environments where the
    # table already existed.
    pass
