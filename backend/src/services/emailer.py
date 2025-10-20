"""Email delivery stubs for auth-related notifications."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Mapping

logger = logging.getLogger(__name__)


def send_welcome_email(email: str, role: str, context: Mapping[str, Any] | None = None) -> None:
    """Log welcome email intent; replace with real provider in production."""

    logger.info("Welcome email queued", extra={"email": email, "role": role, "context": dict(context or {})})


def send_password_reset_email(email: str, reset_url: str, expires_at: datetime) -> None:
    """Log password reset email intent."""

    logger.info(
        "Password reset email queued",
        extra={
            "email": email,
            "reset_url": reset_url,
            "expires_at": expires_at.isoformat(),
        },
    )
