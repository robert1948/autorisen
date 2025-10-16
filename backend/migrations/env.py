# backend/migrations/env.py
from __future__ import annotations

import os
import sys
from pathlib import Path
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# ------------------------------------------------------------
# Make sure the project root is on sys.path so
# `import backend.src...` works regardless of CWD.
# env.py is at: <repo>/backend/migrations/env.py
# repo_root = parents[2] of this file
#   env.py -> migrations -> backend -> <repo_root>
# ------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Alembic Config object, provides access to .ini values
config = context.config

# Configure Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ------------------------------------------------------------
# Load SQLAlchemy metadata from your app
# ------------------------------------------------------------
try:
    from backend.src.db.models import Base  # adjust if your Base lives elsewhere
except Exception as e:
    raise RuntimeError(
        "Failed to import Base metadata from backend.src.db.models. "
        "Check sys.path and package layout."
    ) from e

target_metadata = Base.metadata

# ------------------------------------------------------------
# Configure DB URL from env if not already set in alembic.ini
# (alembic.ini should have: sqlalchemy.url = %(DATABASE_URL)s)
# This ensures local runs don't fail if env is missing.
# ------------------------------------------------------------
DEFAULT_LOCAL_URL = "postgresql+psycopg2://devuser:devpass@localhost:5433/devdb"
db_url = os.getenv("DATABASE_URL", DEFAULT_LOCAL_URL)
config.set_main_option("sqlalchemy.url", db_url)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,  # detect column type changes
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section) or {},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        future=True,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
