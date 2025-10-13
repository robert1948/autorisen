"""Pydantic schemas for the agent registry."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Iterable, Optional

from pydantic import Field, field_validator

from backend.src.schemas.base import SchemaBase


class AgentBase(SchemaBase):
    name: str = Field(..., min_length=3, max_length=160)
    slug: str = Field(..., min_length=3, max_length=100, pattern=r"^[a-z0-9-]+$")
    description: Optional[str] = Field(default=None, max_length=2000)
    visibility: str = Field(default="private")


class AgentCreate(AgentBase):
    pass


class AgentUpdate(SchemaBase):
    name: Optional[str] = Field(default=None, min_length=3, max_length=160)
    description: Optional[str] = Field(default=None, max_length=2000)
    visibility: Optional[str] = Field(default=None)


class AgentVersionBase(SchemaBase):
    version: str = Field(..., min_length=1, max_length=20)
    manifest: Dict[str, Any]
    changelog: Optional[str] = None
    status: str = Field(default="draft")

    @field_validator("manifest")
    @classmethod
    def ensure_manifest_keys(cls, value: Dict[str, Any]) -> Dict[str, Any]:
        required: Iterable[str] = ("name", "description", "placement", "tools")
        missing = [key for key in required if key not in value]
        if missing:
            raise ValueError(f"manifest missing keys: {', '.join(missing)}")
        tools = value.get("tools")
        if not isinstance(tools, list) or not tools:
            raise ValueError("manifest.tools must be a non-empty list")
        if not all(isinstance(tool, str) and tool for tool in tools):
            raise ValueError("manifest.tools entries must be non-empty strings")
        return value


class AgentVersionCreate(AgentVersionBase):
    pass


class AgentVersionResponse(AgentVersionBase):
    id: str
    created_at: datetime
    published_at: Optional[datetime]

class AgentResponse(AgentBase):
    id: str
    owner_id: Optional[str]
    created_at: datetime
    updated_at: datetime
    versions: list[AgentVersionResponse] = Field(default_factory=list)
