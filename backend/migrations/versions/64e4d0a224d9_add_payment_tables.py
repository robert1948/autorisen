"""add_payment_tables

Revision ID: 64e4d0a224d9
Revises: f942a87c00c5
Create Date: 2025-11-09 08:27:41.313747

"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "64e4d0a224d9"
down_revision: Union[str, None] = "f942a87c00c5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create invoices table
    op.create_table(
        "invoices",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("amount", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("item_name", sa.String(length=255), nullable=False),
        sa.Column("item_description", sa.Text(), nullable=True),
        sa.Column("customer_email", sa.String(length=255), nullable=False),
        sa.Column("customer_first_name", sa.String(length=64), nullable=True),
        sa.Column("customer_last_name", sa.String(length=64), nullable=True),
        sa.Column("payment_provider", sa.String(length=32), nullable=False),
        sa.Column("external_reference", sa.String(length=255), nullable=True),
        sa.Column("metadata_json", sa.JSON(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            server_onupdate=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint(
            "status IN ('pending', 'paid', 'cancelled', 'failed', 'refunded')",
            name="invoice_status_check",
        ),
        sa.CheckConstraint("amount > 0", name="invoice_amount_positive"),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("external_reference"),
    )
    op.create_index("ix_invoices_user_id", "invoices", ["user_id"], unique=False)
    op.create_index("ix_invoices_status", "invoices", ["status"], unique=False)
    op.create_index(
        "ix_invoices_external_reference",
        "invoices",
        ["external_reference"],
        unique=False,
    )

    # Create transactions table
    op.create_table(
        "transactions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("invoice_id", sa.String(length=36), nullable=False),
        sa.Column("amount", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("transaction_type", sa.String(length=32), nullable=False),
        sa.Column("payment_provider", sa.String(length=32), nullable=False),
        sa.Column("provider_transaction_id", sa.String(length=255), nullable=True),
        sa.Column("provider_reference", sa.String(length=255), nullable=True),
        sa.Column("itn_data", sa.JSON(), nullable=True),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("metadata_json", sa.JSON(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            server_onupdate=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint(
            "status IN ('pending', 'completed', 'failed', 'cancelled', 'refunded')",
            name="transaction_status_check",
        ),
        sa.CheckConstraint(
            "transaction_type IN ('payment', 'refund', 'chargeback')",
            name="transaction_type_check",
        ),
        sa.CheckConstraint("amount > 0", name="transaction_amount_positive"),
        sa.ForeignKeyConstraint(
            ["invoice_id"],
            ["invoices.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("provider_transaction_id"),
    )
    op.create_index(
        "ix_transactions_invoice_id", "transactions", ["invoice_id"], unique=False
    )
    op.create_index("ix_transactions_status", "transactions", ["status"], unique=False)
    op.create_index(
        "ix_transactions_provider_transaction_id",
        "transactions",
        ["provider_transaction_id"],
        unique=False,
    )
    op.create_index(
        "ix_transactions_provider_reference",
        "transactions",
        ["provider_reference"],
        unique=False,
    )

    # Create payment_methods table
    op.create_table(
        "billing_payment_methods",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("provider", sa.String(length=32), nullable=False),
        sa.Column("method_type", sa.String(length=32), nullable=False),
        sa.Column("is_default", sa.Boolean(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("provider_token", sa.String(length=255), nullable=True),
        sa.Column("last_four", sa.String(length=4), nullable=True),
        sa.Column("card_brand", sa.String(length=32), nullable=True),
        sa.Column("expiry_month", sa.Integer(), nullable=True),
        sa.Column("expiry_year", sa.Integer(), nullable=True),
        sa.Column("metadata_json", sa.JSON(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            server_onupdate=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint(
            "method_type IN ('card', 'eft', 'instant_eft', 'bank_transfer')",
            name="payment_method_type_check",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "user_id", "provider_token", name="unique_user_provider_token"
        ),
    )
    op.create_index(
        "ix_payment_methods_user_id",
        "billing_payment_methods",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    # Drop payment tables in reverse order
    op.drop_index("ix_payment_methods_user_id", table_name="billing_payment_methods")
    op.drop_table("billing_payment_methods")

    op.drop_index("ix_transactions_provider_reference", table_name="transactions")
    op.drop_index("ix_transactions_provider_transaction_id", table_name="transactions")
    op.drop_index("ix_transactions_status", table_name="transactions")
    op.drop_index("ix_transactions_invoice_id", table_name="transactions")
    op.drop_table("transactions")

    op.drop_index("ix_invoices_external_reference", table_name="invoices")
    op.drop_index("ix_invoices_status", table_name="invoices")
    op.drop_index("ix_invoices_user_id", table_name="invoices")
    op.drop_table("invoices")
