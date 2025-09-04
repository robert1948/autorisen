# backend/app/api/agents.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime
import json

from app.database import get_db
from app import models
from app.core.settings import settings
from app.services.ai_provider import AIProvider, get_ai_provider

router = APIRouter(prefix=f"{settings.API_V1_PREFIX}/agents", tags=["agents"])


class FAQRequest(BaseModel):
    question: str


class FAQResponse(BaseModel):
    answer: str


class ScheduleRequest(BaseModel):
    command: str


class ScheduleResponse(BaseModel):
    status: str
    when: str | None = None
    meta: dict | None = None


def provider_dep() -> AIProvider:
    return get_ai_provider()


@router.post("/faq", response_model=FAQResponse)
async def faq(req: FAQRequest, provider: AIProvider = Depends(provider_dep)):
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="question is required")
    answer = await provider.answer_faq(req.question)
    return FAQResponse(answer=answer)


@router.post("/scheduler", response_model=ScheduleResponse)
async def scheduler(
    req: ScheduleRequest,
    provider: AIProvider = Depends(provider_dep),
    db: Session = Depends(get_db),
) -> ScheduleResponse:
    """Interpret scheduling command via AIProvider and persist the event."""
    if not req.command.strip():
        raise HTTPException(status_code=400, detail="command is required")
    # Call provider to schedule
    result = await provider.schedule(req.command)
    # Persist scheduled event
    event = models.ScheduledEvent(
        user_id=None,
        conversation_id=None,
        command=req.command,
        scheduled_time=result.get("when", ""),
        metadata=json.dumps(result),
        created_at=datetime.utcnow(),
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return ScheduleResponse(
        status=result.get("status", "ok"),
        when=result.get("when"),
        meta=result,
    )


# === Alias router for non-versioned routes (/api/agents/*) ===
alias_router = APIRouter(
    prefix=f"{settings.API_V1_PREFIX.replace('/v1', '')}/agents", tags=["agents"]
)
alias_router.post("/faq", response_model=FAQResponse)(faq)
alias_router.post("/scheduler", response_model=ScheduleResponse)(scheduler)

# Duplicate unreachable code removed
