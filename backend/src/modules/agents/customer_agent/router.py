"""
Customer Agent Router

FastAPI router providing endpoints for the Customer Agent.
Helps customers express goals and suggests appropriate workflows.
"""

import os
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from backend.src.core.config import get_settings
from backend.src.db.session import get_session
from backend.src.modules.auth.deps import get_verified_user as get_current_user
from backend.src.db.models import User
from .schemas import CustomerAgentTaskInput, CustomerAgentTaskOutput
from .service import CustomerAgentService

router = APIRouter(prefix="/customer-agent", tags=["Customer Agent"])

_service = None


def get_customer_agent_service() -> CustomerAgentService:
    """Get or create Customer Agent service instance."""
    global _service
    if _service is None:
        settings = get_settings()
        _service = CustomerAgentService(
            openai_api_key=settings.openai_api_key,
            anthropic_api_key=settings.anthropic_api_key,
            model=os.getenv("CUSTOMER_AGENT_MODEL", "claude-3-5-haiku-20241022"),
        )
    return _service


@router.post("/ask", response_model=CustomerAgentTaskOutput)
async def ask_customer_agent(
    input_data: CustomerAgentTaskInput,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
    service: CustomerAgentService = Depends(get_customer_agent_service),
):
    """
    Submit a query to the Customer Agent.

    The agent helps customers express their goals, suggests workflows,
    and provides personalized recommendations.
    """
    try:
        result = await service.process_query(input_data, db=db, user=current_user)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error processing request: {str(e)}"
        )


@router.get("/health")
async def customer_agent_health():
    """Health check endpoint for the Customer Agent."""
    return {
        "status": "healthy",
        "agent": "customer-agent",
        "model": os.getenv("CUSTOMER_AGENT_MODEL", "claude-3-5-haiku-20241022"),
        "knowledge_base": "operational",
        "capabilities": [
            "goal_expression",
            "workflow_suggestion",
            "plan_guidance",
            "industry_expertise",
        ],
    }


@router.get("/capabilities")
async def customer_agent_capabilities():
    """Get information about Customer Agent capabilities."""
    return {
        "agent_id": "customer-agent",
        "name": "Customer Agent",
        "description": "AI assistant that helps customers express goals and find the right workflows",
        "capabilities": [
            "Goal analysis and articulation",
            "Workflow template suggestions",
            "Industry-specific recommendations",
            "Subscription plan guidance",
            "Onboarding assistance",
            "Support ticket creation",
        ],
        "supported_industries": [
            "finance",
            "energy",
            "legal",
            "healthcare",
            "retail",
        ],
        "supported_intents": [
            "general",
            "goal_expression",
            "workflow_suggestion",
            "support",
            "onboarding",
        ],
    }
