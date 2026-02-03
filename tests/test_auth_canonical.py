from backend.src.modules.auth.schemas import LoginResponse, MeResponse


def test_login_success_returns_jwt_and_user_info(client):
    # 1. Register a user
    register_payload = {
        "first_name": "Canonical",
        "last_name": "User",
        "email": "canonical@example.com",
        "password": "Password123!@#",
        "confirm_password": "Password123!@#",
        "terms_accepted": True,
        "role": "Customer",
        "company_name": "Canonical Corp",
        "recaptcha_token": "dummy"
    }
    
    # Get CSRF token
    csrf_resp = client.get("/api/auth/csrf")
    assert csrf_resp.status_code == 200
    csrf_token = csrf_resp.json()["token"]
    headers = {"X-CSRF-Token": csrf_token}

    # Register
    reg_resp = client.post("/api/auth/register", json=register_payload, headers=headers)
    assert reg_resp.status_code == 201
    
    # 2. Login
    login_payload = {
        "email": "canonical@example.com",
        "password": "Password123!@#"
    }
    login_resp = client.post("/api/auth/login", json=login_payload, headers=headers)
    assert login_resp.status_code == 200
    
    # 3. Validate Response Shape
    data = login_resp.json()
    # Validate against Pydantic schema
    model = LoginResponse(**data)
    assert model.access_token
    assert model.refresh_token
    assert model.token_type == "bearer"

def test_me_rejects_without_token(client):
    resp = client.get("/api/auth/me")
    assert resp.status_code == 401

def test_me_returns_profile_with_token(client):
    # 1. Register & Login (reuse logic or just register since it returns tokens)
    register_payload = {
        "first_name": "Me",
        "last_name": "Tester",
        "email": "me@example.com",
        "password": "Password123!@#",
        "confirm_password": "Password123!@#",
        "terms_accepted": True,
        "role": "Customer",
        "company_name": "Me Corp",
        "recaptcha_token": "dummy"
    }
    
    csrf_resp = client.get("/api/auth/csrf")
    csrf_token = csrf_resp.json()["token"]
    headers = {"X-CSRF-Token": csrf_token}

    reg_resp = client.post("/api/auth/register", json=register_payload, headers=headers)
    assert reg_resp.status_code == 201
    token = reg_resp.json()["access_token"]
    
    # 2. Call /me
    auth_headers = {"Authorization": f"Bearer {token}"}
    me_resp = client.get("/api/auth/me", headers=auth_headers)
    assert me_resp.status_code == 200
    
    # 3. Validate Response Shape
    data = me_resp.json()
    model = MeResponse(**data)
    assert model.email == "me@example.com"
    assert model.first_name == "Me"
