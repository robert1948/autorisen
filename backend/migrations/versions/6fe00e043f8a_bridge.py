"""bridge missing revision 6fe00e043f8a

Revision ID: 6fe00e043f8a
Revises: c1e2d3f4g5h6
Create Date: 2026-02-07
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "6fe00e043f8a"
down_revision: Union[str, None] = "c1e2d3f4g5h6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # NO-OP bridge revision to restore missing history in autorisen
    pass


def downgrade() -> None:
    # NO-OP
    pass
