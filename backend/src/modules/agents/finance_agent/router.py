"""
Finance Agent Router

FastAPI router providing endpoints for the Finance Agent.
Provides financial analysis, forecasting, and compliance support.
"""

import os
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from backend.src.core.config import get_settings
from backend.src.db.session import get_session
from backend.src.modules.auth.deps import get_verified_user as get_current_user
from backend.src.db.models import User
from .schemas import FinanceAgentTaskInput, FinanceAgentTaskOutput
from .service import FinanceAgentService

router = APIRouter(prefix="/finance-agent", tags=["Finance Agent"])

_service = None


def get_finance_agent_service() -> FinanceAgentService:
    """Get or create Finance Agent service instance."""
    global _service
    if _service is None:
        settings = get_settings()
        _service = FinanceAgentService(
            openai_api_key=settings.openai_api_key,
            anthropic_api_key=settings.anthropic_api_key,
            model=os.getenv("FINANCE_AGENT_MODEL", "claude-3-5-haiku-20241022"),
        )
    return _service


@router.post("/ask", response_model=FinanceAgentTaskOutput)
async def ask_finance_agent(
    input_data: FinanceAgentTaskInput,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
    service: FinanceAgentService = Depends(get_finance_agent_service),
):
    """
    Submit a financial query to the Finance Agent.

    The agent provides financial analysis, forecasting, compliance checking,
    and budgeting assistance.
    """
    try:
        result = await service.process_query(input_data, db=db, user=current_user)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error processing request: {str(e)}"
        )


@router.get("/health")
async def finance_agent_health():
    """Health check endpoint for the Finance Agent."""
    return {
        "status": "healthy",
        "agent": "finance-agent",
        "model": os.getenv("FINANCE_AGENT_MODEL", "claude-3-5-haiku-20241022"),
        "knowledge_base": "operational",
        "capabilities": [
            "financial_analysis",
            "forecasting",
            "budgeting",
            "compliance",
            "risk_assessment",
            "reporting",
        ],
    }


@router.get("/capabilities")
async def finance_agent_capabilities():
    """Get information about Finance Agent capabilities."""
    return {
        "agent_id": "finance-agent",
        "name": "Finance Agent",
        "description": "AI-powered financial analysis and advisory for the CapeControl platform",
        "capabilities": [
            "Cash flow analysis and optimization",
            "Budget forecasting with scenario modeling",
            "Financial compliance checking (IFRS, SARS)",
            "Risk assessment and mitigation planning",
            "KPI tracking and financial reporting",
            "Invoice processing optimization",
        ],
        "supported_analysis_types": [
            "general",
            "forecasting",
            "budgeting",
            "compliance",
            "risk",
            "reporting",
        ],
        "supported_currencies": ["ZAR", "USD", "EUR", "GBP"],
    }
