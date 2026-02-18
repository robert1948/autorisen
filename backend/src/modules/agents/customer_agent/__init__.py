"""
Customer Agent - AI-powered customer support and goal expression assistant.

Helps customers articulate their goals, suggests appropriate workflows,
and provides personalized recommendations based on their industry and needs.
"""

from .router import router
from .schemas import CustomerAgentTaskInput, CustomerAgentTaskOutput
from .service import CustomerAgentService

__all__ = [
    "router",
    "CustomerAgentTaskInput",
    "CustomerAgentTaskOutput",
    "CustomerAgentService",
]
