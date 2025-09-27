# Master Project Plan — autorisen

Snapshot: 2025-09-26

Purpose
- Provide a single, actionable project plan derived from `docs/senior_devops.md` for ops, infra, and product to execute and update.
- Make tasks small, assign owners, set target dates, list dependencies, acceptance criteria, and status.

How to use this document
- Owners update their task status inline (To Do / In Progress / Done) and append short notes with date + initials.
- The project lead runs weekly triage against this plan and updates priorities.

Legend
- R: Responsible (executor)
- A: Accountable (decision owner)
- S: Stakeholders / Support
- Dates are target dates (YYYY-MM-DD)

Master milestones (high level)

1. OIDC & Secrets alignment — validate OIDC assume-role and sync GitHub → Heroku (Target: 2025-09-27)
2. Live audit run & artifact capture (Target: 2025-09-28)
3. Deliverables A–E produced and reviewed (Target: 2025-09-29)
4. Minimal ECS migration plan (cluster + single task) and cost estimate (Target: 2025-10-06)

Detailed tasks

Task 1 — Verify OIDC assume-role end-to-end
- ID: T1
- Owner (R/A): ops / repo-admin
- Target: 2025-09-26 -> 2025-09-27
- Steps:
  1. Merge PR #7 (test workflow) into `main` (A: repo-admin)
  2. Dispatch `Test OIDC Assume Role` workflow on `main` and confirm `aws sts get-caller-identity` returns the assumed role ARN (R: ops)
  3. If failure, troubleshoot trust policy (`infra/aws-ecs-skel/trust-policy.json`), OIDC provider, and repo secret `AWS_OIDC_ROLE` (R: ops)
- Dependencies: role ARN present in `AWS_OIDC_ROLE`, GH Actions runner network egress to AWS
- Acceptance criteria: workflow prints expected ARN that matches the IAM role `gh-oidc-autorisen-ecr`.
- Status: Not Started

Task 2 — Create safe GitHub -> Heroku sync workflow (dry-run then apply)
- ID: T2
- Owner (R/A): ops / repo-admin
- Target: 2025-09-27
- Steps:
  1. Create a workflow `ci/sync-github-to-heroku.yml` that runs on `workflow_dispatch` and executes `infra/scripts/sync_github_to_heroku.sh` without `--apply` (dry-run) and uploads output as an artifact. (R: ops)
  2. Dispatch the workflow, review artifact, and confirm planned writes. (R: ops, S: infra)
  3. If confirmed, re-run with `--apply` in a second, narrowly permissioned workflow run. (R: ops)
  4. Record audit log and update `docs/senior_devops.md` and secrets matrix with any changes. (R: ops)
- Dependencies: `HEROKU_API_KEY` and `HEROKU_APP_NAME` present as repo secrets; mapping `infra/secrets-mapping.json` correctness.
- Acceptance criteria: Heroku config-vars updated to match GitHub SSOT mappings; audit log captured and saved as artifact.
- Status: Not Started

Task 3 — Run Live Audit (Heroku + AWS) and capture artifact
- ID: T3
- Owner (R/A): ops / project lead
- Target: 2025-09-28
- Steps:
  1. Ensure Task 1 and Task 2 completed (or at least Task 1 validated). (A: project lead)
  2. Dispatch `.github/workflows/live-audit.yml` on `main` with `HEROKU_API_KEY` present in secrets. (R: ops)
  3. Download `live-audit-output` artifact and archive it in the repo under `artifacts/live-audit/` with date prefix. (R: ops)
  4. Run quick checks: Heroku dynos, config-vars, DB connectivity tests (if available). (R: ops)
- Dependencies: `HEROKU_API_KEY` and `AWS_OIDC_ROLE` present and valid.
- Acceptance criteria: `live-audit-output` artifact present and contains Heroku and AWS read-only inventory.
- Status: Not Started

Task 4 — Produce Deliverables A–E from audit output
- ID: T4
- Owner (R/A): project lead / ops
- Target: 2025-09-29
- Steps:
  1. Parse the live-audit artifact and fill in Deliverables A–E in `docs/senior_devops.md` and `docs/Master_Projectplan.md` (R: project lead)
  2. Add decision log entries with rationale and impact (B). (R: project lead)
  3. Confirm secrets matrix and schedule rotation items (C). (R: ops)
  4. Finalize 7-day action plan and assign owners (E). (R: project lead)
- Acceptance criteria: Deliverables A–E are completed, peer-reviewed, and stored in the repo.
- Status: Not Started

Task 5 — Create minimal ECS migration proposal (cluster + single task)
- ID: T5
- Owner (R/A): infra lead / project lead
- Target: 2025-10-06
- Steps:
  1. Capture current infra costs and identify required AWS resources for minimal migration. (R: infra)
  2. Produce Terraform plan under `infra/aws-ecs-skel/` for ECR + ECS cluster + single task definition (no ALB, no RDS). (R: infra)
  3. Estimate costs (monthly) and failure/recovery plan. (R: infra)
  4. Present to project lead for sign-off. (A: project lead)
- Acceptance criteria: Terraform plan reviewed, cost estimate within budget thresholds, rollback strategy documented.
- Status: Not Started

Communications & Reporting
- Weekly sync: every Monday 10:00 UTC — short triage to move tasks forward (owner: project lead).
- Slack channel: #autorisen-ops — use for immediate blockers.
- Artifacts: place audit artifacts into `artifacts/live-audit/YYYYMMDD/` in the repo (or in a secure artifact store if size is large).

Risks & Mitigations
- Secret drift — mitigate by running controlled sync from Actions (never export secrets locally). Use audit logs.
- Unintended writes — require dry-run & manual approval before `--apply`.
- Cost overrun — keep AWS changes in skeleton stage and only provision after sign-off.

Templates (for updating tasks)
- Status line example: `T1 — Verify OIDC — In Progress — 2025-09-26 — notes: assumed role test returned ARN xxxxx (ops)`

Appendix — Useful commands
- Create role (example):
```
aws iam create-role --role-name gh-oidc-autorisen-ecr \
  --assume-role-policy-document file://infra/aws-ecs-skel/trust-policy.json
```

Maintainers: ops@example.com, infra@example.com, repo-admin@example.com
