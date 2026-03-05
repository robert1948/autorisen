"""SEC-003: Test admin invite email delivery wiring."""

from __future__ import annotations

from unittest.mock import patch

from backend.src.services.emailer import send_admin_invite_email


def test_send_admin_invite_email_calls_mailer(monkeypatch):
    """send_admin_invite_email should call send_email with correct params."""
    monkeypatch.setenv("ENV", "test")

    with patch("backend.src.services.emailer.send_email") as mock_send:
        send_admin_invite_email(
            "newadmin@example.com",
            invite_token="test-token-abc",
            invited_by="Robert",
        )

        mock_send.assert_called_once()
        call_kwargs = mock_send.call_args[1]
        assert call_kwargs["to"] == ["newadmin@example.com"]
        assert "invited" in call_kwargs["subject"].lower()
        assert "test-token-abc" in call_kwargs["text_body"]
        assert "Robert" in call_kwargs["text_body"]
        assert "test-token-abc" in call_kwargs["html_body"]


def test_send_admin_invite_email_soft_fails(monkeypatch):
    """Email failures should be caught, not raised."""
    monkeypatch.setenv("ENV", "test")

    from backend.src.core.mailer import MailerError

    with patch(
        "backend.src.services.emailer.send_email",
        side_effect=MailerError("SMTP down"),
    ):
        # Should not raise
        send_admin_invite_email(
            "fail@example.com",
            invite_token="tok",
        )
