"""Enhance payment tracking: invoice numbers, ITN fee/net fields.

Revision ID: 7a1b2c3d4e5f
Revises: 664311d39585
Create Date: 2026-03-04
"""

from alembic import op
import sqlalchemy as sa

revision = "7a1b2c3d4e5f"
down_revision = "664311d39585"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Sequential human-readable invoice number
    op.add_column(
        "invoices",
        sa.Column("invoice_number", sa.String(32), nullable=True, unique=True),
    )
    op.create_index("ix_invoices_invoice_number", "invoices", ["invoice_number"])

    # PayFast fee and net amounts from ITN
    op.add_column(
        "transactions",
        sa.Column("amount_fee", sa.Numeric(10, 2), nullable=True),
    )
    op.add_column(
        "transactions",
        sa.Column("amount_net", sa.Numeric(10, 2), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("transactions", "amount_net")
    op.drop_column("transactions", "amount_fee")
    op.drop_index("ix_invoices_invoice_number", table_name="invoices")
    op.drop_column("invoices", "invoice_number")
