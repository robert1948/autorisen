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

    # Now craft tokens:
    # 1) token with iat_ms older than password_changed_at -> should be rejected
    now_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
    old_ms = now_ms - 10_000
    payload_old = {"sub": email, "type": "access", "exp": int((datetime.now(timezone.utc)+timedelta(minutes=5)).timestamp()), "iat_ms": old_ms, "iat": int(old_ms/1000)}
    t_old = jwt.encode(payload_old, JWT_SECRET, algorithm=JWT_ALG)
    r_old = get_me_with_token(t_old)
    assert r_old.status_code == 401

    # 2) token with iat_ms newer than password_changed_at -> should be allowed
    new_ms = now_ms + 10_000
    payload_new = {"sub": email, "type": "access", "exp": int((datetime.now(timezone.utc)+timedelta(minutes=5)).timestamp()), "iat_ms": new_ms, "iat": int(new_ms/1000)}
    t_new = jwt.encode(payload_new, JWT_SECRET, algorithm=JWT_ALG)
    r_new = get_me_with_token(t_new)
    assert r_new.status_code == 200

    # 3) token with only iat (seconds) older than password change -> rejected
    old_sec = int((now_ms - 10_000) / 1000)
    payload_old_sec = {"sub": email, "type": "access", "exp": int((datetime.now(timezone.utc)+timedelta(minutes=5)).timestamp()), "iat": old_sec}
    t_old_s = jwt.encode(payload_old_sec, JWT_SECRET, algorithm=JWT_ALG)
    r_old_s = get_me_with_token(t_old_s)
    assert r_old_s.status_code == 401

    # 4) token with malformed iat_ms (string) and good iat newer -> fallback to iat -> allowed
    bad_payload = {"sub": email, "type": "access", "exp": int((datetime.now(timezone.utc)+timedelta(minutes=5)).timestamp()), "iat_ms": "not-an-int", "iat": int((now_ms + 20_000) / 1000)}
    t_bad = jwt.encode(bad_payload, JWT_SECRET, algorithm=JWT_ALG)
    r_bad = get_me_with_token(t_bad)
    assert r_bad.status_code == 200
