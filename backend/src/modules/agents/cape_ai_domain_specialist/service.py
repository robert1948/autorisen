"""
CapeAI Domain Specialist service.

Provides a reusable service that combines lightweight determinism (knowledge base
search + heuristics) with optional OpenAI completions to deliver domain-aware
guidance for workflow automation, data analytics, security audit, and
integration helper use cases.
"""

from __future__ import annotations

import time
from typing import Dict, List, Optional

from openai import AsyncOpenAI
from anthropic import AsyncAnthropic

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
        self, input_data: DomainSpecialistTaskInput
    ) -> DomainSpecialistTaskOutput:
        """Main entry point for executing a domain-specific task."""

        start = time.time()
        domain: DomainLiteral = input_data.domain

        # Lookups and heuristics
        knowledge = await self.knowledge_base.search(
            domain=domain, query=input_data.query, context=input_data.context
        )
        playbook_steps = await self.knowledge_base.recommended_steps(
            domain, input_data.query
        )

        # Generate narrative response
        response = await self._generate_response(
            domain=domain,
            query=input_data.query,
            knowledge=knowledge,
            objectives=input_data.objectives,
            preferred_format=input_data.preferred_format,
        )

        # Build structured output
        insights = self._derive_insights(domain, input_data, knowledge)
        resources = [
            ResourceLink(title=doc["title"], url=doc["url"], type=doc["type"])
            for doc in knowledge[:3]
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
    ) -> str:
        """Call OpenAI to craft the domain-tailored response."""

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
            f"- {doc['title']}: {doc['snippet']}" for doc in knowledge
        )
        format_hint = f"Preferred format: {preferred_format or 'summary'}."

        user_prompt = (
            f"{domain_blurb}\n{objectives_section}\n{format_hint}\n\n"
            f"User query: {query}\n\nRelevant knowledge:\n{knowledge_section or '- None'}\n\n"
            "Craft an answer that includes deployment considerations, quick wins, and risk mitigations."
        )

        try:
            if self.model.startswith("claude"):
                if not self.anthropic_client:
                    return "Anthropic API key not configured."

                completion = await self.anthropic_client.messages.create(
                    model=self.model,
                    max_tokens=700,
                    temperature=0.6,
                    system=system_prompt,
                    messages=[
                        {"role": "user", "content": user_prompt},
                    ],
                )
                return completion.content[0].text

            if not self.openai_client:
                return "OpenAI API key not configured."

            completion = await self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.6,
                max_tokens=700,
            )
            return completion.choices[0].message.content.strip()
        except Exception as exc:  # pragma: no cover - external dependency
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

        # Add knowledge-derived insight if available
        if knowledge:
            insights.append(
                DomainInsight(
                    label="Related doc",
                    detail=f"Consider '{knowledge[0]['title']}' for additional context.",
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

        score = 0.4  # base score
        if len(response) > 200:
            score += 0.2
        if knowledge:
            score += 0.2
        if len(insights) >= 2:
            score += 0.1

        return min(score, 0.98)
