"""
CapeAI Guide Agent Service

Core business logic for the CapeAI Guide agent including OpenAI integration,
knowledge base searching, and response generation.
"""

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

from .schemas import CapeAIGuideTaskInput, CapeAIGuideTaskOutput, ResourceLink
from .knowledge_base import KnowledgeBase
from .prompts import PromptTemplates


class CapeAIGuideService:
    """Service class for CapeAI Guide agent operations."""

    def __init__(
        self,
        openai_api_key: Optional[str] = None,
        anthropic_api_key: Optional[str] = None,
        model: str = "gpt-4",
    ):
        """Initialize the CapeAI Guide service."""
        self.openai_client = (
            AsyncOpenAI(api_key=openai_api_key) if openai_api_key else None
        )
        self.anthropic_client = (
            AsyncAnthropic(api_key=anthropic_api_key) if anthropic_api_key else None
        )
        self.model = model
        self.knowledge_base = KnowledgeBase()
        self.prompts = PromptTemplates()

    async def process_query(
        self,
        input_data: CapeAIGuideTaskInput,
        *,
        db: Session | None = None,
        user: models.User | None = None,
    ) -> CapeAIGuideTaskOutput:
        """Process a user query and generate a helpful response."""
        start_time = time.time()

        try:
            # Step 1: Analyze context and extract key information
            context_analysis = await self._analyze_context(input_data)

            # Step 2: Search knowledge base for relevant information
            relevant_docs = await self.knowledge_base.search(
                query=input_data.query, context=input_data.context, limit=5
            )

            # Step 3: Generate AI response using OpenAI
            tool_ctx: ToolUseContext | None = None
            if db is not None and user is not None:
                context_payload = input_data.context or {}
                placement = context_payload.get("placement")
                thread_id = context_payload.get("thread_id")
                allowed_tools = context_payload.get("allowed_tools")

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
            ai_response = await self._generate_ai_response(
                query=input_data.query,
                context=context_analysis,
                knowledge=relevant_docs,
                user_level=input_data.user_level,
                preferred_format=input_data.preferred_format,
                db=db,
                user=user,
                tool_ctx=tool_ctx,
            )

            # Step 4: Extract suggestions and format response
            suggestions = await self._extract_suggestions(ai_response, input_data)

            # Step 5: Find relevant resources
            resources = await self._find_resources(input_data.query, relevant_docs)

            # Step 6: Calculate confidence score
            confidence = self._calculate_confidence(ai_response, relevant_docs)
            processing_time = int((time.time() - start_time) * 1000)

            return CapeAIGuideTaskOutput(
                response=ai_response,
                suggestions=suggestions,
                resources=resources,
                confidence_score=confidence,
                processing_time_ms=processing_time,
            )

        except (
            AnthropicError,
            OpenAIError,
            RuntimeError,
            ValueError,
            TypeError,
            KeyError,
        ) as e:
            # Fallback response for errors
            processing_time = int((time.time() - start_time) * 1000)
            return CapeAIGuideTaskOutput(
                response=f"I apologize, but I'm having trouble processing your request right now. Please try again or contact support if the issue persists. Error: {str(e)}",
                suggestions=[
                    "Try rephrasing your question",
                    "Check the help documentation",
                    "Contact support",
                ],
                resources=[],
                confidence_score=0.1,
                processing_time_ms=processing_time,
            )

    async def _analyze_context(
        self, input_data: CapeAIGuideTaskInput
    ) -> Dict[str, Any]:
        """Analyze user context to understand their current situation."""
        context = input_data.context or {}

        return {
            "current_page": context.get("current_page", "unknown"),
            "user_role": context.get("user_role", "user"),
            "features_used": context.get("features_used", []),
            "query_intent": await self._classify_query_intent(input_data.query),
            "user_level": input_data.user_level,
            "preferred_format": input_data.preferred_format,
        }

    async def _classify_query_intent(self, query: str) -> str:
        """Classify the user's query intent (navigation, troubleshooting, learning, etc.)."""
        query_lower = query.lower()

        if any(
            word in query_lower for word in ["how to", "how do", "setup", "configure"]
        ):
            return "how_to"
        elif any(
            word in query_lower for word in ["error", "problem", "not working", "issue"]
        ):
            return "troubleshooting"
        elif any(word in query_lower for word in ["where", "find", "locate"]):
            return "navigation"
        elif any(word in query_lower for word in ["what is", "explain", "understand"]):
            return "learning"
        else:
            return "general"

    async def _generate_ai_response(
        self,
        query: str,
        context: Dict[str, Any],
        knowledge: List[Dict[str, Any]],
        user_level: Optional[str],
        preferred_format: Optional[str],
        db: Session | None,
        user: models.User | None,
        tool_ctx: ToolUseContext | None,
    ) -> str:
        """Generate AI response using OpenAI/Anthropic, optionally with tools."""

        system_prompt = self.prompts.get_system_prompt(user_level, preferred_format)
        user_prompt = self.prompts.get_user_prompt(query, context, knowledge)

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
                    response = await self.anthropic_client.messages.create(
                        model=self.model,
                        max_tokens=1000,
                        temperature=0.7,
                        system=system_prompt,
                        messages=messages,
                        tools=tools_payload,
                    )

                    content = getattr(response, "content", None)
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

                    # Preserve assistant blocks (including tool_use) in the conversation.
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
                response = await self.openai_client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=tools_payload,
                    max_tokens=1000,
                    temperature=0.7,
                )

                message = response.choices[0].message
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
        ) as e:
            return (
                "I'm having trouble generating a response right now. "
                f"Please try again. (Error: {str(e)})"
            )

    async def _extract_suggestions(
        self, _ai_response: str, input_data: CapeAIGuideTaskInput
    ) -> List[str]:
        """Extract relevant suggestions based on the query and response."""

        suggestions = []
        query_lower = input_data.query.lower()

        # Intent-based suggestions
        if "workflow" in query_lower:
            suggestions.extend(
                [
                    "Learn about workflow triggers",
                    "Explore automation templates",
                    "Set up workflow notifications",
                ]
            )
        elif "dashboard" in query_lower:
            suggestions.extend(
                [
                    "Customize your dashboard layout",
                    "Add new dashboard widgets",
                    "Export dashboard data",
                ]
            )
        elif "integration" in query_lower:
            suggestions.extend(
                [
                    "Check our API documentation",
                    "Explore webhook configurations",
                    "Review security settings",
                ]
            )

        # General helpful suggestions
        suggestions.extend(
            [
                "Check out our video tutorials",
                "Join our community forum",
                "Schedule a demo with our team",
            ]
        )

        return suggestions[:3]  # Limit to top 3 suggestions

    async def _find_resources(
        self, query: str, relevant_docs: List[Dict[str, Any]]
    ) -> List[ResourceLink]:
        """Find relevant resource links based on query and documentation."""

        resources = []

        # Add resources from knowledge base
        for doc in relevant_docs[:3]:  # Limit to top 3
            if doc.get("url"):
                resources.append(
                    ResourceLink(
                        title=doc.get("title", "Documentation"),
                        url=doc["url"],
                        type=doc.get("type", "doc"),
                    )
                )

        # Add common helpful resources
        query_lower = query.lower()
        if "api" in query_lower or "integration" in query_lower:
            resources.append(
                ResourceLink(title="API Documentation", url="/docs/api", type="doc")
            )

        if "workflow" in query_lower or "automation" in query_lower:
            resources.append(
                ResourceLink(
                    title="Workflow Tutorial Series",
                    url="/tutorials/workflows",
                    type="tutorial",
                )
            )

        return resources[:5]  # Limit to top 5 resources

    def _calculate_confidence(
        self, ai_response: str, relevant_docs: List[Dict[str, Any]]
    ) -> float:
        """Calculate confidence score based on response quality and knowledge match."""

        base_confidence = 0.7

        # Increase confidence if we have relevant documentation
        if relevant_docs:
            base_confidence += min(0.2, len(relevant_docs) * 0.05)

        # Decrease confidence for error responses
        if "error" in ai_response.lower() or "trouble" in ai_response.lower():
            base_confidence -= 0.3

        # Increase confidence for detailed responses
        if len(ai_response) > 200:
            base_confidence += 0.1

        return max(0.1, min(1.0, base_confidence))
