"""Transactional email helpers for auth flows."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from math import ceil
from pathlib import Path
from typing import Any, Mapping, Optional

from backend.src.core.mailer import MailerError, send_email

logger = logging.getLogger(__name__)

LOGIN_NOTIFY_RECIPIENT = "bobby@cape-control.com"

TEMPLATE_DIR = Path(__file__).resolve().parent / "email_templates"


def _load_template(name: str, ext: str) -> str:
    path = TEMPLATE_DIR / f"{name}.{ext}"
    return path.read_text(encoding="utf-8")


def _render_template(template: str, context: Mapping[str, Any]) -> str:
    rendered = template
    for key, value in context.items():
        rendered = rendered.replace(f"{{{{ {key} }}}}", str(value))
    return rendered


def send_welcome_email(
    email: str, role: str, context: Mapping[str, Any] | None = None
) -> None:
    """Send a welcome email. Soft-fail with logging on error."""

    subject = "Welcome to CapeControl"
    text_body = (
        f"Hi,\n\nThanks for joining CapeControl as a {role}.\n"
        "Sign in to get started: https://dev.cape-control.com/login\n\n"
        "— CapeControl Team"
    )
    html_body = f"""
    <p>Hi,</p>
    <p>Thanks for joining CapeControl as a <strong>{role}</strong>.</p>
    <p><a href="https://dev.cape-control.com/login">Sign in</a> to get started.</p>
    <p>— CapeControl Team</p>
    """

    try:
        send_email(
            subject=subject, to=[email], text_body=text_body, html_body=html_body
        )
    except MailerError:
        logger.warning(
            "Welcome email delivery failed",
            extra={"email": email, "role": role, "context": dict(context or {})},
        )
    else:
        logger.info(
            "Welcome email dispatched",
            extra={"email": email, "role": role, "context": dict(context or {})},
        )


def send_password_reset_email(email: str, reset_url: str, expires_at: datetime) -> None:
    """Send password reset instructions via SMTP."""

    subject = "Reset your CapeControl password"
    now = datetime.now(timezone.utc)
    expires_at_aware = expires_at
    if expires_at_aware.tzinfo is None:
        expires_at_aware = expires_at_aware.replace(tzinfo=timezone.utc)
    expires_minutes = max(
        1, int(ceil((expires_at_aware - now).total_seconds() / 60.0))
    )

    context = {
        "app_name": "CapeControl",
        "reset_url": reset_url,
        "expires_minutes": expires_minutes,
    }
    text_template = _load_template("password_reset", "txt")
    html_template = _load_template("password_reset", "html")
    text_body = _render_template(text_template, context)
    html_body = _render_template(html_template, context)

    try:
        send_email(
            subject=subject, to=[email], text_body=text_body, html_body=html_body
        )
    except MailerError:
        logger.exception(
            "Password reset email failed",
            extra={
                "email": email,
                "reset_url": reset_url,
                "expires_at": expires_at.isoformat(),
            },
        )
        raise
    else:
        logger.info(
            "Password reset email dispatched",
            extra={
                "email": email,
                "reset_url": reset_url,
                "expires_at": expires_at.isoformat(),
            },
        )


def send_verification_email(
    email: str, verify_url: str, *, first_name: Optional[str] = None
) -> None:
    """Send an email verification link to the user."""

    subject = "Verify your CapeControl email"
    greeting = f"Hi {first_name}," if first_name else "Hi,"
    text_body = (
        f"{greeting}\n\n"
        "Thanks for creating a CapeControl account. Please verify your email address within 24 hours:\n\n"
        f"{verify_url}\n\n"
        "If you did not sign up, you can safely ignore this message.\n"
        "— CapeControl Team"
    )
    html_body = f"""
    <p>{greeting}</p>
    <p>Thanks for creating a CapeControl account. Please verify your email address within 24 hours.</p>
    <p>
      <a href="{verify_url}" style="display:inline-block;padding:12px 20px;background:#2563eb;color:#fff;
      border-radius:8px;text-decoration:none;">Verify email</a>
    </p>
    <p>If you did not sign up, you can safely ignore this message.</p>
    <p>— CapeControl Team</p>
    """

    try:
        send_email(
            subject=subject, to=[email], text_body=text_body, html_body=html_body
        )
    except MailerError:
        logger.exception(
            "Verification email failed",
            extra={"email": email, "verify_url": verify_url},
        )
        raise
    else:
        logger.info(
            "Verification email dispatched",
            extra={"email": email, "verify_url": verify_url},
        )


def send_login_notification(
    email: str,
    *,
    ip_address: str = "unknown",
    user_agent: str | None = None,
) -> None:
    """Notify bobby@cape-control.com that a user logged in. Soft-fail."""

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    subject = f"[CapeControl] Login: {email}"
    text_body = (
        f"Login notification\n\n"
        f"User: {email}\n"
        f"Time: {now}\n"
        f"IP:   {ip_address}\n"
        f"UA:   {user_agent or 'N/A'}\n"
    )
    html_body = f"""
    <h3>Login Notification</h3>
    <table style="border-collapse:collapse;">
      <tr><td style="padding:4px 12px 4px 0;font-weight:bold;">User</td><td>{email}</td></tr>
      <tr><td style="padding:4px 12px 4px 0;font-weight:bold;">Time</td><td>{now}</td></tr>
      <tr><td style="padding:4px 12px 4px 0;font-weight:bold;">IP</td><td>{ip_address}</td></tr>
      <tr><td style="padding:4px 12px 4px 0;font-weight:bold;">User-Agent</td><td>{user_agent or 'N/A'}</td></tr>
    </table>
    <p style="color:#888;font-size:12px;">— CapeControl Platform</p>
    """

    try:
        send_email(
            subject=subject,
            to=[LOGIN_NOTIFY_RECIPIENT],
            text_body=text_body,
            html_body=html_body,
        )
    except MailerError:
        logger.warning(
            "Login notification email failed",
            extra={"email": email, "ip": ip_address},
        )
    else:
        logger.info(
            "Login notification sent to %s for %s",
            LOGIN_NOTIFY_RECIPIENT,
            email,
        )
