"""Tool registry and adapters for ChatKit placements."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, List

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.src.db import models
from backend.src.modules.flows.constants import DEFAULT_ONBOARDING_TASKS

ToolPayload = Dict[str, Any]
ToolResult = Dict[str, Any]
ToolHandler = Callable[[Session, models.User, models.ChatThread, ToolPayload], ToolResult]


@dataclass(frozen=True)
class ToolSpec:
    """Metadata and handler for a ChatKit tool."""

    name: str
    description: str
    placement: str
    handler: ToolHandler
    schema: Dict[str, Any] | None = None


def _onboarding_brief(
    db: Session,  # noqa: ARG001 - reserved for future DB-backed logic
    user: models.User,
    thread: models.ChatThread,
    payload: ToolPayload,
) -> ToolResult:
    goals = payload.get("goals") or []
    industries = payload.get("industries") or []
    return {
        "summary": {
            "user": user.email,
            "thread_id": thread.id,
            "goals": goals,
            "industries": industries,
        },
        "next_steps": [
            "Confirm org profile and invite teammates",
            "Connect primary data sources",
            "Schedule CapeAI walkthrough",
        ],
    }


def _support_triage(
    db: Session,
    user: models.User,
    thread: models.ChatThread,
    payload: ToolPayload,
) -> ToolResult:
    topic = payload.get("topic", "general")
    urgency = payload.get("urgency", "medium")
    return {
        "ticket": {
            "submitted_by": user.email,
            "thread_id": thread.id,
            "topic": topic,
            "urgency": urgency,
        },
        "recommendation": "A support specialist will review this conversation shortly.",
    }


def _energy_insights(
    db: Session,
    user: models.User,
    thread: models.ChatThread,
    payload: ToolPayload,
) -> ToolResult:
    window = payload.get("window", "24h")
    metric = payload.get("metric", "consumption")
    return {
        "analysis": {
            "window": window,
            "metric": metric,
            "trend": "up",
            "variance": 0.18,
        },
        "insight": "Usage increased due to HVAC load. Consider scheduling an energy saver scene.",
    }


def _money_summary(
    db: Session,
    user: models.User,
    thread: models.ChatThread,
    payload: ToolPayload,
) -> ToolResult:
    period = payload.get("period", "current_month")
    return {
        "summary": {
            "period": period,
            "top_merchants": ["Cape Supplies", "CloudCompute"]
        },
        "note": "Connect accounting for deeper benchmarking.",
    }


def _onboarding_checklist(
    db: Session,
    user: models.User,
    thread: models.ChatThread,
    payload: ToolPayload,
) -> ToolResult:
    checklist = db.scalar(
        select(models.OnboardingChecklist).where(models.OnboardingChecklist.user_id == user.id)
    )
    if checklist is None:
        checklist = models.OnboardingChecklist(
            user_id=user.id,
            thread_id=thread.id,
            tasks={
                task["id"]: {"label": task["label"], "done": False}
                for task in DEFAULT_ONBOARDING_TASKS
            },
        )
        db.add(checklist)

    tasks = checklist.tasks or {
        task["id"]: {"label": task["label"], "done": False}
        for task in DEFAULT_ONBOARDING_TASKS
    }

    task_id = payload.get("task_id")
    if isinstance(task_id, str) and task_id:
        done_flag = bool(payload.get("done"))
        label = payload.get("label") or task_id.replace("_", " ").title()
        tasks[task_id] = {"label": label, "done": done_flag}

    checklist.tasks = tasks
    checklist.thread_id = thread.id
    db.add(checklist)

    completed = sum(1 for task in tasks.values() if task.get("done"))
    total = len(tasks)
    return {
        "tasks": tasks,
        "summary": {
            "completed": completed,
            "total": total,
        },
    }


TOOLS: Dict[str, ToolSpec] = {
    "onboarding.plan": ToolSpec(
        name="onboarding.plan",
        placement="onboarding",
        description="Generate a guided onboarding checklist based on client goals.",
        handler=_onboarding_brief,
    ),
    "onboarding.checklist": ToolSpec(
        name="onboarding.checklist",
        placement="onboarding",
        description="Update onboarding checklist progress for the current tenant.",
        handler=_onboarding_checklist,
    ),
    "support.ticket": ToolSpec(
        name="support.ticket",
        placement="support",
        description="File a structured support ticket from the conversation context.",
        handler=_support_triage,
    ),
    "energy.usage": ToolSpec(
        name="energy.usage",
        placement="energy",
        description="Explain recent usage patterns and highlight anomalies.",
        handler=_energy_insights,
    ),
    "money.summary": ToolSpec(
        name="money.summary",
        placement="money",
        description="Summarize financial transactions for a given period.",
        handler=_money_summary,
    ),
}


def tools_for_placement(placement: str) -> List[str]:
    """Return the list of tool identifiers allowed for a given placement."""

    return [spec.name for spec in TOOLS.values() if spec.placement == placement]


def get_tool(placement: str, tool_name: str) -> ToolSpec:
    spec = TOOLS.get(tool_name)
    if not spec or spec.placement != placement:
        raise ValueError("tool not available for placement")
    return spec


def invoke_tool(
    db: Session,
    *,
    spec: ToolSpec,
    user: models.User,
    thread: models.ChatThread,
    payload: ToolPayload,
) -> ToolResult:
    return spec.handler(db, user, thread, payload)
