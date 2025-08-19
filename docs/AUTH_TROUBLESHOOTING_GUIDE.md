# Auth Troubleshooting Guide
Quick fixes for common login/registration issues.

## Check 1 – Environment Variables
- `SECRET_KEY` set?
- `DATABASE_URL` reachable?
- `ENVIRONMENT` = development/staging/production

## Check 2 – Password Hashing
- Ensure passlib/bcrypt installed and imported.
- Confirm `pwd_context` usage consistent in register/login.

## Check 3 – JWT
- Clock skew? Validate expiration & time zone.
- Token prefix: `Bearer <token>` in Authorization header.

## Check 4 – Database
- Run `alembic upgrade head`.
- Inspect user row; verify hashed password not plaintext.

## Check 5 – CORS/Frontend
- `CORS_ORIGINS` permits your domain (staging & prod).

## Logs
- Enable debug logging in `auth_service.py` (without leaking secrets).
