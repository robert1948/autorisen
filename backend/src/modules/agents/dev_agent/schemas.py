"""
Dev Agent Pydantic Schemas

Defines the input/output models for the Dev Agent task execution.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class DevAgentTaskInput(BaseModel):
    """Input schema for Dev Agent tasks."""

    query: str = Field(
        ...,
        description="Developer's question or task description",
        min_length=1,
        max_length=3000,
    )
    context: Optional[Dict[str, Any]] = Field(
        default={},
        description="Current development context (agent being built, errors, config, etc.)",
    )
    task_type: Optional[str] = Field(
        default="general",
        description="Task type: general, build, test, debug, publish, optimize, review",
    )
    agent_slug: Optional[str] = Field(
        default=None,
        description="Slug of the agent being developed",
    )
    code_snippet: Optional[str] = Field(
        default=None,
        description="Code snippet for review or debugging",
    )

    class Config:
        schema_extra = {
            "example": {
                "query": "How do I add tool calling capabilities to my custom agent?",
                "task_type": "build",
                "agent_slug": "my-custom-agent",
                "code_snippet": None,
            }
        }


class CodeSuggestion(BaseModel):
    """A code suggestion from the Dev Agent."""

    title: str = Field(..., description="Description of the suggestion")
    code: str = Field(..., description="Code snippet")
    language: str = Field(default="python", description="Programming language")
    explanation: str = Field(..., description="Why this code is recommended")


class DevAgentTaskOutput(BaseModel):
    """Output schema for Dev Agent tasks."""

    response: str = Field(..., description="AI assistant response to the developer")
    code_suggestions: List[CodeSuggestion] = Field(
        default_factory=list,
        description="Code examples and suggestions",
    )
    best_practices: List[str] = Field(
        default_factory=list,
        description="Relevant best practices and tips",
    )
    documentation_links: List[Dict[str, str]] = Field(
        default_factory=list,
        description="Links to relevant documentation",
    )
    next_steps: List[str] = Field(
        default_factory=list,
        description="Recommended next steps",
    )
    confidence_score: float = Field(
        ..., description="Response confidence score (0.0-1.0)", ge=0.0, le=1.0
    )
    processing_time_ms: Optional[int] = Field(
        None, description="Time taken to process the request in milliseconds"
    )

    class Config:
        schema_extra = {
            "example": {
                "response": "To add tool calling capabilities to your agent...",
                "code_suggestions": [
                    {
                        "title": "Tool Definition",
                        "code": "tools = [{'name': 'search', 'description': '...'}]",
                        "language": "python",
                        "explanation": "Define tools your agent can use",
                    }
                ],
                "best_practices": [
                    "Always validate tool inputs",
                    "Implement proper error handling",
                ],
                "documentation_links": [
                    {
                        "title": "Tool Use Guide",
                        "url": "/docs/agents/tool-use",
                    }
                ],
                "next_steps": [
                    "Define your tool schemas",
                    "Test tool calling in the Agent Workbench",
                ],
                "confidence_score": 0.9,
                "processing_time_ms": 1500,
            }
        }
