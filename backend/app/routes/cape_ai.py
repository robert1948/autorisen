"""Cape_ai Routes"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
from app.services.cape_ai_service import get_cape_ai_service

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    response: str
    timestamp: str
    context_used: bool
    type: str

@router.get("/")
async def cape_ai_root():
    return {"message": "CapeAI endpoint - Your AI assistant for CapeControl"}

@router.post("/chat", response_model=ChatResponse)
async def cape_ai_chat(request: ChatRequest):
    """
    CapeAI Chat Endpoint - Demo AI Assistant
    
    Provides intelligent responses for platform guidance and support.
    Works without external AI providers using built-in knowledge.
    """
    try:
        cape_ai_service = get_cape_ai_service()
        result = await cape_ai_service.generate_response(
            message=request.message,
            context=request.context
        )
        
        return ChatResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating response: {str(e)}")

@router.get("/status")
async def cape_ai_status():
    """Check CapeAI service status"""
    return {
        "status": "operational",
        "service": "CapeAI Demo Assistant",
        "features": [
            "Platform guidance",
            "Contextual help",
            "Business workflow advice",
            "Demo responses (no external AI required)"
        ]
    }
