# RFC: Modularization of autorisen

Status: Proposal

Owner: Architectural team / repo maintainers

Date: 2025-09-22

Summary
-------
This RFC proposes migrating the monolithic `backend` + `client` repository into a modular monorepo layout that groups independently deployable services under `services/` while preserving a single repository for coordinated development and CI.

Goals
-----
- Reduce cognitive load when working on small features by isolating area of code.
- Enable independent builds, tests, and deployments per service.
- Keep developer experience fast with shared tooling (workspaces) and a simple migration path.

Non-goals
--------
- Full microservices decomposition right away. We will start with small, low-risk modules.
- Immediate history rewriting or destructive monorepo operations. Those can be planned later.

Recommended approach
--------------------
Use a modular monorepo pattern: create a top-level `services/` directory and move logically grouped code into individual service folders. Each service should have its own `Dockerfile`, test suite, and CI build step, while common code can live in a `libs/` or `packages/` folder and be versioned/consumed via relative imports.

Proposed initial services
-------------------------
1. services/health
   - Very small service exposing `/alive` and `/api/status` for smoke tests and internal health.
   - Purpose: PoC for service extraction and CI integration.

2. services/api
   - The main API surface (current `backend/app`) split to only include HTTP routes, routers, and service wiring.
   - Responsibilities: authentication, business endpoints, API models, DB access via a clear service layer.

3. services/auth
   - Authentication and identity management logic (optional initial extraction). Contains user management, tokens, password reset flows, and dependencies.

4. services/web (client)
   - The existing `client` (Vite) kept as its own service with a focused Dockerfile and CI build.

5. libs/shared
   - Small shared library containing Pydantic schemas, common utilities, and DB migration helpers. This will be imported by services via relative paths or a simple package install step in CI.

File layout (example)
---------------------
services/
  health/
    app/
    Dockerfile
    requirements.txt
    tests/
  api/
    backend/...
    Dockerfile
    requirements.txt
    tests/
  auth/
    ...
client/
  ... (leave as-is or move to `services/web`)
libs/
  shared/

Data ownership, migrations, and DB access
----------------------------------------
- Owner per table: assign which service is the authoritative writer for each DB table. Document these in `docs/data-ownership.md` when migrations begin.
- Migrations: centralize migration scripts temporarily (e.g., `infra/migrations`) or keep per-service alembic directories. For the initial phase, keep migrations where they are and document migration order in the RFC.
- Access: use service-level repositories/DAOs and expose narrow interfaces; avoid direct cross-service DB writes.

API contracts & inter-service communication
-----------------------------------------
- Prefer synchronous HTTP REST for now between services with clear versioning (e.g., `/v1/`).
- Optionally add an internal RPC or message bus (redis/stream) later for async flows.
- Document public endpoints for each service in its README and add contract tests in CI.

Migration plan (phased)
-----------------------
Phase 0 — Prepare (non-breaking)
- Create `docs/RFC-modularization.md` and gather stakeholders.
- Add `services/health` PoC or create RFC-only plan (this RFC).
- Decide where shared libraries live (`libs/shared` vs package repo).

Phase 1 — PoC extraction (low-risk)
- Extract a tiny, read-only service: `services/health`.
- Add `Dockerfile`, `requirements.txt`, `pytest` tests, and a CI workflow that builds and tests the image.
- Update `docker-compose.yml` to include the new `health` service and adjust the backend healthcheck to call the `health` service or align endpoints.

Phase 2 — API extraction and refactor
- Move core `backend/app` code into `services/api` and preserve functionality.
- Keep a compatibility proxy or API gateway to route requests to the new service and to avoid breaking external callers.
- Run integration tests in CI that exercise the whole stack via `docker-compose` or a test-specific compose file.

Phase 3 — Auth & other bounded contexts
- Incrementally extract `auth` and other logical domains into services.
- Move shared code to `libs/shared` and replace intra-repo imports with explicit relative package installs or editable installs in CI.

Phase 4 — Harden & optimize CI
- Add per-service build/push steps to GitHub Actions and make Compose orchestrations per environment.
- Add contract tests, canary deployments, and monitoring for inter-service calls.

Rollback & fallback plan
-----------------------
- Each extraction step must be non-destructive: keep original code until the new service is fully tested and traffic is routed to it.
- Use feature flags and API gateway routing to switch between old and new implementations.

Risks & mitigations
-------------------
- Risk: Too many small services increases operational complexity.
  Mitigation: Start small (health PoC, then api), keep services coarse-grained.
- Risk: Shared code duplication or import complexity.
  Mitigation: Use `libs/shared` early and standardize a pattern for editable installs in dev and CI.

Acceptance criteria
-------------------
- An RFC file exists and is approved by maintainers.
- A `services/health` PoC exists, builds in CI, and passes an integration smoke test.
- `docker-compose.yml` can run the PoC alongside the current stack without breaking existing endpoints.

Next steps
----------
1. Review this RFC with maintainers and get approval to proceed.
2. Create branch `modularization/rfc` and open a PR with this RFC file.
3. After approval, implement `Phase 1` PoC (`services/health`) and update compose and CI.

Appendix: Example `services/health` quick sketch
----------------------------------------------
Minimal FastAPI app exposing `/alive` and `/api/status`. Keep it intentionally tiny to validate builds, compose wiring, and healthchecks.

---

End of RFC
