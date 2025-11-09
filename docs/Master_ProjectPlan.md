# Master Project Plan — autorisen

Snapshot: 2025-09-27

See also: `senior_devops.md`

<!-- markdownlint-disable MD013 -->

Overview

- Purpose: provide a single, actionable project plan for ops, infra, and product to execute and update. Keep AWS changes minimal and reversible. Where data is missing, tasks include TODO placeholders.
- Scope: align secrets (GitHub → Heroku), validate OIDC assume-role, run a live audit (Heroku + AWS), produce Deliverables A–E, and prepare a minimal ECS migration proposal (cluster + single task).

Scope & MVP definition

- MVP scope (minimal):
  - Stable Heroku deployment for `autorisen` (no change in app platform during MVP).
  - GitHub as SSOT for secrets; GitHub → Heroku sync for mapped keys.
  - Read-only AWS access via OIDC for audits.
  - Terraform skeleton only for ECS (ECR + cluster) — no ALB or RDS in MVP.

Workstreams

- App (R: app lead)
  - Verify health endpoints, container image tagging, release process.
  - Acceptance: `/alive` returns 200 from deployed container.

- Infra (R: infra lead)
  - Maintain `infra/aws-ecs-skel/` Terraform skeleton.
  - Create and validate the OIDC trust policy (done) and role (ARN present).

- CI/CD (R: ci lead)
  - Validate `ci-health.yml`, `docker-publish.yml`, and manual `live-audit.yml`.
  - Add `ci/sync-github-to-heroku.yml` for dry-run/apply sync.

- Security (R: security lead)
  - Confirm secrets mapping in `infra/secrets-mapping.json`.
  - Approve the sync plan and rotation cadence.

- Cost (R: finance/ops)
  - Track and limit AWS provisioning; prefer Fargate Spot for dev.

Authoritative project plan (CSV)

The primary source of truth for actionable tasks is the CSV located at `docs/autorisen_project_plan.csv`. Edit that file to add, update, or change task rows; the Markdown narrative in this document provides context and milestones but the CSV is the machine-readable, team-facing plan.

Snapshot (from `docs/autorisen_project_plan.csv`) — 2025-09-27

- Total tasks: 70
- Status counts: todo: 64, busy: 4, done: 2

Recent updates (2025-09-27): DEVOPS-033 set to `busy`; DEVOPS-034 and ADMIN-030 marked `done` after staging deploy and smoke-test validation. DEVOPS-035, OBS-036, and OBS-037 are `busy` as work begins. Many rows updated with today's timestamp.  
Recent updates (2025-10-20): AUTH-005 remains `busy` while CSRF/rate-limit pytest refactor completes; migration `202502191200_email_verification.py` now handles SQLite via `CURRENT_TIMESTAMP`, and FE-004/DEVOPS-035 stay blocked until backend suite passes.

Top priority (P1) tasks — quick view

| Task ID | Title | Owner | Estimate | Depends On |
|---|---|---:|---:|---:|
| AUTH-001 | Design auth data model | backend | 6 | |
| AUTH-002 | Implement /auth/register + hashing | backend | 8 | AUTH-001 |
| AUTH-003 | Implement /auth/login + JWT | backend | 8 | AUTH-002 |
| AUTH-004 | /auth/me and refresh flow | backend | 6 | AUTH-003 |
| AUTH-005 | Security hardening & tests | backend | 6 | AUTH-003 |
| ORG-006 | Org model + memberships | backend | 8 | AUTH-001 |
| ORG-007 | /orgs CRUD + /orgs/{id}/members | backend | 8 | ORG-006, AUTH-004 |
| AIGW-009 | Provider adapter interface | backend | 6 | |
| AIGW-010 | OpenAI adapter + quotas | backend | 10 | AIGW-009, AUTH-003 |
| AIGW-011 | /ai/complete & /ai/chat routes | backend | 8 | AIGW-010 |
| ORCH-012 | Run model + state machine | backend | 10 | AIGW-011 |
| ORCH-013 | POST /flows/{name}/run | backend | 8 | ORCH-012 |

How to use and update

- Edit `docs/autorisen_project_plan.csv` for day-to-day task changes (status, owner, estimates). Follow the CSV schema:
  - Required header: id,phase,task,owner,status,priority,dependencies,estimated_hours,completion_date,artifacts,verification,notes,codex_hints
  - `status` must be one of: todo, in-progress, completed, blocked, deferred
  - `completion_date` values (when present) use ISO 8601 (YYYY-MM-DD)
- Commit message convention: `docs(plan): <short description>` (e.g., `docs(plan): mark AUTH-002 in-progress`)
- When milestones or high-level narrative shift, update this Markdown to record rationale and dates; include links to PRs or Action runs in the CSV `notes` column.

Automation note

- We include `scripts/plan_md_to_csv.py` which extracts Markdown tables to CSV for one-way conversions; currently the workflow is manual: update the CSV and keep this Markdown in sync. If you want, I can add a reverse helper to regenerate this snapshot from the CSV automatically.

Milestones & dates (Gantt-style)

| ID | Milestone | Owner | Start | Target | Notes |
|---:|---|---|---:|---:|---|
| M1 | OIDC assume-role validated | ops | 2025-09-26 | 2025-09-27 | Merge PR #7 and run `Test OIDC` workflow |
| M2 | Secrets sync dry-run | ops | 2025-09-27 | 2025-09-27 | `ci/sync-github-to-heroku.yml` dispatch |
| M3 | Secrets sync apply (controlled) | ops | 2025-09-27 | 2025-09-28 | Manual approval required |
| M4 | Live audit run & artifact | ops | 2025-09-28 | 2025-09-28 | `live-audit.yml` dispatch |
| M5 | Deliverables A–E published | project lead | 2025-09-29 | 2025-09-29 | Based on audit artifact |
| M6 | ECS minimal migration proposal | infra lead | 2025-09-29 | 2025-10-06 | Cost estimate + rollback plan |

