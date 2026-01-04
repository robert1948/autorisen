"""CapeAI Domain Specialist service.

Provides a reusable service that combines lightweight determinism (knowledge base
search + heuristics) with optional LLM completions to deliver domain-aware
guidance for workflow automation, data analytics, security audit, and
integration helper use cases.
"""

from __future__ import annotations

import json
import time
from typing import Any, Dict, List, Optional

from anthropic import AnthropicError, AsyncAnthropic
from openai import AsyncOpenAI, OpenAIError
from sqlalchemy.orm import Session

from backend.src.db import models
from backend.src.modules.agents.tool_use import (
    ToolUseContext,
    anthropic_tools_payload,
    execute_tool,
    normalize_anthropic_tool_input,
    normalize_openai_tool_args,
    openai_tools_payload,
    resolve_allowed_tools,
    tool_result_text,
)

from .knowledge_base import DomainKnowledgeBase, DomainLiteral
from .schemas import (
    DomainInsight,
    DomainSpecialistTaskInput,
    DomainSpecialistTaskOutput,
    ResourceLink,
)


class DomainSpecialistService:
    """Encapsulates LLM prompting, knowledge lookups, and scoring logic."""

    def __init__(
        self,
        openai_api_key: Optional[str] = None,
        anthropic_api_key: Optional[str] = None,
        model: str = "gpt-4o-mini",
    ) -> None:
        self.openai_client = (
            AsyncOpenAI(api_key=openai_api_key) if openai_api_key else None
        )
        self.anthropic_client = (
            AsyncAnthropic(api_key=anthropic_api_key) if anthropic_api_key else None
        )
        self.model = model
        self.knowledge_base = DomainKnowledgeBase()

    async def process_task(
        self,
        input_data: DomainSpecialistTaskInput,
        *,
        db: Session | None = None,
        user: models.User | None = None,
    ) -> DomainSpecialistTaskOutput:
        """Main entry point for executing a domain-specific task."""

        start = time.time()
        domain: DomainLiteral = input_data.domain

        knowledge = await self.knowledge_base.search(
            domain=domain, query=input_data.query, context=input_data.context
        )
        playbook_steps = await self.knowledge_base.recommended_steps(
            domain, input_data.query
        )

        tool_ctx: ToolUseContext | None = None
        if db is not None and user is not None and isinstance(input_data.context, dict):
            placement = input_data.context.get("placement")
            thread_id = input_data.context.get("thread_id")
            allowed_tools = input_data.context.get("allowed_tools")

            if not isinstance(allowed_tools, list) or not all(
                isinstance(item, str) and item for item in allowed_tools
            ):
                allowed_tools = None

            if isinstance(placement, str) and placement:
                tool_ctx = ToolUseContext(
                    placement=placement,
                    thread_id=thread_id if isinstance(thread_id, str) else None,
                    allowed_tools=allowed_tools,
                )

        response = await self._generate_response(
            domain=domain,
            query=input_data.query,
            knowledge=knowledge,
            objectives=input_data.objectives,
            preferred_format=input_data.preferred_format,
            db=db,
            user=user,
            tool_ctx=tool_ctx,
        )

        insights = self._derive_insights(domain, input_data, knowledge)
        resources = [
            ResourceLink(title=doc["title"], url=doc["url"], type=doc.get("type"))
            for doc in knowledge[:3]
            if doc.get("url")
        ]
        domain_score = self._calculate_confidence(response, knowledge, insights)
        processing_time_ms = int((time.time() - start) * 1000)

        return DomainSpecialistTaskOutput(
            response=response,
            playbook_steps=playbook_steps,
            insights=insights,
            resources=resources,
            domain_score=domain_score,
            processing_time_ms=processing_time_ms,
        )

    async def _generate_response(
        self,
        domain: DomainLiteral,
        query: str,
        knowledge: List[Dict[str, str]],
        objectives: List[str],
        preferred_format: Optional[str],
        db: Session | None,
        user: models.User | None,
        tool_ctx: ToolUseContext | None,
    ) -> str:
        """Generate the domain-tailored response, optionally with tools."""

        system_prompt = (
            "You are the CapeAI Domain Specialist for the CapeControl platform. "
            "Provide actionable, concise guidance with audit-ready language."
        )
        domain_blurb = f"Domain focus: {domain.replace('_', ' ').title()}."
        objectives_section = (
            f"Objectives: {', '.join(objectives)}."
            if objectives
            else "Objectives: N/A."
        )
        knowledge_section = "\n".join(
            f"- {doc.get('title', 'Doc')}: {doc.get('snippet', '')}"
            for doc in knowledge
        )
        format_hint = f"Preferred format: {preferred_format or 'summary'}."

        user_prompt = (
            f"{domain_blurb}\n{objectives_section}\n{format_hint}\n\n"
            f"User query: {query}\n\nRelevant knowledge:\n{knowledge_section or '- None'}\n\n"
            "Craft an answer that includes deployment considerations, quick wins, and risk mitigations."
        )

        def _extract_first_text(blocks: Any) -> str:
            if not blocks:
                return ""
            for block in blocks:
                text = getattr(block, "text", None)
                if isinstance(text, str) and text.strip():
                    return text.strip()
            return ""

        try:
            tool_specs = None
            if db is not None and user is not None and tool_ctx is not None:
                tool_specs = resolve_allowed_tools(tool_ctx)

            if self.model.startswith("claude"):
                if not self.anthropic_client:
                    return "Anthropic API key not configured."

                messages: List[Dict[str, Any]] = [
                    {"role": "user", "content": user_prompt},
                ]
                tools_payload = (
                    anthropic_tools_payload(tool_specs) if tool_specs else None
                )

                for _ in range(3):
                    completion = await self.anthropic_client.messages.create(
                        model=self.model,
                        max_tokens=700,
                        temperature=0.6,
                        system=system_prompt,
                        messages=messages,
                        tools=tools_payload,
                    )

                    content = getattr(completion, "content", None)
                    tool_uses = [
                        block
                        for block in (content or [])
                        if getattr(block, "type", None) == "tool_use"
                    ]

                    if (
                        not tool_uses
                        or not tool_specs
                        or db is None
                        or user is None
                        or tool_ctx is None
                    ):
                        return _extract_first_text(content)

                    messages.append(
                        {
                            "role": "assistant",
                            "content": [
                                (
                                    block.model_dump()
                                    if hasattr(block, "model_dump")
                                    else {
                                        "type": getattr(block, "type", None),
                                        "id": getattr(block, "id", None),
                                        "name": getattr(block, "name", None),
                                        "input": getattr(block, "input", None),
                                        "text": getattr(block, "text", None),
                                    }
                                )
                                for block in (content or [])
                            ],
                        }
                    )

                    tool_results: List[Dict[str, Any]] = []
                    for block in tool_uses:
                        tool_name = getattr(block, "name", None)
                        tool_input = normalize_anthropic_tool_input(
                            getattr(block, "input", None)
                        )
                        tool_use_id = getattr(block, "id", None)

                        if not isinstance(tool_name, str) or not tool_name:
                            continue
                        if not isinstance(tool_use_id, str) or not tool_use_id:
                            continue

                        try:
                            tool_result = execute_tool(
                                db,
                                user=user,
                                ctx=tool_ctx,
                                tool_name=tool_name,
                                tool_payload=tool_input,
                            )
                            tool_results.append(
                                {
                                    "type": "tool_result",
                                    "tool_use_id": tool_use_id,
                                    "content": tool_result_text(tool_result["result"]),
                                }
                            )
                        except (RuntimeError, ValueError, TypeError, KeyError) as exc:
                            tool_results.append(
                                {
                                    "type": "tool_result",
                                    "tool_use_id": tool_use_id,
                                    "content": tool_result_text({"error": str(exc)}),
                                }
                            )

                    messages.append({"role": "user", "content": tool_results})

                return "Unable to complete tool-enabled response."

            if not self.openai_client:
                return "OpenAI API key not configured."

            messages: List[Dict[str, Any]] = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]
            tools_payload = openai_tools_payload(tool_specs) if tool_specs else None

            for _ in range(3):
                completion = await self.openai_client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=tools_payload,
                    temperature=0.6,
                    max_tokens=700,
                )

                message = completion.choices[0].message
                tool_calls = getattr(message, "tool_calls", None) or []
                if (
                    not tool_calls
                    or not tool_specs
                    or db is None
                    or user is None
                    or tool_ctx is None
                ):
                    content = getattr(message, "content", None)
                    return content.strip() if isinstance(content, str) else ""

                assistant_tool_calls: List[Dict[str, Any]] = []
                for call in tool_calls:
                    call_id = getattr(call, "id", None)
                    fn = getattr(call, "function", None)
                    fn_name = getattr(fn, "name", None)
                    fn_args = getattr(fn, "arguments", None)
                    if not isinstance(call_id, str) or not isinstance(fn_name, str):
                        continue
                    assistant_tool_calls.append(
                        {
                            "id": call_id,
                            "type": "function",
                            "function": {
                                "name": fn_name,
                                "arguments": (
                                    fn_args
                                    if isinstance(fn_args, str)
                                    else json.dumps(fn_args or {})
                                ),
                            },
                        }
                    )

                messages.append(
                    {
                        "role": "assistant",
                        "content": getattr(message, "content", "") or "",
                        "tool_calls": assistant_tool_calls,
                    }
                )

                for call in assistant_tool_calls:
                    tool_name = call["function"]["name"]
                    args = normalize_openai_tool_args(call["function"].get("arguments"))
                    try:
                        tool_result = execute_tool(
                            db,
                            user=user,
                            ctx=tool_ctx,
                            tool_name=tool_name,
                            tool_payload=args,
                        )
                        messages.append(
                            {
                                "role": "tool",
                                "tool_call_id": call["id"],
                                "content": tool_result_text(tool_result["result"]),
                            }
                        )
                    except (RuntimeError, ValueError, TypeError, KeyError) as exc:
                        messages.append(
                            {
                                "role": "tool",
                                "tool_call_id": call["id"],
                                "content": tool_result_text({"error": str(exc)}),
                            }
                        )

            return "Unable to complete tool-enabled response."

        except (
            AnthropicError,
            OpenAIError,
            RuntimeError,
            ValueError,
            TypeError,
            KeyError,
        ) as exc:  # pragma: no cover - external dependency
            return (
                "Unable to contact the LLM right now. "
                f"Fallback guidance for {domain}: emphasize guardrails, document dependencies, "
                f"and review the knowledge snippets below.\n\n{knowledge_section}\n\nError: {exc}"
            )

    def _derive_insights(
        self,
        domain: DomainLiteral,
        input_data: DomainSpecialistTaskInput,
        knowledge: List[Dict[str, str]],
    ) -> List[DomainInsight]:
        """Generate deterministic insight cards so UI can render chips."""

        insights: List[DomainInsight] = []
        query_lower = input_data.query.lower()

        if domain == "workflow_automation":
            if "rollback" not in query_lower:
                insights.append(
                    DomainInsight(
                        label="Rollback coverage",
                        detail="Define rollback hooks for each automation branch.",
                        severity="medium",
                    )
                )
            if "approval" not in query_lower:
                insights.append(
                    DomainInsight(
                        label="Approval gates",
                        detail="Consider adding human-in-the-loop gates for high-risk runs.",
                    )
                )
        elif domain == "data_analytics":
            insights.append(
                DomainInsight(
                    label="Semantic drift watch",
                    detail="Schedule metric audits to detect schema or definition drift.",
                    severity="low",
                )
            )
        elif domain == "security_audit":
            insights.append(
                DomainInsight(
                    label="Evidence freshness",
                    detail="Attach timestamps and owners to each control evidence artifact.",
                    severity="high",
                )
            )
        elif domain == "integration_helper":
            insights.append(
                DomainInsight(
                    label="Credential rotation",
                    detail="Ensure OAuth tokens rotate automatically and are scoped minimally.",
                    severity="medium",
                )
            )

        if knowledge:
            insights.append(
                DomainInsight(
                    label="Related doc",
                    detail=f"Consider '{knowledge[0].get('title', 'documentation')}' for additional context.",
                )
            )

        return insights[:4]

    def _calculate_confidence(
        self,
        response: str,
        knowledge: List[Dict[str, str]],
        insights: List[DomainInsight],
    ) -> float:
        """Heuristic confidence score derived from available signals."""

        score = 0.4
        if len(response) > 200:
            score += 0.2
        if knowledge:
            score += 0.2
        if len(insights) >= 2:
            score += 0.1

        return min(score, 0.98)
