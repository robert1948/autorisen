"""placeholder migration to satisfy missing revision

Revision ID: add_integrations_tables
Revises: users_001
Create Date: 2025-09-20

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "add_integrations_tables"
down_revision = "users_001"
branch_labels = None
depends_on = None

def upgrade() -> None:
    # No-op placeholder. Replace with real integration table creation if needed.
    pass


def downgrade() -> None:
    # No-op
    pass
