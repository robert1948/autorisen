# 🚀 AutoLocal MVP Scope — October 2025

**Project Name:** AutoLocal (CapeControl MVP)  
**Goal:** Deliver a fully working, minimal AI-agent SaaS foundation deployable to Heroku within current Codex quota.

## Contents

- [Objective](#objective)
- [Core Components](#core-components)
- [Success Criteria](#success-criteria)
- [Delivery Plan](#delivery-plan)
- [Constraints](#constraints)
- [Output](#output)
- [Owner & Version](#owner--version)

---

## Objective

Build a stable, minimal slice of the AutoLocal platform that demonstrates:

- Secure user authentication
- Role-based access (Developer / Customer)
- Agent listing and basic execution flow
- Operational readiness (CI, health checks, deployment)
- Clean, responsive UI with working login/register

The MVP serves as a public proof-of-concept and developer baseline for the full CapeControl platform.

---

## Core Components

### 1. Backend (FastAPI + PostgreSQL)

#### Backend Scope

- `/api/health`, `/api/version`
- `/api/auth/register`, `/api/auth/login`, `/api/auth/refresh`, `/api/auth/me`
- `/api/agents` (list) and `/api/agents/{id}/run` stub
- Rate limiting, audit log hooks, minimal test coverage
- Alembic migration sanity (PostgreSQL + Heroku)
- Lightweight middleware: `AuditLoggingMiddleware`, `InputSanitizationMiddleware`

#### Backend Out of scope

- Complex agent execution engine
- Task queue, Redis, or async orchestration

---

### 2. Frontend (React + Vite + Tailwind)

#### Frontend Scope

- Landing page with link to login
- Login & Register forms (working against backend API)
- Auth context: token storage + `/me` fetch + redirect logic
- Agent list page with mock data + "Run" button calling `/agents/:id/run`
- Activity pane listing past runs (simple local state)

#### Frontend Out of scope

- Full dashboard analytics
- Onboarding wizard
- Agent configuration editor

---

### 3. DevOps / Deployment

#### DevOps Scope

- GitHub Actions CI: lint, test, build, smoke
- Heroku container deployment (backend + frontend)
- Environment config via `.env` and `Makefile`
- `/api/health` and `/api/version` checks post-deploy

#### DevOps Out of scope

- AWS or Kubernetes deployment
- Advanced monitoring and alerts

---

## Success Criteria

| Area | Success Metric |
| --- | --- |
| Auth | Register → Login → `/me` flow works in staging |
| Agents | List and Run stub return valid JSON |
| Frontend | Login/Register UI connected to backend |
| DevOps | Heroku deploy runs end-to-end with passing smoke tests |
| Performance | P95 < 500 ms for `/api/health` and `/auth/login` |
| Docs | `README.md`, `MVP_SCOPE.md`, `Checklist_MVP.md` committed |

---

## Delivery Plan

| Stage | Focus | Estimated Codex Use | Status |
| --- | --- | --- | --- |
| 0 | Scope finalization (this doc) | 5 low | ✅ Done |
| 1 | Backend core endpoints | 25 med | ⏳ Next |
| 2 | Frontend auth | 25 med | Pending |
| 3 | Agent stub | 15 med | Pending |
| 4 | CI/tests | 15 med | Pending |
| 5 | Deploy polish | 10 low | Pending |

---

## Constraints

- Must remain under **120 medium-equivalent Codex requests**
- All code must pass local tests before deploy
- Only dependencies currently in `requirements.txt` allowed
- No additional SaaS integrations (payment, email, etc.)

---

## Output

- Live Heroku app: `https://autorisen.herokuapp.com`
- GitHub repo: `https://github.com/robert1948/autolocal`
- Documentation: `/docs/MVP_SCOPE.md`, `/docs/Checklist_MVP.md`

---

## Owner & Version

- **Owner:** Robert Kleyn  
- **Date:** 20 Oct 2025  
- **Version:** 1.0
