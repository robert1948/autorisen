"""Plan limit enforcement dependencies.

Provides FastAPI ``Depends`` callables that check subscription quotas
before an endpoint executes.  When a limit is exceeded, a **429** is
returned with a JSON body containing ``detail``, ``code``, and
``upgrade_url`` so the frontend can display a targeted upgrade prompt.

Usage
-----
::

    from backend.src.modules.payments.enforcement import (
        enforce_execution_limit,
        enforce_agent_limit,
    )

    @router.post("/chat/threads/{thread_id}/events")
    async def create_event(
        ...,
        _quota=Depends(enforce_execution_limit),
    ):
        ...

    @router.post("/agents")
    def create_agent(
        ...,
        _quota=Depends(enforce_agent_limit),
    ):
        ...
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.src.db.models import Agent, Subscription, UsageLog
from backend.src.db.session import get_session
from backend.src.modules.auth.deps import get_current_user
from backend.src.modules.payments.constants import get_plan_limits

log = logging.getLogger(__name__)

_UPGRADE_URL = "/app/pricing"


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _platform_month_start() -> datetime:
    """Return the first instant of the current UTC month."""
    now = datetime.now(timezone.utc)
    return now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)


def _total_platform_spend(db: Session, since: datetime) -> float:
    """Sum cost_usd across ALL users since the given timestamp."""
    total = db.execute(
        select(func.coalesce(func.sum(UsageLog.cost_usd), 0)).where(
            UsageLog.created_at >= since,
        )
    ).scalar_one()
    return float(total)


def _user_spend(db: Session, user_id: str, since: datetime) -> float:
    """Sum cost_usd for a single user since the given timestamp."""
    total = db.execute(
        select(func.coalesce(func.sum(UsageLog.cost_usd), 0)).where(
            UsageLog.user_id == user_id,
            UsageLog.created_at >= since,
        )
    ).scalar_one()
    return float(total)

def _get_plan_id(db: Session, user_id: str) -> str:
    """Return the user's active plan_id, defaulting to 'free'."""
    sub = (
        db.query(Subscription)
        .filter(Subscription.user_id == user_id)
        .first()
    )
    if sub and sub.status in ("active", "trialing"):
        return sub.plan_id
    return "free"


def _billing_period_start(db: Session, user_id: str) -> datetime:
    """Derive billing period start from the subscription or fall back to
    the first day of the current UTC month."""
    sub = (
        db.query(Subscription)
        .filter(Subscription.user_id == user_id)
        .first()
    )
    if sub and sub.current_period_start:
        return sub.current_period_start
    now = datetime.now(timezone.utc)
    return now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)


def _current_execution_count(db: Session, user_id: str, period_start: datetime) -> int:
    """Fast count of usage-log entries in the current billing period."""
    return db.execute(
        select(func.count(UsageLog.id)).where(
            UsageLog.user_id == user_id,
            UsageLog.created_at >= period_start,
        )
    ).scalar_one()


def _current_agent_count(db: Session, user_id: str) -> int:
    """Count agents owned by the user."""
    return db.execute(
        select(func.count(Agent.id)).where(Agent.owner_id == user_id)
    ).scalar_one()


def _raise_limit_exceeded(
    *,
    limit_type: str,
    current: int,
    maximum: int,
    plan_id: str,
) -> None:
    """Raise an HTTP 429 with a structured error body."""
    if limit_type == "executions":
        detail = (
            f"Monthly execution limit reached ({current}/{maximum}). "
            f"Upgrade your plan for more capacity."
        )
    else:
        detail = (
            f"Agent limit reached ({current}/{maximum}). "
            f"Upgrade your plan to create more agents."
        )

    raise HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail={
            "message": detail,
            "code": f"plan_limit_{limit_type}",
            "current": current,
            "maximum": maximum,
            "plan_id": plan_id,
            "upgrade_url": _UPGRADE_URL,
        },
    )


# ---------------------------------------------------------------------------
# Public FastAPI dependencies
# ---------------------------------------------------------------------------

