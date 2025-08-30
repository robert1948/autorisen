import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Get DATABASE_URL from environment with fallback to SQLite for development
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./localstorm.db')

# For PostgreSQL URLs from Heroku, fix the protocol if needed
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Create the SQLAlchemy engine with production settings
if DATABASE_URL.startswith('postgresql://'):
    # Decide SSL mode: default to 'require' for remote DBs, but disable for
    # local/dev hosts (db, localhost, host.docker.internal) or when explicitly
    # overridden by DISABLE_DB_SSL=1 in the environment.
    disable_ssl_flag = os.getenv('DISABLE_DB_SSL', '') == '1'
    lower_url = DATABASE_URL.lower()
    local_host_hint = any(x in lower_url for x in ('localhost', 'db:', 'host.docker.internal'))
    sslmode = 'disable' if (disable_ssl_flag or local_host_hint) else 'require'

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
    # Development SQLite settings
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
