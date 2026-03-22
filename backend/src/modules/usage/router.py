"""Usage module router — expose usage summary for dashboard widgets."""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from backend.src.db.models import Subscription
from backend.src.db.session import get_session
from backend.src.modules.auth.deps import get_verified_user, require_roles
from backend.src.modules.payments.constants import get_plan_limits
from fastapi import APIRouter, Depends
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from . import service

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
    try:
        sub = db.query(Subscription).filter(Subscription.user_id == user_id).first()
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
    except SQLAlchemyError:
        log.warning(
            "Usage summary query failed for user=%s; returning zeroed summary",
            user_id,
            exc_info=True,
        )
        period_start = _period_start_for_subscription(None)
        from datetime import timedelta

        period_end = period_start + timedelta(days=30)
        limits = get_plan_limits("free")
        return {
            "api_calls_used": 0,
            "api_calls_limit": limits.max_executions_per_month,
            "total_tokens_in": 0,
            "total_tokens_out": 0,
            "total_cost_usd": 0.0,
            "storage_used_mb": 0,
            "storage_limit_mb": limits.storage_limit_mb,
            "period_start": period_start.isoformat(),
            "period_end": period_end.isoformat(),
            "plan_id": "free",
            "agent_runs": 0,
            "documents_count": 0,
            "rag_queries": 0,
            "evidence_exports": 0,
            "agent_count": 0,
            "max_agents": limits.max_agents,
        }


@router.get("/admin/costs")
async def admin_cost_report(
    _admin=Depends(require_roles("admin")),
    db: Session = Depends(get_session),
):
    """Admin-only: per-user cost aggregation for the current month.

    Returns a list of ``{user_id, total_calls, tokens_in, tokens_out,
    cost_usd}`` sorted by cost descending.
    """
    now = datetime.now(timezone.utc)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    rows = service.get_admin_cost_report(db, period_start=month_start)
    by_agent = service.get_agent_cost_breakdown(db, period_start=month_start)

    # Compute platform total
    total_cost = sum(r["cost_usd"] for r in rows)
    total_calls = sum(r["total_calls"] for r in rows)

    # Budget alert status
    from backend.src.core.config import get_settings
    from backend.src.modules.usage.budget_alerts import (
        budget_tracker,
        check_budget_thresholds,
    )

    cap = get_settings().max_monthly_ai_spend_usd
    active_alerts = check_budget_thresholds(total_cost, cap)

    return {
        "period_start": month_start.isoformat(),
        "total_cost_usd": round(total_cost, 4),
        "total_calls": total_calls,
        "budget_cap_usd": cap,
        "budget_pct_used": round((total_cost / cap) * 100, 1) if cap > 0 else 0,
        "alerts": active_alerts,
        "users": rows,
        "by_agent": by_agent,
    }
