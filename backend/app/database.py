"""
Compatibility wrapper for database symbols.
Older tests import `from app.database import Base, SessionLocal, engine, get_db`.
The project uses `app.db.session` for the SQLAlchemy engine/session; export those here
to maintain compatibility for the test suite.
"""
from typing import Generator
from app.db.session import engine, SessionLocal, Base


def get_db() -> Generator:
    """Yield a database session and ensure it is closed after use."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
