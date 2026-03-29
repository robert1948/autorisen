"""Chat service — thread CRUD and AI message generation via Anthropic."""

from __future__ import annotations

import logging
import os
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from backend.src.core.config import get_settings
from backend.src.db import models
from backend.src.modules.ai_router.bedrock import (
    invoke_bedrock_text,
    is_bedrock_enabled,
)
from backend.src.modules.ai_router.strategy import resolve_available_provider_order
from backend.src.modules.usage.input_guard import validate_llm_input
from backend.src.modules.usage.model_router import select_model
from backend.src.modules.usage.token_counter import count_tokens as _count_tokens
from sqlalchemy import select
from sqlalchemy.orm import Session

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

# Rough token estimate: ~4 chars per token for English text.
_CHARS_PER_TOKEN = 4
# Max tokens to allocate for conversation context (leaves room for system
# prompt + response within the model's context window).
_MAX_CONTEXT_TOKENS = 6000
# Maximum characters allowed in a single user message before truncation.
MAX_INPUT_CHARS = 8000


def _estimate_tokens(text: str) -> int:
    """Token count — uses tiktoken when available, else 4-chars heuristic."""
    return _count_tokens(text) or max(1, len(text) // _CHARS_PER_TOKEN)


def _build_messages_for_ai(
    db: Session,
    *,
    thread: models.ChatThread,
    limit: int = 50,
) -> list[dict[str, str]]:
    """Retrieve recent events and map them to Anthropic message format.

    Applies a sliding window that keeps the most recent messages up to
    ``_MAX_CONTEXT_TOKENS`` estimated tokens.  Messages that fall outside
    the window are compressed into a short summary prepended as context,
    keeping total token usage bounded while preserving key decisions and
    facts from earlier in the conversation.
    """
    events = list_events(db, thread_id=thread.id, limit=limit)
    raw_messages: list[dict[str, str]] = []
    for event in events:
        role = event.role
        # Anthropic only accepts "user" or "assistant"
        if role in ("system", "tool"):
            role = "user"
        elif role not in ("user", "assistant"):
            role = "user"
        # Merge consecutive same-role messages
        if raw_messages and raw_messages[-1]["role"] == role:
            raw_messages[-1]["content"] += "\n\n" + event.content
        else:
            raw_messages.append({"role": role, "content": event.content})

    # ── Token-budgeted sliding window ─────────────────────────────────
    # Reserve ~200 tokens for the summary prefix.
    _SUMMARY_BUDGET = 200
    budget = _MAX_CONTEXT_TOKENS - _SUMMARY_BUDGET
    selected: list[dict[str, str]] = []
    split_idx = len(raw_messages)  # index where we stopped including

    for i, msg in enumerate(reversed(raw_messages)):
        cost = _estimate_tokens(msg["content"])
        if cost > budget and selected:
            split_idx = len(raw_messages) - i
            break
        budget -= cost
        selected.append(msg)

    selected.reverse()  # restore chronological order

    # ── Summarise dropped messages ────────────────────────────────────
    dropped = raw_messages[:split_idx] if split_idx < len(raw_messages) else []
    if dropped and len(dropped) >= 3:
        summary = _summarise_dropped_messages(dropped)
        if summary:
            # Prepend as a "user" context message so the model has the gist.
            selected.insert(0, {"role": "user", "content": summary})

    return selected


def _summarise_dropped_messages(messages: list[dict[str, str]]) -> str:
    """Create a lightweight extractive summary of older conversation turns.

    This is NOT an LLM call — it's a fast heuristic extraction that pulls
    the first sentence of each dropped message.  Keeps cost at zero while
    still preserving key context.  A future upgrade can use a small model
    for abstractive summarisation.
    """
    import re

    snippets: list[str] = []
    for msg in messages[-6:]:  # last 6 dropped messages are most relevant
        text = msg["content"].strip()
        # Extract first sentence (up to 120 chars)
        match = re.match(r"^(.{10,120}?[.!?])\s", text)
        if match:
            snippets.append(f"- {msg['role']}: {match.group(1)}")
        else:
            snippets.append(f"- {msg['role']}: {text[:100]}…")

    if not snippets:
        return ""

    return (
        "[Earlier conversation summary]\n"
        + "\n".join(snippets)
        + "\n[End summary — recent messages follow]"
    )


def generate_ai_response(
    db: Session,
    *,
    thread: models.ChatThread,
    user_message: str,  # noqa: ARG001 — reserved for future prompt augmentation
) -> models.ChatEvent:
    """Call configured LLM providers to generate a response and persist it."""
    settings = get_settings()
    anthropic_key = settings.anthropic_api_key or os.getenv("ANTHROPIC_API_KEY", "")
    openai_key = settings.openai_api_key or os.getenv("OPENAI_API_KEY", "")
    env_model = os.getenv("ANTHROPIC_MODEL")  # explicit override

    # ── Intelligent model routing ─────────────────────────────────
    # If no explicit model override, route based on prompt complexity.
    anthropic_model = select_model(user_message, force_model=env_model)
    openai_model = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini")

    system_prompt = PLACEMENT_SYSTEM_PROMPTS.get(
        thread.placement, DEFAULT_SYSTEM_PROMPT
    )

    # Build conversation history
    messages = _build_messages_for_ai(db, thread=thread)

    # ── Input length guard ────────────────────────────────────────
    # Truncate the most recent user message if it exceeds the cap
    if messages:
        last = messages[-1]
        if last["role"] == "user":
            last["content"] = validate_llm_input(last["content"], label="chat message")

    provider_order = resolve_available_provider_order(
        strategy=settings.ai_provider_strategy,
        fallback_order=settings.ai_provider_fallback_order,
        has_bedrock=settings.ai_bedrock_enabled or is_bedrock_enabled(),
        has_anthropic=bool(anthropic_key),
        has_openai=bool(openai_key),
    )

    if not provider_order:
        log.warning("No AI provider key configured — returning placeholder response")
        content = (
            "I'm CapeAI, but my AI backend is not configured yet. "
            "Please ask your administrator to configure ANTHROPIC_API_KEY and/or OPENAI_API_KEY."
        )
        return create_event(
            db,
            thread_id=thread.id,
            role="assistant",
            content=content,
            event_metadata={"model": "placeholder", "error": "no_api_key"},
        )

    last_error: Exception | None = None

    for provider in provider_order:
        if provider == "bedrock":
            try:
                conversation = "\n\n".join(
                    f"{msg['role']}: {msg['content']}" for msg in messages
                )
                user_prompt = (
                    "Conversation context follows. Respond as the assistant to the "
                    "latest user intent.\n\n"
                    f"{conversation}"
                )
                bedrock = invoke_bedrock_text(
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    model_id=os.getenv("CHAT_BEDROCK_MODEL_ID")
                    or settings.ai_bedrock_model_id,
                    region=settings.ai_bedrock_region,
                )
                content = (
                    bedrock.text
                    if bedrock.text
                    else "I wasn't able to generate a response. Please try again."
                )

                event = create_event(
                    db,
                    thread_id=thread.id,
                    role="assistant",
                    content=content,
                    event_metadata={
                        "provider": "bedrock",
                        "model": bedrock.model_id,
                        "region": bedrock.region,
                        "usage": {
                            "input_tokens": bedrock.input_tokens,
                            "output_tokens": bedrock.output_tokens,
                            "estimated_usd": bedrock.estimated_usd,
                            "latency_ms": bedrock.latency_ms,
                        },
                    },
                )

                try:
                    from backend.src.modules.usage import service as usage_svc

                    usage_svc.record_usage(
                        db,
                        user_id=thread.user_id,
                        event_type="chat",
                        model=bedrock.model_id,
                        tokens_in=bedrock.input_tokens,
                        tokens_out=bedrock.output_tokens,
                        thread_id=thread.id,
                    )
                    db.commit()
                except Exception:  # noqa: BLE001
                    log.warning("Failed to record usage log", exc_info=True)

                return event
            except Exception as exc:  # noqa: BLE001
                last_error = exc
                log.warning("Bedrock API call failed, trying next provider: %s", exc)
                continue

        if provider == "anthropic" and anthropic_key:
            try:
                import anthropic

                client = anthropic.Anthropic(api_key=anthropic_key)
                response = client.messages.create(
                    model=anthropic_model,
                    max_tokens=2048,
                    system=[
                        {
                            "type": "text",
                            "text": system_prompt,
                            "cache_control": {"type": "ephemeral"},
                        }
                    ],
                    messages=messages,
                )
                content = ""
                for block in response.content:
                    if hasattr(block, "text"):
                        content += block.text
                if not content:
                    content = "I wasn't able to generate a response. Please try again."

                event = create_event(
                    db,
                    thread_id=thread.id,
                    role="assistant",
                    content=content,
                    event_metadata={
                        "provider": "anthropic",
                        "model": response.model,
                        "usage": {
                            "input_tokens": response.usage.input_tokens,
                            "output_tokens": response.usage.output_tokens,
                        },
                    },
                )

                try:
                    from backend.src.modules.usage import service as usage_svc

                    usage_svc.record_usage(
                        db,
                        user_id=thread.user_id,
                        event_type="chat",
                        model=response.model,
                        tokens_in=response.usage.input_tokens,
                        tokens_out=response.usage.output_tokens,
                        thread_id=thread.id,
                    )
                    db.commit()
                except Exception:  # noqa: BLE001
                    log.warning("Failed to record usage log", exc_info=True)

                return event
            except Exception as exc:  # noqa: BLE001
                last_error = exc
                log.warning("Anthropic API call failed, trying next provider: %s", exc)
                continue

        if provider == "openai" and openai_key:
            try:
                from openai import OpenAI

                client = OpenAI(api_key=openai_key)
                response = client.chat.completions.create(
                    model=openai_model,
                    max_tokens=2048,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        *messages,
                    ],
                )
                content = response.choices[0].message.content or ""
                if not content:
                    content = "I wasn't able to generate a response. Please try again."
                usage = getattr(response, "usage", None)

                event = create_event(
                    db,
                    thread_id=thread.id,
                    role="assistant",
                    content=content,
                    event_metadata={
                        "provider": "openai",
                        "model": response.model,
                        "usage": {
                            "input_tokens": getattr(usage, "prompt_tokens", 0),
                            "output_tokens": getattr(usage, "completion_tokens", 0),
                        },
                    },
                )

                try:
                    from backend.src.modules.usage import service as usage_svc

                    usage_svc.record_usage(
                        db,
                        user_id=thread.user_id,
                        event_type="chat",
                        model=response.model,
                        tokens_in=getattr(usage, "prompt_tokens", 0),
                        tokens_out=getattr(usage, "completion_tokens", 0),
                        thread_id=thread.id,
                    )
                    db.commit()
                except Exception:  # noqa: BLE001
                    log.warning("Failed to record usage log", exc_info=True)

                return event
            except Exception as exc:  # noqa: BLE001
                last_error = exc
                log.warning("OpenAI API call failed, trying next provider: %s", exc)
                continue

    error_content = (
        "I encountered an error generating a response. " "Please try again in a moment."
    )
    return create_event(
        db,
        thread_id=thread.id,
        role="assistant",
        content=error_content,
        event_metadata={
            "error": str(last_error) if last_error else "provider_unavailable"
        },
    )
