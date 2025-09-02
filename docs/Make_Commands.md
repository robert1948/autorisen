# Make Commands (Local Dev + Heroku)

This document lists available `make` targets and what they do.  
You can override the Heroku app per command with:  
`HEROKU_APP=my-app make heroku-deploy`  

You can also test against a custom domain with:  
`HOST=cape-control.com make smoke`

---

## Heroku (Container Deploy)

- **`make heroku-login`** — Log in to the Heroku Container Registry.  
- **`make heroku-push`** — Build and push the Docker image to Heroku for the app (`$(HEROKU_APP)`).  
- **`make heroku-release`** — Release the pushed image on Heroku (deploys the container).  
- **`make heroku-deploy`** — Runs `predeploy` checks, then `heroku-push` and `heroku-release` (one-shot deploy).  
- **`make heroku-logs`** — Tail Heroku logs for the configured app.  
- **`make smoke`** — Health check against the configured app.  
  - Defaults to `https://$(HEROKU_APP).herokuapp.com`  
  - If `HOST` is set, it uses `https://$(HOST)`  
  - Tries `/api/health`, then `/health`, then `/` until one responds `200 OK`.  
- **`make smoke-local`** — Same as `smoke`, but checks your local dev stack at `http://localhost:8000`.

> Tip:  
> - Override the app inline: `HEROKU_APP=tailstorm-a57f748ab672 make smoke`  
> - Or use a custom domain: `HOST=cape-control.com make smoke`

---

## Local Development (Docker Compose)

- **`make up`** — Start all core services in detached mode (backend, frontend, db, redis).  
- **`make down`** — Stop containers and remove orphans (leaves volumes intact).  
- **`make clean`** — ⚠️ Prompts for confirmation, then stops containers and **removes all named volumes** (`-v`) for a full reset.  
- **`make rebuild`** — Rebuild images without cache.  
- **`make logs`** — Tail logs for all services.  
- **`make be-logs`** — Tail backend logs only.  
- **`make fe-logs`** — Tail frontend logs only.  
- **`make ps`** — Show running containers and status.  
- **`make tools`** — Start optional tools profile:  
  - **pgAdmin** → http://localhost:5050  
  - **Redis Commander** → http://localhost:8081  
- **`make psql`** — Open a `psql` session to the local Postgres via host port **5433** using env vars (`POSTGRES_*`).  

---

## Python Dependencies (local)

- **`make deps`** — Install Python dependencies from `requirements.txt` and `backend/requirements.txt` (best-effort).  

---

## Pre-deployment Gate

- **`make predeploy`** — Run `scripts/predeploy_gate.sh` (lint/tests/sanity checks as defined in your repo).  

---

## Notes

- Compose uses env from `.env.development.local` (gitignored). See [Local_Dev.md](./Local_Dev.md) for setup.  
- `make clean` **deletes data** in named volumes (e.g., Postgres, Redis). Use with caution.  
- Frontend default dev URL: `http://localhost:3000`  
- Backend default dev URL: `http://localhost:8000`
