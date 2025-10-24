# backend/src/db/session.py
from __future__ import annotations

import os
from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

try:
    # Your project settings should expose DATABASE_URL
    from backend.src.settings import settings  # type: ignore

    DATABASE_URL = getattr(settings, "DATABASE_URL", None) or os.getenv(
        "DATABASE_URL", ""
    )
except Exception:
    DATABASE_URL = os.getenv("DATABASE_URL", "")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set")


# --- URL normalization (Heroku often provides 'postgres://') ---
def _normalize_db_url(url: str) -> str:
    # Prefer psycopg (SQLAlchemy 2.x)
    if url.startswith("postgres://"):
        url = "postgresql+psycopg" + url[len("postgres") :]
    elif url.startswith("postgresql://"):
        # Allow driverless; you can force psycopg if you prefer
        url = "postgresql+psycopg" + url[len("postgresql") :]
    return url


DB_URL = _normalize_db_url(DATABASE_URL)

# --- SSL for managed Postgres (Heroku/RDS) ---
# Opt-in via env var or auto-detect by URL host
SSL_REQUIRED = os.getenv("DATABASE_SSL", "").lower() in {"1", "true", "yes", "require"}
if ("amazonaws.com" in DB_URL or "heroku" in DB_URL) and os.getenv(
    "DATABASE_SSL"
) is None:
    SSL_REQUIRED = True


connect_args = {}
sqlite_connect_args = None
if DB_URL.startswith("sqlite"):
    sqlite_connect_args = {"check_same_thread": False}
elif SSL_REQUIRED:
    # psycopg accepts sslmode in query, but connect_args keeps it explicit
    connect_args["sslmode"] = "require"


# --- Engine configuration ---
# Tune pools conservatively for Heroku’s single dyno web process
def _create_engine(url: str) -> Engine:
    if url.startswith("sqlite"):
        return create_engine(
            url,
            connect_args=sqlite_connect_args or {"check_same_thread": False},
            future=True,
        )

    return create_engine(
        url,
        pool_pre_ping=True,
        pool_size=int(os.getenv("DB_POOL_SIZE", "5")),
        max_overflow=int(os.getenv("DB_MAX_OVERFLOW", "5")),
        pool_recycle=int(os.getenv("DB_POOL_RECYCLE", "1800")),  # 30 minutes
        connect_args=connect_args,
        future=True,
    )


engine: Engine = _create_engine(DB_URL)

# Session factory (synchronous)
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    class_=Session,
)

__all__ = ["engine", "SessionLocal", "get_db", "get_session"]


def get_db() -> Iterator[Session]:
    """
    FastAPI dependency that yields a DB session and ensures it closes.
    Import path used by routers: backend.src.db.session.get_db
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_session() -> Iterator[Session]:
    """Backward-compatible alias exposing the legacy dependency name."""

    yield from get_db()
