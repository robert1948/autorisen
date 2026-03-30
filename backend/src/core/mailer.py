"""SMTP helper for outbound transactional email."""

from __future__ import annotations

import logging
import smtplib
import ssl
from email.message import EmailMessage
from typing import Iterable, Mapping, Optional

from backend.src.core.config import settings
from backend.src.core.telegram import send_telegram_alert

log = logging.getLogger("mailer")


TEST_OUTBOX: list[EmailMessage] = []


class MailerError(RuntimeError):
    """Raised when an email could not be dispatched."""


def _notify_telegram_email_activity(
    *,
    status: str,
    recipients: Iterable[str],
    subject: str,
    error_message: Optional[str] = None,
) -> None:
    recipient_text = ", ".join(recipients)
    lines = [
        "CapeControl email activity",
        f"Status: {status}",
        f"To: {recipient_text}",
        f"Subject: {subject}",
        "Source: https://cape-control.com",
    ]
    if error_message:
        lines.append(f"Error: {error_message}")
    send_telegram_alert("\n".join(lines))


def _require(value: Optional[str], name: str) -> str:
    if not value:
        raise MailerError(f"Missing required mail configuration: {name}")
    return value


def send_email(
    *,
    subject: str,
    to: Iterable[str],
    text_body: str,
    html_body: Optional[str] = None,
    headers: Optional[Mapping[str, str]] = None,
) -> None:
    """
    Send an email using the configured SMTP server.

    Raises MailerError when dispatch fails. Callers should decide whether to surface
    the exception or log-and-continue.
    """

    from_email = _require(settings.from_email, "FROM_EMAIL")
    smtp_host = _require(settings.smtp_host, "SMTP_HOST")
    smtp_username = _require(settings.smtp_username, "SMTP_USERNAME")
    smtp_password = _require(settings.smtp_password, "SMTP_PASSWORD")

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = ", ".join(to)
    for key, value in (headers or {}).items():
        msg[key] = value
    msg.set_content(text_body)

    if html_body:
        msg.add_alternative(html_body, subtype="html")

    recipients = list(to)

    if settings.env == "test":
        TEST_OUTBOX.append(msg)
        log.info(
            "Email captured in TEST_OUTBOX",
            extra={"to": recipients, "subject": subject},
        )
        _notify_telegram_email_activity(
            status="captured-test",
            recipients=recipients,
            subject=subject,
        )
        return

    use_ssl = bool(settings.smtp_use_ssl)
    use_tls = bool(settings.smtp_use_tls)
    port = int(settings.smtp_port or (465 if use_ssl else 587))

    try:
        if use_ssl:
            context = ssl.create_default_context()
            mailer: smtplib.SMTP = smtplib.SMTP_SSL(smtp_host, port, context=context)
        else:
            mailer = smtplib.SMTP(smtp_host, port, timeout=10)

        with mailer as client:
            client.ehlo()
            if use_tls and not use_ssl:
                context = ssl.create_default_context()
                client.starttls(context=context)
                client.ehlo()
            client.login(smtp_username, smtp_password)
            client.send_message(msg)
            log.info("Email dispatched", extra={"to": recipients, "subject": subject})
            _notify_telegram_email_activity(
                status="sent",
                recipients=recipients,
                subject=subject,
            )
    except Exception as exc:  # pragma: no cover - network-specific path
        log.exception(
            "Failed to send email", extra={"to": recipients, "subject": subject}
        )
        _notify_telegram_email_activity(
            status="failed",
            recipients=recipients,
            subject=subject,
            error_message=str(exc),
        )
        raise MailerError("Failed to send email") from exc
