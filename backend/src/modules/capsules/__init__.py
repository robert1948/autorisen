"""
Workflow Capsule Engine.

Capsules are composable, template-driven workflow runs that encode
domain-specific tasks: SOP answering, audit summaries, clause finding,
compliance checklists, etc.

Each capsule defines:
- A system prompt tailored to the task
- Required document types it expects
- RAG retrieval parameters
- Output format specification
"""

from .router import router
from .schemas import (
    CapsuleDefinition,
    CapsuleRunRequest,
    CapsuleRunResponse,
)
from .service import CapsuleService

__all__ = [
    "router",
    "CapsuleDefinition",
    "CapsuleRunRequest",
    "CapsuleRunResponse",
    "CapsuleService",
]
