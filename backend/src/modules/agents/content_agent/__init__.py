"""
Content Agent - AI-powered content generation and management assistant.

Generates, reviews, and optimizes content across channels with AI assistance.
Supports blog posts, social media, email campaigns, and documentation.
"""

from .router import router
from .schemas import ContentAgentTaskInput, ContentAgentTaskOutput
from .service import ContentAgentService

__all__ = [
    "router",
    "ContentAgentTaskInput",
    "ContentAgentTaskOutput",
    "ContentAgentService",
]
