"""Pydantic schemas for the agent registry."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import Field, field_validator

from backend.src.schemas.base import SchemaBase
from backend.src.modules.agents.manifest_validator import validate_manifest


class AgentBase(SchemaBase):
    name: str = Field(..., min_length=3, max_length=160)
    slug: str = Field(..., min_length=3, max_length=100, pattern=r"^[a-z0-9-]+$")
    description: Optional[str] = Field(default=None, max_length=2000)
    category: Optional[str] = Field(default=None, max_length=64)
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
    def validate_manifest_schema(cls, value: Dict[str, Any]) -> Dict[str, Any]:
        validate_manifest(value)
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
    current_version_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    versions: list[AgentVersionResponse] = Field(default_factory=list)
