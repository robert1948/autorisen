"""create app_builds table

Revision ID: 20260211_app_builds
Revises: 403640c4100a
Create Date: 2026-02-11

"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "20260211_app_builds"
down_revision: Union[str, None] = "403640c4100a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "app_builds",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "app_name",
            sa.String(length=64),
            nullable=False,
            server_default="autorisen",
        ),
        sa.Column("version_label", sa.String(length=128), nullable=False),
        sa.Column("build_number", sa.Integer(), nullable=True),
        sa.Column("git_sha", sa.String(length=64), nullable=False),
        sa.Column("build_epoch", sa.BigInteger(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.UniqueConstraint(
            "app_name",
            "git_sha",
            "build_epoch",
            name="uq_app_builds_identity",
        ),
    )
    op.create_index(
        "ix_app_builds_app_name_created_at",
        "app_builds",
        ["app_name", "created_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_app_builds_app_name_created_at", table_name="app_builds")
    op.drop_table("app_builds")
