# Changelog

## 3.1.0 - 2025-09-05

Enhancements

- Unified health check endpoint response serialization via helper utilities.
- Added real process uptime reporting (`uptime_seconds`) on `/api/health/status`.
- Standardized unhealthy service responses to HTTP 503 with structured JSON.
- Implemented database health check failure path with consistent JSON formatting.
- Added robust fallback logic to root `/api/health` endpoint to preserve liveness.
- Centralized version handling (updated to 3.1.0) with environment fallback.

Internal / Maintenance

- Refactored duplicate logic across system/error/disk/process health endpoints.
- Added release documentation scaffold (commit / PR template guidance).

Deferred / Known

- Pydantic v1 style validators still present; migration to V2 `field_validator` deferred.
- Remaining docstring references to v3.0.0 intentionally untouched (non-functional).
