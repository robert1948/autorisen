# backend/alembic/env.py
from logging.config import fileConfig
from alembic import context
from sqlalchemy import engine_from_config, pool
import os, sys

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Ensure project root (/app/backend) is importable
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# --- Import SQLAlchemy Base and models so tables are registered ---
from app.database import Base  # must define class Base(DeclarativeBase): pass

# Import model modules to populate Base.metadata for autogenerate
# (add more modules here as you create them)
try:
    from app.models import user as _user  # noqa: F401
except Exception:
    # It's okay if this doesn't exist yet; autogenerate will be empty.
    pass

target_metadata = Base.metadata


def _db_url() -> str:
    return os.environ.get("DATABASE_URL") or config.get_main_option("sqlalchemy.url")


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    context.configure(
        url=_db_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    section = config.get_section(config.config_ini_section)
    section["sqlalchemy.url"] = _db_url()

    connectable = engine_from_config(
        section, prefix="sqlalchemy.", poolclass=pool.NullPool
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
