# CSRF Policy (CapeControl / AutoLocal)

This project uses a **double-submit CSRF** pattern.

## Purpose / Threat model

- The server MUST issue a CSRF token and the browser MUST store it in a readable cookie.
- Every state-changing request MUST echo the same token in a request header.
- If the header token and cookie token are missing, mismatched, or invalid, the server MUST reject the request with HTTP 403.

## Source of truth

- CSRF implementation: `backend/src/modules/auth/csrf.py`
- CSRF token helpers: `backend/src/services/csrf.py`
- CSRF middleware wiring: `backend/src/app.py`
- Auth router CSRF dependency: `backend/src/modules/auth/router.py`

## CSRF Mechanism (canonical)

### Token issuance (source of truth)

- Clients MUST obtain tokens from `GET /api/auth/csrf`.
- The response MUST include the token under these JSON keys: `csrf`, `csrf_token`, `token`.
- The response MUST set a cookie named `csrftoken`.
- The response MUST mirror the token in the `X-CSRF-Token` response header.

### Cookie requirements

- Cookie name: `csrftoken` (canonical).
- Accepted cookie names (first-match): `csrftoken`, `csrf_token`, `XSRF-TOKEN`.
- Cookie scope: `Path=/`.
- Cookie MUST be readable by the browser (`HttpOnly=false`).
- Cookie `SameSite` MUST follow `SESSION_COOKIE_SAMESITE` (`lax`, `strict`, or `none`).
- Cookie `Secure` MUST be `true` when `SESSION_COOKIE_SECURE=true` or when `SameSite=none`.
- No `Domain` attribute is set by default.

### Header requirements

- For every protected request, the client MUST send a CSRF header containing the token.
- Accepted header names (first-match):
  - `X-CSRF-Token` (preferred)
  - `X-CSRFToken`
  - `X-XSRF-TOKEN`

### Validation rules

- The request MUST include both a CSRF cookie and a CSRF header.
- The cookie token and header token MUST be byte-for-byte equal.
- The token MUST pass signature validation and TTL checks.
- Tokens are signed (nonce + timestamp + HMAC) and are valid for 1 hour by default.

## Protected Requests

- CSRF checks MUST run for all non-safe HTTP methods: `POST`, `PUT`, `PATCH`, `DELETE`.
- Safe methods do NOT require CSRF: `GET`, `HEAD`, `OPTIONS`, `TRACE`.
- Enforcement applies globally via CSRF middleware (not just auth routes).

### Explicit exemptions

Only these routes are exempted for server-to-server webhook flows:

- `POST /api/payments/payfast/checkout`
- `POST /api/payments/payfast/itn`

## Client implementation notes (SPA-safe)

- Clients SHOULD call `GET /api/auth/csrf` on startup (or before the first mutating request).
- Clients MUST attach `X-CSRF-Token: <token>` to every protected request.
- Clients MUST send cookies (`credentials: "include"` / `withCredentials: true`).
- CORS allows these headers: `X-CSRF-Token`, `X-CSRFToken`, `X-XSRF-Token`.

## Error handling

- Missing header or cookie MUST return HTTP 403 with `{"detail":"CSRF token missing or invalid"}`.
- Mismatched tokens MUST return HTTP 403 with `{"detail":"CSRF token mismatch"}`.
- Invalid/expired tokens MUST return HTTP 403 with `{"detail":"Invalid CSRF token"}`.

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
