"""Usage module router — expose usage summary for dashboard widgets."""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.src.db.session import get_session
from backend.src.modules.auth.deps import get_verified_user

from . import service
from backend.src.modules.subscriptions import service as sub_service

log = logging.getLogger(__name__)

router = APIRouter(prefix="/usage", tags=["usage"])


def _period_start_for_subscription(sub) -> datetime:
    """Derive the billing period start from the subscription record."""
    if sub and sub.current_period_start:
        return sub.current_period_start
    # Fallback: first day of current month
    now = datetime.now(timezone.utc)
    return now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)


@router.get("/summary")
async def usage_summary(
    current_user=Depends(get_verified_user),
    db: Session = Depends(get_session),
):
    """Return aggregated usage for the current billing period."""
    user_id: str = current_user.id  # type: ignore[union-attr]
    sub = sub_service.get_subscription(db, user_id)
    plan_id = sub.plan_id if sub else "free"
    period_start = _period_start_for_subscription(sub)

    summary = service.get_usage_summary(
        db,
        user_id=user_id,
        period_start=period_start,
        plan_id=plan_id,
    )
    # Add period_end for the frontend reset timer
    if sub and sub.current_period_end:
        summary["period_end"] = sub.current_period_end.isoformat()
    else:
        # Default: 30d from period_start
        from datetime import timedelta

        summary["period_end"] = (period_start + timedelta(days=30)).isoformat()

    return summary
