"""
Content Agent Router

FastAPI router providing endpoints for the Content Agent.
Generates, reviews, and optimizes content across channels.
"""

import os
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from backend.src.core.config import get_settings
from backend.src.db.session import get_session
from backend.src.modules.auth.deps import get_verified_user as get_current_user
from backend.src.db.models import User
from .schemas import ContentAgentTaskInput, ContentAgentTaskOutput
from .service import ContentAgentService

router = APIRouter(prefix="/content-agent", tags=["Content Agent"])

_service = None


def get_content_agent_service() -> ContentAgentService:
    """Get or create Content Agent service instance."""
    global _service
    if _service is None:
        settings = get_settings()
        _service = ContentAgentService(
            openai_api_key=settings.openai_api_key,
            anthropic_api_key=settings.anthropic_api_key,
            model=os.getenv("CONTENT_AGENT_MODEL", "claude-3-5-haiku-20241022"),
        )
    return _service


@router.post("/ask", response_model=ContentAgentTaskOutput)
async def ask_content_agent(
    input_data: ContentAgentTaskInput,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
    service: ContentAgentService = Depends(get_content_agent_service),
):
    """
    Submit a content generation/editing request to the Content Agent.

    The agent generates, reviews, and optimizes content for blogs,
    social media, emails, documentation, and landing pages.
    """
    try:
        result = await service.process_query(input_data, db=db, user=current_user)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error processing request: {str(e)}"
        )


@router.get("/health")
async def content_agent_health():
    """Health check endpoint for the Content Agent."""
    return {
        "status": "healthy",
        "agent": "content-agent",
        "model": os.getenv("CONTENT_AGENT_MODEL", "claude-3-5-haiku-20241022"),
        "knowledge_base": "operational",
        "capabilities": [
            "content_generation",
            "content_editing",
            "seo_optimization",
            "multi_channel",
        ],
    }


@router.get("/capabilities")
async def content_agent_capabilities():
    """Get information about Content Agent capabilities."""
    return {
        "agent_id": "content-agent",
        "name": "Content Agent",
        "description": "AI-powered content generation and optimization for the CapeControl platform",
        "capabilities": [
            "Blog post generation and optimization",
            "Social media content creation",
            "Email campaign copy writing",
            "Technical documentation generation",
            "Landing page copy optimization",
            "SEO keyword optimization",
            "Brand voice consistency",
            "Multi-channel content adaptation",
        ],
        "supported_content_types": [
            "general",
            "blog_post",
            "social_media",
            "email",
            "documentation",
            "landing_page",
        ],
        "supported_tones": [
            "professional",
            "casual",
            "technical",
            "persuasive",
            "friendly",
        ],
    }
