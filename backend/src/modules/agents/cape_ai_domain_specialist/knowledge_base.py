"""
Domain-specific knowledge base for the CapeAI Domain Specialist agent.

Provides lightweight, asynchronous helpers for retrieving curated guidance that
can be injected into prompt construction without hitting the external
documentation stack. This mirrors the CapeAI Guide knowledge base but adds
domain scoping for Workflow Automation, Data Analytics, Security Audit, and
Integration Helper personas.
"""

from __future__ import annotations

import asyncio
from typing import Any, Dict, List, Literal, Optional

DomainLiteral = Literal[
    "workflow_automation", "data_analytics", "security_audit", "integration_helper"
]


class DomainKnowledgeBase:
    """In-memory domain knowledge used to augment LLM responses."""

    def __init__(self) -> None:
        self._documents: Dict[DomainLiteral, List[Dict[str, Any]]] = {
            "workflow_automation": [
                {
                    "id": "wf-blueprints",
                    "title": "Reusable Workflow Blueprints",
                    "url": "/docs/automation/blueprints",
                    "type": "playbook",
                    "keywords": ["trigger", "action", "workflow", "blueprint"],
                    "snippet": "Blueprints define reusable trigger-action combinations with guardrails.",
                },
                {
                    "id": "wf-observability",
                    "title": "Monitoring Automation Pipelines",
                    "url": "/docs/automation/observability",
                    "type": "doc",
                    "keywords": ["metrics", "monitor", "alert"],
                    "snippet": "Use run-level metrics and alerting policies to detect stuck automations.",
                },
            ],
            "data_analytics": [
                {
                    "id": "da-metrics-layer",
                    "title": "Authoring Metrics in the Analytics Layer",
                    "url": "/docs/analytics/metrics-layer",
                    "type": "doc",
                    "keywords": ["metrics", "semantic", "analytics"],
                    "snippet": "Define semantic metrics once and share across dashboards and notebooks.",
                },
                {
                    "id": "da-query-optimizer",
                    "title": "Optimizing Warehouse Queries",
                    "url": "/docs/analytics/query-optimizer",
                    "type": "guide",
                    "keywords": ["warehouse", "performance", "sql"],
                    "snippet": "Leverage persisted models and predicate pushdown to reduce latency.",
                },
            ],
            "security_audit": [
                {
                    "id": "sec-controls",
                    "title": "Security Control Checklist",
                    "url": "/docs/security/audit-checklist",
                    "type": "checklist",
                    "keywords": ["control", "audit", "compliance"],
                    "snippet": "Ensure MFA, least-privilege roles, logging, and vendor attestations are enabled.",
                },
                {
                    "id": "sec-findings",
                    "title": "Documenting Audit Findings",
                    "url": "/docs/security/findings",
                    "type": "doc",
                    "keywords": ["finding", "severity", "remediation"],
                    "snippet": "Classify findings by severity and attach remediation owners and due dates.",
                },
            ],
            "integration_helper": [
                {
                    "id": "int-webhooks",
                    "title": "Webhook Orchestration Guide",
                    "url": "/docs/integrations/webhooks",
                    "type": "doc",
                    "keywords": ["webhook", "retry", "payload"],
                    "snippet": "Validate signatures and implement exponential backoff on non-2xx responses.",
                },
                {
                    "id": "int-sdks",
                    "title": "SDK Authentication Patterns",
                    "url": "/docs/integrations/sdks",
                    "type": "tutorial",
                    "keywords": ["sdk", "oauth", "token"],
                    "snippet": "Use short-lived OAuth tokens with automatic rotation for partner APIs.",
                },
            ],
        }

        self._capability_map: Dict[DomainLiteral, List[str]] = {
            "workflow_automation": [
                "trigger design",
                "conditional routing",
                "runbooks",
                "observability",
            ],
            "data_analytics": [
                "metrics modeling",
                "dataset governance",
                "visualization tuning",
                "pipeline SLAs",
            ],
            "security_audit": [
                "control validation",
                "evidence collection",
                "risk scoring",
                "remediation planning",
            ],
            "integration_helper": [
                "API onboarding",
                "webhook hygiene",
                "auth patterns",
                "runtime troubleshooting",
            ],
        }

    async def search(
        self,
        domain: DomainLiteral,
        query: str,
        context: Optional[Dict[str, Any]] = None,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """Return domain-filtered documents ranked by rudimentary keyword scoring."""

        await asyncio.sleep(0.05)  # simulate IO latency
        documents = self._documents[domain]
        query_terms = query.lower().split()
        results: List[Dict[str, Any]] = []

        for doc in documents:
            score = sum(0.3 for term in query_terms if term in doc["keywords"])
            if context:
                current_stage = (context or {}).get("stage", "")
                if current_stage and current_stage.lower() in doc["snippet"].lower():
                    score += 0.2
            if score > 0:
                enriched = doc.copy()
                enriched["search_score"] = score
                results.append(enriched)

        results.sort(key=lambda item: item["search_score"], reverse=True)
        return results[:limit]

    async def get_domain_summary(self, domain: DomainLiteral) -> Dict[str, Any]:
        """Return a short descriptor and the core capabilities for the requested domain."""

        await asyncio.sleep(0)  # keep signature async for parity
        return {
            "domain": domain,
            "focus": self._capability_map[domain],
            "playbook_count": len(self._documents[domain]),
        }

    async def recommended_steps(
        self, domain: DomainLiteral, query: str
    ) -> List[str]:
        """Generate deterministic suggested steps based on domain heuristics."""

        await asyncio.sleep(0)
        base_map = {
            "workflow_automation": [
                "Confirm trigger, conditions, and action catalog alignment",
                "Simulate the workflow with sample data",
                "Enable run monitoring and configure rollback hooks",
            ],
            "data_analytics": [
                "Validate metric definitions against semantic layer",
                "Profile source datasets for freshness and null drift",
                "Publish dashboards with owner and SLA metadata",
            ],
            "security_audit": [
                "Collect evidence for each high-priority control",
                "Assign remediation owners with due dates",
                "Log findings in the compliance workspace",
            ],
            "integration_helper": [
                "Verify credential scopes and rotation policy",
                "Test retry logic with synthetic 4xx/5xx responses",
                "Instrument integration flows with structured logs",
            ],
        }

        steps = base_map[domain].copy()
        if "rollback" in query.lower() and domain == "workflow_automation":
            steps.append("Document rollback procedure inside the automation metadata.")
        return steps
