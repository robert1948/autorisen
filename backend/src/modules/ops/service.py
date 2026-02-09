"""Ops insights service."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.src.db import models


def build_insight(db: Session, user: models.User, intent: str) -> dict[str, Any]:
    intent = intent.strip().lower()
    now = datetime.utcnow()

    if intent == "project_status":
        latest_task = db.scalars(
            select(models.Task)
            .where(models.Task.user_id == user.id)
            .order_by(models.Task.created_at.desc())
            .limit(1)
        ).first()
        status_value = latest_task.status if latest_task else "Unknown (not set)"
        summary = (
            f"Most recent task status is '{status_value}'."
            if latest_task
            else "No active tasks yet. Status is unknown until work begins."
        )
        return {
            "title": "Project status",
            "summary": summary,
            "key_metrics": [
                {"label": "status", "value": status_value},
                {
                    "label": "last_activity",
                    "value": latest_task.created_at.isoformat()
                    if latest_task
                    else "n/a",
                },
            ],
            "sources": [
                {"table": "tasks", "window": "latest"},
            ],
        }

    if intent == "top_blockers":
        window_start = now - timedelta(days=30)
        events = db.scalars(
            select(models.OnboardingEventLog)
            .where(
                models.OnboardingEventLog.user_id == user.id,
                models.OnboardingEventLog.event_type == "step_blocked",
                models.OnboardingEventLog.created_at >= window_start,
            )
            .order_by(models.OnboardingEventLog.created_at.desc())
        ).all()
        counts: dict[str, int] = {}
        for event in events:
            payload = event.payload or {}
            reason = str(payload.get("reason") or "Unspecified")
            counts[reason] = counts.get(reason, 0) + 1
        ranked = sorted(counts.items(), key=lambda item: item[1], reverse=True)
        key_metrics = [
            {"label": reason, "value": count} for reason, count in ranked[:5]
        ]
        summary = (
            "No blockers recorded in the last 30 days."
            if not ranked
            else f"Top blockers include: {', '.join(reason for reason, _ in ranked[:3])}."
        )
        return {
            "title": "Top blockers",
            "summary": summary,
            "key_metrics": key_metrics,
            "sources": [
                {"table": "onboarding_event_log", "window": "30d"},
            ],
        }

    if intent == "onboarding_completion_rate":
        total_sessions = db.scalar(
            select(func.count()).select_from(models.OnboardingSession).where(
                models.OnboardingSession.user_id == user.id
            )
        )
        completed_sessions = db.scalar(
            select(func.count()).select_from(models.OnboardingSession).where(
                models.OnboardingSession.user_id == user.id,
                models.OnboardingSession.onboarding_completed.is_(True),
            )
        )
        total_sessions = int(total_sessions or 0)
        completed_sessions = int(completed_sessions or 0)
        rate = int((completed_sessions / total_sessions) * 100) if total_sessions else 0
        return {
            "title": "Onboarding completion rate",
            "summary": f"{rate}% of onboarding sessions are completed.",
            "key_metrics": [
                {"label": "completion_rate", "value": rate},
                {"label": "completed", "value": completed_sessions},
                {"label": "total_sessions", "value": total_sessions},
            ],
            "sources": [
                {"table": "onboarding_sessions", "window": "all"},
            ],
        }

    if intent == "agent_usage_last_7d":
        window_start = now - timedelta(days=7)
        run_count = db.scalar(
            select(func.count()).select_from(models.AgentRun).where(
                models.AgentRun.user_id == user.id,
                models.AgentRun.created_at >= window_start,
            )
        )
        run_count = int(run_count or 0)
        return {
            "title": "Agent usage (last 7 days)",
            "summary": f"{run_count} agent runs recorded in the last 7 days.",
            "key_metrics": [
                {"label": "run_count", "value": run_count},
            ],
            "sources": [
                {"table": "agent_runs", "window": "7d"},
            ],
        }

    if intent == "open_support_tickets":
        open_count = db.scalar(
            select(func.count()).select_from(models.SupportTicket).where(
                models.SupportTicket.user_id == user.id,
                models.SupportTicket.status == "open",
            )
        )
        open_count = int(open_count or 0)
        return {
            "title": "Open support tickets",
            "summary": f"{open_count} open support ticket(s).",
            "key_metrics": [
                {"label": "open_tickets", "value": open_count},
            ],
            "sources": [
                {"table": "support_tickets", "window": "current"},
            ],
        }

    return {
        "title": "Unknown intent",
        "summary": "This insight intent is not supported.",
        "key_metrics": [],
        "sources": [],
    }
