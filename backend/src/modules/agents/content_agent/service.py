"""
Content Agent Service

Core business logic for the Content Agent including LLM integration,
content generation, editing, and optimization across content types.
"""

import time
import logging
from typing import Any, Dict, List, Optional

from anthropic import AsyncAnthropic
from openai import AsyncOpenAI
from sqlalchemy.orm import Session

from backend.src.db import models

from .schemas import ContentAgentTaskInput, ContentAgentTaskOutput, ContentPiece

log = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are the CapeControl Content Agent — an expert AI content creator \
and editor for the CapeControl platform.

Your capabilities:
1. **Content Generation**: Blog posts, social media, emails, documentation, landing pages
2. **Content Editing**: Grammar, style, clarity, tone adjustments
3. **SEO Optimization**: Keyword integration, meta descriptions, heading structure
4. **Brand Consistency**: Maintain voice and style across all content
5. **Multi-Channel**: Adapt content for different platforms and audiences

Communication style:
- Write engaging, clear, and purposeful content
- Adapt tone and style to match the requested format
- Always consider the target audience
- Include actionable takeaways in every piece
- Follow SEO best practices naturally (not keyword-stuffed)

Content guidelines:
- Use active voice and strong verbs
- Break content into scannable sections with headers
- Include concrete examples and data points when possible
- End with a clear call-to-action when appropriate
- Keep paragraphs focused and concise (3-5 sentences)"""

USER_PROMPT_TEMPLATE = """Content Request: {query}

Content Type: {content_type}
Tone: {tone}
Target Audience: {target_audience}
Maximum Length: {max_length} words

{context_info}

