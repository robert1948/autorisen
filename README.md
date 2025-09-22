# AutoLocal — FastAPI + Postgres (no GitHub/Heroku)

## Ports

- API: `http://localhost:8000`
- Frontend (Vite): `http://localhost:3000`
- Postgres: `localhost:5433`
- Redis: `localhost:6379`
- MinIO: `http://localhost:9000` (S3 API), `http://localhost:9001` (console)
- pgAdmin (optional tools profile): `http://localhost:5050`

## Repo layout

```text
.
├─ backend/                 # FastAPI app (entry: app/main.py → app.main:app)
│  ├─ app/
│  ├─ requirements.txt
│  └─ (optional) alembic.ini
├─ client/                  # Vite frontend (optional)
├─ docker-compose.yml
├─ Makefile                 # helper commands
├─ .env                     # local config
└─ .env.example

```
