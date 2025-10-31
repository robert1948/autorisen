from fastapi import APIRouter
from pydantic import BaseModel
from .._shim_utils import _first_ok

try:
    _m = _first_ok([
        lambda: __import__("backend.src.modules.cape_ai.router", fromlist=["router","AIPromptRequest","AIResponse","CapeAIService"]),
        lambda: __import__("backend.src.modules.cape_ai", fromlist=["router","AIPromptRequest","AIResponse","CapeAIService"]),
    ])
    router = getattr(_m, "router")
    AIPromptRequest = getattr(_m, "AIPromptRequest")
    AIResponse = getattr(_m, "AIResponse")
    CapeAIService = getattr(_m, "CapeAIService")
except ImportError:
    class AIPromptRequest(BaseModel):
        prompt: str
    class AIResponse(BaseModel):
        text: str
    class CapeAIService: ...
    router = APIRouter()
