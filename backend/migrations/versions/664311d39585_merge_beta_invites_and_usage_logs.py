"""merge_beta_invites_and_usage_logs

Revision ID: 664311d39585
Revises: c3d4e5f6a7b8, e5f6a7b8c9d0
Create Date: 2026-03-03 16:33:07.695587

"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '664311d39585'
down_revision: Union[str, None] = ('c3d4e5f6a7b8', 'e5f6a7b8c9d0')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
