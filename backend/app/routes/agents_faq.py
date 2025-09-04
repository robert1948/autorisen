"""Simple FAQ Agent endpoints for MVP

Provides `/api/agents/faq` POST endpoint which records a conversation (if not present)
and uses `cape_ai_service` to generate a demo FAQ-style response. This keeps the
implementation lightweight for MVP and matches the Checklist_MVP deliverable.
"""
import logging
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.cape_ai_service import get_cape_ai_service
from app import models

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/agents", tags=["Agents"])


class FAQRequest(BaseModel):
    user_id: int | None = Field(default=None, description="Optional user id")
    conversation_id: str | None = Field(default=None, description="Existing conversation id")
    question: str = Field(..., description="User question for the FAQ agent")


class FAQResponse(BaseModel):
    conversation_id: str
    answer: str
    timestamp: str


@router.post("/faq", response_model=FAQResponse)
async def faq_agent(request: FAQRequest, db: Session = Depends(get_db)) -> FAQResponse:
    """Generate a short FAQ-style answer and persist conversation/message.

    Behavior:
    - If `conversation_id` is not provided, create a lightweight Conversation row.
    - Persist the user question as a ConversationMessage (role=user).
    - Use `CapeAIService.generate_response` to get a demo answer.
    - Persist the assistant response as a ConversationMessage (role=assistant).
    """
    try:
        cape = get_cape_ai_service()

        # Ensure conversation exists
        conv_id = request.conversation_id
        if not conv_id:
            conv = models.Conversation()
            conv.user_id = request.user_id if request.user_id else None
            conv.title = "FAQ Session"
            conv.status = "active"
            conv.created_at = datetime.utcnow()
            db.add(conv)
            db.commit()
            db.refresh(conv)
            conv_id = conv.id

        # Store user message
        user_msg = models.ConversationMessage()
        user_msg.conversation_id = conv_id
        user_msg.role = "user"
        user_msg.content = request.question
        user_msg.created_at = datetime.utcnow()
        db.add(user_msg)
        db.commit()
        db.refresh(user_msg)

        # Generate demo AI response via cape_ai_service
        ai_result = await cape.generate_response(request.question, context={"path": "/agents/faq"})
        answer_text = ai_result.get("response") if isinstance(ai_result, dict) else str(ai_result)

        # Persist assistant message
        assistant_msg = models.ConversationMessage()
        assistant_msg.conversation_id = conv_id
        assistant_msg.role = "assistant"
        assistant_msg.content = answer_text
        assistant_msg.created_at = datetime.utcnow()
        db.add(assistant_msg)

        # Update conversation counts
        conv = db.query(models.Conversation).filter(models.Conversation.id == conv_id).first()
        if conv:
            conv.total_messages = (conv.total_messages or 0) + 2
            conv.updated_at = datetime.utcnow()

        db.commit()

        return FAQResponse(conversation_id=conv_id, answer=answer_text, timestamp=datetime.utcnow().isoformat())

    except Exception as e:
        logger.error(f"FAQ agent error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
