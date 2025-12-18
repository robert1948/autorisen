# Auth Demo Runbook

This guide demonstrates how to verify the canonical authentication flow locally.

## 1. Start the Server

Run the backend in Docker:

```bash
make docker-run
```

Or locally with Python:

```bash
uvicorn backend.src.app:app --reload --port 8000
```

## 2. Register a User (One-time)

```bash
# Get CSRF Token
CSRF=$(curl -s -c cookies.txt http://localhost:8000/api/auth/csrf | jq -r .token)

# Register
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -H "X-CSRF-Token: $CSRF" \
  -b cookies.txt \
  -d '{
    "first_name": "Demo",
    "last_name": "User",
    "email": "demo@example.com",
    "password": "Password123!@#",
    "confirm_password": "Password123!@#",
    "role": "Customer",
    "company_name": "Demo Corp",
    "recaptcha_token": "dummy"
  }'
```

## 3. Login

```bash
# Get CSRF Token (if session expired)
CSRF=$(curl -s -c cookies.txt http://localhost:8000/api/auth/csrf | jq -r .token)

# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -H "X-CSRF-Token: $CSRF" \
  -b cookies.txt -c cookies.txt \
  -d '{
    "email": "demo@example.com",
    "password": "Password123!@#"
  }' > login_response.json
```

**Expected Response Shape (LoginResponse):**

```json
{
  "access_token": "eyJhbG...",
  "refresh_token": "eyJhbG...",
  "token_type": "bearer",
  "email_verified": true
}
```

## 4. Get User Profile (/me)

```bash
TOKEN=$(jq -r .access_token login_response.json)

curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response Shape (MeResponse):**

```json
{
  "id": "uuid...",
  "email": "demo@example.com",
  "first_name": "Demo",
  "last_name": "User",
  "role": "Customer",
  "is_active": true,
  "email_verified": true
}
```
