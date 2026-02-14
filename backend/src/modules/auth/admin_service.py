"""Service layer for Developer and Admin registration flows."""

from __future__ import annotations

import base64
import hashlib
import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Tuple
from uuid import uuid4

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.src.core.config import settings
from backend.src.db import models
from backend.src.modules.auth.schemas import UserRole
from backend.src.modules.auth.service import (
    DuplicateEmailError,
    _generate_refresh_token,
    _create_session,
    _is_unique_violation,
    _normalize_email,
    _token_version_for,
    ensure_email_available,
    ACCESS_TOKEN_PURPOSE,
    TERMS_VERSION_DEFAULT,
)
from backend.src.services.security import create_jwt, hash_password

log = logging.getLogger("auth.admin")

ADMIN_INVITE_TTL_HOURS = int(os.getenv("ADMIN_INVITE_TTL_HOURS", "48"))
DEVELOPER_TERMS_VERSION = os.getenv("DEVELOPER_TERMS_VERSION", "dev-v1")


def _invite_token_hash(raw_token: str) -> str:
    """Hash an invite token for safe storage."""
    return hashlib.sha256(raw_token.encode()).hexdigest()


def _generate_client_id() -> str:
    """Generate a unique client_id for developer API credentials."""
    return f"cc_{base64.urlsafe_b64encode(os.urandom(24)).decode().rstrip('=')}"


def _generate_client_secret() -> str:
    """Generate a cryptographically random client secret."""
    return base64.urlsafe_b64encode(os.urandom(48)).decode().rstrip("=")


# ---------------------------------------------------------------------------
# Developer registration
# ---------------------------------------------------------------------------


def register_developer(
    db: Session,
    *,
    first_name: str,
    last_name: str,
    email: str,
    password: str,
    company_name: str = "",
    terms_accepted: bool = True,
    organization: Optional[str] = None,
    use_case: Optional[str] = None,
    website_url: Optional[str] = None,
    github_url: Optional[str] = None,
) -> Tuple[str, str, datetime, models.User]:
    """
    Create a user with the Developer role, a developer profile,
    and return access/refresh tokens.

    API credentials are provisioned separately after email verification.
    """
    normalized_email = _normalize_email(email)
    ensure_email_available(db, normalized_email)

    now = datetime.now(timezone.utc)
    password_hash = hash_password(password)

    user = models.User(
        email=normalized_email,
        first_name=first_name.strip(),
        last_name=last_name.strip(),
        full_name=f"{first_name.strip()} {last_name.strip()}".strip(),
        role=UserRole.DEVELOPER.value,
        hashed_password=password_hash,
        company_name=company_name,
        is_email_verified=False,
        password_changed_at=now,
    )
    if terms_accepted:
        user.terms_accepted_at = now
        user.terms_version = TERMS_VERSION_DEFAULT

    credential = models.Credential(
        user=user,
        provider="password",
        provider_uid=normalized_email,
        secret_hash=password_hash,
    )

    dev_profile = models.DeveloperProfile(
        user=user,
        organization=organization,
        use_case=use_case,
        website_url=website_url,
        github_url=github_url,
        developer_terms_accepted_at=now,
        developer_terms_version=DEVELOPER_TERMS_VERSION,
    )

    # Standard profile (same as normal registration)
    user_profile = models.UserProfile(profile={})
    setattr(user, "profile", user_profile)

    try:
        db.add(user)
        db.add(credential)
        db.add(dev_profile)
        db.flush()

        refresh_token = _generate_refresh_token()
        _create_session(db, user, refresh_token)

        token_version = _token_version_for(user)
        access_payload = {
            "sub": user.email,
            "user_id": user.id,
            "role": user.role,
            "purpose": ACCESS_TOKEN_PURPOSE,
            "jti": str(uuid4()),
            "token_version": token_version,
        }
        access_token, expires_at = create_jwt(
            access_payload, settings.access_token_ttl_minutes
        )

        db.commit()
    except IntegrityError as exc:
        db.rollback()
        if _is_unique_violation(exc):
            raise DuplicateEmailError("Email already registered.") from exc
        raise

    log.info(
        "developer_registered user_id=%s email=%s", user.id, normalized_email
    )
    return access_token, refresh_token, expires_at, user


def provision_api_credentials(
    db: Session,
    *,
    user_id: str,
    label: Optional[str] = None,
) -> Tuple[str, str]:
    """
    Generate and store API credentials for a verified developer.

    Returns (client_id, client_secret). The client_secret is only shown once.
    """
    client_id = _generate_client_id()
    client_secret = _generate_client_secret()
    secret_hash = hashlib.sha256(client_secret.encode()).hexdigest()

    api_cred = models.ApiCredential(
        user_id=user_id,
        client_id=client_id,
        client_secret_hash=secret_hash,
        label=label or "Default",
    )
    db.add(api_cred)
    db.commit()

    log.info("api_credentials_provisioned user_id=%s client_id=%s", user_id, client_id)
    return client_id, client_secret


# ---------------------------------------------------------------------------
# Admin invite
# ---------------------------------------------------------------------------


