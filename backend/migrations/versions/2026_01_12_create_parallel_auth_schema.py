"""create parallel uuid auth/org schema (no cutover)

Revision ID: 20260112_auth_parallel
Revises: c1e2d3f4g5h6
Create Date: 2026-01-12

Additive-only: introduces a parallel, UUID-first auth/org schema without
modifying any existing authentication tables or routes.

PostgreSQL-only operations (CREATE EXTENSION citext + ALTER COLUMN TYPE citext)
are guarded so SQLite test runs remain green.
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# NOTE: importing postgresql dialect types is safe; statements that require
# PostgreSQL are executed only when the bound dialect is postgresql.
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "20260112_auth_parallel"
down_revision = "c1e2d3f4g5h6"
branch_labels = None
depends_on = None


def _is_postgres() -> bool:
    bind = op.get_bind()
    return getattr(bind.dialect, "name", None) == "postgresql"


def upgrade() -> None:
    is_pg = _is_postgres()

    # 1) Extensions (safe additive). CITEXT is used for case-insensitive emails.
    if is_pg:
        op.execute('CREATE EXTENSION IF NOT EXISTS "citext";')

    # Defaults that work on both engines
    now_default = sa.text("now()") if is_pg else sa.text("CURRENT_TIMESTAMP")
    true_default = sa.text("true") if is_pg else sa.text("1")

    # 2) users_new
    op.create_table(
        "users_new",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True) if is_pg else sa.String(36),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "email", sa.Text(), nullable=False
        ),  # converted to CITEXT below on PG
        sa.Column("password_hash", sa.Text(), nullable=True),
        sa.Column("email_verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "is_active",
            sa.Boolean() if is_pg else sa.Integer(),
            nullable=False,
            server_default=true_default,
        ),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=now_default,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=now_default,
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("email", name="uq_users_new_email"),
    )

    # Convert email to CITEXT (Postgres only)
    if is_pg:
        op.execute("ALTER TABLE users_new ALTER COLUMN email TYPE citext;")

    op.create_index("ix_users_new_email", "users_new", ["email"], unique=False)

    # 3) organizations_new
    op.create_table(
        "organizations_new",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True) if is_pg else sa.String(36),
            primary_key=True,
            nullable=False,
        ),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("industry", sa.String(length=100), nullable=True),
        sa.Column("size_bucket", sa.String(length=50), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=now_default,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=now_default,
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_orgs_new_name", "organizations_new", ["name"], unique=False)

    # 4) organization_members_new
    op.create_table(
        "organization_members_new",
        sa.Column(
            "organization_id",
            postgresql.UUID(as_uuid=True) if is_pg else sa.String(36),
            sa.ForeignKey("organizations_new.id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True) if is_pg else sa.String(36),
            sa.ForeignKey("users_new.id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "role",
            sa.String(length=50),
            nullable=False,
            server_default=sa.text("'member'") if is_pg else sa.text("member"),
        ),
        sa.Column(
            "joined_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=now_default,
        ),
    )
    op.create_index(
        "ix_org_members_new_user_id",
        "organization_members_new",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        "ix_org_members_new_org_id",
        "organization_members_new",
        ["organization_id"],
        unique=False,
    )

    # 5) user_profiles_new
    op.create_table(
        "user_profiles_new",
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True) if is_pg else sa.String(36),
            sa.ForeignKey("users_new.id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False,
        ),
        sa.Column("full_name", sa.String(length=255), nullable=True),
        sa.Column("avatar_url", sa.Text(), nullable=True),
        sa.Column("timezone", sa.String(length=64), nullable=True),
        sa.Column("locale", sa.String(length=32), nullable=True),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=now_default,
        ),
    )


def downgrade() -> None:
    # Downgrade is safe because we only added parallel tables.
    op.drop_table("user_profiles_new")
    op.drop_index("ix_org_members_new_org_id", table_name="organization_members_new")
    op.drop_index("ix_org_members_new_user_id", table_name="organization_members_new")
    op.drop_table("organization_members_new")
    op.drop_index("ix_orgs_new_name", table_name="organizations_new")
    op.drop_table("organizations_new")
    op.drop_index("ix_users_new_email", table_name="users_new")
    op.drop_table("users_new")
    # We do NOT drop citext extension in downgrade (other parts may use it).
