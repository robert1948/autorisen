# backend/app/models/audit_log.py
from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db.base import Base
from .common import TimestampMixin


class AuditLog(TimestampMixin, Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    event: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    actor: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
    level: Mapped[str] = mapped_column(
        String(20), nullable=False, default="info"
    )  # info|warn|error
    meta: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
