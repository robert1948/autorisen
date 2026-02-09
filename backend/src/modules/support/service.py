"""Support service utilities."""

from __future__ import annotations

from typing import Optional
import zlib

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from backend.src.db import models


def search_faqs(db: Session, query: Optional[str]) -> list[models.FaqArticle]:
    stmt = select(models.FaqArticle).where(models.FaqArticle.is_published.is_(True))
    if query:
        pattern = f"%{query.lower()}%"
        stmt = stmt.where(
            or_(
                models.FaqArticle.question.ilike(pattern),
                models.FaqArticle.answer.ilike(pattern),
            )
        )
    stmt = stmt.order_by(models.FaqArticle.created_at.desc())
    return db.scalars(stmt).all()


def support_user_id(user_id: str) -> int:
    return int(zlib.crc32(user_id.encode("utf-8")) & 0xFFFFFFFF)


def create_ticket(
    db: Session,
    *,
    user_id: str,
    subject: str,
    body: str,
) -> models.SupportTicket:
    ticket = models.SupportTicket(
        user_id=support_user_id(user_id),
        title=subject,
        description=body,
        status="open",
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


def list_tickets(db: Session, user_id: str) -> list[models.SupportTicket]:
    stmt = (
        select(models.SupportTicket)
        .where(models.SupportTicket.user_id == support_user_id(user_id))
        .order_by(models.SupportTicket.created_at.desc())
    )
    return db.scalars(stmt).all()
