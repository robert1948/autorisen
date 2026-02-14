# backend/src/modules/dev/router.py
"""
Developer Dashboard API routes.

All endpoints require an authenticated, email-verified user with the
Developer (or Admin) role.

Endpoints:
  GET    /api/dev/profile           — developer profile
  PATCH  /api/dev/profile           — update developer profile
  GET    /api/dev/api-keys          — list API credentials
  POST   /api/dev/api-keys          — provision a new API credential
  DELETE /api/dev/api-keys/{id}     — revoke an API credential
  GET    /api/dev/usage             — aggregated usage stats
"""

from __future__ import annotations

import logging
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from backend.src.db.session import get_db
from backend.src.modules.auth.csrf import require_csrf_token
from backend.src.modules.auth.deps import require_roles
from backend.src.modules.dev.schemas import (
    ApiCredentialCreateIn,
    ApiCredentialCreateOut,
    ApiCredentialOut,
    DeveloperProfileOut,
    DeveloperProfileUpdateIn,
    DeveloperUsageOut,
)

log = logging.getLogger("dev.router")

router = APIRouter(
    tags=["developer"],
    dependencies=[Depends(require_csrf_token)],
)

_developer_or_admin = require_roles("developer", "admin")


# ---------------------------------------------------------------------------
# Developer Profile
# ---------------------------------------------------------------------------


@router.get("/profile", response_model=DeveloperProfileOut)
async def get_profile(
    db: Session = Depends(get_db),
    current_user: Any = Depends(_developer_or_admin),
):
    """Return the developer profile for the authenticated user."""
    from backend.src.modules.dev.service import get_developer_profile

    profile = get_developer_profile(db, user=current_user)

    return DeveloperProfileOut(
        user_id=current_user.id,
        email=current_user.email,
        first_name=current_user.first_name or "",
        last_name=current_user.last_name or "",
        organization=getattr(profile, "organization", None) if profile else None,
        use_case=getattr(profile, "use_case", None) if profile else None,
        website_url=getattr(profile, "website_url", None) if profile else None,
        github_url=getattr(profile, "github_url", None) if profile else None,
        developer_terms_accepted_at=(
            getattr(profile, "developer_terms_accepted_at", None) if profile else None
        ),
        developer_terms_version=(
            getattr(profile, "developer_terms_version", None) if profile else None
        ),
        created_at=current_user.created_at,
        email_verified=getattr(current_user, "is_email_verified", False),
    )


@router.patch("/profile", response_model=DeveloperProfileOut)
async def update_profile(
    payload: DeveloperProfileUpdateIn,
    db: Session = Depends(get_db),
    current_user: Any = Depends(_developer_or_admin),
):
    """Update editable fields on the developer profile."""
    from backend.src.modules.dev.service import update_developer_profile

    profile = update_developer_profile(
        db,
        user=current_user,
        organization=payload.organization,
        use_case=payload.use_case,
        website_url=payload.website_url,
        github_url=payload.github_url,
    )

    return DeveloperProfileOut(
        user_id=current_user.id,
        email=current_user.email,
        first_name=current_user.first_name or "",
        last_name=current_user.last_name or "",
        organization=profile.organization,
        use_case=profile.use_case,
        website_url=profile.website_url,
        github_url=profile.github_url,
        developer_terms_accepted_at=profile.developer_terms_accepted_at,
        developer_terms_version=profile.developer_terms_version,
        created_at=current_user.created_at,
        email_verified=getattr(current_user, "is_email_verified", False),
    )


# ---------------------------------------------------------------------------
# API Credentials
# ---------------------------------------------------------------------------


@router.get("/api-keys", response_model=List[ApiCredentialOut])
async def list_api_keys(
    db: Session = Depends(get_db),
    current_user: Any = Depends(_developer_or_admin),
):
    """List all API credentials for the authenticated developer."""
    from backend.src.modules.dev.service import list_api_credentials

    creds = list_api_credentials(db, user_id=current_user.id)
    return [
        ApiCredentialOut(
            id=c.id,
            client_id=c.client_id,
            label=c.label,
            is_active=c.is_active,
            created_at=c.created_at,
            revoked_at=c.revoked_at,
        )
        for c in creds
    ]


@router.post(
    "/api-keys",
    response_model=ApiCredentialCreateOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_api_key(
    payload: ApiCredentialCreateIn,
    request: Request,
    db: Session = Depends(get_db),
    current_user: Any = Depends(_developer_or_admin),
):
    """Provision a new API credential.

    The ``client_secret`` is returned once and never stored in plain text.
    """
    from backend.src.modules.dev.service import create_api_credential

    if not getattr(current_user, "is_email_verified", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email must be verified before provisioning API credentials.",
        )

    try:
        client_id, client_secret, cred = create_api_credential(
            db, user_id=current_user.id, label=payload.label
        )
    except Exception as exc:
        log.exception("api_key_provision_error user_id=%s: %s", current_user.id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to provision API credential.",
        )

    log.info(
        "api_key_provisioned user_id=%s client_id=%s",
        current_user.id,
        client_id,
    )

    return ApiCredentialCreateOut(
        id=cred.id,
        client_id=client_id,
        client_secret=client_secret,
        label=cred.label or payload.label,
        created_at=cred.created_at,
    )


@router.delete("/api-keys/{credential_id}", status_code=status.HTTP_200_OK)
async def revoke_api_key(
    credential_id: str,
    db: Session = Depends(get_db),
    current_user: Any = Depends(_developer_or_admin),
):
    """Revoke an API credential owned by the authenticated developer."""
    from backend.src.modules.dev.service import revoke_api_credential

    try:
        revoke_api_credential(
            db, credential_id=credential_id, user_id=current_user.id
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        )

    return {"message": "API credential revoked."}


# ---------------------------------------------------------------------------
# Usage / Stats
# ---------------------------------------------------------------------------


@router.get("/usage", response_model=DeveloperUsageOut)
async def get_usage(
    db: Session = Depends(get_db),
    current_user: Any = Depends(_developer_or_admin),
):
    """Return aggregated usage stats for the developer dashboard."""
    from backend.src.modules.dev.service import get_developer_usage

    stats = get_developer_usage(db, user_id=current_user.id, user=current_user)
    return DeveloperUsageOut(**stats)
