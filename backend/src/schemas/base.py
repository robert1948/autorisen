"""Shared Pydantic base configuration."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class SchemaBase(BaseModel):
    """Project-wide base schema using Pydantic v2 config."""

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        str_strip_whitespace=True,
    )
