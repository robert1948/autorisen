"""Audit module — FastAPI router for evidence export & audit events."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from backend.src.db import models
from backend.src.db.session import get_session
from backend.src.modules.auth.deps import get_verified_user
from backend.src.modules.rag.evidence import EvidencePack, generate_evidence_pack

from .pdf_renderer import render_evidence_pdf

log = logging.getLogger(__name__)

router = APIRouter(prefix="/audit", tags=["audit"])


# ------------------------------------------------------------------
# Evidence pack export  (JSON **or** PDF)
# ------------------------------------------------------------------

@router.get("/export")
def export_evidence(
    format: str = Query("pdf", description="Export format: 'pdf' or 'json'"),
    period_start: Optional[datetime] = Query(None, description="ISO datetime filter start"),
    period_end: Optional[datetime] = Query(None, description="ISO datetime filter end"),
    current_user: models.User = Depends(get_verified_user),
    db: Session = Depends(get_session),
):
    """Export a full evidence pack for compliance review.

    Supports two formats:
    - **pdf** (default): Branded PDF document suitable for board packs
    - **json**: Raw JSON data for programmatic consumption

    Both formats contain identical data: all approved documents (metadata),
    RAG query logs with full provenance, and summary statistics.
    """
    fmt = format.lower().strip()
    if fmt not in ("pdf", "json"):
        raise HTTPException(status_code=400, detail="format must be 'pdf' or 'json'")

    pack = generate_evidence_pack(
        db,
        current_user,
        period_start=period_start,
        period_end=period_end,
    )

    if fmt == "json":
        return pack

    # PDF export
    try:
        pdf_bytes = render_evidence_pdf(pack)
    except Exception:
        log.exception("PDF rendering failed")
        raise HTTPException(status_code=500, detail="Failed to generate PDF")

    filename = f"evidence-pack-{pack.export_id[:8]}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
        },
    )


# ------------------------------------------------------------------
# Audit events listing
# ------------------------------------------------------------------

@router.get("/events")
def list_audit_events(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    event_type: Optional[str] = Query(None, description="Filter by event_type"),
    current_user: models.User = Depends(get_verified_user),
    db: Session = Depends(get_session),
):
    """List audit events for the authenticated user.

    Returns recent audit trail entries. Admin users see all events;
    regular users see only their own.
    """
    q = select(models.AuditEvent)

    # Non-admin users see only their own events
    is_admin = getattr(current_user, "role", None) == "admin"
    if not is_admin:
        q = q.where(models.AuditEvent.user_id == current_user.id)

    if event_type:
        q = q.where(models.AuditEvent.event_type == event_type)

    total_q = select(func.count()).select_from(q.subquery())
    total = db.scalar(total_q) or 0

    q = q.order_by(models.AuditEvent.created_at.desc()).offset(offset).limit(limit)
    events = db.scalars(q).all()

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "events": [
            {
                "id": str(e.id),
                "event_type": e.event_type,
                "user_id": e.user_id,
                "agent_id": e.agent_id,
                "payload": e.event_data,
                "ip_address": e.ip_address,
                "created_at": e.created_at.isoformat() if e.created_at else None,
            }
            for e in events
        ],
    }


# ------------------------------------------------------------------
# Audit summary stats
# ------------------------------------------------------------------

@router.get("/stats")
def audit_stats(
    current_user: models.User = Depends(get_verified_user),
    db: Session = Depends(get_session),
):
    """Get summary audit statistics for the current user."""
    is_admin = getattr(current_user, "role", None) == "admin"

    base = select(models.AuditEvent)
    if not is_admin:
        base = base.where(models.AuditEvent.user_id == current_user.id)

    total = db.scalar(select(func.count()).select_from(base.subquery())) or 0

    # Event type breakdown
    type_q = (
        select(models.AuditEvent.event_type, func.count().label("cnt"))
        .group_by(models.AuditEvent.event_type)
    )
    if not is_admin:
        type_q = type_q.where(models.AuditEvent.user_id == current_user.id)
    type_rows = db.execute(type_q).all()
    type_breakdown = {row[0]: row[1] for row in type_rows}

    # Login audit stats
    login_q = select(func.count()).select_from(models.LoginAudit)
    if not is_admin:
        login_q = login_q.where(models.LoginAudit.email == current_user.email)
    login_total = db.scalar(login_q) or 0

    failed_q = select(func.count()).select_from(models.LoginAudit).where(
        models.LoginAudit.success == False  # noqa: E712
    )
    if not is_admin:
        failed_q = failed_q.where(models.LoginAudit.email == current_user.email)
    login_failed = db.scalar(failed_q) or 0

    return {
        "total_events": total,
        "event_types": type_breakdown,
        "login_attempts": login_total,
        "failed_logins": login_failed,
    }
