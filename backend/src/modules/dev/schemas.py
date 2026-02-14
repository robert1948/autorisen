"""Pydantic schemas for the Developer Dashboard module."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Developer Profile
# ---------------------------------------------------------------------------


class DeveloperProfileOut(BaseModel):
    """Public-facing developer profile data."""

    user_id: str
    email: str
    first_name: str
    last_name: str
    organization: Optional[str] = None
    use_case: Optional[str] = None
    website_url: Optional[str] = None
    github_url: Optional[str] = None
    developer_terms_accepted_at: Optional[datetime] = None
    developer_terms_version: Optional[str] = None
    created_at: datetime
    email_verified: bool = False


class DeveloperProfileUpdateIn(BaseModel):
    """Editable fields on the developer profile."""

    organization: Optional[str] = Field(default=None, max_length=200)
    use_case: Optional[str] = Field(default=None, max_length=64)
    website_url: Optional[str] = Field(default=None, max_length=500)
    github_url: Optional[str] = Field(default=None, max_length=500)


# ---------------------------------------------------------------------------
# API Credentials
# ---------------------------------------------------------------------------


class ApiCredentialOut(BaseModel):
    """API credential (safe view — no secret)."""

    id: str
    client_id: str
    label: Optional[str] = None
    is_active: bool = True
    created_at: datetime
    revoked_at: Optional[datetime] = None


class ApiCredentialCreateIn(BaseModel):
    """Payload for provisioning a new API credential."""

    label: str = Field(default="Default", max_length=100)


class ApiCredentialCreateOut(BaseModel):
    """Response after creating an API credential.

    client_secret is shown once and never returned again.
    """

    id: str
    client_id: str
    client_secret: str  # shown once!
    label: str
    created_at: datetime
    message: str = "Store the client_secret securely — it will not be shown again."


# ---------------------------------------------------------------------------
# Usage / Stats (placeholder)
# ---------------------------------------------------------------------------


class DeveloperUsageOut(BaseModel):
    """Aggregated API usage stats for the developer."""

    total_api_keys: int = 0
    active_api_keys: int = 0
    revoked_api_keys: int = 0
    account_created_at: Optional[datetime] = None
    email_verified: bool = False


# Resolve forward references
DeveloperProfileOut.model_rebuild()
DeveloperProfileUpdateIn.model_rebuild()
ApiCredentialOut.model_rebuild()
ApiCredentialCreateIn.model_rebuild()
ApiCredentialCreateOut.model_rebuild()
DeveloperUsageOut.model_rebuild()
