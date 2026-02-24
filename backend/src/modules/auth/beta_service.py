"""Beta invite service — create, validate, consume, list, and revoke beta invites."""

from __future__ import annotations

import base64
import hashlib
import logging
import os
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.src.db import models

log = logging.getLogger("auth.beta")

BETA_INVITE_TTL_HOURS = int(os.getenv("BETA_INVITE_TTL_HOURS", "168"))  # 7 days
BETA_MODE = os.getenv("BETA_MODE", "0").lower() in ("1", "true", "yes")


def _token_hash(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode()).hexdigest()


# ---------------------------------------------------------------------------
# Create
# ---------------------------------------------------------------------------


def create_beta_invite(
    db: Session,
    *,
    target_email: str,
    invited_by_user_id: Optional[str] = None,
    company_name: Optional[str] = None,
    plan_override: str = "pro",
    note: Optional[str] = None,
    expiry_hours: int = BETA_INVITE_TTL_HOURS,
) -> Tuple[str, models.BetaInvite]:
    """Create a beta invite. Returns (raw_token, invite_record)."""
    normalized = target_email.strip().lower()
    now = datetime.now(timezone.utc)

    existing = db.scalar(
        select(models.BetaInvite).where(
            func.lower(models.BetaInvite.target_email) == normalized,
            models.BetaInvite.used_at.is_(None),
            models.BetaInvite.revoked_at.is_(None),
            models.BetaInvite.expires_at > now,
        )
    )
    if existing:
        raise ValueError("An active beta invite already exists for this email.")

    raw_token = base64.urlsafe_b64encode(os.urandom(32)).decode().rstrip("=")

    invite = models.BetaInvite(
        target_email=normalized,
        company_name=company_name,
        invited_by=invited_by_user_id,
        token_hash=_token_hash(raw_token),
        plan_override=plan_override,
        note=note,
        expires_at=now + timedelta(hours=expiry_hours),
    )
    db.add(invite)
    db.commit()

    log.info(
        "beta_invite_created target=%s company=%s by=%s",
        normalized,
        company_name,
        invited_by_user_id,
    )
    return raw_token, invite


# ---------------------------------------------------------------------------
# Validate & consume
# ---------------------------------------------------------------------------


def validate_beta_invite(
    db: Session,
    *,
    raw_token: str,
    email: str,
) -> models.BetaInvite:
    """Validate a beta invite token. Returns the invite if valid."""
    token_h = _token_hash(raw_token.strip())
    now = datetime.now(timezone.utc)

    invite = db.scalar(
        select(models.BetaInvite).where(
            models.BetaInvite.token_hash == token_h,
        )
    )
    if invite is None:
        raise ValueError("Invalid or expired beta invite code.")

    if invite.used_at is not None:
        raise ValueError("This beta invite has already been used.")

    if invite.revoked_at is not None:
        raise ValueError("This beta invite has been revoked.")

    expires_at = invite.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at <= now:
        raise ValueError("This beta invite has expired. Please request a new one.")

    if email.strip().lower() != invite.target_email.strip().lower():
        raise ValueError("Email does not match the beta invite.")

    return invite


def consume_beta_invite(
    db: Session,
    *,
    invite: models.BetaInvite,
    user_id: str,
) -> None:
    """Mark a beta invite as used."""
    invite.used_at = datetime.now(timezone.utc)
    invite.used_by = user_id
    db.add(invite)
    db.commit()
    log.info("beta_invite_consumed invite_id=%s user_id=%s", invite.id, user_id)


# ---------------------------------------------------------------------------
# List & revoke
# ---------------------------------------------------------------------------


def list_beta_invites(
    db: Session,
    *,
    include_used: bool = False,
    include_revoked: bool = False,
) -> List[models.BetaInvite]:
    """List beta invites with optional filtering."""
    q = select(models.BetaInvite)
    if not include_used:
        q = q.where(models.BetaInvite.used_at.is_(None))
    if not include_revoked:
        q = q.where(models.BetaInvite.revoked_at.is_(None))
    return list(db.scalars(q.order_by(models.BetaInvite.created_at.desc())).all())


def revoke_beta_invite(db: Session, *, invite_id: str) -> bool:
    """Revoke a beta invite. Returns True if found and revoked."""
    invite = db.scalar(
        select(models.BetaInvite).where(models.BetaInvite.id == invite_id)
    )
    if not invite or invite.used_at or invite.revoked_at:
        return False
    invite.revoked_at = datetime.now(timezone.utc)
    db.commit()
    log.info("beta_invite_revoked invite_id=%s", invite_id)
    return True


def get_beta_stats(db: Session) -> dict:
    """Return beta program statistics."""
    now = datetime.now(timezone.utc)
    total = db.scalar(select(func.count()).select_from(models.BetaInvite)) or 0
    used = db.scalar(
        select(func.count())
        .select_from(models.BetaInvite)
        .where(models.BetaInvite.used_at.is_not(None))
    ) or 0
    active = db.scalar(
        select(func.count())
        .select_from(models.BetaInvite)
        .where(
            models.BetaInvite.used_at.is_(None),
            models.BetaInvite.revoked_at.is_(None),
            models.BetaInvite.expires_at > now,
        )
    ) or 0
    expired = db.scalar(
        select(func.count())
        .select_from(models.BetaInvite)
        .where(
            models.BetaInvite.used_at.is_(None),
            models.BetaInvite.revoked_at.is_(None),
            models.BetaInvite.expires_at <= now,
        )
    ) or 0
    revoked = db.scalar(
        select(func.count())
        .select_from(models.BetaInvite)
        .where(models.BetaInvite.revoked_at.is_not(None))
    ) or 0

    return {
        "beta_mode": BETA_MODE,
        "total_invites": total,
        "used": used,
        "active_pending": active,
        "expired": expired,
        "revoked": revoked,
        "conversion_rate": round(used / total * 100, 1) if total > 0 else 0,
    }


def is_beta_gated() -> bool:
    """Return True if registration requires a beta invite code."""
    return BETA_MODE
