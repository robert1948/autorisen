"""Support FAQs and ticket endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.src.db.session import get_session
from backend.src.modules.auth.deps import get_verified_user
from backend.src.db import models

from . import schemas, service
from .sla import estimated_response_time

router = APIRouter(prefix="/support", tags=["support"])


def _ticket_out(ticket: models.SupportTicket, response_label: str) -> schemas.SupportTicketOut:
    """Build a SupportTicketOut from a model instance."""
    return schemas.SupportTicketOut(
        id=ticket.id,
        subject=ticket.title,
        body=ticket.description,
        status=ticket.status,
        priority=ticket.priority,
        estimated_response_time=response_label,
        created_at=ticket.created_at,
    )


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
        priority=payload.priority,
    )
    return _ticket_out(ticket, estimated_response_time(db, current_user.id))


@router.get("/tickets", response_model=schemas.SupportTicketList)
def list_tickets(
    current_user: models.User = Depends(get_verified_user),
    db: Session = Depends(get_session),
) -> schemas.SupportTicketList:
    tickets = service.list_tickets(db, current_user.id)
    label = estimated_response_time(db, current_user.id)
    return schemas.SupportTicketList(
        tickets=[_ticket_out(t, label) for t in tickets],
    )


@router.get("/tickets/{ticket_id}", response_model=schemas.SupportTicketOut)
def get_ticket(
    ticket_id: str,
    current_user: models.User = Depends(get_verified_user),
    db: Session = Depends(get_session),
) -> schemas.SupportTicketOut:
    """Get a single support ticket by ID."""
    tickets = service.list_tickets(db, current_user.id)
    ticket = next((t for t in tickets if t.id == ticket_id), None)
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
    return _ticket_out(ticket, estimated_response_time(db, current_user.id))
