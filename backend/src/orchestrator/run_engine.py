"""Lightweight orchestrator entry point for ChatKit-driven workflows."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from backend.src.db import models
from backend.src.modules.chatkit import service as chatkit_service
from backend.src.modules.flows.constants import DEFAULT_ONBOARDING_TASKS
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


@dataclass(frozen=True)
class AgentContext:
    """Resolved agent + version context for orchestrator execution."""

    agent: models.Agent
    version: models.AgentVersion
    placement: str
    allowed_tools: Tuple[str, ...]


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

    version_stmt = select(models.AgentVersion).where(models.AgentVersion.agent_id == agent.id)
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
) -> RunResult:
    """Execute a sequence of tool calls and return structured trace data."""
    steps: List[RunStep] = []
    steps_payload: List[Dict[str, Any]] = []
    current_thread_id = thread_id
    if agent:
        effective_placement = agent.placement
        allowed_tools = set(agent.allowed_tools)
    else:
        if not placement:
            raise ValueError("placement required when agent context is absent")
        effective_placement = placement
        allowed_tools = None

    for call in tool_calls:
        if allowed_tools is not None and call.name not in allowed_tools:
            raise ValueError(f"tool '{call.name}' not allowed for agent")
        thread, result, event = chatkit_service.invoke_tool(
            db,
            user=user,
            placement=effective_placement,
            tool_name=call.name,
            payload=call.payload,
            thread_id=current_thread_id,
        )
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

    if current_thread_id is None:
        raise RuntimeError("No thread produced during orchestration run.")

    flow_run = models.FlowRun(
        user_id=getattr(user, "id", None),
        agent_id=agent.agent.id if agent else None,
        agent_version_id=agent.version.id if agent else None,
        placement=effective_placement,
        thread_id=current_thread_id,
        steps=steps_payload,
    )
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
    )
