from __future__ import annotations

import hashlib
import uuid
from urllib.parse import quote_plus


def _set_payfast_env(monkeypatch) -> None:
    monkeypatch.setenv("PAYFAST_MERCHANT_ID", "10000100")
    monkeypatch.setenv("PAYFAST_MERCHANT_KEY", "abc123")
    monkeypatch.setenv("PAYFAST_RETURN_URL", "https://example.test/return")
    monkeypatch.setenv("PAYFAST_CANCEL_URL", "https://example.test/cancel")
    monkeypatch.setenv("PAYFAST_NOTIFY_URL", "https://example.test/itn")
    monkeypatch.setenv("PAYFAST_MODE", "sandbox")


def _payfast_reference_signature(fields: dict[str, str], passphrase: str | None) -> str:
    """Recompute the PayFast MD5 signature using insertion order (matching server)."""
    parts: list[str] = []
    for key in fields:
        if key == "signature":
            continue
        value = fields.get(key)
        if value is None or value == "":
            continue
        value_str = str(value).strip().replace("+", " ")
        parts.append(
            f"{key}={quote_plus(value_str)}"
        )

    payload = "&".join(parts)
    if passphrase is not None and passphrase != "":
        payload = f"{payload}&passphrase={quote_plus(str(passphrase).strip())}"
    return hashlib.md5(payload.encode("utf-8")).hexdigest()


def _ensure_test_user(email: str):
    from backend.src.db import models
    from backend.src.db.session import SessionLocal
    from backend.src.services.security import hash_password

    db = SessionLocal()
    try:
        existing = db.query(models.User).filter(models.User.email == email).first()
        if existing:
            return existing
        user = models.User(
            email=email,
            hashed_password=hash_password("TestPass123!"),
            is_email_verified=True,
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    finally:
        db.close()


def _auth_headers(user) -> dict:
    from backend.src.services.security import create_jwt

    token, _ = create_jwt(
        {
            "user_id": user.id,
            "email": user.email,
            "jti": str(uuid.uuid4()),
            "token_version": getattr(user, "token_version", 0),
        },
        expires_in=60,
    )
    return {"Authorization": f"Bearer {token}"}


def _csrf_headers(client) -> dict:
    """Fetch a CSRF token and return headers + set cookie."""
    r = client.get("/api/auth/csrf")
    data = r.json() if r.status_code == 200 else {}
    token = data.get("csrf") or data.get("csrf_token") or data.get("token") or "test-csrf"
    client._c.cookies.set("csrftoken", token)
    return {"X-CSRF-Token": token}


def test_payfast_signature_with_passphrase(client, monkeypatch):
    _set_payfast_env(monkeypatch)
    monkeypatch.setenv("PAYFAST_PASSPHRASE", "testpass")

    from backend.src.modules.payments.config import reset_payfast_settings_cache

    reset_payfast_settings_cache()

    user = _ensure_test_user("buyer@example.test")

    resp = client.post(
        "/api/payments/payfast/checkout",
        json={"product_code": "LIVE_VERIFY_R5", "customer_email": "buyer@example.test"},
        headers={**_auth_headers(user), **_csrf_headers(client)},
    )

    assert resp.status_code == 200
    fields = resp.json()["fields"]

    assert "m_payment_id" in fields

    computed = _payfast_reference_signature(fields, passphrase="testpass")
    assert computed == fields["signature"]


def test_payfast_signature_without_passphrase(client, monkeypatch):
    _set_payfast_env(monkeypatch)
    monkeypatch.delenv("PAYFAST_PASSPHRASE", raising=False)

    from backend.src.modules.payments.config import reset_payfast_settings_cache

    reset_payfast_settings_cache()

    user = _ensure_test_user("buyer@example.test")

    resp = client.post(
        "/api/payments/payfast/checkout",
        json={"product_code": "LIVE_VERIFY_R5", "customer_email": "buyer@example.test"},
        headers={**_auth_headers(user), **_csrf_headers(client)},
    )

    assert resp.status_code == 200
    fields = resp.json()["fields"]

    assert "m_payment_id" in fields

    computed = _payfast_reference_signature(fields, passphrase=None)
    assert computed == fields["signature"]
