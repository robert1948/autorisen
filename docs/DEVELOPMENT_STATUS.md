# Development Status — Autorisen

Last updated: PLACEHOLDER_UTC_

## Summary

Local dev stack (Docker Compose) is up: **API + DB (Postgres) + Redis + Frontend (Vite)**.  
DB-backed auth is working; initial migration applied (`users_001`).

- API: [http://localhost:8000](http://localhost:8000) → `/docs`, `/api/status`
- Frontend (Vite): [http://localhost:3000](http://localhost:3000)
- DB: `postgres://devuser:devpass@localhost:5433/devdb`

---

## ✅ Features Shipped

- Docker Compose stack for local dev (db, redis, backend, frontend).
- Hot reload for backend (`uvicorn --reload`) and frontend (Vite).
- CORS configured for `http://localhost:3000` and `http://localhost:5173` (container internal `5173`, host `3000`).
- DB-backed auth:
  - `POST /api/auth/register`
  - `POST /api/auth/login`
  - `GET  /api/auth/me`
- Health & basics:
  - `GET /api/status`
  - `GET /` (root JSON)
- Alembic migrations on startup (`upgrade heads`).
- Makefile with common flows (`make up`, `make migrate`, `make be-logs`, `make smoke`, etc.).

---

## 🚧 In Progress / Next Up

- Refresh tokens (short-lived access + refresh, Redis rotation).
- Email verification + password reset (tokenized links).
- Roles/permissions scaffold (e.g., `role` on `users`, route guards).
- Payments: Stripe / PayFast sandbox wiring.
- File uploads via MinIO (S3) + presigned URLs.
- Monitoring / audit logging (flags exist; connect sinks).
- CI: basic lint/test; Docker build.

---

## 🔌 Live Endpoints (local)

> Source of truth: OpenAPI at [http://localhost:8000/docs](http://localhost:8000/docs)

- `GET /api/status`
- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET  /api/auth/me`

---

## 🗄️ Database & Migrations

- Engine: Postgres 15 (Docker)
- DSN: `postgres://devuser:devpass@localhost:5433/devdb`
- Applied:
  - `users_001` — create `users` table (unique `email`, password hash, timestamps)

Notes:

- Multiple Alembic heads handled in dev with `upgrade heads`. Consider a merge revision before staging/prod.

### Useful commands

```bash
# Services & health
docker compose ps
make smoke

# Migrations
docker compose exec -T backend sh -lc 'cd /app/backend && alembic -c alembic.ini current'
make migrate   # runs `alembic upgrade heads`

# DB inspect
docker compose exec -T db psql -U devuser -d devdb -c '\dt'
