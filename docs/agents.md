# Agents Overview

Concise inventory of the agents used (or planned) in this project.

| Category        | Purpose                                                         | Status  | Linked Path / Ref |
|---|---|---|---|
| Auth Agent      | Handles register/login/refresh/me and JWT flows                 | active  | `backend/src/modules/auth/` (routes, schemas) |
| Onboarding (CapeAI) | Guides first-login setup, profile, and checklist nudges     | planned | `client/src/pages/onboarding/`, `client/src/components/ai/` |
| Docs Agent      | Surfaces project docs (MVP scope, checklist, dev context)       | planned | `docs/*.md`, `client/src/components/docs/` |
| Agents Router   | Aggregates agent endpoints under `/api/agents`                  | active  | `backend/src/modules/agents/router.py` |
| DevOps Agent    | Triggers health/smoke checks and deploy notes                   | planned | `Makefile` targets (`health`, `deploy-heroku`, etc.) |
| Sitemap Agent   | Keeps static sitemap in sync for SEO                            | active  | `docs/sitemap.*`, `Makefile` `sitemap-generate-*` |

## Notes

- **Auth Agent** is production-critical; keep its tests green (`backend/tests/test_auth.py`).
- **Onboarding (CapeAI)** will persist progress in Postgres and display a smart checklist on first login.
- **DevOps Agent** is represented by Make targets + CI jobs; emits short, human-readable status.
