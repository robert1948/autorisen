"""
Dev Agent Service

Core business logic for the Dev Agent including LLM integration,
code generation, debugging assistance, and agent building guidance.
"""

import time
import logging
from typing import Any, Dict, List, Optional

from anthropic import AsyncAnthropic
from openai import AsyncOpenAI
from sqlalchemy.orm import Session

from backend.src.db import models

from .schemas import DevAgentTaskInput, DevAgentTaskOutput, CodeSuggestion
from .knowledge_base import DevKnowledgeBase

log = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are the CapeControl Dev Agent — an expert AI assistant for developers \
building and deploying AI agents on the CapeControl platform.

Your expertise covers:
1. **Agent Architecture**: Module structure, router patterns, schemas, services
2. **LLM Integration**: Anthropic Claude and OpenAI GPT model integration
3. **Tool Calling**: Function calling, tool definitions, multi-turn tool loops
4. **Testing**: pytest patterns, fixtures, test database isolation
5. **Publishing**: Agent versioning, manifests, marketplace publishing
6. **Best Practices**: Error handling, fallbacks, security, performance

Communication style:
- Be precise, technical, and code-focused
- Always include working code examples
- Explain design decisions and trade-offs
- Reference CapeControl-specific patterns and conventions
- Include relevant documentation links

When providing code:
- Use Python for backend, TypeScript for frontend
- Follow the existing codebase conventions
- Include type hints and docstrings
- Show complete, runnable examples when possible"""

USER_PROMPT_TEMPLATE = """Developer Query: {query}

Task Type: {task_type}
Agent Being Developed: {agent_slug}

{code_context}

Relevant Documentation:
{knowledge}

