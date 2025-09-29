"""Database ORM models."""

from __future__ import annotations

import uuid

from sqlalchemy import Column, DateTime, String, func

from .base import Base


class User(Base):
    """Minimal user model used for authentication flows."""

    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(320), unique=True, nullable=False, index=True)
    full_name = Column(String(100), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
