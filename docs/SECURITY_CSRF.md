# CSRF Policy (CapeControl / AutoLocal)

This project uses a **double-submit CSRF** pattern:

- The backend issues a CSRF token.
- The browser stores it in a readable cookie (not HttpOnly).
- Every **state-changing** request must echo the same token in a request header.

If the header token and cookie token are missing/mismatched/invalid, the request is rejected with **HTTP 403**.

## Source of truth

- CSRF implementation: `backend/src/modules/auth/csrf.py`
- Auth router CSRF dependency: `backend/src/modules/auth/router.py`

## What requires CSRF

CSRF checks apply to **all non-safe HTTP methods**:

- Safe methods (no CSRF required): `GET`, `HEAD`, `OPTIONS`, `TRACE`
- CSRF required by default: `POST`, `PUT`, `PATCH`, `DELETE`

### Auth endpoints (common ones)

Most `/api/auth/*` endpoints that mutate state are `POST` and therefore require CSRF, including:

- `POST /api/auth/login`
- `POST /api/auth/register` and `POST /api/auth/register/step1`, `POST /api/auth/register/step2`
- `POST /api/auth/refresh`
- `POST /api/auth/logout`
- `POST /api/auth/verify/resend`
- `POST /api/auth/password/forgot`
- `POST /api/auth/password/reset`

`GET /api/auth/me` does **not** require CSRF (it’s a safe method).

### Exemptions

A small number of routes may be exempted for server-to-server webhook flows. Exemptions are defined in `EXEMPT_ROUTES` in `backend/src/modules/auth/csrf.py` and should remain narrow (method + path).

## How to obtain a CSRF token

Call:

- `GET /api/auth/csrf`

Response behavior:

- Returns JSON containing the token under multiple keys: `csrf`, `csrf_token`, and `token`.
- Sets a cookie named `csrftoken` (path `/`, not HttpOnly).
- Mirrors the token into the `X-CSRF-Token` response header.

## What to send on protected requests

For any CSRF-protected request, send **both**:

1) A cookie named `csrftoken` with the token value.
2) A header containing the same token.

### Header names accepted

The backend accepts any of these request headers:

- `X-CSRF-Token` (preferred)
- `X-CSRFToken`
- `X-XSRF-TOKEN`

### Cookie names accepted

The backend accepts any of these cookie names:

- `csrftoken` (preferred)
- `csrf_token`
- `XSRF-TOKEN`

## Refresh endpoint specifics

`POST /api/auth/refresh` supports two ways to provide the refresh token:

- Cookie-based: the refresh token is read from the `refresh_token` cookie.
- Body-based: JSON `{ "refresh_token": "..." }`.

Regardless of how the refresh token is provided, **CSRF is still required** because the request is a `POST`.

## Curl examples

### 1) Fetch CSRF token (and cookie)

```bash
# Writes cookies to a jar and prints the CSRF token from JSON
csrf=$(curl -s -c cookies.txt http://localhost:8000/api/auth/csrf | python -c 'import json,sys; print(json.load(sys.stdin)["token"])')
```

### 2) Login

```bash
curl -i -b cookies.txt -c cookies.txt \
  -H "X-CSRF-Token: $csrf" \
  -H "Content-Type: application/json" \
  -X POST http://localhost:8000/api/auth/login \
  -d '{"email":"user@example.com","password":"StrongerPass123!"}'
```

### 3) Refresh (cookie-based)

```bash
# If you have a refresh_token cookie set from login
curl -i -b cookies.txt -c cookies.txt \
  -H "X-CSRF-Token: $csrf" \
  -X POST http://localhost:8000/api/auth/refresh
```

### 4) Refresh (body-based)

```bash
curl -i -b cookies.txt -c cookies.txt \
  -H "X-CSRF-Token: $csrf" \
  -H "Content-Type: application/json" \
  -X POST http://localhost:8000/api/auth/refresh \
  -d '{"refresh_token":"<refresh token>"}'
```

## Frontend guidance

- Always use `credentials: "include"` (Fetch) / `withCredentials: true` (Axios) so cookies are sent.
- On app startup (or before the first mutating request), call `GET /api/auth/csrf` and store the returned token in memory.
- For every mutating request, attach `X-CSRF-Token: <token>`.
- If you receive `403` with `{"detail":"CSRF token missing or invalid"}` or `"CSRF token mismatch"`, fetch a new CSRF token and retry once.
