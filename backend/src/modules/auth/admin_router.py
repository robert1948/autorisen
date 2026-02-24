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


# ===================================================================
# Beta Invite Management (admin-only)
# ===================================================================


@admin_router.post("/beta/invite", status_code=201)
async def create_beta_invite_endpoint(
    request: Request,
    payload: dict,
    db: Session = Depends(get_db),
    current_user: Any = Depends(require_roles("admin")),
):
    """Create a beta invite for a prospective pilot user (admin-only).

    Body: { "target_email": str, "company_name"?: str, "plan_override"?: str, "note"?: str }
    """
    from backend.src.modules.auth.beta_service import create_beta_invite

    target_email = payload.get("target_email")
    if not target_email:
        raise HTTPException(status_code=400, detail="target_email is required")

    try:
        raw_token, invite = create_beta_invite(
            db,
            target_email=target_email,
            invited_by_user_id=current_user.id,
            company_name=payload.get("company_name"),
            plan_override=payload.get("plan_override", "pro"),
            note=payload.get("note"),
        )
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc))

    # Send beta invite email
    try:
        from backend.src.services.emailer import send_beta_invite_email

        send_beta_invite_email(
            email=target_email,
            invite_token=raw_token,
            company_name=payload.get("company_name"),
        )
    except Exception as exc:
        log.warning("beta_invite_email_failed target=%s: %s", target_email, exc)

    return {
        "invite_id": invite.id,
        "target_email": invite.target_email,
        "company_name": invite.company_name,
        "plan_override": invite.plan_override,
        "expires_at": invite.expires_at.isoformat(),
        "token": raw_token,
    }


@admin_router.get("/beta/invites")
async def list_beta_invites_endpoint(
    include_used: bool = False,
    include_revoked: bool = False,
    db: Session = Depends(get_db),
    current_user: Any = Depends(require_roles("admin")),
):
    """List beta invites (admin-only)."""
    from backend.src.modules.auth.beta_service import list_beta_invites

    invites = list_beta_invites(
        db, include_used=include_used, include_revoked=include_revoked
    )
    return [
        {
            "id": inv.id,
            "target_email": inv.target_email,
            "company_name": inv.company_name,
            "plan_override": inv.plan_override,
            "note": inv.note,
            "invited_by": inv.invited_by,
            "created_at": inv.created_at.isoformat() if inv.created_at else None,
            "expires_at": inv.expires_at.isoformat() if inv.expires_at else None,
            "used_at": inv.used_at.isoformat() if inv.used_at else None,
            "revoked_at": inv.revoked_at.isoformat() if inv.revoked_at else None,
        }
        for inv in invites
    ]


@admin_router.delete("/beta/invite/{invite_id}")
async def revoke_beta_invite_endpoint(
    invite_id: str,
    db: Session = Depends(get_db),
    current_user: Any = Depends(require_roles("admin")),
):
    """Revoke a pending beta invite (admin-only)."""
    from backend.src.modules.auth.beta_service import revoke_beta_invite

    if not revoke_beta_invite(db, invite_id=invite_id):
        raise HTTPException(status_code=404, detail="Invite not found or already used/revoked.")
    return {"message": "Beta invite revoked."}


@admin_router.get("/beta/stats")
async def beta_stats_endpoint(
    db: Session = Depends(get_db),
    current_user: Any = Depends(require_roles("admin")),
):
    """Return beta program statistics (admin-only)."""
    from backend.src.modules.auth.beta_service import get_beta_stats

    return get_beta_stats(db)
