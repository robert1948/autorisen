# backend/src/modules/auth/admin_router.py
"""
Routes for Developer and Admin registration flows.

Developer registration:
  POST /api/auth/register/developer — self-service developer signup

Admin invite management (admin-only):
  POST   /api/admin/invite         — create an admin invite
  GET    /api/admin/invites         — list all invites
  DELETE /api/admin/invite/{id}     — revoke a pending invite

Admin registration (invite-only):
  POST /api/admin/register          — register using an invite token
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from backend.src.db.session import get_db
from backend.src.modules.auth.csrf import require_csrf_token
from backend.src.modules.auth.deps import get_verified_user, require_roles
from backend.src.modules.auth.rate_limiter import auth_rate_limit
from backend.src.modules.auth.schemas import (
    AdminInviteIn,
    AdminInviteListOut,
    AdminInviteOut,
    AdminRegisterIn,
    AdminRegisterOut,
    DeveloperRegisterIn,
    DeveloperRegisterOut,
)

log = logging.getLogger("auth.admin_router")

# ---------------------------------------------------------------------------
# Developer registration router
# ---------------------------------------------------------------------------

developer_router = APIRouter(
    tags=["auth"],
    dependencies=[Depends(require_csrf_token)],
)

# ---------------------------------------------------------------------------
# Admin management router (requires admin role)
# ---------------------------------------------------------------------------

admin_router = APIRouter(
    tags=["admin"],
    dependencies=[Depends(require_csrf_token)],
)


# ===== Developer Registration =====


@developer_router.post(
    "/register/developer",
    response_model=DeveloperRegisterOut,
    status_code=201,
)
@auth_rate_limit()
async def register_developer(
    payload: DeveloperRegisterIn,
    request: Request,
    db: Session = Depends(get_db),
    _: None = Depends(require_csrf_token),
):
    """
    Self-service developer registration.

    Creates a user with role=Developer, a developer_profile,
    and returns auth tokens. Email verification required before
    API credentials can be provisioned.
    """
    from backend.src.modules.auth.admin_service import (
        register_developer as svc_register_developer,
    )
    from backend.src.modules.auth.service import DuplicateEmailError

    try:
        access_token, refresh_token, expires_at, user = svc_register_developer(
            db,
            first_name=payload.first_name,
            last_name=payload.last_name,
            email=payload.email,
            password=payload.password,
            company_name=payload.company_name,
            terms_accepted=payload.terms_accepted,
            organization=payload.organization,
            use_case=payload.use_case,
            website_url=payload.website_url,
            github_url=payload.github_url,
        )
    except DuplicateEmailError:
        raise HTTPException(
            status_code=409,
            detail="An account with this email may already exist.",
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        log.exception("developer_register_error email=%s: %s", payload.email, exc)
        raise HTTPException(status_code=500, detail="Registration failed.")

    # Dispatch verification email
    try:
        from backend.src.modules.auth.router import (
            _dispatch_verification_email,
            _get_user_by_email,
        )

        user_obj = _get_user_by_email(db, payload.email)
        if user_obj and not getattr(user_obj, "is_email_verified", False):
            _dispatch_verification_email(user_obj)
    except Exception as exc:
        log.warning("developer_verification_email_failed email=%s: %s", payload.email, exc)

    return DeveloperRegisterOut(
        access_token=access_token,
        refresh_token=refresh_token,
        email_verified=False,
    )


# ===== Admin Invite Management =====


@admin_router.post(
    "/invite",
    response_model=AdminInviteOut,
    status_code=201,
)
async def create_invite(
    payload: AdminInviteIn,
    request: Request,
    db: Session = Depends(get_db),
    current_user: Any = Depends(require_roles("admin")),
):
    """
    Create an admin invite (admin-only).

    Generates a signed invite token and sends an invite email.
    """
    from backend.src.modules.auth.admin_service import create_admin_invite

    try:
        raw_token, invite = create_admin_invite(
            db,
            target_email=payload.target_email,
            invited_by_user_id=current_user.id,
            expiry_hours=payload.expiry_hours,
        )
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    except Exception as exc:
        log.exception("admin_invite_error: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to create invite.")

    # TODO: send invite email with raw_token
    # The invite link format: {frontend_origin}/auth/register?invite={raw_token}&email={target_email}
    log.info(
        "admin_invite_created id=%s target=%s by=%s",
        invite.id,
        payload.target_email,
        current_user.id,
    )

    return AdminInviteOut(
        invite_id=invite.id,
        target_email=invite.target_email,
        expires_at=invite.expires_at,
    )


@admin_router.get(
    "/invites",
    response_model=List[AdminInviteListOut],
)
async def list_invites(
    db: Session = Depends(get_db),
    current_user: Any = Depends(require_roles("admin")),
):
    """List all admin invites (admin-only)."""
    from backend.src.modules.auth.admin_service import list_admin_invites

    invites = list_admin_invites(db)
    return [
        AdminInviteListOut(
            id=inv.id,
            target_email=inv.target_email,
            invited_by=inv.invited_by,
            created_at=inv.created_at,
            expires_at=inv.expires_at,
            used_at=inv.used_at,
            revoked_at=inv.revoked_at,
        )
        for inv in invites
    ]


@admin_router.delete(
    "/invite/{invite_id}",
    status_code=200,
)
async def revoke_invite(
    invite_id: str,
    db: Session = Depends(get_db),
    current_user: Any = Depends(require_roles("admin")),
):
    """Revoke a pending admin invite (admin-only)."""
    from backend.src.modules.auth.admin_service import revoke_admin_invite

    try:
        revoke_admin_invite(db, invite_id=invite_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return {"message": "Invite revoked."}


# ===== Admin Registration (invite-only) =====


@admin_router.post(
    "/register",
    response_model=AdminRegisterOut,
    status_code=201,
)
@auth_rate_limit()
async def register_admin(
    payload: AdminRegisterIn,
    request: Request,
    db: Session = Depends(get_db),
    _: None = Depends(require_csrf_token),
):
    """
    Register a new admin using an invite token.

    No authentication required (the invite token is the auth).
    Email is pre-verified since the invite was sent to that address.
    """
    from backend.src.modules.auth.admin_service import register_admin as svc_register_admin
    from backend.src.modules.auth.service import DuplicateEmailError

    try:
        access_token, refresh_token, expires_at, user = svc_register_admin(
            db,
            invite_token=payload.invite_token,
            first_name=payload.first_name,
            last_name=payload.last_name,
            email=payload.email,
            password=payload.password,
            company_name=payload.company_name,
            terms_accepted=payload.terms_accepted,
        )
    except DuplicateEmailError:
        raise HTTPException(
            status_code=409,
            detail="An account with this email may already exist.",
        )
    except ValueError as exc:
        detail = str(exc)
        # Map invite-specific errors to appropriate status codes
        if "expired" in detail.lower() or "invalid" in detail.lower():
            raise HTTPException(status_code=403, detail=detail)
        if "revoked" in detail.lower():
            raise HTTPException(status_code=403, detail=detail)
        if "already been used" in detail.lower():
            raise HTTPException(status_code=403, detail=detail)
        if "does not match" in detail.lower():
            raise HTTPException(status_code=403, detail=detail)
        raise HTTPException(status_code=400, detail=detail)
    except Exception as exc:
        log.exception("admin_register_error email=%s: %s", payload.email, exc)
        raise HTTPException(status_code=500, detail="Registration failed.")

    return AdminRegisterOut(
        access_token=access_token,
        refresh_token=refresh_token,
        email_verified=True,
    )
