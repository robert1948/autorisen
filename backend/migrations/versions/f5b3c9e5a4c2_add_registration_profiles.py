"""add registration-specific user fields and profiles"""

from __future__ import annotations

from typing import Any, Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "f5b3c9e5a4c2"
down_revision: Union[str, None] = "3d1a7b7b4c1c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    dialect = bind.dialect.name if bind else None
    inspector = sa.inspect(bind)

    if dialect == "postgresql":
        op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto";')
        op.execute('CREATE EXTENSION IF NOT EXISTS "citext";')

    user_columns = {column["name"] for column in inspector.get_columns("users")}
    with op.batch_alter_table("users", schema=None) as batch_op:
        if "first_name" not in user_columns:
            batch_op.add_column(
                sa.Column("first_name", sa.String(length=50), nullable=False, server_default="")
            )
        if "last_name" not in user_columns:
            batch_op.add_column(
                sa.Column("last_name", sa.String(length=50), nullable=False, server_default="")
            )
        if "role" not in user_columns:
            batch_op.add_column(
                sa.Column("role", sa.String(length=32), nullable=False, server_default="Customer")
            )
        if "company_name" not in user_columns:
            batch_op.add_column(
                sa.Column("company_name", sa.String(length=100), nullable=False, server_default="")
            )
        if "is_email_verified" not in user_columns:
            batch_op.add_column(
                sa.Column("is_email_verified", sa.Boolean(), nullable=False, server_default=sa.text("false"))
            )

    existing_checks = {constraint["name"] for constraint in inspector.get_check_constraints("users")}
    if dialect != "sqlite":
        if "ck_users_first_name_length" not in existing_checks:
            op.create_check_constraint(
                "ck_users_first_name_length", "users", "length(first_name) <= 50"
            )
        if "ck_users_last_name_length" not in existing_checks:
            op.create_check_constraint(
                "ck_users_last_name_length", "users", "length(last_name) <= 50"
            )
        if "ck_users_company_name_length" not in existing_checks:
            op.create_check_constraint(
                "ck_users_company_name_length", "users", "length(company_name) <= 100"
            )

    if dialect == "postgresql":
        op.alter_column(
            "users",
            "email",
            type_=postgresql.CITEXT(),
            existing_nullable=False,
        )

    existing_tables = set(inspector.get_table_names())
    user_profiles_columns = set()
    profile_type = (
        postgresql.JSONB(astext_type=sa.Text()) if dialect == "postgresql" else sa.JSON()
    )
    profile_default = sa.text("'{}'::jsonb") if dialect == "postgresql" else sa.text("'{}'")

    user_profiles_columns_info: list[dict[str, Any]] = []
    if "user_profiles" not in existing_tables:
        op.create_table(
            "user_profiles",
            sa.Column("user_id", sa.String(length=36), nullable=False),
            sa.Column("profile", profile_type, nullable=False, server_default=profile_default),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=True),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
            ),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("user_id"),
        )
        user_profiles_columns = {"user_id", "profile", "created_at", "updated_at"}
    else:
        user_profiles_columns_info = inspector.get_columns("user_profiles")
        user_profiles_columns = {column["name"] for column in user_profiles_columns_info}
        with op.batch_alter_table("user_profiles") as batch_op:
            if "profile" not in user_profiles_columns:
                batch_op.add_column(
                    sa.Column("profile", profile_type, nullable=False, server_default=profile_default)
                )
                user_profiles_columns.add("profile")
            if "created_at" not in user_profiles_columns:
                batch_op.add_column(
                    sa.Column(
                        "created_at",
                        sa.DateTime(timezone=True),
                        nullable=False,
                        server_default=sa.text("CURRENT_TIMESTAMP"),
                    )
                )
                user_profiles_columns.add("created_at")
            if "updated_at" not in user_profiles_columns:
                batch_op.add_column(
                    sa.Column(
                        "updated_at",
                        sa.DateTime(timezone=True),
                        nullable=False,
                        server_default=sa.text("CURRENT_TIMESTAMP"),
                    )
                )
                user_profiles_columns.add("updated_at")
        if (
            dialect == "postgresql"
            and any(
                column["name"] == "profile" and not isinstance(column["type"], postgresql.JSONB)
                for column in user_profiles_columns_info
            )
        ):
            op.execute(
                "ALTER TABLE user_profiles ALTER COLUMN profile TYPE jsonb USING profile::jsonb"
            )
            op.execute("ALTER TABLE user_profiles ALTER COLUMN profile SET DEFAULT '{}'::jsonb")

    if "analytics_events" not in existing_tables:
        op.create_table(
            "analytics_events",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("event_type", sa.String(length=64), nullable=False),
            sa.Column("step", sa.String(length=32), nullable=True),
            sa.Column("role", sa.String(length=32), nullable=True),
            sa.Column("details", sa.JSON(), nullable=True),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
            ),
            sa.PrimaryKeyConstraint("id"),
        )

    if dialect == "postgresql" and "profile" in user_profiles_columns:
        op.execute(
            'CREATE INDEX IF NOT EXISTS ix_user_profiles_profile_gin ON user_profiles USING GIN (profile jsonb_path_ops)'
        )


def downgrade() -> None:
    bind = op.get_bind()
    dialect = bind.dialect.name if bind else None

    if dialect == "postgresql":
        op.execute('DROP INDEX IF EXISTS ix_user_profiles_profile_gin')

    op.drop_table("analytics_events")
    op.drop_table("user_profiles")

    if dialect == "postgresql":
        op.alter_column(
            "users",
            "email",
            type_=sa.String(length=320),
            existing_nullable=False,
        )

    op.drop_constraint("ck_users_company_name_length", "users", type_="check")
    op.drop_constraint("ck_users_last_name_length", "users", type_="check")
    op.drop_constraint("ck_users_first_name_length", "users", type_="check")

    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.drop_column("is_email_verified")
        batch_op.drop_column("company_name")
        batch_op.drop_column("role")
        batch_op.drop_column("last_name")
        batch_op.drop_column("first_name")
