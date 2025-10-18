# backend/migrations/env.py
from __future__ import annotations

import os
import sys
from pathlib import Path
from logging.config import fileConfig
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode

from alembic import context
from sqlalchemy import engine_from_config, pool

# -------------------------------------------------------------------
# Ensure project root on sys.path so `import backend.src...` works
# env.py -> migrations -> backend -> <repo root>
# -------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Alembic Config object, provides access to .ini values in use.
config = context.config

# Configure Python logging from alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# -------------------------------------------------------------------
# Load SQLAlchemy metadata from your app
# -------------------------------------------------------------------
try:
    from backend.src.db.models import Base  # adjust if Base lives elsewhere
except Exception as e:
    raise RuntimeError(
        "Failed to import Base metadata from backend.src.db.models. "
        "Check sys.path and package layout."
    ) from e

target_metadata = Base.metadata


# -------------------------------------------------------------------
# URL helpers
# -------------------------------------------------------------------
def _normalize_url(url: str) -> str:
    """
    Normalize DB URL for SQLAlchemy & ensure SSL if requested.
    - Convert postgres:// -> postgresql://
    - Append sslmode=require when DB_SSLMODE_REQUIRE=1 (default) and missing
    """
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://") :]

    if os.getenv("DB_SSLMODE_REQUIRE", "1") == "1":
        parsed = urlparse(url)
        params = dict(parse_qsl(parsed.query, keep_blank_values=True))
        if "sslmode" not in params:
            params["sslmode"] = "require"
            parsed = parsed._replace(query=urlencode(params))
            url = urlunparse(parsed)

    return url


def _resolved_sqlalchemy_url() -> str:
    """
    Choose DB URL in priority order:
      1) ALEMBIC_DATABASE_URL (preferred for running migrations)
      2) DATABASE_URL
      3) sensible local default
    NOTE: we intentionally do NOT read sqlalchemy.url from alembic.ini
          to avoid ConfigParser %(...) interpolation errors.
    """
    env_url = os.getenv("ALEMBIC_DATABASE_URL") or os.getenv("DATABASE_URL")
    default_local = "postgresql://postgres:postgres@localhost:5433/autorisen"
    url: str = env_url or default_local
    return _normalize_url(url)


# -------------------------------------------------------------------
# Offline / Online migration runners
# -------------------------------------------------------------------
def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    sa_url = _resolved_sqlalchemy_url()
    context.configure(
        url=sa_url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,            # detect column type changes
        compare_server_default=True,  # detect server_default changes
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    sa_url = _resolved_sqlalchemy_url()

    connectable = engine_from_config(
        {"sqlalchemy.url": sa_url},
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