RACI (key roles)

| Role | Short | Responsibility |
|---|---|---|
| Project Lead | PL | Decide priorities, merge PRs, sign-off deliverables |
| Ops | OPS | Run audits, secrets sync, validate OIDC |
| Infra Lead | INFRA | Terraform, ECS plan, AWS interactions |
| CI Lead | CI | GitHub Actions workflows, builds, smoke tests |
| Security Lead | SEC | Secrets, rotation policy, audit of config-vars |

Risk Register

| ID | Risk | Impact | Likelihood | Mitigation |
|---:|---|---|---:|---|
| R1 | Secret drift between GitHub and Heroku | High | Medium | One-way sync from GitHub -> Heroku, dry-run + audit logs, run from Actions |
| R2 | OIDC misconfiguration prevents assume-role | High | Low | Validate trust policy, test workflow, limit `sub` to repo/branch |
| R3 | Unexpected AWS spend during migration | High | Medium | Keep AWS changes minimal; cost estimate + approval before provisioning |
| R4 | Accidental secret exposure via local apply | High | Low | Require Actions-run with repo secrets; default to dry-run locally |

Operating Cadence

- Daily (async): short status updates in `#autorisen-ops` channel.
- Weekly: Monday 10:00 UTC sync meeting (owner: PL) — review Milestones, blockers.
- On-demand: merge PRs for urgent fixes only after 1 review.

Checklists

Release checklist (minimal)

1. CI green for `ci-health` and `docker-publish` (or run locally).
1. `HEROKU_APP_NAME` and `HEROKU_API_KEY` present in repo secrets.
1. Smoke test `services/health` passes after deploy.

Rollback checklist

1. Revert release commit and re-run deploy using previous image tag.
1. Verify `/alive` returns 200.

Secrets & Infra change checklist

1. Create mapping in `infra/secrets-mapping.json` (reviewed by SEC).
1. Run sync in dry-run (`ci/sync-github-to-heroku.yml`).
1. Approve and run `--apply` in controlled workflow.

Appendix — Helpful commands

```bash
## Validate role exists
aws iam get-role --role-name gh-oidc-autorisen-ecr --query 'Role.Arn' --output text
## Master Project Plan — autorisen

Snapshot: 2025-09-26

See also: `docs/senior_devops.md`

Overview
- Purpose: single, actionable project plan for ops/infra/product to validate platform, secure secrets, and prepare a minimal ECS migration. Keep operations minimal and reversible.

Scope & MVP
- Retain Heroku as runtime for MVP.
- GitHub as SSOT for secrets with controlled GitHub → Heroku sync.
- OIDC-based, read-only AWS access for audit purposes.
- Terraform skeleton only for ECS (ECR + cluster stake) — no ALB/RDS in MVP.

Workstreams & Owners
- App (R: App lead)
  - Validate `services/health` and release process.
  - Acceptance: `/alive` returns 200 from running container.
- Infra (R: Infra lead)
  - Maintain `infra/aws-ecs-skel`, trust policy, IAM role(s).
- CI/CD (R: CI lead)
  - Validate CI workflows, add `ci/sync-github-to-heroku.yml`.
- Security (R: Sec lead)
  - Validate secrets mapping, approve sync plan.
- Finance/Ops (R: Ops/Finance)
  - Review cost/approval for AWS resources.

Milestones (high-level)
- M1 (2025-09-26 → 2025-09-27): OIDC assume-role validated (merge PR #7, dispatch test).
- M2 (2025-09-27): Secrets sync dry-run from Actions.
- M3 (2025-09-27 → 2025-09-28): Secrets sync apply with approval.
- M4 (2025-09-28): Live audit run and artifact collected.
- M5 (2025-09-29): Deliverables A–E published.
- M6 (2025-09-29 → 2025-10-06): ECS minimal migration proposal and cost estimate.

Risk Register (key items)
- Secret drift: mitigate with dry-run, Actions-run, and audit logs.
- OIDC misconfig: mitigate by restricting `sub` in trust policy and testing on `main`.
- Unexpected cost: minimize by avoiding resource provisioning until approved.

Checklists
- Release checklist: CI green; repo secrets set; smoke tests pass.
- Secrets change checklist: mapping reviewed; dry-run → approval → apply.
- Rollback checklist: revert PR, re-run previous deployment tag.

Appendix — Helpful commands
- Check role ARN:
  aws iam get-role --role-name gh-oidc-autorisen-ecr --query 'Role.Arn' --output text

- Create role (example):
  aws iam create-role --role-name gh-oidc-autorisen-ecr \
    --assume-role-policy-document file://infra/aws-ecs-skel/trust-policy.json

Maintainers: ops@example.com, infra@example.com, repo-admin@example.com

<!-- PLAN:BEGIN -->

| Id | Title | Status | Owner | Priority |
| --- | --- | --- | --- | --- |
| AUTH-005 | Security hardening & tests | todo | backend | high |
| FE-004 | Login page + form | todo | frontend | high |
| DEVOPS-035 | Prod deploy / Capecraft | blocked | devops | high |

<!-- PLAN:END -->
