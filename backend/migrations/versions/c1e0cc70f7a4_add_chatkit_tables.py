"""add ChatKit thread and event tables

Revision ID: c1e0cc70f7a4
Revises: 5aa1a34332a8
Create Date: 2025-10-11 06:20:00.000000

"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c1e0cc70f7a4"
down_revision: Union[str, None] = "5aa1a34332a8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "app_chat_threads",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("placement", sa.String(length=64), nullable=False),
        sa.Column("context", sa.JSON(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            server_onupdate=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_app_chat_threads_user_id", "app_chat_threads", ["user_id"], unique=False
    )
    op.create_index(
        "ix_app_chat_threads_user_placement",
        "app_chat_threads",
        ["user_id", "placement"],
        unique=False,
    )

    op.create_table(
        "app_chat_events",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("thread_id", sa.String(length=36), nullable=False),
        sa.Column("role", sa.String(length=32), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("tool_name", sa.String(length=64), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["thread_id"], ["app_chat_threads.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_app_chat_events_thread_id", "app_chat_events", ["thread_id"], unique=False
    )


def downgrade() -> None:
    op.drop_index("ix_app_chat_events_thread_id", table_name="app_chat_events")
    op.drop_table("app_chat_events")
    op.drop_index("ix_app_chat_threads_user_placement", table_name="app_chat_threads")
    op.drop_index("ix_app_chat_threads_user_id", table_name="app_chat_threads")
    op.drop_table("app_chat_threads")
