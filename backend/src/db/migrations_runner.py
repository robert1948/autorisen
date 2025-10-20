"""Helpers to ensure Alembic migrations run when the app boots."""

from __future__ import annotations

import logging
import os
from pathlib import Path
from threading import Lock

from alembic import command
from alembic.config import Config

log = logging.getLogger(__name__)

_RUN_LOCK = Lock()
_HAS_RUN = False


def _should_run() -> bool:
    flag = os.getenv("RUN_DB_MIGRATIONS_ON_STARTUP", "1").lower()
    return flag in {"1", "true", "yes", "on"}


def run_migrations_on_startup() -> bool:
    """
    Apply Alembic migrations once per process when enabled.

    Returns True when migrations executed, False otherwise.
    Raises the underlying exception if Alembic reports a failure.
    """

    global _HAS_RUN

    if not _should_run():
        log.info("Skipping DB migrations (RUN_DB_MIGRATIONS_ON_STARTUP disabled).")
        return False

    if _HAS_RUN:
        return False

    with _RUN_LOCK:
        if _HAS_RUN:
            return False

        backend_root = Path(__file__).resolve().parents[2]
        alembic_ini = backend_root / "alembic.ini"
        migrations_dir = backend_root / "migrations"

        if not alembic_ini.exists():
            log.warning("Alembic config not found at %s; skipping migrations.", alembic_ini)
            _HAS_RUN = True
            return False

        cfg = Config(str(alembic_ini))
        cfg.set_main_option("script_location", str(migrations_dir))

        db_url = os.getenv("ALEMBIC_DATABASE_URL") or os.getenv("DATABASE_URL")
        if db_url:
            cfg.set_main_option("sqlalchemy.url", db_url)

        log.info("Applying database migrations (alembic upgrade head).")
        command.upgrade(cfg, "head")
        log.info("Database migrations applied successfully.")

        _HAS_RUN = True
        return True


__all__ = ["run_migrations_on_startup"]
