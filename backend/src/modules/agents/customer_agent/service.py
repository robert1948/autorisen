"""
Customer Agent Service

Core business logic for the Customer Agent including LLM integration,
goal analysis, workflow suggestion, and personalized recommendations.
"""

import json
import time
import logging
from typing import Any, Dict, List, Optional

from anthropic import AsyncAnthropic
from openai import AsyncOpenAI
from sqlalchemy.orm import Session

from backend.src.db import models

from .schemas import (
    CustomerAgentTaskInput,
    CustomerAgentTaskOutput,
    WorkflowSuggestion,
)
from .knowledge_base import CustomerKnowledgeBase

log = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are the CapeControl Customer Agent — a friendly, knowledgeable AI assistant \
that helps customers achieve their business goals through AI automation.

Your responsibilities:
1. **Understand Goals**: Help customers articulate what they want to accomplish
2. **Suggest Workflows**: Recommend appropriate AI workflows and agent combinations
3. **Industry Expertise**: Provide industry-specific advice for finance, energy, legal, healthcare, and retail
4. **Onboarding Support**: Guide new customers through platform features
5. **Plan Guidance**: Help customers choose the right subscription plan

Communication style:
- Be warm, professional, and solution-oriented
- Use clear, jargon-free language
- Provide concrete, actionable recommendations
- Always include specific next steps
- If you're unsure, acknowledge it and suggest alternatives

When suggesting workflows, always explain:
- What the workflow does
- How long it takes to set up
- Which AI agents are involved
- Expected benefits and outcomes"""

USER_PROMPT_TEMPLATE = """Customer Query: {query}

Industry: {industry}
Intent: {intent}
Subscription Tier: {tier}

Relevant Knowledge:
{knowledge}

Workflow Templates Available:
{templates}

