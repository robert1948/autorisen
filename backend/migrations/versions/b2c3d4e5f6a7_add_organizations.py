"""Add organizations and organization_members tables.

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-02-24 12:00:00.000000

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = "b2c3d4e5f6a7"
down_revision = "a1b2c3d4e5f6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "organizations",
        sa.Column("id", sa.String(36), primary_key=True, nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("industry", sa.String(100), nullable=True),
        sa.Column("size_bucket", sa.String(50), nullable=True),
        sa.Column(
            "is_active",
            sa.Boolean,
            nullable=False,
            server_default=sa.text("1"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index("ix_organizations_name", "organizations", ["name"])

    op.create_table(
        "organization_members",
        sa.Column(
            "organization_id",
            sa.String(36),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "user_id",
            sa.String(36),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "org_role",
            sa.String(50),
            nullable=False,
            server_default=sa.text("'member'"),
        ),
        sa.Column(
            "joined_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index(
        "ix_org_members_user_id", "organization_members", ["user_id"]
    )
    op.create_index(
        "ix_org_members_org_id", "organization_members", ["organization_id"]
    )


def downgrade() -> None:
    op.drop_index("ix_org_members_org_id", table_name="organization_members")
    op.drop_index("ix_org_members_user_id", table_name="organization_members")
    op.drop_table("organization_members")
    op.drop_index("ix_organizations_name", table_name="organizations")
    op.drop_table("organizations")