Please provide a comprehensive response with:
1. Clear explanation of the solution
2. Working code examples
3. Best practices to follow
4. Next steps for implementation"""


class DevAgentService:
    """Service class for Dev Agent operations."""

    def __init__(
        self,
        openai_api_key: Optional[str] = None,
        anthropic_api_key: Optional[str] = None,
        model: str = "claude-3-5-haiku-20241022",
    ):
        self.openai_client = (
            AsyncOpenAI(api_key=openai_api_key) if openai_api_key else None
        )
        self.anthropic_client = (
            AsyncAnthropic(api_key=anthropic_api_key) if anthropic_api_key else None
        )
        self.model = model
        self.knowledge_base = DevKnowledgeBase()

    async def process_query(
        self,
        input_data: DevAgentTaskInput,
        *,
        db: Session | None = None,
        user: models.User | None = None,
    ) -> DevAgentTaskOutput:
        """Process a developer query and generate a helpful response."""
        start_time = time.time()

        try:
            # Search knowledge base
            context = input_data.context or {}
            context["task_type"] = input_data.task_type
            relevant_docs = await self.knowledge_base.search(
                query=input_data.query, context=context, limit=4
            )

            # Build knowledge context
            knowledge_text = "\n".join(
                f"- {doc.title}: {doc.content}" for doc in relevant_docs
            ) or "No specific documentation found."

            code_context = ""
            if input_data.code_snippet:
                code_context = f"Developer's Code:\n```\n{input_data.code_snippet}\n```\n"

            user_prompt = USER_PROMPT_TEMPLATE.format(
                query=input_data.query,
                task_type=input_data.task_type or "general",
                agent_slug=input_data.agent_slug or "not specified",
                code_context=code_context,
                knowledge=knowledge_text,
            )

            # Generate AI response
            ai_response = await self._call_llm(user_prompt)

            # Build code suggestions from matching docs
            code_suggestions = [
                CodeSuggestion(
                    title=doc.title,
                    code=doc.code_example,
                    language="python",
                    explanation=doc.content[:200],
                )
                for doc in relevant_docs
                if doc.code_example
            ]

            # Extract best practices
            best_practices = self._get_best_practices(input_data.task_type)

            # Build doc links
            doc_links = [
                {"title": doc.title, "url": f"/docs/agents/{doc.id}"}
                for doc in relevant_docs
            ]

            # Next steps
            next_steps = self._get_next_steps(input_data.task_type)

            processing_time = int((time.time() - start_time) * 1000)

            return DevAgentTaskOutput(
                response=ai_response,
                code_suggestions=code_suggestions,
                best_practices=best_practices,
                documentation_links=doc_links,
                next_steps=next_steps,
                confidence_score=self._calculate_confidence(relevant_docs, ai_response),
                processing_time_ms=processing_time,
            )

        except Exception as e:
            log.error("DevAgent error: %s", e)
            processing_time = int((time.time() - start_time) * 1000)
            return DevAgentTaskOutput(
                response=(
                    "I can help you with that! Here's what I'd recommend based on the "
                    "CapeControl agent development patterns. Check the documentation "
                    "links below for more details."
                ),
                code_suggestions=[],
                best_practices=self._get_best_practices("general"),
                documentation_links=[
                    {"title": "Agent Development Guide", "url": "/docs/agents/getting-started"},
                ],
                next_steps=["Review the agent module structure documentation"],
                confidence_score=0.3,
                processing_time_ms=processing_time,
            )

    async def _call_llm(self, user_prompt: str) -> str:
        """Call the LLM provider."""
        if self.anthropic_client and "claude" in self.model:
            try:
                response = await self.anthropic_client.messages.create(
                    model=self.model,
                    max_tokens=2048,
                    system=SYSTEM_PROMPT,
                    messages=[{"role": "user", "content": user_prompt}],
                )
                return response.content[0].text
            except Exception as e:
                log.warning("Anthropic call failed: %s", e)

        if self.openai_client:
            try:
                response = await self.openai_client.chat.completions.create(
                    model="gpt-4o-mini" if "claude" in self.model else self.model,
                    max_tokens=2048,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt},
                    ],
                )
                return response.choices[0].message.content or ""
            except Exception as e:
                log.error("OpenAI call also failed: %s", e)

        return (
            "Based on CapeControl's agent development patterns, I'd recommend following "
            "the standard module structure with router.py, schemas.py, and service.py. "
            "Check the documentation for detailed examples and code templates."
        )

    def _get_best_practices(self, task_type: Optional[str]) -> List[str]:
        """Get relevant best practices for the task type."""
        common = [
            "Always implement graceful error handling with fallback responses",
            "Include type hints and docstrings in all functions",
            "Use the safe import pattern for router registration",
        ]

        specific = {
            "build": [
                "Follow the standard agent module structure (router, schemas, service)",
                "Use Pydantic models for input validation and output serialization",
            ],
            "test": [
                "Use pytest fixtures for database and auth setup",
                "Test both success and error paths",
            ],
            "debug": [
                "Check logs with appropriate severity levels",
                "Verify API key configuration and model availability",
            ],
            "publish": [
                "Include a complete manifest with name, description, placement, and tools",
                "Test thoroughly before publishing to the marketplace",
            ],
            "optimize": [
                "Cache frequently used knowledge base queries",
                "Set appropriate max_tokens limits for each use case",
            ],
        }

        return common + specific.get(task_type or "general", [])

    def _get_next_steps(self, task_type: Optional[str]) -> List[str]:
        """Get next steps based on task type."""
        steps_map = {
            "build": [
                "Create the module directory structure",
                "Define your Pydantic schemas",
                "Implement the service logic",
                "Register the router in the agents module",
            ],
            "test": [
                "Run existing tests with 'make codex-test'",
                "Add new test cases for edge scenarios",
                "Verify test database isolation",
            ],
            "debug": [
                "Check the application logs",
                "Verify environment configuration",
                "Test the endpoint with curl or httpx",
            ],
            "publish": [
                "Create the agent record via API",
                "Prepare the version manifest",
                "Submit for marketplace review",
            ],
            "general": [
                "Explore the agent development documentation",
                "Try building a simple agent using the template",
                "Test in the Agent Workbench sandbox",
            ],
        }
        return steps_map.get(task_type or "general", steps_map["general"])

    def _calculate_confidence(self, docs: list, response: str) -> float:
        """Calculate confidence score."""
        score = 0.4
        if docs:
            score += min(len(docs) * 0.1, 0.3)
        if len(response) > 300:
            score += 0.1
        if len(response) > 600:
            score += 0.1
        return min(score, 1.0)