Please provide a helpful response that:
1. Directly addresses the customer's needs
2. Suggests relevant workflows if applicable
3. Includes clear next steps
4. Recommends a plan upgrade only if genuinely needed"""


class CustomerAgentService:
    """Service class for Customer Agent operations."""

    def __init__(
        self,
        openai_api_key: Optional[str] = None,
        anthropic_api_key: Optional[str] = None,
        model: str = "claude-3-5-haiku-20241022",
    ):
        """Initialize the Customer Agent service."""
        self.openai_client = (
            AsyncOpenAI(api_key=openai_api_key) if openai_api_key else None
        )
        self.anthropic_client = (
            AsyncAnthropic(api_key=anthropic_api_key) if anthropic_api_key else None
        )
        self.model = model
        self.knowledge_base = CustomerKnowledgeBase()

    async def process_query(
        self,
        input_data: CustomerAgentTaskInput,
        *,
        db: Session | None = None,
        user: models.User | None = None,
    ) -> CustomerAgentTaskOutput:
        """Process a customer query and generate a helpful response."""
        start_time = time.time()

        try:
            # Search knowledge base
            context = input_data.context or {}
            relevant_docs = await self.knowledge_base.search(
                query=input_data.query, context=context, limit=3
            )

            # Suggest workflows
            workflow_templates = self.knowledge_base.suggest_workflows(
                query=input_data.query,
                industry=input_data.industry,
                limit=3,
            )

            # Build knowledge context
            knowledge_text = "\n".join(
                f"- {doc.title}: {doc.content}" for doc in relevant_docs
            ) or "No specific knowledge found."

            template_text = "\n".join(
                f"- {t.name} ({t.complexity}, {t.setup_time}): {t.description}"
                for t in workflow_templates
            ) or "No matching templates."

            # Generate AI response
            user_prompt = USER_PROMPT_TEMPLATE.format(
                query=input_data.query,
                industry=input_data.industry or "not specified",
                intent=input_data.intent or "general",
                tier=context.get("subscription_tier", "free"),
                knowledge=knowledge_text,
                templates=template_text,
            )

            ai_response = await self._call_llm(user_prompt)

            # Build workflow suggestions from templates
            suggestions = [
                WorkflowSuggestion(
                    name=t.name,
                    description=t.description,
                    estimated_setup_time=t.setup_time,
                    complexity=t.complexity,
                    agents_required=t.agents,
                )
                for t in workflow_templates
            ]

            # Extract next steps
            next_steps = self._extract_next_steps(ai_response, workflow_templates)

            # Determine if plan upgrade recommended
            recommended_plan = self._check_plan_recommendation(
                input_data, context
            )

            processing_time = int((time.time() - start_time) * 1000)

            return CustomerAgentTaskOutput(
                response=ai_response,
                workflow_suggestions=suggestions,
                next_steps=next_steps,
                recommended_plan=recommended_plan,
                confidence_score=self._calculate_confidence(
                    relevant_docs, workflow_templates, ai_response
                ),
                processing_time_ms=processing_time,
            )

        except Exception as e:
            log.error("CustomerAgent error: %s", e)
            processing_time = int((time.time() - start_time) * 1000)
            return CustomerAgentTaskOutput(
                response=(
                    "I'd be happy to help you with that! While I'm processing your request, "
                    "here are some general suggestions based on your query. For more specific "
                    "guidance, please try again or contact our support team."
                ),
                workflow_suggestions=[],
                next_steps=[
                    "Explore the Agent Marketplace for pre-built solutions",
                    "Check our documentation for workflow templates",
                    "Contact support for personalized assistance",
                ],
                confidence_score=0.3,
                processing_time_ms=processing_time,
            )

    async def _call_llm(self, user_prompt: str) -> str:
        """Call the LLM provider (Anthropic preferred, OpenAI fallback)."""
        if self.anthropic_client and "claude" in self.model:
            try:
                response = await self.anthropic_client.messages.create(
                    model=self.model,
                    max_tokens=1024,
                    system=SYSTEM_PROMPT,
                    messages=[{"role": "user", "content": user_prompt}],
                )
                return response.content[0].text
            except Exception as e:
                log.warning("Anthropic call failed, trying OpenAI fallback: %s", e)

        if self.openai_client:
            try:
                response = await self.openai_client.chat.completions.create(
                    model="gpt-4o-mini" if "claude" in self.model else self.model,
                    max_tokens=1024,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt},
                    ],
                )
                return response.choices[0].message.content or ""
            except Exception as e:
                log.error("OpenAI call also failed: %s", e)

        return (
            "I understand you're looking for help with your business automation needs. "
            "Based on the available information, I'd recommend exploring our workflow templates "
            "in the Agent Marketplace. Our team can also provide personalized guidance — "
            "feel free to reach out to support@capecontrol.ai."
        )

    def _extract_next_steps(
        self, response: str, templates: list
    ) -> List[str]:
        """Extract actionable next steps from the response and templates."""
        steps = []

        if templates:
            steps.append(f"Review the '{templates[0].name}' workflow template")
            steps.append("Configure the workflow with your specific requirements")

        steps.append("Test the workflow in sandbox mode before going live")
        steps.append("Monitor performance via the analytics dashboard")

        return steps[:5]

    def _check_plan_recommendation(
        self,
        input_data: CustomerAgentTaskInput,
        context: Dict[str, Any],
    ) -> Optional[str]:
        """Check if a plan upgrade would benefit the customer."""
        tier = context.get("subscription_tier", "free")

        # Count requested agents/features
        query_lower = input_data.query.lower()
        needs_advanced = any(
            kw in query_lower
            for kw in ["custom integration", "sla", "enterprise", "white-label",
                        "on-premise", "advanced security", "dedicated support"]
        )
        needs_pro = any(
            kw in query_lower
            for kw in ["multiple", "team", "analytics", "priority", "workflow",
                        "automation", "50 agents"]
        )

        if tier == "free" and needs_advanced:
            return "enterprise"
        if tier == "free" and needs_pro:
            return "pro"
        if tier == "pro" and needs_advanced:
            return "enterprise"

        return None

    def _calculate_confidence(
        self, docs: list, templates: list, response: str
    ) -> float:
        """Calculate confidence score based on matching knowledge."""
        score = 0.4  # Base confidence

        if docs:
            score += min(len(docs) * 0.1, 0.2)
        if templates:
            score += min(len(templates) * 0.1, 0.2)
        if len(response) > 200:
            score += 0.1
        if len(response) > 500:
            score += 0.1

        return min(score, 1.0)
