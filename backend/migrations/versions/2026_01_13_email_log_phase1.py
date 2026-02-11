"""email communications logging tables (Phase 1)

Revision ID: 20260113_email_log_phase1
Revises: 20260112_users_email_norm_trg
Create Date: 2026-01-13

Additive-only tables:
- email_threads
- email_messages
- email_attachments

Stores metadata only; no body_html/body_text in Phase 1.
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

try:
    from sqlalchemy.dialects import postgresql
except Exception:  # pragma: no cover
    postgresql = None  # type: ignore


# revision identifiers, used by Alembic.
revision: str = "20260113_email_log_phase1"
down_revision: Union[str, None] = "20260112_users_email_norm_trg"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _dialect_name() -> str:
    bind = op.get_bind()
    return str(getattr(bind.dialect, "name", ""))


def upgrade() -> None:
    dialect = _dialect_name()

    json_type = sa.JSON
    if dialect == "postgresql" and postgresql is not None:
        json_type = postgresql.JSONB

    op.create_table(
        "email_threads",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("provider", sa.Text(), nullable=False),
        sa.Column("provider_thread_id", sa.Text(), nullable=True),
        sa.Column("subject", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )

    op.create_index(
        "ix_email_threads_tenant_provider_thread",
        "email_threads",
        ["tenant_id", "provider", "provider_thread_id"],
    )

    op.create_table(
        "email_messages",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column(
            "thread_id",
            sa.String(length=36),
            sa.ForeignKey("email_threads.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "direction",
            sa.Text(),
            nullable=False,
        ),
        sa.Column("provider", sa.Text(), nullable=False),
        sa.Column("provider_message_id", sa.Text(), nullable=True),
        sa.Column("from_addr", sa.Text(), nullable=False),
        sa.Column(
            "to_addrs",
            json_type,
            nullable=False,
            server_default=sa.text("'[]'"),
        ),
        sa.Column(
            "cc_addrs",
            json_type,
            nullable=False,
            server_default=sa.text("'[]'"),
        ),
        sa.Column(
            "bcc_addrs",
            json_type,
            nullable=False,
            server_default=sa.text("'[]'"),
        ),
        sa.Column("subject", sa.Text(), nullable=True),
        sa.Column("snippet", sa.Text(), nullable=True),
        sa.Column(
            "status",
            sa.Text(),
            nullable=False,
            server_default=sa.text("'recorded'"),
        ),
        sa.Column("error_code", sa.Text(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("received_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "meta",
            json_type,
            nullable=False,
            server_default=sa.text("'{}'"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.CheckConstraint(
            "direction IN ('inbound','outbound')",
            name="ck_email_messages_direction",
        ),
    )

    op.create_index(
        "ix_email_messages_tenant_thread_created",
        "email_messages",
        ["tenant_id", "thread_id", "created_at"],
    )

    if dialect == "postgresql":
        # Enforce uniqueness only when provider_message_id is present.
        op.create_index(
            "uq_email_messages_provider_message_id",
            "email_messages",
            ["provider", "provider_message_id"],
            unique=True,
            postgresql_where=sa.text("provider_message_id IS NOT NULL"),
        )
    else:
        # SQLite treats NULLs as distinct in UNIQUE indexes, so this is close enough.
        op.create_index(
            "uq_email_messages_provider_message_id",
            "email_messages",
            ["provider", "provider_message_id"],
            unique=True,
        )

    op.create_table(
        "email_attachments",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column(
            "message_id",
            sa.String(length=36),
            sa.ForeignKey("email_messages.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("filename", sa.Text(), nullable=False),
        sa.Column("mime_type", sa.Text(), nullable=True),
        sa.Column("size_bytes", sa.BigInteger(), nullable=True),
        sa.Column("checksum", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )

    op.create_index(
        "ix_email_attachments_message_id",
        "email_attachments",
        ["message_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_email_attachments_message_id", table_name="email_attachments")
    op.drop_table("email_attachments")

    op.drop_index("uq_email_messages_provider_message_id", table_name="email_messages")
    op.drop_index(
        "ix_email_messages_tenant_thread_created", table_name="email_messages"
    )
    op.drop_table("email_messages")

    op.drop_index("ix_email_threads_tenant_provider_thread", table_name="email_threads")
    op.drop_table("email_threads")
