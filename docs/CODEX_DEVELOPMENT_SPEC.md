# CODEX: Pluggable Modules Development Specification

Status: Working Draft

Purpose
-------
This document defines the repository conventions, service layout, and development workflow for a pluggable-modules architecture applied to this codebase. It complements `docs/RFC-modularization.md` by specifying exact file shapes, entrypoint signatures, CI expectations, and migration acceptance criteria so that services can be developed, tested, and deployed independently while sharing common libraries.

Scope
-----
- Applies to all services extracted from the monolith (`backend/app`) and to any new services created under `services/`.
- Does NOT apply to demos/one-off scripts; those should be moved to `tools/` or removed.

Design principles
-----------------
- Small number of coarse-grained services rather than many nano-services.
- Each service is self-contained: it has its own `Dockerfile`, `requirements.txt` (or `pyproject.toml`), tests, and CI job.
- Common code is placed under `libs/` and consumed via editable installs in development and explicit installs in CI.
- Backwards-compatible incremental migration: services can be extracted one at a time and run side-by-side via `docker-compose` and a simple gateway/proxy.

Top-level layout (required)
--------------------------
Root repo layout (canonical):

```
.
├─ services/
│  ├─ api/                 # main API service (extracted from backend/app)
│  │  ├─ app/
│  │  │  ├─ main.py        # FastAPI app (app: FastAPI instance)
│  │  │  ├─ routes/
│  │  │  ├─ services/
│  │  │  └─ config.py
│  │  ├─ Dockerfile
│  │  ├─ requirements.txt
│  │  └─ tests/
│  ├─ health/              # small health service PoC
│  │  ├─ main.py
│  │  ├─ Dockerfile
│  │  ├─ requirements.txt
│  │  └─ tests/
│  └─ auth/
├─ libs/                   # shared code (schemas, utils)
│  └─ shared/
├─ client/                 # frontend (Vite)
├─ docker-compose.yml
├─ .github/workflows/
└─ docs/
```

Service entrypoint shape (required)
----------------------------------
- Each Python service must expose a top-level module that creates a FastAPI `app` instance named `app`.
- Example minimal `main.py`:

```python
from fastapi import FastAPI

app = FastAPI(title="svc-name")

@app.get("/alive")
def alive():
    return {"status": "ok", "ts": datetime.utcnow().isoformat()}

```

- Reason: `uvicorn` and Compose healthchecks expect `module:app` as the canonical import.

Router & discovery conventions
-----------------------------
- Each service should register routers in `app/routes/` and expose a single importable router or mount them in `main.py`.
- If a service wants to expose a pluggable router for the API gateway to mount, it should expose a variable `router: APIRouter` in `app/routes/__init__.py`.

Config conventions
------------------
- Services use `pydantic-settings` (`BaseSettings`) in `app/config/settings.py` to declare configuration.
- Provide a small `get_settings()` helper returning a singleton Settings instance.
- `ENVIRONMENT` variable controls env-file selection; services should support `.env` for local dev and `.env.production` for prod.

Shared libraries
----------------
- Put common Pydantic schemas, utilities, DB types, and client libraries under `libs/shared`.
- Use editable installs during development:

```bash
pip install -e libs/shared
```

Testing conventions
-------------------
- Tests must live in `tests/` under each service.
- Use `pytest` and keep tests fast; mock external services when possible.
- Provide small contract tests that validate public endpoints (e.g., `/health` and minimal `/status`) and a CI `smoke` job to run them against a composed test environment.

Docker & Compose conventions
---------------------------
- Each service contains a `Dockerfile` that exposes the same HTTP port (e.g., 8000) internally.
- The recommended `Dockerfile` base is `python:3.11-slim` with a multi-stage build for production.
- `docker-compose.yml` defines per-service images with a `healthcheck` calling `/alive` on the container network (not `localhost`).

CI conventions
--------------
- GitHub Actions must be updated to build and test each service independently.
- Workflow pattern:
  1. Lint & unit tests per service.
  2. Build per-service Docker image and tag with `service-${GITHUB_SHA}`.
  3. Push per-service images when `main` is updated and secrets are present.
- Use a matrix job for services when possible to reuse workflow code.

Migration checklist (per-service)
--------------------------------
1. Create `services/<name>/app` and move the smallest, self-contained code (routes + direct services) into the new package.
2. Add `main.py` exposing `app`, `requirements.txt`, `Dockerfile`, and `tests/` with at least a smoke test.
3. Run `docker-compose` with the new service alongside the monolith and ensure no breakage.
4. Update CI to lint and test the new service.
5. Move shared code into `libs/shared` if needed and update imports.
6. Repeat iteratively, keeping the monolith until the new service is proven.

Acceptance criteria (for Phase 1 PoC)
-----------------------------------
- `services/health` present with `main.py` exposing `app` and endpoints `/alive` and `/ping`.
- A `Dockerfile` and `requirements.txt` exist and CI builds the image successfully (or a local `docker build` succeeds).
- `docker-compose.yml` runs the `health` service and the compose healthcheck uses `http://health:8000/alive` (or the equivalent internal name) and passes.

Rollback & safety
-----------------
- Keep code in the monolith until the extracted service is fully validated.
- Use feature flags and gateway routing to control traffic cutover.

Housekeeping & cleanup rules
---------------------------
- Move demos and one-off scripts to `tools/` or remove them.
- Keep `backend/Dockerfile` and the repository root `Dockerfile` only if they serve a distinct purpose; prefer per-service Dockerfiles.
- Keep the RFC and CODEX docs in `docs/` and update them as decisions are made.

Open items / decisions needed
----------------------------
- Exact python base image and pinned dependency policy (e.g., use `requirements.txt` vs `pyproject.toml`).
- Decision on API gateway: simple nginx reverse-proxy in `infra/` or keep a small monolith-based proxy during migration.

Appendix: Example minimal `services/health/main.py`
--------------------------------------------------
This is a suggested shape (not yet implemented by this change):

```python
from fastapi import FastAPI
from datetime import datetime, timezone

app = FastAPI(title="health")

@app.get("/alive")
def alive():
    return {"status":"ok", "ts": datetime.now(timezone.utc).isoformat()}

@app.get("/ping")
def ping():
    return {"status":"pong", "ts": datetime.now(timezone.utc).isoformat()}
```

End of spec
