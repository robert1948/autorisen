"""Placeholder for legacy add_integrations_tables revision

Revision ID: add_integrations_tables
Revises: c1e0cc70f7a4
Create Date: 2025-10-12 04:00:00.000000

"""

from __future__ import annotations

from typing import Sequence, Union


# revision identifiers, used by Alembic.
revision: str = "add_integrations_tables"
down_revision: Union[str, None] = "c1e0cc70f7a4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Legacy environments referenced a migration named "add_integrations_tables".
    # That change has been superseded; this placeholder keeps the revision chain intact.
    pass


def downgrade() -> None:
    pass
