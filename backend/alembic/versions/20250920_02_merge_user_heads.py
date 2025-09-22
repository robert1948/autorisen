"""merge users heads

Revision ID: users_merge_001
Revises: users_add_001, add_integrations_tables
Create Date: 2025-09-20

This is a merge revision to combine two heads that both descend from users_001.
"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "users_merge_001"
down_revision = ("users_add_001", "add_integrations_tables")
branch_labels = None
depends_on = None


def upgrade() -> None:
    # merge-only revision: no schema changes
    pass


def downgrade() -> None:
    # no-op
    pass