def create_admin_invite(
    db: Session,
    *,
    target_email: str,
    invited_by_user_id: str,
    expiry_hours: int = ADMIN_INVITE_TTL_HOURS,
) -> Tuple[str, models.AdminInvite]:
    """
    Create an admin invite token.

    Only callable by existing admins. Returns (raw_token, invite_record).
    """
    normalized_email = _normalize_email(target_email)
    now = datetime.now(timezone.utc)

    # Check for existing unused invite for the same email
    existing = db.scalar(
        select(models.AdminInvite).where(
            func.lower(models.AdminInvite.target_email) == normalized_email,
            models.AdminInvite.used_at.is_(None),
            models.AdminInvite.revoked_at.is_(None),
            models.AdminInvite.expires_at > now,
        )
    )
    if existing:
        raise ValueError("An active invite already exists for this email.")

    raw_token = base64.urlsafe_b64encode(os.urandom(32)).decode().rstrip("=")
    token_hash = _invite_token_hash(raw_token)

    invite = models.AdminInvite(
        target_email=normalized_email,
        invited_by=invited_by_user_id,
        token_hash=token_hash,
        expires_at=now + timedelta(hours=expiry_hours),
    )
    db.add(invite)
    db.commit()

    log.info(
        "admin_invite_created target=%s by=%s expires_hours=%d",
        normalized_email,
        invited_by_user_id,
        expiry_hours,
    )
    return raw_token, invite


def validate_admin_invite(
    db: Session,
    *,
    raw_token: str,
    email: str,
) -> models.AdminInvite:
    """
    Validate an admin invite token. Returns the invite record if valid.
    Raises ValueError with a user-friendly message if invalid.
    """
    token_hash = _invite_token_hash(raw_token.strip())
    now = datetime.now(timezone.utc)

    invite = db.scalar(
        select(models.AdminInvite).where(
            models.AdminInvite.token_hash == token_hash,
        )
    )

    if invite is None:
        raise ValueError("Invalid or expired invite.")

    if invite.used_at is not None:
        raise ValueError("This invite has already been used.")

    if invite.revoked_at is not None:
        raise ValueError("This invite has been revoked.")

    expires_at = invite.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at <= now:
        raise ValueError("This invite has expired. Please request a new one.")

    if _normalize_email(email) != _normalize_email(invite.target_email):
        raise ValueError("Email does not match the invite.")

    return invite


def register_admin(
    db: Session,
    *,
    invite_token: str,
    first_name: str,
    last_name: str,
    email: str,
    password: str,
    company_name: str = "",
    terms_accepted: bool = True,
) -> Tuple[str, str, datetime, models.User]:
    """
    Register a new admin user using an invite token.

    The invite is consumed within the same transaction.
    Email is pre-verified since the invite was sent to that email.
    """
    # Validate the invite first
    invite = validate_admin_invite(db, raw_token=invite_token, email=email)

    normalized_email = _normalize_email(email)
    ensure_email_available(db, normalized_email)

    now = datetime.now(timezone.utc)
    password_hash = hash_password(password)

    user = models.User(
        email=normalized_email,
        first_name=first_name.strip(),
        last_name=last_name.strip(),
        full_name=f"{first_name.strip()} {last_name.strip()}".strip(),
        role=UserRole.ADMIN.value,
        hashed_password=password_hash,
        company_name=company_name,
        is_email_verified=True,  # Invite proves email ownership
        email_verified_at=now,
        password_changed_at=now,
    )
    if terms_accepted:
        user.terms_accepted_at = now
        user.terms_version = TERMS_VERSION_DEFAULT

    credential = models.Credential(
        user=user,
        provider="password",
        provider_uid=normalized_email,
        secret_hash=password_hash,
    )

    # Standard profile
    user_profile = models.UserProfile(profile={})
    setattr(user, "profile", user_profile)

    try:
        db.add(user)
        db.add(credential)
        db.flush()

        # Consume the invite
        invite.used_at = now
        invite.used_by = user.id
        db.add(invite)

        refresh_token = _generate_refresh_token()
        _create_session(db, user, refresh_token)

        token_version = _token_version_for(user)
        access_payload = {
            "sub": user.email,
            "user_id": user.id,
            "role": user.role,
            "purpose": ACCESS_TOKEN_PURPOSE,
            "jti": str(uuid4()),
            "token_version": token_version,
        }
        access_token, expires_at = create_jwt(
            access_payload, settings.access_token_ttl_minutes
        )

        db.commit()
    except IntegrityError as exc:
        db.rollback()
        if _is_unique_violation(exc):
            raise DuplicateEmailError("Email already registered.") from exc
        raise

    log.info(
        "admin_registered user_id=%s email=%s invited_by=%s",
        user.id,
        normalized_email,
        invite.invited_by,
    )
    return access_token, refresh_token, expires_at, user


def list_admin_invites(
    db: Session,
) -> list[models.AdminInvite]:
    """List all admin invites (for admin dashboard)."""
    return list(
        db.scalars(
            select(models.AdminInvite).order_by(
                models.AdminInvite.created_at.desc()
            )
        )
    )


def revoke_admin_invite(
    db: Session,
    *,
    invite_id: str,
) -> models.AdminInvite:
    """Revoke a pending admin invite."""
    invite = db.get(models.AdminInvite, invite_id)
    if invite is None:
        raise ValueError("Invite not found.")
    if invite.used_at is not None:
        raise ValueError("Cannot revoke an already-used invite.")
    if invite.revoked_at is not None:
        raise ValueError("Invite already revoked.")

    invite.revoked_at = datetime.now(timezone.utc)
    db.add(invite)
    db.commit()

    log.info("admin_invite_revoked invite_id=%s", invite_id)
    return invite
