from __future__ import annotations


def test_csrf_still_applies_to_auth_login(client):
    # Auth endpoints are browser/cookie flows and must remain protected by CSRF.
    resp = client.post(
        "/api/auth/login",
        json={"email": "user@example.test", "password": "not-a-real-password"},
    )
    assert resp.status_code == 403
    payload = resp.json()
    error = payload.get("error", {}) if isinstance(payload, dict) else {}
    assert error.get("code") == "CSRF_FAILED"
    assert error.get("message") == "CSRF token missing or invalid"


def test_payfast_itn_post_is_csrf_exempt(client, monkeypatch):
    # ITN is server-to-server; CSRF must not block it.
    monkeypatch.setenv("PAYFAST_MERCHANT_ID", "10000100")
    monkeypatch.setenv("PAYFAST_MERCHANT_KEY", "46f0cd694581a")
    monkeypatch.setenv("PAYFAST_RETURN_URL", "https://example.test/return")
    monkeypatch.setenv("PAYFAST_CANCEL_URL", "https://example.test/cancel")
    monkeypatch.setenv("PAYFAST_NOTIFY_URL", "https://example.test/itn")
    monkeypatch.setenv("PAYFAST_MODE", "sandbox")
    monkeypatch.setenv("PAYFAST_PASSPHRASE", "test-passphrase")

    from backend.src.modules.payments import config as payfast_config
    from backend.src.modules.payments import service as payfast_service

    payfast_config.reset_payfast_settings_cache()

    monkeypatch.setattr(
        payfast_service, "verify_itn_signature", lambda *_a, **_kw: True
    )

    async def _ok_validate(*_a, **_kw):
        return True

    monkeypatch.setattr(payfast_service, "validate_itn_with_server", _ok_validate)
    monkeypatch.setattr(payfast_service, "process_itn", lambda *_a, **_kw: None)

    resp = client.post(
        "/api/payments/payfast/itn",
        data="m_payment_id=test&pf_payment_id=pf123&payment_status=COMPLETE&amount_gross=5.00&signature=fake",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert resp.status_code == 200
    assert resp.text == "OK"
