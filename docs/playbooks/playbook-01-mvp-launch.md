# Playbook 01: MVP Launch

**Owner**: Release Captain (Robert)

**Supporting Agents**: TestGuardianAgent, DevOps Pilot, Onboarding Maestro

**Status**: Doing
**Priority**: P0

---

## 1) Outcome

Deliver a stable, tested, and production-deployed MVP of the CapeControl platform — including backend auth, onboarding flow, CI/CD pipeline, and user-visible reliability (health checks, smoke tests, and runbooks).

**Definition of Done (DoD):**

* MVP live at production domain (`https://cape-control.com`) with working login and onboarding.
* Backend authentication (JWT, CSRF, `/me`) verified through pytest suite.
* Frontend passes functional smoke tests (login, profile setup, dashboard entry).
* Heroku and GitHub Actions pipelines green with Makefile parity.
* Release runbook signed off and stored under `docs/`.

---

## 2) Scope (In / Out)

**In Scope:**

* Backend: Auth routes, JWT flow, `/me` endpoints, CSRF protection.
* Frontend: Login, register, onboarding, and basic dashboard shell.
* CI/CD: Makefile automation, GitHub Actions, Heroku pipeline, and smoke verification.
* QA: pytest suite and deterministic fixtures using TestGuardianAgent.

**Out of Scope:**

* Payment integration.
* Marketplace or AI catalog features.
* Post-MVP analytics and GTM activities.

---

## 3) Dependencies

**Upstream:**

* Playbook 02 – Backend Auth & Security
* Playbook 04 – DevOps CI/CD

**Downstream:**

* Playbook 03 – Frontend Onboarding & Dashboard
* Playbook 05 – Quality & Test Readiness

---

## 4) Milestones

| Milestone | Description                          | Owner              | Status        |
| --------- | ------------------------------------ | ------------------ | ------------- |
| M1        | Auth & CSRF tests green              | Auth Guardian      | ✅ Done        |
| M2        | Makefile deploy targets stable       | DevOps Pilot       | ✅ Done        |
| M3        | Frontend login + onboarding verified | Onboarding Maestro | ⏳ In Progress |
| M4        | Heroku smoke test pass               | Release Captain    | 🔄 Pending    |
| M5        | Docs + runbook committed             | Release Captain    | 🔄 Pending    |

---

## 5) Checklist (Executable)

* [x] `make install` installs deps without error.
* [x] `make test` runs pytest suite with green output.
* [x] `make deploy-heroku` succeeds for staging + production.
* [ ] Run full smoke test (`/api/health`, `/api/auth/csrf`, frontend login flow).
* [ ] Create `docs/Release_Runbook.md` (deployment, rollback, smoke test steps).
* [ ] Confirm public MVP access at `https://cape-control.com`.

---

## 6) Runbook / Commands

```bash
# Local sanity
make venv install format lint test

# Deploy staging
make heroku-deploy-stg

# Deploy production
make deploy-heroku

# Verify smoke
curl -fsSL https://dev.cape-control.com/api/health
```

---

## 7) Risks & Mitigations

| Risk                                           | Mitigation                                                    |
| ---------------------------------------------- | ------------------------------------------------------------- |
| Staging → prod environment mismatch            | Enforce `.env.example` parity and heroku config sync          |
| CSRF/rate-limit tests intermittently fail      | Keep TestGuardianAgent auto-heal fixtures deterministic       |
| Frontend-backend token mismatch                | Use unified API base URLs in `.env` and check CORS middleware |
| Heroku build fails due to Docker version drift | Add Makefile target to update DockerHub image tags            |

---

## 8) Links

* [`docs/PLAYBOOKS_OVERVIEW.md`](../PLAYBOOKS_OVERVIEW.md)
* [`docs/Release_Runbook.md`](../Release_Runbook.md)
* [`docs/Checklist_MVP.md`](../Checklist_MVP.md)
* GitHub Repo: [robert1948/autolocal](https://github.com/robert1948/autolocal)
* Staging: [https://dev.cape-control.com](https://dev.cape-control.com)
* Production: [https://cape-control.com](https://cape-control.com)

---

## ✅ Next Actions

1. Complete onboarding verification (M3).
2. Execute final smoke and runbook test (M4, M5).
3. Tag release and push to Heroku prod.
4. Announce MVP completion in project log.
