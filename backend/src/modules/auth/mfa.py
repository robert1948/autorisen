"""MFA (TOTP authenticator) endpoints — setup, verify, disable, status."""

from __future__ import annotations

import base64
import io
import logging
from datetime import datetime, timezone
from typing import Optional

import pyotp
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.src.core.crypto import decrypt_secret, encrypt_secret
from backend.src.db.models import MfaFactor
from backend.src.db.session import get_db
from backend.src.modules.auth.deps import get_verified_user

log = logging.getLogger(__name__)

router = APIRouter(prefix="/mfa", tags=["mfa"])

# ── Pydantic schemas ──────────────────────────────────────────────────────────


class MfaStatusOut(BaseModel):
    enabled: bool
    type: Optional[str] = None
    enabled_at: Optional[str] = None


class MfaSetupOut(BaseModel):
    secret: str
    otpauth_uri: str
    qr_svg: str  # inline SVG data-URI for the QR code


class MfaVerifyIn(BaseModel):
    code: str = Field(..., min_length=6, max_length=6, pattern=r"^\d{6}$")


class MfaVerifyOut(BaseModel):
    verified: bool
    message: str


class MfaDisableIn(BaseModel):
    code: str = Field(..., min_length=6, max_length=6, pattern=r"^\d{6}$")


# ── Helpers ───────────────────────────────────────────────────────────────────


def _generate_qr_svg(data: str, box_size: int = 6) -> str:
    """Generate a minimal SVG QR code without external dependencies.

    Uses pyotp-compatible otpauth URI.  We build a simple matrix-based SVG
    using the ``qrcode`` library if available, otherwise fall back to a
    placeholder that tells the user to enter the secret manually.
    """
    try:
        import qrcode  # type: ignore[import-untyped]
        from qrcode.image.svg import SvgPathImage  # type: ignore[import-untyped]

        img = qrcode.make(data, image_factory=SvgPathImage, box_size=box_size, border=2)
        buf = io.BytesIO()
        img.save(buf)
        svg_bytes = buf.getvalue()
        return "data:image/svg+xml;base64," + base64.b64encode(svg_bytes).decode()
    except ImportError:
        # qrcode not installed — return a text placeholder SVG
        svg = (
            "<svg xmlns='http://www.w3.org/2000/svg' width='200' height='200'>"
            "<rect width='100%' height='100%' fill='#0b1220'/>"
            "<text x='50%' y='45%' fill='#fff' font-size='11' text-anchor='middle'>"
            "Scan not available</text>"
            "<text x='50%' y='60%' fill='#aaa' font-size='10' text-anchor='middle'>"
            "Enter secret manually</text>"
            "</svg>"
        )
        return "data:image/svg+xml;utf8," + svg


def _get_enabled_factor(db: Session, user_id: str) -> Optional[MfaFactor]:
    return (
        db.query(MfaFactor)
        .filter(MfaFactor.user_id == user_id, MfaFactor.enabled_at.isnot(None))
        .first()
    )


def _get_pending_factor(db: Session, user_id: str) -> Optional[MfaFactor]:
    return (
        db.query(MfaFactor)
        .filter(MfaFactor.user_id == user_id, MfaFactor.enabled_at.is_(None))
        .first()
    )


# ── Endpoints ─────────────────────────────────────────────────────────────────


@router.get("/status", response_model=MfaStatusOut)
async def mfa_status(
    user: dict = Depends(get_verified_user),
    db: Session = Depends(get_db),
):
    """Return whether MFA is enabled for the current user."""
    factor = _get_enabled_factor(db, user["id"])
    if factor:
        return MfaStatusOut(
            enabled=True,
            type=factor.type,
            enabled_at=factor.enabled_at.isoformat() if factor.enabled_at else None,
        )
    return MfaStatusOut(enabled=False)


@router.post("/setup", response_model=MfaSetupOut)
async def mfa_setup(
    user: dict = Depends(get_verified_user),
    db: Session = Depends(get_db),
):
    """Generate a new TOTP secret and return QR code + secret for enrolment.

    If MFA is already enabled the user must disable it first.
    Re-calling setup before verification replaces the pending secret.
    """
    existing = _get_enabled_factor(db, user["id"])
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="MFA is already enabled. Disable it first to re-enrol.",
        )

    # Replace any pending (unverified) setup
    pending = _get_pending_factor(db, user["id"])
    if pending:
        db.delete(pending)
        db.flush()

    secret = pyotp.random_base32()
    totp = pyotp.TOTP(secret)
    otpauth_uri = totp.provisioning_uri(name=user["email"], issuer_name="CapeControl")

    factor = MfaFactor(
        user_id=user["id"],
        type="totp",
        secret_encrypted=encrypt_secret(secret),
    )
    db.add(factor)
    db.commit()

    qr_svg = _generate_qr_svg(otpauth_uri)

    log.info("mfa_setup user=%s", user["id"])
    return MfaSetupOut(secret=secret, otpauth_uri=otpauth_uri, qr_svg=qr_svg)


@router.post("/verify", response_model=MfaVerifyOut)
async def mfa_verify(
    payload: MfaVerifyIn,
    user: dict = Depends(get_verified_user),
    db: Session = Depends(get_db),
):
    """Verify a TOTP code to complete MFA enrolment (first-time) or
    to validate during a login challenge.

    For enrolment: activates the pending factor.
    For challenge: returns verified=True if the code matches.
    """
    # Try pending factor first (enrolment flow)
    factor = _get_pending_factor(db, user["id"])
    is_enrolment = factor is not None

    if not factor:
        # Already enrolled — challenge flow
        factor = _get_enabled_factor(db, user["id"])

    if not factor or not factor.secret_encrypted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No MFA factor found. Call /mfa/setup first.",
        )

    plaintext_secret = decrypt_secret(factor.secret_encrypted)
    totp = pyotp.TOTP(plaintext_secret)
    if not totp.verify(payload.code, valid_window=1):
        log.warning("mfa_verify_failed user=%s enrolment=%s", user["id"], is_enrolment)
        return MfaVerifyOut(verified=False, message="Invalid code. Please try again.")

    if is_enrolment:
        factor.enabled_at = datetime.now(timezone.utc)
        db.commit()
        log.info("mfa_enabled user=%s", user["id"])
        return MfaVerifyOut(verified=True, message="MFA enabled successfully.")

    log.info("mfa_challenge_passed user=%s", user["id"])
    return MfaVerifyOut(verified=True, message="Verification successful.")


@router.post("/disable", response_model=MfaVerifyOut)
async def mfa_disable(
    payload: MfaDisableIn,
    user: dict = Depends(get_verified_user),
    db: Session = Depends(get_db),
):
    """Disable MFA — requires a valid TOTP code as confirmation."""
    factor = _get_enabled_factor(db, user["id"])
    if not factor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="MFA is not enabled.",
        )

    plaintext_secret = decrypt_secret(factor.secret_encrypted)
    totp = pyotp.TOTP(plaintext_secret)
    if not totp.verify(payload.code, valid_window=1):
        return MfaVerifyOut(verified=False, message="Invalid code. MFA not disabled.")

    db.delete(factor)
    db.commit()
    log.info("mfa_disabled user=%s", user["id"])
    return MfaVerifyOut(verified=True, message="MFA has been disabled.")
