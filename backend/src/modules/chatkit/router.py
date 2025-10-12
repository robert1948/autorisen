"""API routes exposing ChatKit utilities to the frontend."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.src.db import models
from backend.src.db.session import get_session
from backend.src.modules.auth.deps import get_current_user

from . import schemas, service, tools
from .service import ChatKitConfigError

router = APIRouter(prefix="/chatkit", tags=["chatkit"])


@router.post("/token", response_model=schemas.ChatTokenResponse)
def issue_token(
    payload: schemas.ChatTokenRequest,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_session),
) -> schemas.ChatTokenResponse:
    """Return a ChatKit client token for the requested placement."""
    try:
        token_bundle = service.issue_client_token(
            db,
            user=user,
            placement=payload.placement,
            thread_id=payload.thread_id,
        )
    except ChatKitConfigError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="ChatKit configuration is incomplete.",
        ) from exc

    return schemas.ChatTokenResponse(
        token=token_bundle.token,
        expires_at=token_bundle.expires_at,
        thread_id=token_bundle.thread.id,
        placement=token_bundle.thread.placement,
        allowed_tools=tools.tools_for_placement(token_bundle.thread.placement),
    )


@router.post("/tools/{tool_name}", response_model=schemas.ToolInvokeResponse)
def invoke_tool(
    tool_name: str,
    payload: schemas.ToolInvokeRequest,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_session),
) -> schemas.ToolInvokeResponse:
    try:
        thread, result, event = service.invoke_tool(
            db,
            user=user,
            placement=payload.placement,
            tool_name=tool_name,
            payload=payload.payload,
            thread_id=payload.thread_id,
        )
    except ChatKitConfigError as exc:  # pragma: no cover - should surface during token issuance
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="ChatKit configuration is incomplete.",
        ) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return schemas.ToolInvokeResponse(
        thread_id=thread.id,
        tool_name=tool_name,
        result=result,
        event_id=event.id,
        allowed_tools=tools.tools_for_placement(payload.placement),
    )
