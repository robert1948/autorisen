# Local development with Docker Compose (concise notes)

This document records recommended steps and runtime details for local development and quick troubleshooting.

Checklist

- Prepare environment (.env)

- Start the Docker Compose dev stack (backend, frontend, Postgres, Redis)

- Notes: DB SSL toggle, host port mapping, admin bootstrap, frontend port, CI/deploy safety

Prerequisites

- Docker & Docker Compose

- Node.js & npm (for frontend dev server) or use Docker to run the frontend

- Optional: Heroku CLI if you need to push container images from your machine

Quick start (recommended)

1. Copy and edit the env file

```bash
cp .env.example .env
# Edit .env to set DATABASE_URL or other secrets; compose may set DB host automatically
```

2. Start the dev stack (builds images and starts services)

```bash
docker compose up --build
```

What this runs

- backend: FastAPI / Uvicorn inside the backend image (the container runs the venv Python interpreter directly)

- frontend: Vite dev server (default port 5173) for local development

- db: PostgreSQL (mapped to host port 5433 by default to avoid host conflicts)

- redis: local Redis for caching/dev

## Key runtime notes

- Postgres host mapping: docker-compose maps Postgres to host port 5433 by default ("5433:5432"). Change this mapping in `docker-compose.yml` if you need a different host port.

- DB SSL: the backend inspects the DATABASE_URL and will prefer `sslmode=disable` for local hosts (hostnames like `db`, `localhost`, `host.docker.internal`). You can explicitly force disabling SSL with the `DISABLE_DB_SSL=1` environment variable.

Example: disable SSL explicitly when running locally

```bash
export DISABLE_DB_SSL=1
docker compose up --build
```

- Admin bootstrap: the initial admin bootstrap script was moved to `backend/scripts/bootstrap_admin.py`. Run it inside the backend container when needed (or call it from an interactive shell in the backend container).


- Frontend: Vite serves the SPA on `http://localhost:5173` by default and proxies `/api` to the backend while developing. If the backend is still starting you may see ECONNREFUSED proxy messages until it becomes healthy.

- Global navbar spacing: the frontend uses a CSS variable `--navbar-height` in `client/src/styles.css` and applies `padding-top: var(--navbar-height)` to `body` so the fixed navbar does not overlap page content. If you change navbar classes (heights), update that variable in the CSS.


Running tests

- Backend (run in the backend container or a built image):

```bash
# run pytest in the backend container
docker compose run --rm backend pytest -q

# or, build an image and run tests inside it
docker build -t autorisen:dev .
docker run --rm autorisen:dev pytest -q
```

Frontend development

```bash
cd client
npm install
npm run dev
# opens at http://localhost:5173
```

CI / deploy and safety notes

- CI workflows now skip automated Heroku deploys when required secrets are missing. Prefer manual Heroku container pushes from your workstation when you need to release without relying on Actions.

- If a Heroku API key (or any secret) has been exposed in the past, revoke and rotate it immediately and update repository/org secrets.

Troubleshooting

- If `docker compose up` fails due to port conflicts, modify the host port mapping in `docker-compose.yml` or stop the conflicting host service.

- If the frontend proxy shows ECONNREFUSED, wait for the backend to finish starting and reload the page after the backend becomes healthy.

More details / source pointers

- `client/src/styles.css` — navbar-height variable and breakpoints

- `backend/app/database.py` — DB SSL detection and `DISABLE_DB_SSL` behavior

- `backend/scripts/bootstrap_admin.py` — admin bootstrap helper

