"""add onboarding flow tables

Revision ID: 20260206onboard
Revises: c1e2d3f4g5h6
Create Date: 2026-02-06 18:05:00.000000

"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
import uuid
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260206onboard"
down_revision: Union[str, None] = "c1e2d3f4g5h6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _table_exists(inspector: sa.Inspector, table_name: str) -> bool:
    return table_name in inspector.get_table_names()


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not _table_exists(inspector, "onboarding_sessions"):
        op.create_table(
            "onboarding_sessions",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("user_id", sa.String(length=36), nullable=False),
            sa.Column("status", sa.String(length=32), server_default="active", nullable=False),
            sa.Column(
                "onboarding_completed",
                sa.Boolean(),
                server_default="0",
                nullable=False,
            ),
            sa.Column("last_step_key", sa.String(length=64), nullable=True),
            sa.Column("metadata_json", sa.JSON(), nullable=True),
            sa.Column(
                "started_at",
                sa.DateTime(timezone=True),
                server_default=sa.func.now(),
                nullable=False,
            ),
            sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(
            "ix_onboarding_sessions_user_status",
            "onboarding_sessions",
            ["user_id", "status"],
        )

    if not _table_exists(inspector, "onboarding_steps"):
        op.create_table(
            "onboarding_steps",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("step_key", sa.String(length=64), nullable=False),
            sa.Column("title", sa.String(length=160), nullable=False),
            sa.Column("order_index", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("required", sa.Boolean(), nullable=False, server_default="1"),
            sa.Column("role_scope_json", sa.JSON(), nullable=True),
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
                nullable=False,
            ),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("step_key", name="uq_onboarding_steps_step_key"),
        )

    if not _table_exists(inspector, "user_onboarding_step_state"):
        op.create_table(
            "user_onboarding_step_state",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("session_id", sa.String(length=36), nullable=False),
            sa.Column("step_key", sa.String(length=64), nullable=False),
            sa.Column("status", sa.String(length=32), nullable=False, server_default="pending"),
            sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("skipped_at", sa.DateTime(timezone=True), nullable=True),
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
                nullable=False,
            ),
            sa.ForeignKeyConstraint(
                ["session_id"], ["onboarding_sessions.id"], ondelete="CASCADE"
            ),
            sa.ForeignKeyConstraint(
                ["step_key"], ["onboarding_steps.step_key"], ondelete="CASCADE"
            ),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint(
                "session_id",
                "step_key",
                name="uq_onboarding_step_state_session_step",
            ),
        )

    if not _table_exists(inspector, "onboarding_messages"):
        op.create_table(
            "onboarding_messages",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("session_id", sa.String(length=36), nullable=False),
            sa.Column("user_id", sa.String(length=36), nullable=False),
            sa.Column("role", sa.String(length=32), nullable=True),
            sa.Column("content", sa.Text(), nullable=False),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.func.now(),
                nullable=False,
            ),
            sa.ForeignKeyConstraint(
                ["session_id"], ["onboarding_sessions.id"], ondelete="CASCADE"
            ),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )

    if not _table_exists(inspector, "trust_acknowledgements"):
        op.create_table(
            "trust_acknowledgements",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("session_id", sa.String(length=36), nullable=False),
            sa.Column("user_id", sa.String(length=36), nullable=False),
            sa.Column("key", sa.String(length=64), nullable=False),
            sa.Column("metadata_json", sa.JSON(), nullable=True),
            sa.Column(
                "acknowledged_at",
                sa.DateTime(timezone=True),
                server_default=sa.func.now(),
                nullable=False,
            ),
            sa.ForeignKeyConstraint(
                ["session_id"], ["onboarding_sessions.id"], ondelete="CASCADE"
            ),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("user_id", "key", name="uq_trust_ack_user_key"),
        )

    if not _table_exists(inspector, "onboarding_event_log"):
        op.create_table(
            "onboarding_event_log",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("session_id", sa.String(length=36), nullable=False),
            sa.Column("user_id", sa.String(length=36), nullable=False),
            sa.Column("event_type", sa.String(length=64), nullable=False),
            sa.Column("step_key", sa.String(length=64), nullable=True),
            sa.Column("payload", sa.JSON(), nullable=True),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.func.now(),
                nullable=False,
            ),
            sa.ForeignKeyConstraint(
                ["session_id"], ["onboarding_sessions.id"], ondelete="CASCADE"
            ),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )

    seed_steps = [
        ("welcome", "Welcome", 1, True),
        ("profile", "Confirm your profile", 2, True),
        ("checklist_connect_data", "Connect data", 3, False),
        ("checklist_create_first_project", "Create your first project", 4, False),
        ("checklist_invite_teammate", "Invite a teammate", 5, False),
        ("checklist_run_first_agent", "Run your first agent", 6, False),
        ("trust_privacy", "Review privacy commitments", 7, True),
        ("trust_security", "Review security commitments", 8, True),
        ("complete", "Complete onboarding", 9, True),
    ]
    insert_stmt = sa.text(
        """
        INSERT INTO onboarding_steps (id, step_key, title, order_index, required)
        VALUES (:id, :step_key, :title, :order_index, :required)
        ON CONFLICT(step_key) DO NOTHING
        """
    )
    for step_key, title, order_index, required in seed_steps:
        bind.execute(
            insert_stmt,
            {
                "id": str(uuid.uuid4()),
                "step_key": step_key,
                "title": title,
                "order_index": order_index,
                "required": bool(required),
            },
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    for table_name in (
        "onboarding_event_log",
        "trust_acknowledgements",
        "onboarding_messages",
        "user_onboarding_step_state",
        "onboarding_steps",
        "onboarding_sessions",
    ):
        if _table_exists(inspector, table_name):
            op.drop_table(table_name)
