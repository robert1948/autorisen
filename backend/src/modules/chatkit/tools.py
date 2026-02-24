"""Tool registry and adapters for ChatKit placements."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, List

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.src.db import models
from backend.src.modules.flows.constants import DEFAULT_ONBOARDING_TASKS
from backend.src.modules.payments.config import get_payfast_settings
from backend.src.modules.payments import service as payments_service

ToolPayload = Dict[str, Any]
ToolResult = Dict[str, Any]
ToolHandler = Callable[
    [Session, models.User, models.ChatThread, ToolPayload], ToolResult
]


@dataclass(frozen=True)
class ToolSpec:
    """Metadata and handler for a ChatKit tool."""

    name: str
    description: str
    placement: str
    handler: ToolHandler
    schema: Dict[str, Any] | None = None


def _onboarding_brief(
    _db: Session,
    user: models.User,
    thread: models.ChatThread,
    payload: ToolPayload,
) -> ToolResult:
    del _db
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
    _db: Session,
    user: models.User,
    thread: models.ChatThread,
    payload: ToolPayload,
) -> ToolResult:
    del _db
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
    _db: Session,
    _user: models.User,
    _thread: models.ChatThread,
    payload: ToolPayload,
) -> ToolResult:
    del _db, _user, _thread
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
    _db: Session,
    _user: models.User,
    _thread: models.ChatThread,
    payload: ToolPayload,
) -> ToolResult:
    del _db, _user, _thread
    period = payload.get("period", "current_month")
    return {
        "summary": {
            "period": period,
            "top_merchants": ["Cape Supplies", "CloudCompute"],
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
        select(models.OnboardingChecklist).where(
            models.OnboardingChecklist.user_id == user.id
        )
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


def _payments_checkout(
    _db: Session,
    user: models.User,
    _thread: models.ChatThread,
    payload: ToolPayload,
) -> ToolResult:
    del _db, _thread
    settings = get_payfast_settings()
    amount = payload.get("amount")
    item_name = payload.get("item_name") or "CapeControl Subscription"
    if amount is None:
        raise ValueError("amount is required")

    customer_email = payload.get("customer_email") or user.email
    metadata = payload.get("metadata")
    if metadata and not isinstance(metadata, dict):
        raise ValueError("metadata must be an object")

    session = payments_service.create_checkout_session(
        settings=settings,
        amount=amount,
        item_name=item_name,
        item_description=payload.get("item_description"),
        customer_email=customer_email,
        customer_first_name=payload.get("customer_first_name") or user.first_name,
        customer_last_name=payload.get("customer_last_name") or user.last_name,
        metadata=metadata,
    )

    return {
        "checkout": session,
        "note": "Submit these fields via POST to the PayFast process URL.",
    }


def _rag_search(
    db: Session,
    user: models.User,
    _thread: models.ChatThread,
    payload: ToolPayload,
) -> ToolResult:
    """Synchronous wrapper — runs the async RAG query in a new event loop."""
    import asyncio

    from backend.src.modules.rag.service import RAGService
    from backend.src.modules.rag.schemas import RAGQueryRequest, UnsupportedPolicy

    query = payload.get("query", "")
    if not query:
        return {"error": "query is required"}

    service = RAGService()
    request = RAGQueryRequest(
        query=query,
        doc_types=payload.get("doc_types"),
        top_k=payload.get("top_k", 5),
        similarity_threshold=payload.get("similarity_threshold", 0.25),
        unsupported_policy=payload.get("unsupported_policy", UnsupportedPolicy.FLAG),
        include_response=payload.get("include_response", True),
    )

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as pool:
            result = pool.submit(
                asyncio.run, service.query(db, user, request)
            ).result()
    else:
        result = asyncio.run(service.query(db, user, request))

    return result.dict()


TOOLS: Dict[str, ToolSpec] = {
    "onboarding.plan": ToolSpec(
        name="onboarding.plan",
        placement="onboarding",
        description="Generate a guided onboarding checklist based on client goals.",
        handler=_onboarding_brief,
        schema={
            "type": "object",
            "properties": {
                "goals": {"type": "array", "items": {"type": "string"}},
                "industries": {"type": "array", "items": {"type": "string"}},
            },
        },
    ),
    "onboarding.checklist": ToolSpec(
        name="onboarding.checklist",
        placement="onboarding",
        description="Update onboarding checklist progress for the current tenant.",
        handler=_onboarding_checklist,
        schema={
            "type": "object",
            "properties": {
                "task_id": {"type": "string"},
                "done": {"type": "boolean"},
                "label": {"type": "string"},
            },
        },
    ),
    "support.ticket": ToolSpec(
        name="support.ticket",
        placement="support",
        description="File a structured support ticket from the conversation context.",
        handler=_support_triage,
        schema={
            "type": "object",
            "properties": {
                "topic": {"type": "string"},
                "urgency": {
                    "type": "string",
                    "enum": ["low", "medium", "high"],
                },
            },
        },
    ),
    "energy.usage": ToolSpec(
        name="energy.usage",
        placement="energy",
        description="Explain recent usage patterns and highlight anomalies.",
        handler=_energy_insights,
        schema={
            "type": "object",
            "properties": {
                "window": {"type": "string"},
                "metric": {"type": "string"},
            },
        },
    ),
    "money.summary": ToolSpec(
        name="money.summary",
        placement="money",
        description="Summarize financial transactions for a given period.",
        handler=_money_summary,
        schema={
            "type": "object",
            "properties": {
                "period": {"type": "string"},
            },
        },
    ),
    "payments.payfast.checkout": ToolSpec(
        name="payments.payfast.checkout",
        placement="money",
        description="Generate a signed PayFast checkout payload for a customer.",
        handler=_payments_checkout,
        schema={
            "type": "object",
            "properties": {
                "amount": {"type": "number", "minimum": 1},
                "item_name": {"type": "string"},
                "item_description": {"type": "string"},
                "customer_email": {"type": "string"},
                "metadata": {"type": "object"},
            },
            "required": ["amount"],
        },
    ),
    "rag.search": ToolSpec(
        name="rag.search",
        placement="rag",
        description="Search approved business documents and return evidence-backed answers with citations.",
        handler=_rag_search,
        schema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The question to answer from approved documents"},
                "doc_types": {"type": "array", "items": {"type": "string"}, "description": "Filter by document type"},
                "top_k": {"type": "integer", "minimum": 1, "maximum": 20, "description": "Max chunks to retrieve"},
                "similarity_threshold": {"type": "number", "minimum": 0, "maximum": 1},
                "unsupported_policy": {"type": "string", "enum": ["refuse", "flag", "allow"]},
                "include_response": {"type": "boolean"},
            },
            "required": ["query"],
        },
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
