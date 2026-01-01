"""
CapeAI Guide Agent Service

Core business logic for the CapeAI Guide agent including OpenAI integration,
knowledge base searching, and response generation.
"""

import time
from typing import Any, Dict, List, Optional
from openai import AsyncOpenAI
from anthropic import AsyncAnthropic

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
        self, input_data: CapeAIGuideTaskInput
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
            ai_response = await self._generate_ai_response(
                query=input_data.query,
                context=context_analysis,
                knowledge=relevant_docs,
                user_level=input_data.user_level,
                preferred_format=input_data.preferred_format,
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

        except Exception as e:
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
    ) -> str:
        """Generate AI response using OpenAI API."""

        system_prompt = self.prompts.get_system_prompt(user_level, preferred_format)
        user_prompt = self.prompts.get_user_prompt(query, context, knowledge)

        try:
            if self.model.startswith("claude"):
                if not self.anthropic_client:
                    return "Anthropic API key not configured."

                response = await self.anthropic_client.messages.create(
                    model=self.model,
                    max_tokens=1000,
                    temperature=0.7,
                    system=system_prompt,
                    messages=[
                        {"role": "user", "content": user_prompt},
                    ],
                )
                return response.content[0].text

            if not self.openai_client:
                return "OpenAI API key not configured."

            response = await self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=1000,
                temperature=0.7,
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            return f"I'm having trouble generating a response right now. Please try again. (Error: {str(e)})"

    async def _extract_suggestions(
        self, ai_response: str, input_data: CapeAIGuideTaskInput
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
