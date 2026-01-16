"""registration auth spec v1

Revision ID: 20260112_registration_v1
Revises: 20260112_auth_parallel
Create Date: 2026-01-12

Align the core auth schema to Registration Spec v1.

Cross-DB strategy:
- Store `email_normalized` (lowercased) and enforce uniqueness on it.
  This keeps SQLite tests green and provides deterministic
  case-insensitive uniqueness without relying on Postgres CITEXT.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op


revision = "20260112_registration_v1"
down_revision = "20260112_auth_parallel"
branch_labels = None
depends_on = None


def _dialect_name() -> str:
    bind = op.get_bind()
    return str(getattr(bind.dialect, "name", ""))


def upgrade() -> None:
    dialect = _dialect_name()
    recreate_mode = "always" if dialect == "sqlite" else "auto"

    with op.batch_alter_table("users", recreate=recreate_mode) as batch:
        batch.add_column(
            sa.Column(
                "email_normalized",
                sa.String(length=320),
                nullable=False,
                server_default="",
            )
        )
        batch.add_column(
            sa.Column(
                "password_hash",
                sa.String(length=255),
                nullable=False,
                server_default="",
            )
        )
        batch.add_column(
            sa.Column(
                "password_algo",
                sa.String(length=32),
                nullable=False,
                server_default="bcrypt-v1",
            )
        )
        batch.add_column(
            sa.Column(
                "status",
                sa.String(length=16),
                nullable=False,
                server_default="pending",
            )
        )

    op.execute(
        sa.text(
            "UPDATE users SET email_normalized = lower(email) "
            "WHERE email_normalized = '' OR email_normalized IS NULL"
        )
    )
    op.execute(
        sa.text(
            "UPDATE users SET password_hash = hashed_password "
            "WHERE password_hash = '' OR password_hash IS NULL"
        )
    )
    op.execute(
        sa.text(
            "UPDATE users SET status = CASE "
            "WHEN is_active IS FALSE THEN 'disabled' "
            "WHEN is_email_verified IS TRUE THEN 'active' "
            "ELSE 'pending' END "
            "WHERE status = '' OR status IS NULL"
        )
    )

    with op.batch_alter_table("users", recreate=recreate_mode) as batch:
        batch.create_unique_constraint(
            "uq_users_email_normalized", ["email_normalized"]
        )
        batch.create_index(
            "ix_users_email_normalized", ["email_normalized"], unique=False
        )
        batch.create_index("ix_users_status", ["status"], unique=False)
        batch.create_index("ix_users_password_algo", ["password_algo"], unique=False)

    op.create_table(
        "auth_identities",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column(
            "user_id",
            sa.String(length=36),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("provider", sa.String(length=32), nullable=False),
        sa.Column("provider_subject", sa.String(length=255), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint(
            "provider", "provider_subject", name="uq_auth_identities_provider"
        ),
    )
    op.create_index(
        "ix_auth_identities_user_id", "auth_identities", ["user_id"], unique=False
    )

    op.create_table(
        "email_verification_tokens",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column(
            "user_id",
            sa.String(length=36),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("token_hash", sa.String(length=255), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("token_hash", name="uq_email_verification_tokens_hash"),
    )
    op.create_index(
        "ix_email_verification_tokens_user_id",
        "email_verification_tokens",
        ["user_id"],
        unique=False,
    )

    op.create_table(
        "mfa_factors",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column(
            "user_id",
            sa.String(length=36),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("type", sa.String(length=16), nullable=False),
        sa.Column("secret_encrypted", sa.Text(), nullable=True),
        sa.Column("credential_json", sa.JSON(), nullable=True),
        sa.Column("enabled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )
    op.create_index("ix_mfa_factors_user_id", "mfa_factors", ["user_id"], unique=False)


def downgrade() -> None:
    dialect = _dialect_name()
    recreate_mode = "always" if dialect == "sqlite" else "auto"

    op.drop_index("ix_mfa_factors_user_id", table_name="mfa_factors")
    op.drop_table("mfa_factors")

    op.drop_index(
        "ix_email_verification_tokens_user_id", table_name="email_verification_tokens"
    )
    op.drop_table("email_verification_tokens")

    op.drop_index("ix_auth_identities_user_id", table_name="auth_identities")
    op.drop_table("auth_identities")

    with op.batch_alter_table("users", recreate=recreate_mode) as batch:
        batch.drop_index("ix_users_password_algo")
        batch.drop_index("ix_users_status")
        batch.drop_index("ix_users_email_normalized")
        batch.drop_constraint("uq_users_email_normalized", type_="unique")
        batch.drop_column("status")
        batch.drop_column("password_algo")
        batch.drop_column("password_hash")
        batch.drop_column("email_normalized")
