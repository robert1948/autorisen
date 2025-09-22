# Auth iat_ms Changes — Report

Date: 2025-09-20

Summary

- Implemented high-precision token issue time handling to safely invalidate tokens issued before a user's password change.
- Tokens now include both `iat` (seconds — JWT-compatible) and `iat_ms` (milliseconds — high-precision) claims.
- `get_current_user` checks `iat_ms` (preferred) and falls back to `iat` (converted to ms) when `iat_ms` is absent or malformed.

Files changed

- `backend/app/core/security.py`
  - Added `iat_ms` claim to all token creation functions (`access`, `refresh`, `verify`, `reset`) and consolidated `now` computation.

- `backend/app/deps.py`
  - Modified token validation to prefer `iat_ms`, fall back to `iat` (seconds) converted to ms, and reject tokens with issue times <= `password_changed_at`.

- `backend/tests/test_deps_iat.py` (new)
  - Adds an integration-style test that exercises `get_current_user` via `/api/auth/me` with authored tokens to verify `iat_ms` precedence and `iat` fallback behavior.

- `backend/tests/test_token_invalidation.py` (existing tests run and passed)
- `backend/tests/test_rate_limiter.py` (existing tests run and passed)

Testing performed

- Ran targeted tests inside the project's backend container (via Docker Compose):
  - `pytest -q tests/test_deps_iat.py` — passed
  - `pytest -q tests/test_token_invalidation.py` — passed
  - `pytest -q tests/test_rate_limiter.py` — passed
- Verified `backend/app/deps.py` has no syntax errors.

Rationale

- Keeping `iat` maintains JWT compatibility (most libraries expect `iat` in seconds).
- Adding `iat_ms` provides the precision required to compare tokens' issuance time against `password_changed_at` (which may include sub-second precision) and avoid flaky behavior.
- Using server-issued tokens in tests as the authoritative clock reference reduces race conditions.

Next recommended actions

1. Make `iat_ms` mandatory in all new tokens (done) and deprecate relying on `iat` when possible.
2. Add pure unit tests for `get_current_user` parsing logic by mocking DB and token decoding to avoid network tests for parse behavior (faster and deterministic).
3. Harden rate-limiter keys to include email+IP and add per-IP tests.
4. Add `.env.example` doc entries for `JWT_SECRET_KEY`, cookie flags, and `ENVIRONMENT` guidance.

Status mapping

- DB-backed login & password reset flows — Done (existing)
- Token `iat` vs `password_changed_at` validation — Done (uses `iat_ms` then `iat` fallback)
- Tests for invalidation and rate limiting — Done (targeted tests added and run)

If you'd like, I can implement the unit-only tests for `get_current_user` parsing logic next (mock DB + decode), or start hardening the rate-limiter keys. Which would you prefer?
