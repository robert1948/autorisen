"""Usage tracking service — record billable events and aggregate per-user."""

from __future__ import annotations

import logging
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any, Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.src.db.models import UsageLog, AgentRun, AuditEvent, Agent, AgentInstallation
from backend.src.modules.rag.models import ApprovedDocument, RAGQueryLog

log = logging.getLogger(__name__)

# ── Model cost rates (USD per 1 M tokens) ────────────────────────────────────
# Updated as Anthropic publishes new pricing.
MODEL_RATES: dict[str, dict[str, Decimal]] = {
    # Sonnet family
    "claude-sonnet-4-20250514": {"input": Decimal("3.00"), "output": Decimal("15.00")},
    "claude-3-5-sonnet-20241022": {"input": Decimal("3.00"), "output": Decimal("15.00")},
    "claude-3-sonnet-20240229": {"input": Decimal("3.00"), "output": Decimal("15.00")},
    # Haiku family
    "claude-3-5-haiku-20241022": {"input": Decimal("0.25"), "output": Decimal("1.25")},
    "claude-3-haiku-20240307": {"input": Decimal("0.25"), "output": Decimal("1.25")},
    # Opus family
    "claude-3-opus-20240229": {"input": Decimal("15.00"), "output": Decimal("75.00")},
}

# Fallback for unknown models
_DEFAULT_RATE = {"input": Decimal("3.00"), "output": Decimal("15.00")}

_ONE_MILLION = Decimal("1000000")


def compute_cost_usd(model: str, tokens_in: int, tokens_out: int) -> Decimal:
    """Compute the USD cost for a single LLM call."""
    rates = MODEL_RATES.get(model, _DEFAULT_RATE)
    cost = (
        Decimal(tokens_in) * rates["input"] / _ONE_MILLION
        + Decimal(tokens_out) * rates["output"] / _ONE_MILLION
    )
    return cost.quantize(Decimal("0.000001"))


# ── Write operations ──────────────────────────────────────────────────────────


def record_usage(
    db: Session,
    *,
    user_id: str,
    event_type: str = "chat",
    model: Optional[str] = None,
    tokens_in: int = 0,
    tokens_out: int = 0,
    cost_usd: Optional[Decimal] = None,
    thread_id: Optional[str] = None,
    detail: Optional[dict[str, Any]] = None,
) -> UsageLog:
    """Insert a single usage row.  If cost_usd is not provided it is
    computed from the model's published rates."""
    if cost_usd is None and model:
        cost_usd = compute_cost_usd(model, tokens_in, tokens_out)
    entry = UsageLog(
        id=str(uuid.uuid4()),
        user_id=user_id,
        thread_id=thread_id,
        event_type=event_type,
        model=model,
        tokens_in=tokens_in,
        tokens_out=tokens_out,
        cost_usd=cost_usd or Decimal("0"),
        detail=detail,
    )
    db.add(entry)
    # Caller is responsible for commit (usually piggybacks on the chat commit)
    return entry


# ── Read / aggregation ────────────────────────────────────────────────────────

from backend.src.modules.payments.constants import get_plan_limits as _get_plan_limits


def get_usage_summary(
    db: Session,
    *,
    user_id: str,
    period_start: datetime,
    plan_id: str = "free",
) -> dict[str, Any]:
    """Aggregate usage for a user within the current billing period."""
    row = db.execute(
        select(
            func.count(UsageLog.id).label("api_calls_used"),
            func.coalesce(func.sum(UsageLog.tokens_in), 0).label("total_tokens_in"),
            func.coalesce(func.sum(UsageLog.tokens_out), 0).label("total_tokens_out"),
            func.coalesce(func.sum(UsageLog.cost_usd), 0).label("total_cost_usd"),
        ).where(
            UsageLog.user_id == user_id,
            UsageLog.created_at >= period_start,
        )
    ).one()

    _limits = _get_plan_limits(plan_id)
    quotas = {
        "api_calls_limit": _limits.max_executions_per_month,
        "storage_limit_mb": _limits.storage_limit_mb,
    }

    # ── Real usage metrics from related tables ────────────────────────────
    agent_runs_count = db.execute(
        select(func.count(AgentRun.id)).where(
            AgentRun.user_id == user_id,
            AgentRun.created_at >= period_start,
        )
    ).scalar_one()

    documents_count = db.execute(
        select(func.count(ApprovedDocument.id)).where(
            ApprovedDocument.owner_id == user_id,
        )
    ).scalar_one()

    rag_queries_count = db.execute(
        select(func.count(RAGQueryLog.id)).where(
            RAGQueryLog.user_id == user_id,
            RAGQueryLog.created_at >= period_start,
        )
    ).scalar_one()

    evidence_exports_count = db.execute(
        select(func.count(AuditEvent.id)).where(
            AuditEvent.user_id == user_id,
            AuditEvent.event_type == "evidence_export",
            AuditEvent.created_at >= period_start,
        )
    ).scalar_one()

    # Agent counts — owned + installed
    owned_agents = db.execute(
        select(func.count(Agent.id)).where(Agent.owner_id == user_id)
    ).scalar_one()
    installed_agents = db.execute(
        select(func.count(AgentInstallation.id)).where(
            AgentInstallation.user_id == user_id,
            AgentInstallation.status == "active",
        )
    ).scalar_one()
    agent_count = owned_agents + installed_agents

    return {
        "api_calls_used": row.api_calls_used,
        "api_calls_limit": quotas["api_calls_limit"],
        "total_tokens_in": int(row.total_tokens_in),
        "total_tokens_out": int(row.total_tokens_out),
        "total_cost_usd": float(row.total_cost_usd),
        "storage_used_mb": 0,  # placeholder until file uploads implemented
        "storage_limit_mb": quotas["storage_limit_mb"],
        "period_start": period_start.isoformat(),
        "plan_id": plan_id,
        # Real usage metrics
        "agent_runs": agent_runs_count,
        "documents_count": documents_count,
        "rag_queries": rag_queries_count,
        "evidence_exports": evidence_exports_count,
        # Agent utilisation
        "agent_count": agent_count,
        "max_agents": _limits.max_agents,
    }


def get_admin_cost_report(
    db: Session,
    *,
    period_start: datetime,
) -> list[dict[str, Any]]:
    """Admin-only: per-user cost aggregation for the given period."""
    rows = db.execute(
        select(
            UsageLog.user_id,
            func.count(UsageLog.id).label("total_calls"),
            func.coalesce(func.sum(UsageLog.tokens_in), 0).label("tokens_in"),
            func.coalesce(func.sum(UsageLog.tokens_out), 0).label("tokens_out"),
            func.coalesce(func.sum(UsageLog.cost_usd), 0).label("cost_usd"),
        )
        .where(UsageLog.created_at >= period_start)
        .group_by(UsageLog.user_id)
        .order_by(func.sum(UsageLog.cost_usd).desc())
    ).all()

    return [
        {
            "user_id": r.user_id,
            "total_calls": r.total_calls,
            "tokens_in": int(r.tokens_in),
            "tokens_out": int(r.tokens_out),
            "cost_usd": float(r.cost_usd),
        }
        for r in rows
    ]
