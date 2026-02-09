"""Support FAQs and ticket endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.src.db.session import get_session
from backend.src.modules.auth.deps import get_verified_user
from backend.src.db import models

from . import schemas, service

router = APIRouter(prefix="/support", tags=["support"])


@router.get("/faqs", response_model=list[schemas.FaqArticleOut])
def list_faqs(
    search: str | None = None,
    current_user: models.User = Depends(get_verified_user),
    db: Session = Depends(get_session),
) -> list[schemas.FaqArticleOut]:
    articles = service.search_faqs(db, search)
    return [
        schemas.FaqArticleOut(
            id=article.id,
            question=article.question,
            answer=article.answer,
            tags=list(article.tags or []),
            created_at=article.created_at,
        )
        for article in articles
    ]


@router.post("/tickets", response_model=schemas.SupportTicketOut, status_code=201)
def create_ticket(
    payload: schemas.SupportTicketCreate,
    current_user: models.User = Depends(get_verified_user),
    db: Session = Depends(get_session),
) -> schemas.SupportTicketOut:
    ticket = service.create_ticket(
        db,
        user_id=current_user.id,
        subject=payload.subject.strip(),
        body=payload.body.strip(),
    )
    return schemas.SupportTicketOut(
        id=ticket.id,
        subject=ticket.title,
        body=ticket.description,
        status=ticket.status,
        created_at=ticket.created_at,
    )


@router.get("/tickets", response_model=schemas.SupportTicketList)
def list_tickets(
    current_user: models.User = Depends(get_verified_user),
    db: Session = Depends(get_session),
) -> schemas.SupportTicketList:
    tickets = service.list_tickets(db, current_user.id)
    return schemas.SupportTicketList(
        tickets=[
            schemas.SupportTicketOut(
                id=ticket.id,
                subject=ticket.title,
                body=ticket.description,
                status=ticket.status,
                created_at=ticket.created_at,
            )
            for ticket in tickets
        ]
    )
