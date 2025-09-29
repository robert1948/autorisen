"""add models

Revision ID: 5b937fba0f06
Revises: 1d7a6f4d3935
Create Date: 2025-09-28 08:14:22.462826+00:00
"""

from alembic import op
import sqlalchemy as sa
# from sqlmodel import SQLModel  # if you use SQLModel, keep handy

# revision identifiers, used by Alembic.
revision = '5b937fba0f06'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Apply the migration."""
    pass


def downgrade() -> None:
    """Revert the migration."""
    pass
