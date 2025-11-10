"""merge_heads

Revision ID: f942a87c00c5
Revises: 202502191200, add_integrations_tables
Create Date: 2025-11-09 08:24:09.169940

"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'f942a87c00c5'
down_revision: Union[str, None] = ('202502191200', 'add_integrations_tables')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
