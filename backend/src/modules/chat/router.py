"""Chat module router — thread CRUD, event messaging, and WebSocket."""

from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Any, Optional

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    WebSocket,
    WebSocketDisconnect,
)
from sqlalchemy.orm import Session

from backend.src.db import models
from backend.src.db.session import get_session
from backend.src.modules.auth.deps import get_current_user
from backend.src.modules.payments.enforcement import enforce_execution_limit

from . import schemas, service

log = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])

# ── In-memory WebSocket registry (per-thread) ────────────────────────────────
_ws_connections: dict[str, set[WebSocket]] = {}


def _broadcast_to_thread(thread_id: str, envelope: dict[str, Any]) -> None:
    """Queue a broadcast to all WS clients subscribed to a thread."""
    sockets = _ws_connections.get(thread_id, set())
    dead: list[WebSocket] = []
    for ws in sockets:
        try:
            asyncio.get_event_loop().create_task(ws.send_json(envelope))
        except Exception:  # noqa: BLE001
            dead.append(ws)
    for ws in dead:
        sockets.discard(ws)


def _thread_to_response(thread: models.ChatThread) -> dict[str, Any]:
    return {
        "id": thread.id,
        "placement": thread.placement,
        "title": getattr(thread, "title", None),
        "status": "active",
        "context": thread.context,
        "created_at": thread.created_at.isoformat() if thread.created_at else None,
        "updated_at": thread.updated_at.isoformat() if thread.updated_at else None,
        "last_event_at": None,
        "metadata": None,
    }


def _event_to_response(event: models.ChatEvent) -> dict[str, Any]:
    return {
        "id": event.id,
        "thread_id": event.thread_id,
        "role": event.role,
        "content": event.content,
        "tool_name": event.tool_name,
        "event_metadata": event.event_metadata,
        "created_at": event.created_at.isoformat() if event.created_at else None,
    }


# ── Thread CRUD ───────────────────────────────────────────────────────────────

@router.get("/threads", response_model=schemas.ThreadListResponse)
async def list_threads(
    placement: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """List chat threads for the authenticated user."""
    threads = service.list_threads(db, user=user, placement=placement, limit=limit)
    return schemas.ThreadListResponse(
        results=[
            schemas.ThreadResponse(**_thread_to_response(t))
            for t in threads
        ]
    )


@router.post("/threads", response_model=schemas.ThreadResponse, status_code=201)
async def create_thread(
    payload: schemas.ThreadCreate,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """Create a new chat thread."""
    thread = service.create_thread(
        db,
        user=user,
        placement=payload.placement,
        title=payload.title,
        context=payload.context,
    )
    return schemas.ThreadResponse(**_thread_to_response(thread))


@router.get("/threads/{thread_id}", response_model=schemas.ThreadResponse)
async def get_thread(
    thread_id: str,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """Get a specific chat thread."""
    thread = service.get_thread(db, user=user, thread_id=thread_id)
    if thread is None:
        raise HTTPException(status_code=404, detail="Thread not found")
    return schemas.ThreadResponse(**_thread_to_response(thread))


# ── Event CRUD ────────────────────────────────────────────────────────────────

@router.get(
    "/threads/{thread_id}/events", response_model=schemas.EventListResponse
)
async def list_events(
    thread_id: str,
    limit: int = Query(200, ge=1, le=500),
    before: Optional[str] = Query(None),
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """List events (messages) in a thread."""
    # Verify thread ownership
    thread = service.get_thread(db, user=user, thread_id=thread_id)
    if thread is None:
        raise HTTPException(status_code=404, detail="Thread not found")

    events = service.list_events(db, thread_id=thread_id, limit=limit, before=before)
    return schemas.EventListResponse(
        results=[
            schemas.EventResponse(**_event_to_response(e))
            for e in events
        ]
    )


@router.post(
    "/threads/{thread_id}/events",
    response_model=schemas.EventResponse,
    status_code=201,
)
async def create_event(
    thread_id: str,
    payload: schemas.EventCreate,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_session),
    _quota=Depends(enforce_execution_limit),
):
    """Send a message to a thread and get an AI response."""
    thread = service.get_thread(db, user=user, thread_id=thread_id)
    if thread is None:
        raise HTTPException(status_code=404, detail="Thread not found")

    # 1. Persist the user's message
    user_event = service.create_event(
        db,
        thread_id=thread_id,
        role=payload.role,
        content=payload.content,
        tool_name=payload.tool_name,
        event_metadata=payload.event_metadata,
    )

    # Broadcast user message via WS
    _broadcast_to_thread(thread_id, {
        "type": "chat.event",
        "event": _event_to_response(user_event),
    })

    # 2. Generate AI response (only for user messages)
    if payload.role == "user":
        # Update thread timestamp
        thread.updated_at = datetime.now(timezone.utc)
        db.add(thread)
        db.commit()

        # Run AI generation (synchronous Anthropic call, wrapped for async)
        ai_event = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: service.generate_ai_response(db, thread=thread, user_message=payload.content),
        )

        # Broadcast AI response via WS
        _broadcast_to_thread(thread_id, {
            "type": "chat.event",
            "event": _event_to_response(ai_event),
        })

        # Broadcast thread update
        db.refresh(thread)
        _broadcast_to_thread(thread_id, {
            "type": "thread.updated",
            "thread": _thread_to_response(thread),
        })

        # Return the AI response (the frontend already has the user message optimistically)
        return schemas.EventResponse(**_event_to_response(ai_event))

    # For non-user roles (system), just return the event
    return schemas.EventResponse(**_event_to_response(user_event))


# ── WebSocket endpoint ────────────────────────────────────────────────────────

@router.websocket("/ws")
async def chat_websocket(
    websocket: WebSocket,
    thread_id: str = Query(...),
    token: Optional[str] = Query(None),  # noqa: ARG001 — token verified at proxy/middleware layer
):
    """
    WebSocket endpoint for real-time chat events.
    Clients connect with ?thread_id=<id>&token=<jwt>.
    Receives ping/pong and chat messages; broadcasts events to all
    subscribers on the same thread.
    """
    await websocket.accept()

    # Register connection
    if thread_id not in _ws_connections:
        _ws_connections[thread_id] = set()
    _ws_connections[thread_id].add(websocket)

    log.info("WS connected: thread=%s", thread_id)

    try:
        while True:
            raw = await websocket.receive_text()
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                await websocket.send_json({"type": "error", "message": "Invalid JSON"})
                continue

            msg_type = data.get("type", "")

            if msg_type == "ping":
                await websocket.send_json({
                    "type": "pong",
                    "timestamp": data.get("timestamp", str(int(
                        datetime.now(timezone.utc).timestamp() * 1000
                    ))),
                })
            elif msg_type == "chat.message":
                # Client sent a message via WS — acknowledge receipt
                await websocket.send_json({
                    "type": "chat.ack",
                    "client_id": data.get("client_id", ""),
                })
            else:
                await websocket.send_json({
                    "type": "error",
                    "message": f"Unknown message type: {msg_type}",
                })

    except WebSocketDisconnect:
        log.info("WS disconnected: thread=%s", thread_id)
    except Exception as exc:  # noqa: BLE001
        log.warning("WS error thread=%s: %s", thread_id, exc)
    finally:
        _ws_connections.get(thread_id, set()).discard(websocket)
        if thread_id in _ws_connections and not _ws_connections[thread_id]:
            del _ws_connections[thread_id]
