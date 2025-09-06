import os
import sys
import importlib
import pkgutil
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# --- Make 'app' importable (package lives at backend/app) ---
THIS_DIR = os.path.dirname(os.path.abspath(__file__))  # .../backend/migrations
BACKEND_DIR = os.path.abspath(os.path.join(THIS_DIR, ".."))  # .../backend
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

config = context.config

# Logging config from alembic.ini (if present)
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# --- Import Base and models ---
# Base is defined in backend/app/database.py
from app.database import Base  # <-- your declarative_base()

# Ensure all model modules are imported so their tables are attached to Base.metadata.
# This auto-imports every .py module in app/models/
try:
    import app.models as models_pkg

    for _, modname, ispkg in pkgutil.iter_modules(models_pkg.__path__):
        if not ispkg:
            importlib.import_module(f"{models_pkg.__name__}.{modname}")
except Exception:
    # If you don't have a package-level app/models, ignore; or keep explicit imports here:
    # from app.models import agent, scheduler
    pass

target_metadata = Base.metadata


def get_url() -> str:
    # Prefer env var (Heroku/Compose/local), else fallback to alembic.ini value
    url = os.getenv("DATABASE_URL")
    if url:
        return url
    return config.get_main_option("sqlalchemy.url")


def run_migrations_offline() -> None:
    context.configure(
        url=get_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_url()
    connectable = engine_from_config(
        configuration,
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
