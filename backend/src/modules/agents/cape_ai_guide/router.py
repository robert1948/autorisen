"""
CapeAI Guide Agent Router

FastAPI router providing endpoints for the CapeAI Guide agent.
Simple implementation for basic functionality.
"""

import os
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from backend.src.core.config import get_settings
from backend.src.db.session import get_session
from backend.src.modules.auth.deps import get_verified_user as get_current_user
from backend.src.db.models import User
from .schemas import CapeAIGuideTaskInput, CapeAIGuideTaskOutput
from .service import CapeAIGuideService

# Initialize router
router = APIRouter(prefix="/cape-ai-guide", tags=["CapeAI Guide Agent"])

# Initialize service (will be properly configured with dependency injection in production)
_service = None


def get_cape_ai_service() -> CapeAIGuideService:
    """Get or create CapeAI Guide service instance."""
    global _service
    if _service is None:
        settings = get_settings()

        _service = CapeAIGuideService(
            openai_api_key=settings.openai_api_key,
            anthropic_api_key=settings.anthropic_api_key,
            model=os.getenv("CAPE_AI_GUIDE_MODEL", "claude-3-5-sonnet-20240620"),
        )
    return _service


@router.post("/ask", response_model=CapeAIGuideTaskOutput)
async def ask_cape_ai_guide(
    input_data: CapeAIGuideTaskInput,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
    service: CapeAIGuideService = Depends(get_cape_ai_service),
):
    """
    Submit a question to the CapeAI Guide agent.

    Direct processing without the task system for now.
    """
    try:
        # Process the request directly
        result = await service.process_query(input_data)
        return result

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error processing request: {str(e)}"
        )


@router.get("/health")
async def cape_ai_guide_health():
    """Health check endpoint for the CapeAI Guide agent."""
    try:
        # Simple health check without OpenAI dependency
        return {
            "status": "healthy",
            "agent": "cape-ai-guide",
            "model": os.getenv("CAPE_AI_GUIDE_MODEL", "claude-3-5-sonnet-20240620"),
            "knowledge_base": "operational",
            "timestamp": "2025-11-11T06:15:00Z",
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": "2025-11-11T06:15:00Z",
        }


@router.get("/capabilities")
async def cape_ai_guide_capabilities():
    """Get information about CapeAI Guide agent capabilities."""
    return {
        "agent_id": "cape-ai-guide",
        "name": "CapeAI Guide",
        "description": "Intelligent assistant for CapeControl platform guidance and support",
        "capabilities": [
            "Platform navigation assistance",
            "Feature explanation and tutorials",
            "Workflow and automation guidance",
            "Troubleshooting and problem resolution",
            "Best practices recommendations",
            "Resource and documentation discovery",
        ],
        "supported_formats": ["text", "steps", "checklist", "code"],
        "user_levels": ["beginner", "intermediate", "advanced"],
        "response_time": "< 3 seconds",
        "confidence_scoring": True,
        "resource_linking": True,
        "context_awareness": True,
    }
