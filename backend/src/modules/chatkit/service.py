"""ChatKit service helpers for issuing client tokens and managing threads."""

from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.src.db import models
from . import tools


class ChatKitConfigError(RuntimeError):
    """Raised when required ChatKit configuration is missing."""


@dataclass(frozen=True)
class ChatKitConfig:
    """Runtime configuration required to mint ChatKit tokens."""

    app_id: str
    signing_key: str
    issuer: str
    audience: Optional[str]
    ttl_seconds: int


@dataclass
class TokenBundle:
    """Container for issued ChatKit tokens."""

    token: str
    expires_at: datetime
    thread: models.ChatThread


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _load_config() -> ChatKitConfig:
    app_id = os.getenv("CHATKIT_APP_ID")
    signing_key = os.getenv("CHATKIT_SIGNING_KEY")
    if not app_id or not signing_key:
        raise ChatKitConfigError("CHATKIT_APP_ID and CHATKIT_SIGNING_KEY must be configured.")
    issuer = os.getenv("CHATKIT_ISSUER", "autorisen-chatkit")
    audience = os.getenv("CHATKIT_AUDIENCE") or None
    ttl_seconds = int(os.getenv("CHATKIT_TOKEN_TTL_SECONDS", "300"))
    return ChatKitConfig(
        app_id=app_id,
        signing_key=signing_key,
        issuer=issuer,
        audience=audience,
        ttl_seconds=ttl_seconds,
    )


def _persist_thread(db: Session, thread: models.ChatThread) -> models.ChatThread:
    db.add(thread)
    db.commit()
    db.refresh(thread)
    return thread


def _record_tool_event(
    db: Session,
    *,
    thread: models.ChatThread,
    tool_name: str,
    payload: tools.ToolPayload,
    result: tools.ToolResult,
) -> models.ChatEvent:
    event = models.ChatEvent(
        thread_id=thread.id,
        role="tool",
        tool_name=tool_name,
        content=f"tool:{tool_name}",
        event_metadata={
            "payload": payload,
            "result": result,
        },
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def ensure_thread(
    db: Session,
    *,
    user: models.User,
    placement: str,
    thread_id: Optional[str] = None,
) -> models.ChatThread:
    """Fetch an existing thread or create a new one for the placement."""
    if thread_id:
        stmt = select(models.ChatThread).where(
            models.ChatThread.id == thread_id, models.ChatThread.user_id == user.id
        )
        thread = db.scalar(stmt)
        if thread is None:
            raise ValueError("thread not found")
        return thread

    thread = models.ChatThread(user_id=user.id, placement=placement)
    return _persist_thread(db, thread)


def _encode_token(config: ChatKitConfig, *, user: models.User, thread: models.ChatThread, placement: str) -> TokenBundle:
    issued_at = _now()
    expires_at = issued_at + timedelta(seconds=config.ttl_seconds)

    payload = {
        "iss": config.issuer,
        "sub": user.id,
        "aud": config.audience or config.app_id,
        "app_id": config.app_id,
        "placement": placement,
        "thread_id": thread.id,
        "email": user.email,
        "iat": int(issued_at.timestamp()),
        "exp": int(expires_at.timestamp()),
    }

    token = jwt.encode(payload, config.signing_key, algorithm="HS256")
    return TokenBundle(token=token, expires_at=expires_at, thread=thread)


def issue_client_token(
    db: Session,
    *,
    user: models.User,
    placement: str,
    thread_id: Optional[str] = None,
) -> TokenBundle:
    """Produce a signed ChatKit client token for the user."""
    config = _load_config()
    thread = ensure_thread(db, user=user, placement=placement, thread_id=thread_id)

    bundle = _encode_token(config, user=user, thread=thread, placement=placement)

    # Update thread metadata to reflect most recent use.
    thread.updated_at = _now()
    db.add(thread)
    db.commit()
    db.refresh(thread)

    return bundle


def invoke_tool(
    db: Session,
    *,
    user: models.User,
    placement: str,
    tool_name: str,
    payload: tools.ToolPayload,
    thread_id: str | None = None,
) -> tuple[models.ChatThread, tools.ToolResult, models.ChatEvent]:
    thread = ensure_thread(db, user=user, placement=placement, thread_id=thread_id)
    spec = tools.get_tool(placement, tool_name)
    result = tools.invoke_tool(
        db,
        spec=spec,
        user=user,
        thread=thread,
        payload=payload,
    )

    event = _record_tool_event(db, thread=thread, tool_name=spec.name, payload=payload, result=result)

    return thread, result, event
