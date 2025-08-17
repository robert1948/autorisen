import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Get DATABASE_URL from environment with fallback to SQLite for development
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./localstorm.db')

# For PostgreSQL URLs from Heroku, fix the protocol if needed
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Create the SQLAlchemy engine with production settings
if DATABASE_URL.startswith('postgresql://'):
    # Production PostgreSQL settings with very aggressive timeouts
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,  # Verify connections before use
        pool_recycle=60,     # Recycle connections every minute
        pool_size=2,         # Smaller connection pool
        max_overflow=3,      # Fewer overflow connections
        pool_timeout=3,      # Shorter timeout for pool
        connect_args={
            "connect_timeout": 3,  # Very short connection timeout
            "options": "-c statement_timeout=3000",  # 3 second statement timeout
            "sslmode": "require"  # Force SSL connection
        },
        echo=False  # Disable SQL logging for performance
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
