import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from urllib.parse import urlparse

# Resolve DATABASE_URL with strong preference for PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    # Compose from POSTGRES_* env if available, else use local compose defaults
    pg_user = os.getenv("POSTGRES_USER", "autorisen")
    pg_pass = os.getenv("POSTGRES_PASSWORD", "postgres")
    pg_db = os.getenv("POSTGRES_DB", "autorisen")
    # Default to local docker-compose port mapping
    DATABASE_URL = f"postgresql://{pg_user}:{pg_pass}@127.0.0.1:5433/{pg_db}"

# For PostgreSQL URLs from Heroku, fix the protocol if needed
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Create the SQLAlchemy engine with production settings
if DATABASE_URL.startswith("postgresql://"):
    # Decide SSL mode: default to 'require' for remote DBs, but disable for
    # local/dev hosts (db, localhost, 127.0.0.1, host.docker.internal) or when explicitly
    # overridden by DISABLE_DB_SSL=1 in the environment.
    disable_ssl_flag = os.getenv("DISABLE_DB_SSL", "") == "1"
    host = (urlparse(DATABASE_URL).hostname or "").lower()
    local_hosts = {"localhost", "127.0.0.1", "db", "host.docker.internal"}
    sslmode = "disable" if (disable_ssl_flag or host in local_hosts) else "require"

    # Production PostgreSQL settings with sensible timeouts for this app
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=60,
        pool_size=2,
        max_overflow=3,
        pool_timeout=3,
        connect_args={
            "connect_timeout": 3,
            "options": "-c statement_timeout=3000",
            "sslmode": sslmode,
        },
        echo=False,
    )
else:
    # Development SQLite settings (fallback only)
    engine = create_engine(DATABASE_URL)

# Create a configured "Session" class
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# Base class for declarative models
Base = declarative_base()


def get_db():
    """
    Dependency that provides a database session.
    Closes the session after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
