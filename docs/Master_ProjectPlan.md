# Master Project Plan — autorisen

Snapshot: 2025-09-26

See also: `senior_devops.md`

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
2. `HEROKU_APP_NAME` and `HEROKU_API_KEY` present in repo secrets.
3. Smoke test `services/health` passes after deploy.

Rollback checklist
1. Revert release commit and re-run deploy using previous image tag.
2. Verify `/alive` returns 200.

Secrets & Infra change checklist
1. Create mapping in `infra/secrets-mapping.json` (reviewed by SEC).
2. Run sync in dry-run (`ci/sync-github-to-heroku.yml`).
3. Approve and run `--apply` in controlled workflow.

Appendix — Helpful commands

```bash
# Validate role exists
aws iam get-role --role-name gh-oidc-autorisen-ecr --query 'Role.Arn' --output text
# Master Project Plan — autorisen

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
