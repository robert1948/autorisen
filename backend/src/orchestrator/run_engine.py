"""Lightweight orchestrator entry point for ChatKit-driven workflows."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional, Tuple

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from backend.src.db import models
from backend.src.modules.chatkit import service as chatkit_service
from backend.src.modules.flows.onboarding import update_task


@dataclass
class ToolCall:
    """Declarative tool invocation requested by the frontend."""

    name: str
    payload: Dict[str, Any]


@dataclass
class RunStep:
    """Trace entry generated for each tool invocation."""

    tool: str
    payload: Dict[str, Any]
    result: Dict[str, Any]
    event_id: str


@dataclass
class RunResult:
    """Aggregated orchestrator response."""

    run_id: str
    thread_id: str
    placement: str
    steps: List[RunStep] = field(default_factory=list)
    agent_id: Optional[str] = None
    agent_version_id: Optional[str] = None
    status: str = "pending"
    attempt: int = 0
    max_attempts: int = 1
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


@dataclass(frozen=True)
class AgentContext:
    """Resolved agent + version context for orchestrator execution."""

    agent: models.Agent
    version: models.AgentVersion
    placement: str
    allowed_tools: Tuple[str, ...]


class RunExecutionError(RuntimeError):
    """Raised when the orchestrator exhausts retries or encounters fatal errors."""

    def __init__(self, message: str, *, run_id: str, retryable: bool = False):
        super().__init__(message)
        self.run_id = run_id
        self.retryable = retryable


PENDING_THREAD_PLACEHOLDER = "__pending__"
DEFAULT_RETRY_DELAY = 0.5
RETRY_BACKOFF = 2.0


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _deserialize_steps(payload: Iterable[Dict[str, Any]]) -> List[RunStep]:
    steps: List[RunStep] = []
    for item in payload or []:
        if not isinstance(item, dict):
            continue
        steps.append(
            RunStep(
                tool=item.get("tool", ""),
                payload=item.get("payload", {}) or {},
                result=item.get("result", {}) or {},
                event_id=item.get("event_id", ""),
            )
        )
    return steps


def _build_result_from_model(flow_run: models.FlowRun) -> RunResult:
    return RunResult(
        run_id=flow_run.id,
        thread_id=flow_run.thread_id,
        placement=flow_run.placement,
        steps=_deserialize_steps(flow_run.steps or []),
        agent_id=flow_run.agent_id,
        agent_version_id=flow_run.agent_version_id,
        status=flow_run.status,
        attempt=flow_run.attempt,
        max_attempts=flow_run.max_attempts,
        error_message=flow_run.error_message,
        started_at=flow_run.started_at,
        completed_at=flow_run.completed_at,
    )


def _invoke_with_retry(
    db: Session,
    *,
    user: models.User,
    placement: str,
    tool_name: str,
    payload: Dict[str, Any],
    thread_id: Optional[str],
    max_attempts: int,
    agent_id: str | None = None,
) -> Tuple[models.ChatThread, Dict[str, Any], models.ChatEvent]:
    """Execute a tool call with bounded retries for transient failures."""
    attempts = 0
    delay = DEFAULT_RETRY_DELAY

    while True:
        attempts += 1
        try:
            return chatkit_service.invoke_tool(
                db,
                user=user,
                placement=placement,
                tool_name=tool_name,
                payload=payload,
                thread_id=thread_id,
                agent_id=agent_id,
            )
        except ValueError:
            # Validation/user errors should bubble immediately.
            raise
        except Exception:  # noqa: BLE001
            if attempts >= max_attempts:
                raise
            time.sleep(delay)
            delay *= RETRY_BACKOFF


def _mark_failed(
    db: Session,
    *,
    flow_run: models.FlowRun,
    steps_payload: List[Dict[str, Any]],
    thread_id: Optional[str],
    message: str,
) -> None:
    flow_run.status = "failed"
    flow_run.error_message = message
    if thread_id:
        flow_run.thread_id = thread_id
    flow_run.steps = steps_payload
    flow_run.completed_at = _now()
    db.add(flow_run)
    db.commit()


def _ensure_thread_placeholder(thread_id: Optional[str]) -> str:
    return thread_id or PENDING_THREAD_PLACEHOLDER


def resolve_agent_context(
    db: Session,
    *,
    user: models.User,
    agent_slug: str,
    version: Optional[str],
) -> AgentContext:
    agent_stmt = select(models.Agent).where(
        models.Agent.owner_id == user.id,
        models.Agent.slug == agent_slug,
    )
    agent = db.scalar(agent_stmt)
    if agent is None:
        raise ValueError("agent not found")

    version_stmt = select(models.AgentVersion).where(
        models.AgentVersion.agent_id == agent.id
    )
    if version:
        version_stmt = version_stmt.where(models.AgentVersion.version == version)
    else:
        version_stmt = version_stmt.where(models.AgentVersion.status == "published")
    version_stmt = version_stmt.order_by(desc(models.AgentVersion.created_at))

    agent_version = db.scalar(version_stmt)
    if agent_version is None:
        raise ValueError("agent version not found or not published")

    manifest = agent_version.manifest or {}
    placement = manifest.get("placement")
    tools = manifest.get("tools") or []
    if not placement or not isinstance(placement, str):
        raise ValueError("agent manifest missing placement")
    if not tools or not all(isinstance(tool, str) for tool in tools):
        raise ValueError("agent manifest missing tools list")

    return AgentContext(
        agent=agent,
        version=agent_version,
        placement=placement,
        allowed_tools=tuple(tools),
    )


def execute(
    db: Session,
    *,
    user: models.User,
    placement: Optional[str],
    tool_calls: List[ToolCall],
    thread_id: str | None = None,
    agent: AgentContext | None = None,
    idempotency_key: str | None = None,
    max_attempts: int = 3,
) -> RunResult:
    """Execute a sequence of tool calls and return structured trace data."""
    steps: List[RunStep] = []
    steps_payload: List[Dict[str, Any]] = []
    current_thread_id = thread_id
    max_attempts = max(1, max_attempts)

    if agent:
        effective_placement = agent.placement
        allowed_tools = set(agent.allowed_tools)
    else:
        if not placement:
            raise ValueError("placement required when agent context is absent")
        effective_placement = placement
        allowed_tools = None

    existing_run: Optional[models.FlowRun] = None
    if idempotency_key and getattr(user, "id", None):
        stmt = select(models.FlowRun).where(
            models.FlowRun.user_id == user.id,
            models.FlowRun.idempotency_key == idempotency_key,
        )
        existing_run = db.scalar(stmt)
        if existing_run:
            return _build_result_from_model(existing_run)

    flow_run = models.FlowRun(
        user_id=getattr(user, "id", None),
        agent_id=agent.agent.id if agent else None,
        agent_version_id=agent.version.id if agent else None,
        placement=effective_placement,
        thread_id=_ensure_thread_placeholder(current_thread_id),
        steps=[],
        status="pending",
        attempt=0,
        max_attempts=max_attempts,
        idempotency_key=idempotency_key,
        started_at=_now(),
    )
    db.add(flow_run)
    db.commit()
    db.refresh(flow_run)

    flow_run.status = "running"
    flow_run.attempt = (flow_run.attempt or 0) + 1
    flow_run.max_attempts = max_attempts
    flow_run.started_at = flow_run.started_at or _now()
    db.add(flow_run)
    db.commit()

    for call in tool_calls:
        if allowed_tools is not None and call.name not in allowed_tools:
            raise ValueError(f"tool '{call.name}' not allowed for agent")
        try:
            thread, result, event = _invoke_with_retry(
                db,
                user=user,
                placement=effective_placement,
                tool_name=call.name,
                payload=call.payload,
                thread_id=current_thread_id,
                max_attempts=max_attempts,
                agent_id=agent.agent.id if agent else None,
            )
        except ValueError as exc:
            _mark_failed(
                db,
                flow_run=flow_run,
                steps_payload=steps_payload,
                thread_id=current_thread_id,
                message=str(exc),
            )
            raise
        except (
            Exception
        ) as exc:  # noqa: BLE001 broad but captured for retries exhaustion
            _mark_failed(
                db,
                flow_run=flow_run,
                steps_payload=steps_payload,
                thread_id=current_thread_id,
                message=str(exc),
            )
            raise RunExecutionError(
                "Flow run failed after exhausting retries.",
                run_id=flow_run.id,
                retryable=False,
            ) from exc

        current_thread_id = thread.id
        steps.append(
            RunStep(
                tool=call.name,
                payload=call.payload,
                result=result,
                event_id=event.id,
            )
        )
        steps_payload.append(
            {
                "tool": call.name,
                "payload": call.payload,
                "result": result,
                "event_id": event.id,
            }
        )
        flow_run.thread_id = current_thread_id
        flow_run.steps = steps_payload
        db.add(flow_run)
        db.commit()

        if effective_placement == "onboarding":
            # mark tasks for known onboarding tools
            if call.name == "onboarding.plan":
                # seed default tasks
                update_task(
                    db,
                    user_id=getattr(user, "id", ""),
                    thread_id=thread.id,
                    task_id="invite_team",
                    done=False,
                    label="Invite core teammates",
                )
            if call.name == "onboarding.checklist" and isinstance(call.payload, dict):
                task_id = call.payload.get("task_id")
                if isinstance(task_id, str):
                    update_task(
                        db,
                        user_id=getattr(user, "id", ""),
                        thread_id=thread.id,
                        task_id=task_id,
                        done=bool(call.payload.get("done", True)),
                        label=call.payload.get("label"),
                    )

    if current_thread_id is None or current_thread_id == PENDING_THREAD_PLACEHOLDER:
        message = "No thread produced during orchestration run."
        _mark_failed(
            db,
            flow_run=flow_run,
            steps_payload=steps_payload,
            thread_id=current_thread_id,
            message=message,
        )
        raise RunExecutionError(
            message,
            run_id=flow_run.id,
            retryable=False,
        )

    flow_run.thread_id = current_thread_id
    flow_run.steps = steps_payload
    flow_run.status = "succeeded"
    flow_run.error_message = None
    flow_run.completed_at = _now()
    db.add(flow_run)
    db.commit()
    db.refresh(flow_run)

    return RunResult(
        run_id=flow_run.id,
        thread_id=current_thread_id,
        placement=effective_placement,
        steps=steps,
        agent_id=agent.agent.id if agent else None,
        agent_version_id=agent.version.id if agent else None,
        status=flow_run.status,
        attempt=flow_run.attempt,
        max_attempts=flow_run.max_attempts,
        error_message=flow_run.error_message,
        started_at=flow_run.started_at,
        completed_at=flow_run.completed_at,
    )
