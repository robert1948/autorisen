"""
Customer Agent Knowledge Base

In-memory knowledge base with workflow templates, industry-specific
recommendations, and customer support knowledge.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class WorkflowTemplate:
    """A reusable workflow template."""

    id: str
    name: str
    description: str
    industry: str  # "all", "finance", "energy", "legal", "healthcare", "retail"
    complexity: str  # "simple", "moderate", "advanced"
    setup_time: str
    agents: List[str]
    steps: List[str]


@dataclass
class KnowledgeDocument:
    """A knowledge base document."""

    id: str
    title: str
    content: str
    category: str
    tags: List[str] = field(default_factory=list)
    relevance_score: float = 1.0


WORKFLOW_TEMPLATES = [
    WorkflowTemplate(
        id="invoice-processing",
        name="Invoice Processing Pipeline",
        description="Automatically extract data from invoices, validate against POs, and route for approval",
        industry="finance",
        complexity="moderate",
        setup_time="30 minutes",
        agents=["data-analyst", "finance-agent"],
        steps=[
            "Connect document source (email, upload, or API)",
            "Configure data extraction rules",
            "Set up validation against purchase orders",
            "Define approval routing rules",
            "Enable notifications and reporting",
        ],
    ),
    WorkflowTemplate(
        id="energy-monitoring",
        name="Energy Usage Monitor",
        description="Track energy consumption in real-time, detect anomalies, and generate savings recommendations",
        industry="energy",
        complexity="moderate",
        setup_time="45 minutes",
        agents=["energy-agent", "data-analyst"],
        steps=[
            "Connect smart meter or energy data source",
            "Configure baseline consumption thresholds",
            "Set up anomaly detection alerts",
            "Enable weekly usage reports",
            "Configure cost optimization recommendations",
        ],
    ),
    WorkflowTemplate(
        id="customer-support-bot",
        name="AI Customer Support Bot",
        description="Intelligent chatbot that handles common inquiries, routes complex issues, and learns from interactions",
        industry="all",
        complexity="simple",
        setup_time="15 minutes",
        agents=["cape-ai-guide", "cape-support-bot"],
        steps=[
            "Import your FAQ knowledge base",
            "Configure response tone and style",
            "Set up escalation rules for complex queries",
            "Enable conversation analytics",
            "Deploy to your website or app",
        ],
    ),
    WorkflowTemplate(
        id="content-generation",
        name="Content Generation Pipeline",
        description="Generate, review, and publish content across channels with AI assistance",
        industry="all",
        complexity="moderate",
        setup_time="20 minutes",
        agents=["content-agent", "cape-ai-guide"],
        steps=[
            "Define content templates and brand guidelines",
            "Set up content calendar and topics",
            "Configure AI generation parameters",
            "Add review and approval workflow",
            "Connect publishing channels",
        ],
    ),
    WorkflowTemplate(
        id="data-analytics",
        name="Automated Data Analytics",
        description="Collect, analyze, and visualize business data with automated insights",
        industry="all",
        complexity="advanced",
        setup_time="60 minutes",
        agents=["data-analyst", "cape-ai-domain-specialist"],
        steps=[
            "Connect data sources (databases, APIs, spreadsheets)",
            "Define key metrics and KPIs",
            "Configure automated analysis schedules",
            "Set up dashboard and reporting templates",
            "Enable anomaly alerts and trend notifications",
        ],
    ),
    WorkflowTemplate(
        id="compliance-checker",
        name="Compliance & Audit Checker",
        description="Automated compliance monitoring with audit trail and reporting",
        industry="finance",
        complexity="advanced",
        setup_time="90 minutes",
        agents=["finance-agent", "cape-ai-domain-specialist"],
        steps=[
            "Define compliance rules and regulations",
            "Connect data sources for monitoring",
            "Set up automated compliance checks",
            "Configure audit trail and logging",
            "Enable compliance reporting and alerts",
        ],
    ),
]


KNOWLEDGE_DOCUMENTS = [
    KnowledgeDocument(
        id="getting-started",
        title="Getting Started with CapeControl",
        content="CapeControl helps you deploy AI agents that automate tasks across your business. "
        "Start by exploring the Agent Marketplace, then customize agents for your specific needs. "
        "The platform supports finance, energy, legal, healthcare, and retail industries.",
        category="onboarding",
        tags=["start", "setup", "beginner", "introduction"],
    ),
    KnowledgeDocument(
        id="workflow-basics",
        title="Understanding Workflows",
        content="Workflows connect multiple AI agents to accomplish complex tasks. "
        "Each workflow has triggers (what starts it), actions (what agents do), "
        "and conditions (rules that control flow). You can create workflows visually "
        "or use pre-built templates from the marketplace.",
        category="workflows",
        tags=["workflow", "automation", "triggers", "actions"],
    ),
    KnowledgeDocument(
        id="plan-comparison",
        title="Choosing the Right Plan",
        content="Free plan: 5 agents, 100 executions/month, basic integrations. "
        "Pro plan: 50 agents, 2500 executions/month, all integrations, priority support. "
        "Enterprise: unlimited agents, custom integrations, dedicated support, SLA guarantees. "
        "All plans include access to the Agent Marketplace and community support.",
        category="billing",
        tags=["plan", "pricing", "subscription", "upgrade", "billing"],
    ),
    KnowledgeDocument(
        id="agent-types",
        title="Available AI Agent Types",
        content="CapeControl offers several types of AI agents: "
        "CapeAI Guide for platform assistance, Domain Specialist for industry-specific advice, "
        "Customer Agent for support automation, Dev Agent for developer workflows, "
        "Finance Agent for financial analysis, Energy Agent for energy monitoring, "
        "and Content Agent for content generation. Each agent can be customized and combined into workflows.",
        category="agents",
        tags=["agent", "types", "AI", "automation", "capabilities"],
    ),
]


class CustomerKnowledgeBase:
    """Knowledge base for the Customer Agent."""

    def __init__(self):
        self.templates = {t.id: t for t in WORKFLOW_TEMPLATES}
        self.documents = {d.id: d for d in KNOWLEDGE_DOCUMENTS}

    async def search(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None,
        limit: int = 5,
    ) -> List[KnowledgeDocument]:
        """Search knowledge base using keyword matching with context boosting."""
        query_lower = query.lower()
        scored: List[tuple[float, KnowledgeDocument]] = []

        for doc in KNOWLEDGE_DOCUMENTS:
            score = 0.0
            words = query_lower.split()

            for word in words:
                if word in doc.title.lower():
                    score += 2.0
                if word in doc.content.lower():
                    score += 1.0
                if word in [t.lower() for t in doc.tags]:
                    score += 1.5

            # Context boost
            if context:
                industry = context.get("industry", "")
                if isinstance(industry, str) and industry.lower() in doc.content.lower():
                    score += 1.0

            if score > 0:
                scored.append((score, doc))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [doc for _, doc in scored[:limit]]

    def suggest_workflows(
        self,
        query: str,
        industry: Optional[str] = None,
        limit: int = 3,
    ) -> List[WorkflowTemplate]:
        """Suggest workflow templates based on query and industry."""
        query_lower = query.lower()
        scored: List[tuple[float, WorkflowTemplate]] = []

        for template in WORKFLOW_TEMPLATES:
            score = 0.0

            # Check query relevance
            for word in query_lower.split():
                if word in template.name.lower():
                    score += 2.0
                if word in template.description.lower():
                    score += 1.0
                if word in template.industry.lower():
                    score += 1.5

            # Industry match boost
            if industry:
                if template.industry == industry or template.industry == "all":
                    score += 2.0

            if score > 0 or (industry and (template.industry == industry or template.industry == "all")):
                scored.append((max(score, 0.5), template))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [t for _, t in scored[:limit]]
