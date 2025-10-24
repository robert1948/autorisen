"""rename chat event metadata column

Revision ID: e5e402c7ab39
Revises: dc4ac5c9c3d5
Create Date: 2025-10-12 03:30:00.000000

"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "e5e402c7ab39"
down_revision: Union[str, None] = "dc4ac5c9c3d5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if "app_chat_events" not in inspector.get_table_names():
        return

    column_names = {
        column["name"] for column in inspector.get_columns("app_chat_events")
    }
    if "metadata" not in column_names:
        return

    with op.batch_alter_table("app_chat_events") as batch_op:
        batch_op.alter_column("metadata", new_column_name="event_metadata")


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if "app_chat_events" not in inspector.get_table_names():
        return

    column_names = {
        column["name"] for column in inspector.get_columns("app_chat_events")
    }
    if "event_metadata" not in column_names:
        return

    with op.batch_alter_table("app_chat_events") as batch_op:
        batch_op.alter_column("event_metadata", new_column_name="metadata")
