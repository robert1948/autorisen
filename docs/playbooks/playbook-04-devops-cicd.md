# Playbook 04: DevOps CI/CD & Deployments

**Owner**: DevOps Pilot
**Supporting Agents**: Release Captain, TestGuardianAgent
**Status**: Doing
**Priority**: P0

---

## 1) Outcome

Deliver a reliable, reproducible DevOps pipeline that automates build, test, and deploy cycles for CapeControl. Ensure Makefile, GitHub Actions, and Heroku container workflows operate seamlessly across local, staging, and production.

**Definition of Done (DoD):**

* Full Makefile target coverage for build, test, and deploy.
* GitHub Actions CI workflows validate code and run smoke tests.
* Docker images automatically built, tagged, and pushed to DockerHub.
* Heroku pipeline configured for staging and production with green smoke checks.
* Post-deploy health verified automatically.

---

## 2) Scope (In / Out)

**In Scope:**

* Makefile targets: `docker-build`, `docker-push`, `deploy-heroku`, `github-update`, `test`, `clean`.
* GitHub Actions workflows for CI/CD.
* DockerHub integration and version tagging.
* Heroku staging/production pipelines.
* Automated sitemap and crawl verification.

**Out of Scope:**

* AWS ECS/Fargate migration (Phase 2).
* Multi-cloud deployments.
* Terraform automation.

---

## 3) Dependencies

**Upstream:**

* Playbook 02 – Backend Auth & Security (stable backend required).
* Playbook 05 – Quality & Test Readiness (test automation dependencies).

**Downstream:**

* Playbook 01 – MVP Launch (depends on full deployment pipeline).

---

## 4) Milestones

| Milestone | Description                                  | Owner             | Status        |
| --------- | -------------------------------------------- | ----------------- | ------------- |
| M1        | Update Makefile with complete targets        | DevOps Pilot      | ✅ Done        |
| M2        | CI GitHub Actions (build + test) operational | TestGuardianAgent | ✅ Done        |
| M3        | Heroku container deploy stable for staging   | Release Captain   | ⏳ In Progress |
| M4        | DockerHub image auto-versioning added        | DevOps Pilot      | 🔄 Pending    |
| M5        | Production deploy verified + smoke test      | Release Captain   | 🔄 Pending    |

---

## 5) Checklist (Executable)

* [x] `make docker-build` builds cleanly.
* [x] `make docker-push` pushes latest image tags to DockerHub.
* [x] `make deploy-heroku` succeeds for staging and production.
* [x] GitHub Actions `ci.yml` runs on PR and commit to `main`.
* [ ] `make github-update` triggers workflow dispatch for manual redeploy.
* [ ] Smoke tests verify production health endpoints.
* [ ] Sitemap regeneration and crawl validation automated.

---

## 6) Runbook / Commands

```bash
## Local build
make docker-build

## Push to DockerHub
make docker-push

## Deploy staging
make heroku-deploy-stg

## Deploy production
make deploy-heroku

## Trigger GitHub Action manually
gh workflow run deploy-heroku.yml
```text
---

## 7) Risks & Mitigations

| Risk                                      | Mitigation                                  |
| ----------------------------------------- | ------------------------------------------- |
| Docker version drift causes failed builds | Include DockerHub update target in Makefile |
| CI/CD pipeline stalls due to rate limits  | Cache dependencies and limit rebuilds       |
| Heroku config drift between environments  | Use `make plan-validate` to sync env vars   |
| Build artifact mismatch                   | Tag images with short SHA + timestamp       |

---

## 8) Links

* [`docs/PLAYBOOKS_OVERVIEW.md`](../PLAYBOOKS_OVERVIEW.md)
* [`Makefile`](../../Makefile)
* [`docs/Heroku_Pipeline_Workflow.md`](../Heroku_Pipeline_Workflow.md)
* GitHub Actions: `.github/workflows/deploy-heroku.yml`

---

## ✅ Next Actions

1. Finalize DockerHub tagging automation (M4).
1. Run full staging → production smoke tests (M5).
1. Validate sitemap + crawl checks in pipeline.
1. Confirm successful Heroku promotion and close playbook.
