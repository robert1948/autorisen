import uuid
import requests

from app.deps import get_db
from app.crud import user as crud_user
from app.core.security import verify_password


BASE = "http://127.0.0.1:8000"


def test_password_reset_flow():
    email = f"test+reset-{uuid.uuid4().hex}@example.com"
    # create user with an initial password
    with next(get_db()) as db:
        user = crud_user.create_user(db, email=email, name="Reset Test", password_plain="oldpass")
        assert user is not None
        assert user.password_changed_at is None

    # Request reset (dev returns token)
    resp = requests.post(f"{BASE}/api/auth/request-reset", json={"email": email}, timeout=5)
    assert resp.status_code == 200
    data = resp.json()
    token = data.get('token')
    assert token, f"Expected token in dev response, got: {data}"

    # Confirm reset with new password
    new_password = "newpass123"
    resp2 = requests.post(f"{BASE}/api/auth/confirm-reset", json={"token": token, "new_password": new_password}, timeout=5)
    assert resp2.status_code == 200

    # Verify DB: password_changed_at set and password hash matches new password
    with next(get_db()) as db:
        refreshed = crud_user.get_user_by_email(db, email)
        assert refreshed is not None
        assert refreshed.password_changed_at is not None
        assert verify_password(new_password, refreshed.password_hash)
