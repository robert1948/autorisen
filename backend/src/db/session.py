# backend/src/db/session.py
"""Database session utilities."""

from __future__ import annotations

import os
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

# 1) Read and normalize DATABASE_URL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./dev.db")
if DATABASE_URL.startswith("postgres://"):
    # Heroku-style URL -> SQLAlchemy expects 'postgresql://'
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# 2) Connect args per driver/env
connect_args: dict = {}

if DATABASE_URL.startswith("sqlite"):
    # Needed for SQLite when used in multi-threaded servers
    connect_args = {"check_same_thread": False}
elif DATABASE_URL.startswith("postgresql://"):
    # If not local, assume managed Postgres (e.g., Heroku) -> require SSL
    if "localhost" not in DATABASE_URL and "127.0.0.1" not in DATABASE_URL:
        connect_args["sslmode"] = "require"

# 3) Engine & session factory
engine = create_engine(DATABASE_URL, future=True, echo=False, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


# 4) FastAPI dependency
def get_session() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
