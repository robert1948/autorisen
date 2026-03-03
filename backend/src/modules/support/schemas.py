"""Pydantic schemas for support FAQs and tickets."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class FaqArticleOut(BaseModel):
    id: str
    question: str
    answer: str
    tags: list[str] = Field(default_factory=list)
    created_at: datetime


class SupportTicketCreate(BaseModel):
    subject: str = Field(..., min_length=3, max_length=160)
    body: str = Field(..., min_length=3, max_length=5000)
    priority: Optional[str] = Field(
        default=None,
        pattern="^(low|normal|high|urgent)$",
        description="Ticket priority (low, normal, high, urgent). Defaults to normal.",
    )


class SupportTicketOut(BaseModel):
    id: str
    subject: str
    body: str
    status: str
    priority: Optional[str] = None
    estimated_response_time: Optional[str] = None
    created_at: datetime


class SupportTicketList(BaseModel):
    tickets: list[SupportTicketOut]
