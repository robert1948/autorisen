"""Add missing agents.is_featured column for marketplace compatibility.

Revision ID: 8c9d0e1f2a3b
Revises: 7a1b2c3d4e5f
Create Date: 2026-03-16
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "8c9d0e1f2a3b"
down_revision = "7a1b2c3d4e5f"
branch_labels = None
depends_on = None


def _column_exists(table_name: str, column_name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return any(
        col.get("name") == column_name for col in inspector.get_columns(table_name)
    )


def upgrade() -> None:
    if not _column_exists("agents", "is_featured"):
        op.add_column(
            "agents",
            sa.Column(
                "is_featured",
                sa.Boolean(),
                nullable=False,
                server_default=sa.text("false"),
            ),
        )


def downgrade() -> None:
    if _column_exists("agents", "is_featured"):
        op.drop_column("agents", "is_featured")
