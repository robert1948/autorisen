"""Shared LLM usage-recording helper for all agent services.

Every module that calls an LLM (Anthropic / OpenAI) should import
``try_record_usage`` and call it immediately after a successful API response.
This ensures the ``UsageLog`` table accurately reflects every token consumed
by the platform, regardless of which agent or service triggered the call.
"""

from __future__ import annotations

import logging
from typing import Optional

from sqlalchemy.orm import Session

log = logging.getLogger(__name__)


def try_record_usage(
    db: Session | None,
    *,
    user_id: str | None,
    event_type: str,
    model: Optional[str] = None,
    tokens_in: int = 0,
    tokens_out: int = 0,
    thread_id: Optional[str] = None,
    detail: Optional[dict] = None,
) -> None:
    """Best-effort write to UsageLog.  Never raises.

    Parameters
    ----------
    db : Session or None
        If *None* the call is silently skipped (agent invoked without DB
        context, e.g. from the executor's fire-and-forget path).
    user_id : str or None
        If *None* the call is silently skipped.
    event_type : str
        Descriptive label, e.g. ``"agent:cape-ai-guide"``, ``"rag"``,
        ``"capsule"``, ``"flow_tool"``.
    model, tokens_in, tokens_out : str, int, int
        Straight from the LLM response object.
    thread_id : str, optional
        Chat thread association if applicable.
    detail : dict, optional
        Extra metadata stored as JSON.
    """
    if db is None or user_id is None:
        return
    try:
        from backend.src.modules.usage.service import record_usage

        record_usage(
            db,
            user_id=user_id,
            event_type=event_type,
            model=model,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            thread_id=thread_id,
            detail=detail,
        )
        db.commit()
    except Exception:
        log.warning("Failed to record LLM usage (%s)", event_type, exc_info=True)
