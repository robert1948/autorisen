"""add agents registry tables

Revision ID: dc4ac5c9c3d5
Revises: c1e0cc70f7a4
Create Date: 2025-10-11 07:55:00.000000

"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "dc4ac5c9c3d5"
down_revision: Union[str, None] = "add_integrations_tables"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _table_exists(inspector: sa.Inspector, table_name: str) -> bool:
    return table_name in inspector.get_table_names()


def _index_exists(inspector: sa.Inspector, table_name: str, index_name: str) -> bool:
    return any(idx["name"] == index_name for idx in inspector.get_indexes(table_name))


def _fk_exists(inspector: sa.Inspector, table_name: str, fk_name: str) -> bool:
    return any(fk["name"] == fk_name for fk in inspector.get_foreign_keys(table_name))


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    dialect = bind.dialect.name

    if not _table_exists(inspector, "agents"):
        op.create_table(
            "agents",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("owner_id", sa.String(length=36), nullable=True),
            sa.Column("slug", sa.String(length=100), nullable=False, unique=True),
            sa.Column("name", sa.String(length=160), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column(
                "visibility",
                sa.String(length=32),
                server_default="private",
                nullable=False,
            ),
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
                ["owner_id"],
                ["users.id"],
                name="fk_agents_owner_id_users",
                ondelete="SET NULL",
                use_alter=True,
            ),
            sa.PrimaryKeyConstraint("id"),
        )
        inspector = sa.inspect(bind)

    if _table_exists(inspector, "agents") and not _index_exists(
        inspector, "agents", "ix_agents_owner_id"
    ):
        op.create_index("ix_agents_owner_id", "agents", ["owner_id"], unique=False)
        inspector = sa.inspect(bind)

    if not _table_exists(inspector, "agent_versions"):
        op.create_table(
            "agent_versions",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("agent_id", sa.String(length=36), nullable=False),
            sa.Column("version", sa.String(length=20), nullable=False),
            sa.Column("manifest", sa.JSON(), nullable=False),
            sa.Column("changelog", sa.Text(), nullable=True),
            sa.Column(
                "status", sa.String(length=32), server_default="draft", nullable=False
            ),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.func.now(),
                nullable=False,
            ),
            sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(["agent_id"], ["agents.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint(
                "agent_id", "version", name="uq_agent_versions_version"
            ),
        )
        inspector = sa.inspect(bind)

    if _table_exists(inspector, "agent_versions") and not _index_exists(
        inspector, "agent_versions", "ix_agent_versions_agent_id"
    ):
        op.create_index(
            "ix_agent_versions_agent_id", "agent_versions", ["agent_id"], unique=False
        )
        inspector = sa.inspect(bind)

    if (
        dialect != "sqlite"
        and _table_exists(inspector, "agents")
        and _table_exists(inspector, "users")
        and not _fk_exists(inspector, "agents", "fk_agents_owner_id_users")
    ):
        op.create_foreign_key(
            "fk_agents_owner_id_users",
            "agents",
            "users",
            ["owner_id"],
            ["id"],
            ondelete="SET NULL",
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if (
        _table_exists(inspector, "agents")
        and _fk_exists(inspector, "agents", "fk_agents_owner_id_users")
        and bind.dialect.name != "sqlite"
    ):
        op.drop_constraint("fk_agents_owner_id_users", "agents", type_="foreignkey")
        inspector = sa.inspect(bind)

    if _table_exists(inspector, "agent_versions"):
        if _index_exists(inspector, "agent_versions", "ix_agent_versions_agent_id"):
            op.drop_index("ix_agent_versions_agent_id", table_name="agent_versions")
        op.drop_table("agent_versions")
        inspector = sa.inspect(bind)

    if _table_exists(inspector, "agents"):
        if _index_exists(inspector, "agents", "ix_agents_owner_id"):
            op.drop_index("ix_agents_owner_id", table_name="agents")
        op.drop_table("agents")
