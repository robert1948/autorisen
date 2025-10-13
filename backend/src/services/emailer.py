"""Email delivery stub for welcome notifications."""

from __future__ import annotations

import logging
from typing import Any, Mapping

logger = logging.getLogger(__name__)


async def send_welcome_email(email: str, role: str, context: Mapping[str, Any] | None = None) -> None:
    """Log welcome email intent; replace with real provider in production."""

    logger.info("Welcome email queued", extra={"email": email, "role": role, "context": dict(context or {})})

