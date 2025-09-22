# Local Dev (autolocal) — No GitHub/Heroku

This runs the app + Postgres entirely on localhost using Docker Compose.  
Optional: MinIO for local S3-compatible static/media.

## 0) Prereqs

- Docker & Docker Compose
- A valid `Dockerfile` at project root (see note below)
- `alembic.ini` (if you use Alembic) points to `ALEMBIC_DATABASE_URL` or `DATABASE_URL`

## 1) First-time setup

```bash
cp .env.example .env
# Edit .env with your secrets and preferred S3 backend (real AWS or MinIO)
