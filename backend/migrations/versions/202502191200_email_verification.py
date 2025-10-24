"""Add email verification fields to users."""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.engine import reflection

# revision identifiers, used by Alembic.
revision = "202502191200"
down_revision = "4d7f2a9c1b23"
branch_labels = None
depends_on = None


def _column_exists(inspector: reflection.Inspector, table: str, column: str) -> bool:
    return column in {col["name"] for col in inspector.get_columns(table)}


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    # Add column if missing; normalize token_version default and NULLs.
    with op.batch_alter_table("users") as batch:
        if not _column_exists(inspector, "users", "email_verified_at"):
            batch.add_column(
                sa.Column(
                    "email_verified_at", sa.DateTime(timezone=True), nullable=True
                )
            )

        # Ensure token_version has a non-null default and value.
        batch.alter_column(
            "token_version",
            existing_type=sa.Integer(),
            nullable=False,
            server_default=sa.text("0"),
        )

    # Backfill any NULL token_version to 0
    op.execute("UPDATE users SET token_version = 0 WHERE token_version IS NULL")

    # Backfill email_verified_at for already-verified users.
    # IMPORTANT: choose a timestamp function the current dialect supports.
    if bind.dialect.name == "sqlite":
        timestamp_sql = "CURRENT_TIMESTAMP"
    else:
        timestamp_sql = "NOW()"

    op.execute(
        sa.text(
            f"""
            UPDATE users
            SET email_verified_at = {timestamp_sql}
            WHERE COALESCE(is_email_verified, FALSE) IS TRUE
              AND email_verified_at IS NULL
            """
        )
    )


def downgrade() -> None:
    # Revert token_version default (to previous behavior) and drop the column safely.
    with op.batch_alter_table("users") as batch:
        batch.alter_column(
            "token_version",
            existing_type=sa.Integer(),
            nullable=False,
            server_default=sa.text("1"),
        )

    # DROP COLUMN with IF EXISTS avoids failures on partial/redo migrations.
    op.execute("ALTER TABLE users DROP COLUMN IF EXISTS email_verified_at")
