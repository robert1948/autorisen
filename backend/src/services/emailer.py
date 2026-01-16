"""Transactional email helpers for auth flows."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Mapping, Optional

from backend.src.core.mailer import MailerError, send_email

logger = logging.getLogger(__name__)


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
    text_body = (
        "Hi,\n\n"
        "We received a request to reset your CapeControl password. "
        f"Use the link below within 30 minutes:\n\n{reset_url}\n\n"
        "If you did not request this, you can ignore this message.\n"
        "— CapeControl Security"
    )
    html_body = f"""
    <p>Hi,</p>
    <p>We received a request to reset your CapeControl password. Click the button below within 30 minutes.</p>
    <p>
      <a href="{reset_url}" style="display:inline-block;padding:12px 20px;background:#2563eb;color:#fff;
      border-radius:8px;text-decoration:none;">Reset password</a>
    </p>
    <p>If you did not request this, you can ignore this message.</p>
    <p>— CapeControl Security</p>
    """

    try:
        send_email(
            subject=subject, to=[email], text_body=text_body, html_body=html_body
        )
    except MailerError:
        logger.exception(
            "Password reset email failed",
            extra={"expires_at": expires_at.isoformat()},
        )
        raise
    else:
        logger.info(
            "Password reset email dispatched",
            extra={"expires_at": expires_at.isoformat()},
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
    else:
        logger.info(
            "Verification email dispatched",
            extra={"email": email, "verify_url": verify_url},
        )
