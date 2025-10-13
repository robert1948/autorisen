from datetime import datetime
from typing import Any, Dict

from pydantic import Field

from .base import SchemaBase


class UserOut(SchemaBase):
    """Shared user representation returned from auth endpoints."""

    id: str  # UUID as string
    email: str
    first_name: str = ""
    last_name: str = ""
    role: str = "Customer"
    company_name: str = ""
    is_active: bool = True
    is_email_verified: bool = False
    profile: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime | None = None
