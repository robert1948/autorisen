"""
CapeAI Guide Agent - First production agent implementation using Task execution system.

Provides AI-powered assistance for CapeControl platform users with guidance,
onboarding, and problem resolution capabilities.
"""

from .router import router
from .schemas import CapeAIGuideTaskInput, CapeAIGuideTaskOutput
from .service import CapeAIGuideService

__all__ = [
    "router",
    "CapeAIGuideTaskInput",
    "CapeAIGuideTaskOutput",
    "CapeAIGuideService",
]
