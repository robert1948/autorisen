"""Service layer for the Developer Dashboard module."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import List, Optional, Tuple

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.src.db import models
from backend.src.modules.auth.admin_service import (
    provision_api_credentials,
)

log = logging.getLogger("dev.service")


# ---------------------------------------------------------------------------
# Developer Profile
# ---------------------------------------------------------------------------


def get_developer_profile(
    db: Session,
    *,
    user: models.User,
) -> Optional[models.DeveloperProfile]:
    """Return the DeveloperProfile for a user, or None."""
    return db.scalar(
        select(models.DeveloperProfile).where(
            models.DeveloperProfile.user_id == user.id,
        )
    )


def update_developer_profile(
    db: Session,
    *,
    user: models.User,
    organization: Optional[str] = None,
    use_case: Optional[str] = None,
    website_url: Optional[str] = None,
    github_url: Optional[str] = None,
) -> models.DeveloperProfile:
    """Update editable fields on the developer profile.

    Creates the profile row if it doesn't exist yet (defensive).
    """
    profile = get_developer_profile(db, user=user)
    if profile is None:
        profile = models.DeveloperProfile(user_id=user.id)
        db.add(profile)

    if organization is not None:
        profile.organization = organization
    if use_case is not None:
        profile.use_case = use_case
    if website_url is not None:
        profile.website_url = website_url
    if github_url is not None:
        profile.github_url = github_url

    db.commit()
    db.refresh(profile)
    log.info("developer_profile_updated user_id=%s", user.id)
    return profile


# ---------------------------------------------------------------------------
# API Credentials
# ---------------------------------------------------------------------------


def list_api_credentials(
    db: Session,
    *,
    user_id: str,
) -> List[models.ApiCredential]:
    """Return all API credentials for a developer (active + revoked)."""
    return list(
        db.scalars(
            select(models.ApiCredential)
            .where(models.ApiCredential.user_id == user_id)
            .order_by(models.ApiCredential.created_at.desc())
        )
    )


def create_api_credential(
    db: Session,
    *,
    user_id: str,
    label: str = "Default",
) -> Tuple[str, str, models.ApiCredential]:
    """Provision a new API credential and return (client_id, client_secret, record).

    Delegates to admin_service.provision_api_credentials, then reloads the record.
    """
    client_id, client_secret = provision_api_credentials(
        db, user_id=user_id, label=label
    )
    # Load the freshly-created record
    cred = db.scalar(
        select(models.ApiCredential).where(
            models.ApiCredential.client_id == client_id,
        )
    )
    return client_id, client_secret, cred


def revoke_api_credential(
    db: Session,
    *,
    credential_id: str,
    user_id: str,
) -> models.ApiCredential:
    """Revoke an API credential owned by the given user.

    Raises ValueError if not found, already revoked, or not owned by user.
    """
    cred = db.get(models.ApiCredential, credential_id)
    if cred is None:
        raise ValueError("API credential not found.")
    if cred.user_id != user_id:
        raise ValueError("API credential not found.")  # no info leak
    if cred.revoked_at is not None:
        raise ValueError("API credential already revoked.")

    cred.revoked_at = datetime.now(timezone.utc)
    cred.is_active = False
    db.add(cred)
    db.commit()

    log.info(
        "api_credential_revoked user_id=%s credential_id=%s client_id=%s",
        user_id,
        credential_id,
        cred.client_id,
    )
    return cred


# ---------------------------------------------------------------------------
# Usage / Stats
# ---------------------------------------------------------------------------


def get_developer_usage(
    db: Session,
    *,
    user_id: str,
    user: models.User,
) -> dict:
    """Return aggregated usage stats for the developer dashboard."""
    creds = list_api_credentials(db, user_id=user_id)
    return {
        "total_api_keys": len(creds),
        "active_api_keys": sum(1 for c in creds if c.is_active),
        "revoked_api_keys": sum(1 for c in creds if c.revoked_at is not None),
        "account_created_at": getattr(user, "created_at", None),
        "email_verified": getattr(user, "is_email_verified", False),
    }
