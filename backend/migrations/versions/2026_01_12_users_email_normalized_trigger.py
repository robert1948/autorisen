"""users email_normalized trigger (Postgres)

Revision ID: 20260112_users_email_norm_trg
Revises: 20260112_registration_v1
Create Date: 2026-01-12

Ensure `users.email_normalized` is populated for legacy code paths that
only write `users.email`.

Postgres cannot reference other columns in a DEFAULT expression, so we use a
BEFORE INSERT/UPDATE trigger.
"""

from __future__ import annotations

from alembic import op


revision = "20260112_users_email_norm_trg"
down_revision = "20260112_registration_v1"
branch_labels = None
depends_on = None


def _dialect_name() -> str:
    bind = op.get_bind()
    return str(getattr(bind.dialect, "name", ""))


def upgrade() -> None:
    if _dialect_name() != "postgresql":
        return

    # Backfill existing rows that may have an empty default.
    op.execute(
        "UPDATE users SET email_normalized = lower(email) "
        "WHERE email_normalized IS NULL OR email_normalized = ''"
    )

    op.execute(
        """
        CREATE OR REPLACE FUNCTION set_users_email_normalized()
        RETURNS trigger
        LANGUAGE plpgsql
        AS $$
        BEGIN
          IF NEW.email_normalized IS NULL OR NEW.email_normalized = '' THEN
            NEW.email_normalized := lower(NEW.email);
          END IF;
          RETURN NEW;
        END;
        $$;
        """
    )

    op.execute("DROP TRIGGER IF EXISTS trg_users_email_normalized ON users;")
    op.execute(
        """
        CREATE TRIGGER trg_users_email_normalized
        BEFORE INSERT OR UPDATE ON users
        FOR EACH ROW
        EXECUTE FUNCTION set_users_email_normalized();
        """
    )


def downgrade() -> None:
    if _dialect_name() != "postgresql":
        return

    op.execute("DROP TRIGGER IF EXISTS trg_users_email_normalized ON users;")
    op.execute("DROP FUNCTION IF EXISTS set_users_email_normalized();")
