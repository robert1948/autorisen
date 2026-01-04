"""Shared tool/function calling utilities for agent services.

This module adapts the ChatKit tool registry to LLM tool/function calling APIs.
Tool execution is delegated to ChatKit tool handlers so results are consistent
and audited.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional

from sqlalchemy.orm import Session

from backend.src.db import models
from backend.src.modules.chatkit import service as chatkit_service
from backend.src.modules.chatkit import tools as chatkit_tools


@dataclass
class ToolUseContext:
    placement: str
    thread_id: Optional[str] = None
    allowed_tools: Optional[Iterable[str]] = None


def resolve_allowed_tools(ctx: ToolUseContext) -> List[chatkit_tools.ToolSpec]:
    """Resolve the allowlisted tool specs for the given placement."""

    placement_tools = {
        spec.name: spec
        for spec in chatkit_tools.TOOLS.values()
        if spec.placement == ctx.placement
    }

    if ctx.allowed_tools is None:
        return list(placement_tools.values())

    allowlisted: List[chatkit_tools.ToolSpec] = []
    for tool_name in ctx.allowed_tools:
        spec = placement_tools.get(tool_name)
        if spec:
            allowlisted.append(spec)
    return allowlisted


def openai_tools_payload(specs: List[chatkit_tools.ToolSpec]) -> List[Dict[str, Any]]:
    tools: List[Dict[str, Any]] = []
    for spec in specs:
        schema = spec.schema or {"type": "object", "properties": {}}
        tools.append(
            {
                "type": "function",
                "function": {
                    "name": spec.name,
                    "description": spec.description,
                    "parameters": schema,
                },
            }
        )
    return tools


def anthropic_tools_payload(
    specs: List[chatkit_tools.ToolSpec],
) -> List[Dict[str, Any]]:
    tools: List[Dict[str, Any]] = []
    for spec in specs:
        schema = spec.schema or {"type": "object", "properties": {}}
        tools.append(
            {
                "name": spec.name,
                "description": spec.description,
                "input_schema": schema,
            }
        )
    return tools


def _safe_json_dumps(value: Any) -> str:
    try:
        return json.dumps(value, ensure_ascii=False, default=str)
    except TypeError:
        return json.dumps({"error": "unable to serialize"}, ensure_ascii=False)


def execute_tool(
    db: Session,
    *,
    user: models.User,
    ctx: ToolUseContext,
    tool_name: str,
    tool_payload: Dict[str, Any],
    agent_id: str | None = None,
    task_id: str | None = None,
) -> Dict[str, Any]:
    """Execute a tool via ChatKit tool handlers (audited)."""

    if ctx.allowed_tools is not None:
        allowlisted = set(ctx.allowed_tools)
        if tool_name not in allowlisted:
            raise RuntimeError("tool not allowlisted")

    thread, result, event = chatkit_service.invoke_tool(
        db,
        user=user,
        placement=ctx.placement,
        tool_name=tool_name,
        payload=tool_payload,
        thread_id=ctx.thread_id,
        agent_id=agent_id,
        task_id=task_id,
    )

    ctx.thread_id = thread.id  # type: ignore[misc]

    return {
        "result": result,
        "thread_id": thread.id,
        "chat_event_id": event.id,
        "audit_event_id": (event.event_metadata or {}).get("audit_event_id"),
    }


def normalize_openai_tool_args(raw_args: Any) -> Dict[str, Any]:
    if raw_args is None:
        return {}
    if isinstance(raw_args, dict):
        return raw_args
    if isinstance(raw_args, str):
        try:
            parsed = json.loads(raw_args)
            if isinstance(parsed, dict):
                return parsed
        except (TypeError, ValueError):
            return {}
    return {}


def normalize_anthropic_tool_input(raw_input: Any) -> Dict[str, Any]:
    if raw_input is None:
        return {}
    if isinstance(raw_input, dict):
        return raw_input
    return {}


def tool_result_text(payload: Any) -> str:
    return _safe_json_dumps(payload)
