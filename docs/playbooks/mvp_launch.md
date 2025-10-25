# 🚀 MVP Launch Playbook

**Purpose:**  
Provide a structured, repeatable guide for planning, building, testing, and deploying MVP releases within the CapeControl ecosystem.  
This playbook standardizes how projects move from concept to a stable, production-ready MVP, ensuring consistent quality, traceability, and speed.

---

## 🧭 1. Objective

Deliver MVPs that are:

- Technically sound (passing CI/CD tests and health checks)
- Secure and compliant
- User-centric with validated onboarding
- Deployable to Heroku and S3 with minimal manual steps

---

## ⚙️ 2. Scope

This playbook applies to:

- All internal CapeControl projects (`autolocal`, `autorisen`, `localstorm`, `capeonboard`, etc.)
- Both backend (FastAPI, PostgreSQL, Redis) and frontend (React, Vite, Tailwind) components
- Dev → Staging → Production pipelines managed through **GitHub Actions**, **Docker**, and **Heroku Container Stack**

---

## 🧩 3. Roles & Agents

| Role | Agent | Responsibilities |
|------|--------|------------------|
| **Lead Strategist** | `CodexProjectLead` | Oversees execution, milestone tracking, approval of readiness gates. |
| **Build & Deploy** | `AutoDeployer` | Handles Docker build, push, and Heroku promotion logic. |
| **QA & Validation** | `TestGuardian` | Runs pytest suites, ensures rate-limit/CSRF/security compliance. |
| **Documentation** | `DocSmith` | Maintains versioned changelogs, release notes, and update logs. |
| **CX & Communication** | `CapeAI` | Provides onboarding prompts and in-app notifications post-launch. |
| **Governance** | `ShieldAgent` | Confirms config vars, data protection, and repository compliance. |

---

## 🧱 4. Core Workflow

### **Phase A — Scoping & Planning**

1. Define MVP objectives in `docs/MVP_SCOPE.md`.
2. Update `Checklist_MVP.md` with per-phase deliverables.
3. Confirm environment variables and `.env.example`.
4. Assign agents to roles (Codex prompt → `make codex-assign`).

---

### **Phase B — Build & Test**

1. Initialize local dev container (`make up`).
2. Run lint and format checks (`make lint`, `make format`).
3. Execute unit and integration tests (`make test`).
4. Validate Makefile and CI/CD consistency (`make codex-check`).

---

### **Phase C — Staging Deployment**

1. Build and push image (`make docker-build && make heroku-deploy-stg`).
2. Run smoke tests (`make smoke`).
3. Verify `/api/health` and `/api/auth/csrf` endpoints.
4. QA sign-off from `TestGuardian`.

---

### **Phase D — Production Promotion**

1. Tag release (`git tag -a vX.Y.Z -m "MVP release" && git push origin --tags`).
2. Promote staging → production (`make heroku-promote-prod`).
3. Verify runtime logs (`heroku logs -a capecraft`).
4. Announce live status via `CapeAI` broadcast.

---

## 🧪 5. Validation Gates

| Gate | Validation Criteria | Responsible Agent |
|------|---------------------|-------------------|
| **Code Quality Gate** | Linting, formatting, dependency checks | `CodexProjectLead` |
| **Test Gate** | ≥95% test pass rate, zero critical warnings | `TestGuardian` |
| **Deployment Gate** | Successful Heroku build and health check | `AutoDeployer` |
| **Security Gate** | All environment vars verified, CSRF enabled | `ShieldAgent` |
| **Documentation Gate** | README, CHANGELOG, and sitemap updated | `DocSmith` |

---

## 📈 6. Metrics & KPIs

| KPI | Target | Measured By |
|-----|---------|-------------|
| Time-to-Deploy | ≤ 2 hours from approval to live | CI/CD logs |
| Build Success Rate | ≥ 95% | GitHub Actions |
| Post-Launch Issues | < 3 minor issues in first week | Issue Tracker |
| Docs Coverage | 100% updated README + CHANGELOG | `DocSmith` |
| CSRF & Rate-Limit Test Pass | 100% | `TestGuardian` |

---

## 🧮 7. Artifacts

| Artifact | Location | Description |
|-----------|-----------|-------------|
| `Makefile` | `/home/robert/Development/autolocal/` | Command definitions for build, deploy, test. |
| `docs/MVP_SCOPE.md` | `/docs/` | Defines MVP scope and rationale. |
| `docs/Checklist_MVP.md` | `/docs/` | Tracks all in-progress MVP tasks. |
| `DEVELOPMENT_CONTEXT.md` | `/docs/` | Environment, dependencies, and architecture summary. |
| `GitHub Actions` | `.github/workflows/` | CI/CD deployment pipeline. |

---

## 🪜 8. Review & Continuous Improvement

- **After each MVP release**, log outcomes in `docs/playbooks/logs/mvp_launch_log.md`.
- **Post-mortem meeting** led by `CodexProjectLead` and `TestGuardian` within 48 hours.
- **Improvement items** are integrated into next release cycle and versioned as `vX.Y+1`.

---

## 📅 9. Revision History

| Version | Date | Summary | Author |
|----------|------|----------|--------|
| v1.0 | 2025-10-25 | Initial draft creation | Codex / GPT-5 |
| v1.1 | — | (To be updated after first MVP review) | — |

---

*Document version:* **v1.0-draft**  
*Last updated:* `2025-10-25`  
*Maintainers:* `CodexProjectLead`, `DocSmith`, `TestGuardian`