Please generate high-quality content that:
1. Addresses the request directly
2. Matches the requested tone and style
3. Is appropriate for the target audience
4. Includes relevant headlines and structure
5. Follows SEO best practices"""


class ContentAgentService:
    """Service class for Content Agent operations."""

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

    async def process_query(
        self,
        input_data: ContentAgentTaskInput,
        *,
        db: Session | None = None,
        user: models.User | None = None,
    ) -> ContentAgentTaskOutput:
        """Process a content generation/editing request."""
        start_time = time.time()

        try:
            context_info = ""
            if input_data.context:
                context_parts = []
                if "brand_guidelines" in input_data.context:
                    context_parts.append(f"Brand Guidelines: {input_data.context['brand_guidelines']}")
                if "prior_content" in input_data.context:
                    context_parts.append(f"Prior Content: {input_data.context['prior_content']}")
                if context_parts:
                    context_info = "Additional Context:\n" + "\n".join(context_parts)

            user_prompt = USER_PROMPT_TEMPLATE.format(
                query=input_data.query,
                content_type=input_data.content_type or "general",
                tone=input_data.tone or "professional",
                target_audience=input_data.target_audience or "general audience",
                max_length=input_data.max_length or "no limit",
                context_info=context_info,
            )

            ai_response = await self._call_llm(user_prompt)

            # Build content piece
            word_count = len(ai_response.split())
            content_pieces = [
                ContentPiece(
                    title=self._extract_title(ai_response, input_data.query),
                    body=ai_response,
                    content_type=input_data.content_type or "general",
                    word_count=word_count,
                    seo_keywords=self._extract_keywords(input_data.query, ai_response),
                )
            ]

            # Generate editing suggestions
            editing_suggestions = self._get_editing_suggestions(input_data.content_type)

            # SEO recommendations
            seo_recs = self._get_seo_recommendations(input_data.content_type)

            # Alternative headlines
            alt_headlines = self._generate_alt_headlines(input_data.query, input_data.content_type)

            processing_time = int((time.time() - start_time) * 1000)

            return ContentAgentTaskOutput(
                response=ai_response,
                content_pieces=content_pieces,
                editing_suggestions=editing_suggestions,
                seo_recommendations=seo_recs,
                alternative_headlines=alt_headlines,
                next_steps=[
                    "Review and personalize the generated content",
                    "Add relevant images or media",
                    "Optimize meta description and tags",
                    "Schedule for publication at optimal time",
                ],
                confidence_score=self._calculate_confidence(ai_response, input_data),
                processing_time_ms=processing_time,
            )

        except Exception as e:
            log.error("ContentAgent error: %s", e)
            processing_time = int((time.time() - start_time) * 1000)
            return ContentAgentTaskOutput(
                response=(
                    "I'd be glad to help with your content request. "
                    "Please try again with more specific details about the topic, "
                    "target audience, and desired format."
                ),
                content_pieces=[],
                editing_suggestions=[],
                seo_recommendations=[],
                alternative_headlines=[],
                next_steps=["Provide more details for better content generation"],
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
            "Content generation based on your request is being prepared. "
            "For the best results, our AI content engine leverages advanced language models "
            "to create engaging, audience-appropriate content. Please ensure your API keys "
            "are configured for full content generation capabilities."
        )

    def _extract_title(self, content: str, query: str) -> str:
        """Extract or generate a title from the content."""
        lines = content.strip().split("\n")
        for line in lines[:5]:
            clean = line.strip().lstrip("#").strip()
            if clean and len(clean) > 10 and len(clean) < 200:
                return clean
        # Fallback: derive from query
        return query[:100].strip().title()

    def _extract_keywords(self, query: str, content: str) -> List[str]:
        """Extract SEO keywords from the content."""
        # Simple keyword extraction based on query terms
        words = query.lower().split()
        keywords = [w for w in words if len(w) > 3 and w not in (
            "about", "with", "that", "this", "from", "have", "will",
            "what", "when", "where", "which", "write", "create", "make",
        )]
        return keywords[:5]

    def _get_editing_suggestions(self, content_type: Optional[str]) -> List[str]:
        """Get editing suggestions based on content type."""
        suggestions = {
            "blog_post": [
                "Add specific examples or case studies to support key points",
                "Include internal and external links for SEO value",
                "Add a compelling meta description (155 characters)",
                "Break up long paragraphs for better readability",
            ],
            "social_media": [
                "Keep posts concise and attention-grabbing",
                "Include relevant hashtags (3-5 optimal)",
                "Add a clear call-to-action",
                "Consider adding an image or video",
            ],
            "email": [
                "Craft a compelling subject line (40-60 characters)",
                "Personalize the greeting and content",
                "Include a single, clear call-to-action",
                "Test rendering across email clients",
            ],
            "documentation": [
                "Use consistent terminology throughout",
                "Add code examples where appropriate",
                "Include a table of contents for longer docs",
                "Add cross-references to related documentation",
            ],
            "landing_page": [
                "Lead with the primary value proposition",
                "Include social proof (testimonials, stats)",
                "Add multiple call-to-action buttons",
                "Optimize for mobile readability",
            ],
        }
        return suggestions.get(content_type or "general", [
            "Review for clarity and conciseness",
            "Ensure consistent tone throughout",
            "Add relevant visuals or examples",
        ])

    def _get_seo_recommendations(self, content_type: Optional[str]) -> List[str]:
        """Get SEO recommendations."""
        if content_type in ("social_media", "email"):
            return []
        return [
            "Include primary keyword in the title and first paragraph",
            "Use H2 and H3 headers with relevant keywords",
            "Write a meta description under 155 characters",
            "Add alt text to all images",
            "Aim for 1-2% keyword density naturally",
        ]

    def _generate_alt_headlines(
        self, query: str, content_type: Optional[str]
    ) -> List[str]:
        """Generate alternative headline options."""
        base = query.strip().rstrip(".")

        if content_type == "blog_post":
            return [
                f"The Complete Guide to {base}",
                f"How {base} Can Transform Your Business",
                f"Why {base} Matters Now More Than Ever",
            ]
        elif content_type == "social_media":
            return [
                f"Did you know about {base}?",
                f"Quick tip: {base}",
            ]
        return [
            f"Understanding {base}",
            f"Everything You Need to Know About {base}",
        ]

    def _calculate_confidence(
        self, response: str, input_data: ContentAgentTaskInput
    ) -> float:
        """Calculate confidence score."""
        score = 0.5

        if len(response) > 200:
            score += 0.1
        if len(response) > 500:
            score += 0.1
        if input_data.content_type and input_data.content_type != "general":
            score += 0.1
        if input_data.target_audience:
            score += 0.05
        if input_data.tone and input_data.tone != "professional":
            score += 0.05

        return min(score, 1.0)
