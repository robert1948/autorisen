"""Chat service — thread CRUD and AI message generation via Anthropic."""

from __future__ import annotations

import logging
import os
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.src.db import models

log = logging.getLogger(__name__)

# ── Placement → system prompts ────────────────────────────────────────────────

PLACEMENT_SYSTEM_PROMPTS: dict[str, str] = {
    "support": (
        "You are CapeAI Support, a helpful customer service assistant for the CapeControl platform. "
        "Help users with billing questions, account access, troubleshooting, and general platform queries. "
        "Be concise, friendly, and professional. If you cannot resolve an issue, suggest the user "
        "contact the support team directly."
    ),
    "onboarding": (
        "You are CapeAI Onboarding, a friendly assistant that guides new users through setting up "
        "the CapeControl platform. Help them configure their organisation, connect data sources, "
        "invite team members, and understand key features. Generate personalized launch checklists "
        "and track onboarding progress."
    ),
    "developer": (
        "You are the CapeControl Agent Workbench assistant. Help developers inspect tool calls, "
        "replay flows, validate prompts, and debug agent configurations. Provide technical guidance "
        "on the CapeControl API, agent architecture, and integration patterns. Be precise and "
        "include code examples when helpful."
    ),
    "energy": (
        "You are CapeAI Energy Insights, an analytics assistant for the CapeControl energy monitoring "
        "module. Help users understand energy consumption patterns, identify spikes, and get proactive "
        "savings recommendations. Reference trends, comparisons, and actionable insights."
    ),
    "money": (
        "You are CapeAI Money Copilot, a financial assistant for CapeControl. Help users understand "
        "their spending, invoices, and subscription costs. Provide summaries and benchmarking guidance."
    ),
    "admin": (
        "You are CapeAI Ops Copilot, an administrative assistant for CapeControl operators. "
        "Help with user management, system health, audit logs, and operational tasks."
    ),
}

DEFAULT_SYSTEM_PROMPT = (
    "You are CapeAI, a helpful assistant for the CapeControl platform. "
    "Answer questions clearly and concisely."
)


def _now() -> datetime:
    return datetime.now(timezone.utc)


# ── Thread operations ─────────────────────────────────────────────────────────

def list_threads(
    db: Session,
    *,
    user: models.User,
    placement: Optional[str] = None,
    limit: int = 20,
) -> list[models.ChatThread]:
    stmt = (
        select(models.ChatThread)
        .where(models.ChatThread.user_id == user.id)
        .order_by(models.ChatThread.updated_at.desc())
        .limit(limit)
    )
    if placement:
        stmt = stmt.where(models.ChatThread.placement == placement)
    return list(db.scalars(stmt).all())


def get_thread(
    db: Session,
    *,
    user: models.User,
    thread_id: str,
) -> models.ChatThread | None:
    stmt = select(models.ChatThread).where(
        models.ChatThread.id == thread_id,
        models.ChatThread.user_id == user.id,
    )
    return db.scalar(stmt)


def create_thread(
    db: Session,
    *,
    user: models.User,
    placement: str,
    title: Optional[str] = None,
    context: Optional[dict[str, Any]] = None,
) -> models.ChatThread:
    thread = models.ChatThread(
        id=str(uuid.uuid4()),
        user_id=user.id,
        placement=placement,
        title=title,
        context=context or {},
    )
    db.add(thread)
    db.commit()
    db.refresh(thread)
    return thread


# ── Event / message operations ────────────────────────────────────────────────

def list_events(
    db: Session,
    *,
    thread_id: str,
    limit: int = 200,
    before: Optional[str] = None,
) -> list[models.ChatEvent]:
    stmt = (
        select(models.ChatEvent)
        .where(models.ChatEvent.thread_id == thread_id)
        .order_by(models.ChatEvent.created_at.asc())
        .limit(limit)
    )
    # Optionally paginate with a "before" cursor
    if before:
        stmt = stmt.where(models.ChatEvent.created_at < before)
    return list(db.scalars(stmt).all())


def create_event(
    db: Session,
    *,
    thread_id: str,
    role: str,
    content: str,
    tool_name: Optional[str] = None,
    event_metadata: Optional[dict[str, Any]] = None,
) -> models.ChatEvent:
    event = models.ChatEvent(
        id=str(uuid.uuid4()),
        thread_id=thread_id,
        role=role,
        content=content,
        tool_name=tool_name,
        event_metadata=event_metadata,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


# ── AI response generation ────────────────────────────────────────────────────

def _build_messages_for_ai(
    db: Session,
    *,
    thread: models.ChatThread,
    limit: int = 50,
) -> list[dict[str, str]]:
    """Retrieve recent events and map them to Anthropic message format."""
    events = list_events(db, thread_id=thread.id, limit=limit)
    messages: list[dict[str, str]] = []
    for event in events:
        role = event.role
        # Anthropic only accepts "user" or "assistant"
        if role in ("system", "tool"):
            role = "user"
        elif role not in ("user", "assistant"):
            role = "user"
        # Merge consecutive same-role messages
        if messages and messages[-1]["role"] == role:
            messages[-1]["content"] += "\n\n" + event.content
        else:
            messages.append({"role": role, "content": event.content})
    return messages


def generate_ai_response(
    db: Session,
    *,
    thread: models.ChatThread,
    user_message: str,  # noqa: ARG001 — reserved for future prompt augmentation
) -> models.ChatEvent:
    """Call Anthropic API to generate an assistant response and persist it."""
    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    model = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")

    system_prompt = PLACEMENT_SYSTEM_PROMPTS.get(
        thread.placement, DEFAULT_SYSTEM_PROMPT
    )

    # Build conversation history
    messages = _build_messages_for_ai(db, thread=thread)

    if not api_key:
        log.warning("ANTHROPIC_API_KEY not set — returning placeholder response")
        content = (
            "I'm CapeAI, but my AI backend is not configured yet. "
            "Please ask your administrator to set the ANTHROPIC_API_KEY environment variable."
        )
        return create_event(
            db,
            thread_id=thread.id,
            role="assistant",
            content=content,
            event_metadata={"model": "placeholder", "error": "no_api_key"},
        )

    try:
        import anthropic

        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model=model,
            max_tokens=2048,
            system=system_prompt,
            messages=messages,
        )
        content = ""
        for block in response.content:
            if hasattr(block, "text"):
                content += block.text
        if not content:
            content = "I wasn't able to generate a response. Please try again."

        return create_event(
            db,
            thread_id=thread.id,
            role="assistant",
            content=content,
            event_metadata={
                "model": response.model,
                "usage": {
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                },
            },
        )
    except Exception as exc:  # noqa: BLE001
        log.exception("Anthropic API call failed: %s", exc)
        error_content = (
            "I encountered an error generating a response. "
            "Please try again in a moment."
        )
        return create_event(
            db,
            thread_id=thread.id,
            role="assistant",
            content=error_content,
            event_metadata={"error": str(exc)},
        )
