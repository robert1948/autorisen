"""agents: add tenant_id + current_version_id

Revision ID: 6fe00e043f8a
Revises: 5f20050b5a77
Create Date: 2026-02-02 07:47:16.644047

"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "6fe00e043f8a"
down_revision: Union[str, None] = "5f20050b5a77"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _column_exists(inspector: sa.Inspector, table_name: str, column_name: str) -> bool:
    return any(col["name"] == column_name for col in inspector.get_columns(table_name))


def _index_exists(inspector: sa.Inspector, table_name: str, index_name: str) -> bool:
    return any(idx["name"] == index_name for idx in inspector.get_indexes(table_name))


def _fk_exists(inspector: sa.Inspector, table_name: str, fk_name: str) -> bool:
    return any(fk["name"] == fk_name for fk in inspector.get_foreign_keys(table_name))


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    dialect = bind.dialect.name

    if "agents" in inspector.get_table_names():
        if not _column_exists(inspector, "agents", "tenant_id"):
            op.add_column("agents", sa.Column("tenant_id", sa.String(length=36)))
        if not _column_exists(inspector, "agents", "category"):
            op.add_column("agents", sa.Column("category", sa.String(length=64)))
        if not _column_exists(inspector, "agents", "current_version_id"):
            op.add_column(
                "agents",
                sa.Column("current_version_id", sa.String(length=36)),
            )

        inspector = sa.inspect(bind)
        if not _index_exists(inspector, "agents", "ix_agents_tenant_id"):
            op.create_index(
                "ix_agents_tenant_id", "agents", ["tenant_id"], unique=False
            )
        if not _index_exists(inspector, "agents", "ix_agents_current_version_id"):
            op.create_index(
                "ix_agents_current_version_id",
                "agents",
                ["current_version_id"],
                unique=False,
            )

        if dialect != "sqlite" and not _fk_exists(
            inspector, "agents", "fk_agents_current_version_id"
        ):
            op.create_foreign_key(
                "fk_agents_current_version_id",
                "agents",
                "agent_versions",
                ["current_version_id"],
                ["id"],
                ondelete="SET NULL",
            )

    if "agent_versions" in inspector.get_table_names():
        if not _column_exists(inspector, "agent_versions", "tenant_id"):
            op.add_column(
                "agent_versions", sa.Column("tenant_id", sa.String(length=36))
            )
        inspector = sa.inspect(bind)
        if not _index_exists(
            inspector, "agent_versions", "ix_agent_versions_agent_id_status"
        ):
            op.create_index(
                "ix_agent_versions_agent_id_status",
                "agent_versions",
                ["agent_id", "status"],
                unique=False,
            )

    if "tasks" in inspector.get_table_names():
        if not _column_exists(inspector, "tasks", "tenant_id"):
            op.add_column("tasks", sa.Column("tenant_id", sa.String(length=36)))
        inspector = sa.inspect(bind)
        if not _index_exists(inspector, "tasks", "ix_tasks_status"):
            op.create_index("ix_tasks_status", "tasks", ["status"], unique=False)
        if not _index_exists(inspector, "tasks", "ix_tasks_created_at"):
            op.create_index(
                "ix_tasks_created_at", "tasks", ["created_at"], unique=False
            )

    if "runs" in inspector.get_table_names():
        if not _column_exists(inspector, "runs", "tenant_id"):
            op.add_column("runs", sa.Column("tenant_id", sa.String(length=36)))

    if "audit_events" in inspector.get_table_names():
        if not _column_exists(inspector, "audit_events", "tenant_id"):
            op.add_column("audit_events", sa.Column("tenant_id", sa.String(length=36)))
        inspector = sa.inspect(bind)
        if not _index_exists(inspector, "audit_events", "ix_audit_events_event_type"):
            op.create_index(
                "ix_audit_events_event_type",
                "audit_events",
                ["event_type"],
                unique=False,
            )
        if not _index_exists(inspector, "audit_events", "ix_audit_events_created_at"):
            op.create_index(
                "ix_audit_events_created_at",
                "audit_events",
                ["created_at"],
                unique=False,
            )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if "audit_events" in inspector.get_table_names():
        if _index_exists(inspector, "audit_events", "ix_audit_events_created_at"):
            op.drop_index("ix_audit_events_created_at", table_name="audit_events")
        if _index_exists(inspector, "audit_events", "ix_audit_events_event_type"):
            op.drop_index("ix_audit_events_event_type", table_name="audit_events")
        if _column_exists(inspector, "audit_events", "tenant_id"):
            op.drop_column("audit_events", "tenant_id")

    if "runs" in inspector.get_table_names():
        if _column_exists(inspector, "runs", "tenant_id"):
            op.drop_column("runs", "tenant_id")

    if "tasks" in inspector.get_table_names():
        if _index_exists(inspector, "tasks", "ix_tasks_created_at"):
            op.drop_index("ix_tasks_created_at", table_name="tasks")
        if _index_exists(inspector, "tasks", "ix_tasks_status"):
            op.drop_index("ix_tasks_status", table_name="tasks")
        if _column_exists(inspector, "tasks", "tenant_id"):
            op.drop_column("tasks", "tenant_id")

    if "agent_versions" in inspector.get_table_names():
        if _index_exists(
            inspector, "agent_versions", "ix_agent_versions_agent_id_status"
        ):
            op.drop_index(
                "ix_agent_versions_agent_id_status",
                table_name="agent_versions",
            )
        if _column_exists(inspector, "agent_versions", "tenant_id"):
            op.drop_column("agent_versions", "tenant_id")

    if "agents" in inspector.get_table_names():
        if _fk_exists(inspector, "agents", "fk_agents_current_version_id"):
            op.drop_constraint(
                "fk_agents_current_version_id", "agents", type_="foreignkey"
            )
        if _index_exists(inspector, "agents", "ix_agents_current_version_id"):
            op.drop_index("ix_agents_current_version_id", table_name="agents")
        if _index_exists(inspector, "agents", "ix_agents_tenant_id"):
            op.drop_index("ix_agents_tenant_id", table_name="agents")
        if _column_exists(inspector, "agents", "current_version_id"):
            op.drop_column("agents", "current_version_id")
        if _column_exists(inspector, "agents", "category"):
            op.drop_column("agents", "category")
        if _column_exists(inspector, "agents", "tenant_id"):
            op.drop_column("agents", "tenant_id")
