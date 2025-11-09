"""Routes powering ChatKit token issuance and tool execution."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.src.db import models
from backend.src.db.session import get_session
from backend.src.modules.auth.deps import get_verified_user

from . import schemas, service, tools

router = APIRouter(prefix="/chatkit", tags=["chatkit"])


def _allowed_tools(placement: str) -> list[str]:
    """Utility wrapper to keep responses consistent."""

    return tools.tools_for_placement(placement)


@router.post("/token", response_model=schemas.ChatTokenResponse)
def issue_token(
    payload: schemas.ChatTokenRequest,
    user: models.User = Depends(get_verified_user),
    db: Session = Depends(get_session),
) -> schemas.ChatTokenResponse:
    """Mint a signed ChatKit client token for the authenticated user."""

    try:
        bundle = service.issue_client_token(
            db,
            user=user,
            placement=payload.placement,
            thread_id=payload.thread_id,
        )
    except service.ChatKitConfigError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        ) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return schemas.ChatTokenResponse(
        token=bundle.token,
        expires_at=bundle.expires_at,
        thread_id=bundle.thread.id,
        placement=payload.placement,
        allowed_tools=_allowed_tools(payload.placement),
    )


@router.post("/tools/{tool_name}", response_model=schemas.ToolInvokeResponse)
def invoke_tool(
    tool_name: str,
    payload: schemas.ToolInvokeRequest,
    user: models.User = Depends(get_verified_user),
    db: Session = Depends(get_session),
) -> schemas.ToolInvokeResponse:
    """Invoke a placement-scoped backend tool and record the resulting event."""

    try:
        thread, result, event = service.invoke_tool(
            db,
            user=user,
            placement=payload.placement,
            tool_name=tool_name,
            payload=payload.payload,
            thread_id=payload.thread_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return schemas.ToolInvokeResponse(
        thread_id=thread.id,
        tool_name=tool_name,
        result=result,
        event_id=event.id,
        allowed_tools=_allowed_tools(payload.placement),
    )
