"""Google reCAPTCHA verification helper (classic + enterprise)."""

from __future__ import annotations

import os
from typing import Optional, Tuple

import httpx

from backend.src.core.config import settings

# Classic v2/v3 endpoint
_CLASSIC_VERIFY_URL = "https://www.google.com/recaptcha/api/siteverify"

# ---- Config shims (read from your settings first; fall back to env) ----
DISABLED: bool = bool(getattr(settings, "disable_recaptcha", False))
SECRET: str = getattr(settings, "recaptcha_secret", os.getenv("RECAPTCHA_SECRET", ""))

# Provider: "api" (classic) or "enterprise"
PROVIDER: str = getattr(
    settings, "recaptcha_provider", os.getenv("RECAPTCHA_PROVIDER", "api")
).lower()

# Enterprise settings
SITE_KEY: str = getattr(
    settings, "recaptcha_site_key", os.getenv("RECAPTCHA_SITE_KEY", "")
)
PROJECT_ID: str = getattr(
    settings, "recaptcha_project_id", os.getenv("RECAPTCHA_PROJECT_ID", "")
)
API_KEY: str = getattr(
    settings, "recaptcha_api_key", os.getenv("RECAPTCHA_API_KEY", "")
)

# Optional risk score threshold (used for Enterprise and v3 classic when score is present)
SCORE_THRESHOLD: float = float(
    getattr(
        settings,
        "recaptcha_score_threshold",
        os.getenv("RECAPTCHA_SCORE_THRESHOLD", "0.5"),
    )
)

# Dev bypass token
DEV_BYPASS: str = getattr(
    settings,
    "recaptcha_dev_bypass_token",
    os.getenv("RECAPTCHA_DEV_BYPASS_TOKEN", "dev-bypass-token"),
)


async def verify_detailed(
    token: str,
    *,
    action: Optional[str] = None,
    remote_ip: Optional[str] = None,
) -> Tuple[bool, str, Optional[float]]:
    """
    Return (ok, reason, score).
    - ok: True if verification passed (or disabled)
    - reason: human-friendly reason
    - score: numeric risk score when available, else None
    """
    # 1) Disabled short-circuit
    if DISABLED:
        return True, "captcha disabled", None

    # 2) Dev bypass token short-circuit
    if token and token == DEV_BYPASS:
        return True, "dev bypass token", 1.0

    # 3) Basic validation
    if not token:
        return False, "missing token", None

    # 4) Enterprise flow
    if PROVIDER in {"enterprise", "ent"}:
        if not (SITE_KEY and PROJECT_ID and API_KEY):
            return False, "missing enterprise config", None

        url = f"https://recaptchaenterprise.googleapis.com/v1/projects/{PROJECT_ID}/assessments?key={API_KEY}"
        payload = {"event": {"token": token, "siteKey": SITE_KEY}}
        if action:
            payload["event"]["expectedAction"] = action  # recommended binding

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.post(url, json=payload)
                resp.raise_for_status()
                data = resp.json()
        except httpx.HTTPError as exc:
            return False, f"enterprise verify error: {exc}", None

        props = (data or {}).get("tokenProperties", {}) or {}
        if not props.get("valid", False):
            reason = props.get("invalidReason", "invalid token")
            return False, f"enterprise invalid: {reason}", None

        got_action = props.get("action")
        if action and got_action and got_action != action:
            return (
                False,
                f"enterprise action mismatch (got '{got_action}', want '{action}')",
                None,
            )

        score = (data or {}).get("riskAnalysis", {}).get("score")
        if isinstance(score, (int, float)) and score < SCORE_THRESHOLD:
            return (
                False,
                f"enterprise low score {score:.2f} (< {SCORE_THRESHOLD})",
                float(score),
            )

        return (
            True,
            f"enterprise ok{f' {score:.2f}' if isinstance(score, (int, float)) else ''}",
            (float(score) if isinstance(score, (int, float)) else None),
        )

    # 5) Classic v2/v3 siteverify
    if not SECRET:
        # Fail closed if classic is selected but no secret is configured
        return False, "missing classic secret", None

    form: dict[str, str] = {"secret": SECRET, "response": token}
    if remote_ip:
        form["remoteip"] = remote_ip

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.post(_CLASSIC_VERIFY_URL, data=form)
            resp.raise_for_status()
            payload = resp.json()
    except httpx.HTTPError as exc:
        return False, f"classic verify error: {exc}", None

    success = bool(payload.get("success"))
    score = payload.get("score")
    got_action = payload.get("action")

    if not success:
        # Google may include "error-codes" for debugging
        return (
            False,
            "classic invalid",
            float(score) if isinstance(score, (int, float)) else None,
        )

    if action and got_action and got_action != action:
        return (
            False,
            f"classic action mismatch (got '{got_action}', want '{action}')",
            (float(score) if isinstance(score, (int, float)) else None),
        )

    if isinstance(score, (int, float)) and score < SCORE_THRESHOLD:
        return (
            False,
            f"classic low score {score:.2f} (< {SCORE_THRESHOLD})",
            float(score),
        )

    return True, "classic ok", float(score) if isinstance(score, (int, float)) else None


async def verify(
    token: str, remote_ip: Optional[str] = None, *, action: Optional[str] = None
) -> bool:
    """
    Backward-compatible boolean verifier. Call verify_detailed(...) to inspect reasons/scores.
    """
    ok, _, _ = await verify_detailed(token, action=action, remote_ip=remote_ip)
    return ok
