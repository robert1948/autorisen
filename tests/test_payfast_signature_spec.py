from __future__ import annotations

import hashlib
from urllib.parse import quote_plus


def _set_payfast_env(monkeypatch) -> None:
    monkeypatch.setenv("PAYFAST_MERCHANT_ID", "10000100")
    monkeypatch.setenv("PAYFAST_MERCHANT_KEY", "abc123")
    monkeypatch.setenv("PAYFAST_RETURN_URL", "https://example.test/return")
    monkeypatch.setenv("PAYFAST_CANCEL_URL", "https://example.test/cancel")
    monkeypatch.setenv("PAYFAST_NOTIFY_URL", "https://example.test/itn")
    monkeypatch.setenv("PAYFAST_MODE", "sandbox")


def _payfast_reference_signature(fields: dict[str, str], passphrase: str | None) -> str:
    parts: list[str] = []
    for key in sorted(fields.keys()):
        if key == "signature":
            continue
        value = fields.get(key)
        if value is None or value == "":
            continue
        parts.append(
            f"{quote_plus(str(key), safe='')}={quote_plus(str(value), safe='')}"
        )

    payload = "&".join(parts)
    if passphrase is not None and passphrase != "":
        payload = f"{payload}&passphrase={quote_plus(str(passphrase), safe='')}"

    return hashlib.md5(payload.encode("utf-8")).hexdigest()


def test_payfast_signature_with_passphrase(client, monkeypatch):
    _set_payfast_env(monkeypatch)
    monkeypatch.setenv("PAYFAST_PASSPHRASE", "testpass")

    from backend.src.modules.payments.config import reset_payfast_settings_cache

    reset_payfast_settings_cache()

    resp = client.post(
        "/api/payments/payfast/checkout",
        json={"product_code": "LIVE_VERIFY_R5", "customer_email": "buyer@example.test"},
    )

    assert resp.status_code == 200
    fields = resp.json()["fields"]

    computed = _payfast_reference_signature(fields, passphrase="testpass")
    assert computed == fields["signature"]


def test_payfast_signature_without_passphrase(client, monkeypatch):
    _set_payfast_env(monkeypatch)
    monkeypatch.delenv("PAYFAST_PASSPHRASE", raising=False)

    from backend.src.modules.payments.config import reset_payfast_settings_cache

    reset_payfast_settings_cache()

    resp = client.post(
        "/api/payments/payfast/checkout",
        json={"product_code": "LIVE_VERIFY_R5", "customer_email": "buyer@example.test"},
    )

    assert resp.status_code == 200
    fields = resp.json()["fields"]

    computed = _payfast_reference_signature(fields, passphrase=None)
    assert computed == fields["signature"]