async def enforce_execution_limit(
    request: Request,
    user: Any = Depends(get_current_user),
    db: Session = Depends(get_session),
) -> None:
    """Block the request when the user has exhausted their monthly
    execution quota.  Attach plan metadata to ``request.state`` for
    downstream use."""
    user_id: str = user.id
    plan_id = _get_plan_id(db, user_id)
    limits = get_plan_limits(plan_id)

    period_start = _billing_period_start(db, user_id)
    current = _current_execution_count(db, user_id, period_start)

    # Stash for downstream if needed
    request.state.plan_id = plan_id
    request.state.plan_limits = limits

    if current >= limits.max_executions_per_month:
        log.info(
            "Execution limit hit for user=%s plan=%s (%d/%d)",
            user_id, plan_id, current, limits.max_executions_per_month,
        )
        _raise_limit_exceeded(
            limit_type="executions",
            current=current,
            maximum=limits.max_executions_per_month,
            plan_id=plan_id,
        )


async def enforce_agent_limit(
    request: Request,
    user: Any = Depends(get_current_user),
    db: Session = Depends(get_session),
) -> None:
    """Block agent creation when the user has reached their agent count
    limit."""
    user_id: str = user.id
    plan_id = _get_plan_id(db, user_id)
    limits = get_plan_limits(plan_id)

    current = _current_agent_count(db, user_id)

    request.state.plan_id = plan_id
    request.state.plan_limits = limits

    if current >= limits.max_agents:
        log.info(
            "Agent limit hit for user=%s plan=%s (%d/%d)",
            user_id, plan_id, current, limits.max_agents,
        )
        _raise_limit_exceeded(
            limit_type="agents",
            current=current,
            maximum=limits.max_agents,
            plan_id=plan_id,
        )


async def enforce_platform_budget(
    db: Session = Depends(get_session),
) -> None:
    """Platform-wide circuit breaker.

    If total AI spend this month exceeds ``MAX_MONTHLY_AI_SPEND_USD``
    (from Settings), **all** LLM-dependent endpoints return HTTP 503.
    This protects the operator from runaway costs regardless of
    individual plan limits.

    Set ``MAX_MONTHLY_AI_SPEND_USD=0`` to disable the check entirely.
    """
    from backend.src.core.config import get_settings

    cap = get_settings().max_monthly_ai_spend_usd
    if cap <= 0:
        return  # unlimited — circuit breaker disabled

    month_start = _platform_month_start()
    spent = _total_platform_spend(db, month_start)

    # ── Budget threshold alerts (FinOps) ──────────────────────────
    from backend.src.modules.usage.budget_alerts import check_budget_thresholds

    check_budget_thresholds(spent, cap)

    if spent >= cap:
        log.critical(
            "CIRCUIT BREAKER: monthly AI spend $%.2f >= cap $%.2f – blocking LLM requests",
            spent, cap,
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "message": (
                    "AI services are temporarily unavailable due to platform "
                    "spending limits. Please try again later or contact support."
                ),
                "code": "platform_budget_exceeded",
                "spent_usd": round(spent, 2),
                "cap_usd": cap,
            },
        )


async def enforce_user_budget(
    request: Request,
    user: Any = Depends(get_current_user),
    db: Session = Depends(get_session),
) -> None:
    """Per-user monthly AI spending circuit breaker.

    If the user's total AI spend this month exceeds
    ``MAX_USER_MONTHLY_SPEND_USD`` (from Settings), the request is
    rejected with HTTP 429 and a user-friendly detail payload.

    Set ``MAX_USER_MONTHLY_SPEND_USD=0`` to disable the per-user cap.
    """
    from backend.src.core.config import get_settings

    cap = get_settings().max_user_monthly_spend_usd
    if cap <= 0:
        return  # per-user cap disabled

    user_id: str = user.id
    month_start = _platform_month_start()
    spent = _user_spend(db, user_id, month_start)

    if spent >= cap:
        log.warning(
            "USER CIRCUIT BREAKER: user=%s monthly AI spend $%.2f >= cap $%.2f",
            user_id, spent, cap,
        )
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "message": (
                    f"You have reached your monthly AI spending limit "
                    f"(${spent:.2f}/${cap:.2f}). Upgrade your plan or "
                    f"wait until next month."
                ),
                "code": "user_budget_exceeded",
                "spent_usd": round(spent, 2),
                "cap_usd": cap,
                "upgrade_url": _UPGRADE_URL,
            },
        )
