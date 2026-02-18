"""
Dev Agent Knowledge Base

In-memory knowledge base with agent development documentation,
code templates, best practices, and API reference.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class DevDocument:
    """A development documentation entry."""

    id: str
    title: str
    content: str
    category: str  # "architecture", "api", "tools", "testing", "publishing", "best_practices"
    code_example: str | None = None
    tags: List[str] = field(default_factory=list)


DEV_DOCUMENTS = [
    DevDocument(
        id="agent-structure",
        title="Agent Module Structure",
        content="Every CapeControl agent follows a standard module structure: "
        "__init__.py (exports), router.py (FastAPI endpoints), schemas.py (Pydantic models), "
        "service.py (business logic), and optionally knowledge_base.py (domain knowledge). "
        "Place your agent in backend/src/modules/agents/your_agent_name/.",
        category="architecture",
        code_example=(
            "# backend/src/modules/agents/my_agent/\n"
            "#   __init__.py\n"
            "#   router.py\n"
            "#   schemas.py\n"
            "#   service.py\n"
            "#   knowledge_base.py  (optional)\n"
        ),
        tags=["structure", "module", "architecture", "getting-started"],
    ),
    DevDocument(
        id="router-pattern",
        title="Creating Agent Routers",
        content="Agent routers use FastAPI's APIRouter with a prefix matching your agent slug. "
        "Include /ask (POST), /health (GET), and /capabilities (GET) endpoints. "
        "The router is auto-discovered by the app factory's safe import mechanism.",
        category="api",
        code_example=(
            'router = APIRouter(prefix="/my-agent", tags=["My Agent"])\n\n'
            '@router.post("/ask", response_model=MyAgentOutput)\n'
            'async def ask(input_data: MyAgentInput, db=Depends(get_session)):\n'
            "    service = get_my_agent_service()\n"
            "    return await service.process_query(input_data, db=db)\n"
        ),
        tags=["router", "api", "endpoints", "fastapi"],
    ),
    DevDocument(
        id="tool-use",
        title="Adding Tool Calling to Agents",
        content="CapeControl supports tool/function calling for both OpenAI and Anthropic models. "
        "Use the shared tool_use module (backend/src/modules/agents/tool_use.py) to resolve "
        "allowed tools, format payloads, and execute tool calls. The multi-turn tool loop "
        "supports up to 3 iterations.",
        category="tools",
        code_example=(
            "from backend.src.modules.agents.tool_use import (\n"
            "    ToolUseContext, resolve_allowed_tools, execute_tool\n"
            ")\n\n"
            "tool_ctx = ToolUseContext(placement='my-agent', thread_id=None)\n"
            "tools = resolve_allowed_tools(tool_ctx)\n"
        ),
        tags=["tools", "function-calling", "tool-use", "anthropic", "openai"],
    ),
    DevDocument(
        id="testing-agents",
        title="Testing Your Agent",
        content="Use pytest with the test database for agent testing. Create fixtures in "
        "tests_enabled/. Test the service layer directly and the router via TestClient. "
        "Run 'make codex-test' for CI-safe testing with database isolation.",
        category="testing",
        code_example=(
            "import pytest\n"
            "from httpx import AsyncClient\n\n"
            "async def test_agent_ask(client: AsyncClient, auth_headers):\n"
            '    resp = await client.post("/api/agents/my-agent/ask",\n'
            '        json={"query": "Hello"}, headers=auth_headers)\n'
            "    assert resp.status_code == 200\n"
            '    assert "response" in resp.json()\n'
        ),
        tags=["testing", "pytest", "test", "quality"],
    ),
    DevDocument(
        id="publishing-agents",
        title="Publishing Agents to the Marketplace",
        content="To publish your agent: 1) Create an agent record via POST /api/agents, "
        "2) Create a version with manifest via POST /api/agents/{id}/versions, "
        "3) Publish the version via POST /api/agents/{id}/versions/{vid}/publish. "
        "The manifest must include name, description, placement, and tools keys.",
        category="publishing",
        code_example=(
            "# Manifest schema\n"
            "manifest = {\n"
            '    "name": "My Agent",\n'
            '    "description": "Does amazing things",\n'
            '    "placement": "sidebar",\n'
            '    "tools": ["search", "analyze"],\n'
            '    "config": {"model": "claude-3-5-haiku-20241022"}\n'
            "}\n"
        ),
        tags=["publish", "marketplace", "version", "manifest"],
    ),
    DevDocument(
        id="llm-integration",
        title="LLM Provider Integration",
        content="CapeControl supports Anthropic (Claude 3.5 Haiku default) and OpenAI (GPT-4 family). "
        "Use AsyncAnthropic or AsyncOpenAI clients. Always implement fallback logic: "
        "try Anthropic first, then fallback to OpenAI. Set model via environment variables "
        "for easy configuration per deployment.",
        category="best_practices",
        code_example=(
            "from anthropic import AsyncAnthropic\n"
            "from openai import AsyncOpenAI\n\n"
            "# Prefer Anthropic, fallback to OpenAI\n"
            "try:\n"
            "    response = await anthropic_client.messages.create(...)\n"
            "except Exception:\n"
            "    response = await openai_client.chat.completions.create(...)\n"
        ),
        tags=["llm", "anthropic", "openai", "claude", "gpt", "integration"],
    ),
    DevDocument(
        id="error-handling",
        title="Error Handling Best Practices",
        content="Always return graceful fallback responses when LLM calls fail. "
        "Log errors with appropriate severity. Use try/except around all external API calls. "
        "Return a confidence_score reflecting response quality. Never expose internal "
        "error details to end users.",
        category="best_practices",
        tags=["errors", "handling", "fallback", "logging", "best-practices"],
    ),
    DevDocument(
        id="revenue-sharing",
        title="Developer Revenue Sharing",
        content="Published agents can earn revenue through the subscription model. "
        "Developers receive a percentage of net revenue from agent subscriptions. "
        "Track usage and earnings via the developer dashboard. Payouts are processed "
        "monthly within 30 days of invoice approval.",
        category="publishing",
        tags=["revenue", "earnings", "monetization", "developer"],
    ),
]


class DevKnowledgeBase:
    """Knowledge base for the Dev Agent."""

    def __init__(self):
        self.documents = {d.id: d for d in DEV_DOCUMENTS}

    async def search(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None,
        limit: int = 5,
    ) -> List[DevDocument]:
        """Search developer documentation."""
        query_lower = query.lower()
        scored: List[tuple[float, DevDocument]] = []

        for doc in DEV_DOCUMENTS:
            score = 0.0

            for word in query_lower.split():
                if len(word) < 3:
                    continue
                if word in doc.title.lower():
                    score += 2.0
                if word in doc.content.lower():
                    score += 1.0
                if word in [t.lower() for t in doc.tags]:
                    score += 1.5

            # Boost by task type context
            if context:
                task_type = context.get("task_type", "")
                if isinstance(task_type, str) and task_type in doc.category:
                    score += 1.5

            if score > 0:
                scored.append((score, doc))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [doc for _, doc in scored[:limit]]
