"""add agents registry tables

Revision ID: dc4ac5c9c3d5
Revises: c1e0cc70f7a4
Create Date: 2025-10-11 07:55:00.000000

"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "dc4ac5c9c3d5"
down_revision: Union[str, None] = "add_integrations_tables"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "agents",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("owner_id", sa.String(length=36), nullable=True),
        sa.Column("slug", sa.String(length=100), nullable=False, unique=True),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("visibility", sa.String(length=32), server_default="private", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_agents_owner_id", "agents", ["owner_id"], unique=False)

    op.create_table(
        "agent_versions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("agent_id", sa.String(length=36), nullable=False),
        sa.Column("version", sa.String(length=20), nullable=False),
        sa.Column("manifest", sa.JSON(), nullable=False),
        sa.Column("changelog", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=32), server_default="draft", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["agent_id"], ["agents.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("agent_id", "version", name="uq_agent_versions_version"),
    )
    op.create_index("ix_agent_versions_agent_id", "agent_versions", ["agent_id"], unique=False)

    # Add FK constraint if users table exists (legacy installs may lack it)
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "users" in inspector.get_table_names():
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
    fk_names = [fk["name"] for fk in inspector.get_foreign_keys("agents")]
    if "fk_agents_owner_id_users" in fk_names:
        op.drop_constraint("fk_agents_owner_id_users", "agents", type_="foreignkey")
    op.drop_index("ix_agent_versions_agent_id", table_name="agent_versions")
    op.drop_table("agent_versions")
    op.drop_index("ix_agents_owner_id", table_name="agents")
    op.drop_table("agents")
