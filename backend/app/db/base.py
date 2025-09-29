# backend/app/db/base.py
try:
    # SQLAlchemy 2.x style
    from sqlalchemy.orm import DeclarativeBase

    class Base(DeclarativeBase):
        pass

except ImportError:
    # Fallback for older SQLAlchemy
    from sqlalchemy.orm import declarative_base

    Base = declarative_base()
