"""auth: enforce email uniqueness + terms fields (AUTH-REGISTERFLOW-003)

Revision ID: aa304231e2e8
Revises: 20260206onboard
Create Date: 2026-02-09 08:13:41.700275

"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'aa304231e2e8'
down_revision: Union[str, None] = '20260206onboard'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("terms_accepted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "users",
        sa.Column("terms_version", sa.String(length=32), nullable=True),
    )
    op.create_index(
        "uq_users_email_lower",
        "users",
        [sa.text("lower(email)")],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("uq_users_email_lower", table_name="users")
    op.drop_column("users", "terms_version")
    op.drop_column("users", "terms_accepted_at")
