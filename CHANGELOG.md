# Changelog

## 2025-09-20 — Auth migration and secrets hardening

- Implemented DB-backed authentication:
  - Replaced dev in-memory auth with DB-backed routes (`auth_db`) for register, login, and `me` endpoints.
  - Added `is_verified` (boolean) and `password_changed_at` (timestamp) fields to the `users` model.
  - Added CRUD helpers for user creation and lookup at `backend/app/crud/user.py`.

- Alembic and migrations:
  - Added Alembic migration `20250920_01_add_user_fields.py` to add the new columns.
  - Resolved existing Alembic branching by adding a merge revision `20250920_02_merge_user_heads.py`.
  - Where Alembic graph conflicts prevented automatic upgrades in dev/staging, applied safe `ALTER TABLE IF NOT EXISTS` to ensure schema updated and stamped the DB to the merge revision.

- Secrets and configuration:
  - Added `JWT_SECRET_KEY` and `SECRET_KEY` to local `.env` for development (do NOT commit real secrets to version control).
  - Created `.env.example` with placeholder values to document required environment variables.
  - Updated Docker Compose configuration to load env and run migrations on startup.

- Verification performed:
  - Executed local smoke tests: registration, login, and authenticated `GET /api/auth/me`.
  - Confirmed JWT `access_token` and `refresh_token` issuance.

Notes and next steps:

- For production, set secrets via your platform's secret manager (e.g., Heroku config vars, AWS Secrets Manager) and avoid storing secrets in git.

- Consider replacing placeholder/additional migrations (`add_integrations_tables.py`) with authoritative migrations if integrations tables are required in the schema.

- Add integration tests for the auth flows and CI steps to run migrations against a test database before deploy.
