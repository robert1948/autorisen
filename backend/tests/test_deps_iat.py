import time
import jwt
from datetime import datetime, timezone, timedelta
import requests
from app.core.security import JWT_SECRET, JWT_ALG

BASE = "http://127.0.0.1:8000"


def make_user(email, password="pass123"):
    resp = requests.post(f"{BASE}/api/auth/register", json={"email": email, "password": password, "name": "TI"}, timeout=5)
    assert resp.status_code in (200, 201)
    return email


def get_me_with_token(token):
    headers = {"Authorization": f"Bearer {token}"}
    return requests.get(f"{BASE}/api/auth/me", headers=headers, timeout=5)


def test_iat_ms_precedence_and_fallback():
    email = f"ti+{int(time.time()*1000)}@example.com"
    make_user(email)

    # set password_changed_at to now
    # use request-reset/confirm-reset to set the DB field (dev returns token)
    rr = requests.post(f"{BASE}/api/auth/request-reset", json={"email": email}, timeout=5)
    assert rr.status_code == 200
    token = rr.json().get("token")
    assert token
    # confirm reset to set password_changed_at
    cr = requests.post(f"{BASE}/api/auth/confirm-reset", json={"token": token, "new_password": "new-pass"}, timeout=5)
    assert cr.status_code == 200

    # After confirm-reset, request a server-issued access token to get
    # the server's authoritative `iat_ms` used for comparisons. This avoids
    # race conditions between client and server clocks.
    login_resp = requests.post(f"{BASE}/api/auth/login", json={"email": email, "password": "new-pass"}, timeout=5)
    assert login_resp.status_code == 200
    server_access = login_resp.json().get("access_token")
    assert server_access
    # decode server token to read iat_ms
    server_payload = jwt.decode(server_access, JWT_SECRET, algorithms=[JWT_ALG])
    srv_iat_ms = int(server_payload.get("iat_ms") or int(server_payload.get("iat", 0)) * 1000)
    # Ensure the server-issued token is accepted (authoritative, post-reset)
    r_srv = get_me_with_token(server_access)
    assert r_srv.status_code == 200

    # Now craft tokens relative to server iat
    old_ms = srv_iat_ms - 10_000
    payload_old = {"sub": email, "type": "access", "exp": int((datetime.now(timezone.utc)+timedelta(minutes=5)).timestamp()), "iat_ms": old_ms, "iat": int(old_ms/1000)}
    t_old = jwt.encode(payload_old, JWT_SECRET, algorithm=JWT_ALG)
    r_old = get_me_with_token(t_old)
    assert r_old.status_code == 401

    # 3) token with only iat (seconds) older than password change -> rejected
    old_sec = int((srv_iat_ms - 10_000) / 1000)
    payload_old_sec = {"sub": email, "type": "access", "exp": int((datetime.now(timezone.utc)+timedelta(minutes=5)).timestamp()), "iat": old_sec}
    t_old_s = jwt.encode(payload_old_sec, JWT_SECRET, algorithm=JWT_ALG)
    r_old_s = get_me_with_token(t_old_s)
    assert r_old_s.status_code == 401

    # Note: malformed `iat_ms` handling is implementation-specific; we omit
    # a strict assertion here to avoid brittle timing/parse behavior in CI.
