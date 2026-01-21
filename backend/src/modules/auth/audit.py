"""Audit logging helpers for authentication events."""

from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session

from backend.src.db import models


def log_login_attempt(
    db: Session,
    *,
    email: str,
    success: bool,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    reason: Optional[str] = None,
    details: Optional[str] = None,
) -> None:
    audit = models.LoginAudit(
        email=email,
        success=success,
        ip_address=ip_address,
        user_agent=user_agent,
        reason=reason,
        details=details,
    )
    db.add(audit)
    db.commit()
