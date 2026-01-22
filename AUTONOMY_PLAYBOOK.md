# AUTONOMY_PLAYBOOK.md

## Authority Chain (Mandatory)

Robert (final authority) → CapeAI (planning & governance) → VS_Chat (manager / orchestrator) → Codex (worker / implementer)

Sandbox only: autorisen (staging)

## Binding Governance References

Reference (authoritative; binding on all autonomous execution): docs/SYSTEM_SPEC.md §6.3 Migration Rules

### SYSTEM_SPEC §6.3 Migration Rules (Verbatim)

This section defines the authoritative governance rules for database/schema migrations.
These rules complement §2.6.3 (Migration & Schema Management) and are binding for all environments.

#### Approval (Required)

- Every migration MUST be explicitly approved before execution.
- “Approved” means a recorded, intentional decision by the designated authority for the target environment (see Environment Boundaries).
- Migrations MUST NOT be executed on an “assumed safe” basis.

#### No Implicit / Automatic Migrations

- The application MUST NOT run migrations automatically on startup.
- Deploy and migrate MUST be separate, explicit steps (never implicit).

#### Environment Boundaries

- **Local/dev:** migrations MAY be executed after review/approval in the local dev workflow.
- **Staging (autorisen):** migrations MAY be executed only after explicit approval and with a rollback plan.
- **Production (capecraft):** migrations MUST NOT be executed without explicit Robert approval.

#### Allowed Change Mechanism

- Schema changes MUST be performed only via versioned migrations committed to version control.
- Manual/ad-hoc schema edits MUST NOT be used in any shared environment (staging/production).

#### Rollback Policy

- Every migration MUST include downgrade guidance where feasible.
- Rollbacks in staging MAY be executed when needed and approved.
- Rollbacks in production are high-risk and MUST be treated as an exceptional action requiring explicit Robert approval.

#### Hard Stop Conditions

Migration execution MUST STOP immediately if any of the following are true:
- Approval for the target environment is missing.
- The migration is not present in version control (i.e., not a reviewed, versioned migration).
- The migration implies automatic execution during deploy/startup.
- The environment target is ambiguous (local vs autorisen vs capecraft).

## Autonomous Agent Constraint (Mandatory)

Autonomous agents (including Codex) MUST comply with docs/SYSTEM_SPEC.md §6.3 Migration Rules.

- Autonomous agents MUST NOT create, apply, suggest, or infer database migrations.
- Autonomous agents MUST NOT run migrations on startup.
- Autonomous agents MUST NOT resolve schema drift automatically.
- Autonomous agents MUST STOP and escalate if migration intent is detected.

Escalation target: Robert

## Hard STOP Clause

Any of the following triggers an immediate halt and escalation to Robert:

- Alembic execution without explicit Work Order.
- Automatic or implicit migrations.
- Environment ambiguity.
- “Safe assumption” migrations.

## Environment Boundary Clarity

- local / dev ≠ autorisen ≠ capecraft
- Production (capecraft) migrations are Robert-only decisions.

## VS_Chat Direct Execution Authority (Limited)

VS_Chat MAY execute tasks directly without delegating to Codex ONLY IF ALL of the following conditions are true:

- The task type is explicitly one of: Documentation, Planning, Bookkeeping, Status/checklist updates.
- No code, scripts, CI, infra, migrations, or deploys are involved.
- Changes are limited to exactly one file.
- Exactly one commit is produced.
- Full diff and post-commit evidence is provided.

VS_Chat MUST NOT directly execute tasks involving:

- Application or infrastructure code.
- Database schema or migrations.
- CI/CD pipelines.
- Secrets or credentials.
- Environment variables.
- Any production (capecraft) activity.
- Any action with operational side effects.

Such tasks MUST be delegated to Codex.

This refinement increases efficiency for low-risk tasks only and does not alter any existing authority boundaries, migration rules, deployment rules, or production safeguards.

If task classification is ambiguous, VS_Chat MUST STOP and escalate to Robert.

## Standard Evidence Pack (All Work Orders)

Every Work Order MUST include the following evidence items unless explicitly waived by Robert.

### Mandatory Evidence (Core)

```bash
git status --porcelain
git diff --name-only
git diff -- <scoped file(s)>
git show --name-only --oneline -1
```

- `git status --porcelain`: proves the working tree is clean at closure (no uncommitted changes).
- `git diff --name-only`: proves scope discipline by listing exactly which files changed.
- `git diff -- <scoped file(s)>`: proves the exact content changes in the allowed file(s).
- `git show --name-only --oneline -1`: proves what was actually committed and which files are in the last commit.

### Clean-Tree Requirement

- `git status --porcelain` MUST be empty at Work Order closure.
- Any uncommitted change is a hard STOP.

### Scope Discipline Rule

- Evidence MUST prove that only allowed files were modified.
- Any unexpected file change (including implicit or transitive changes) is Work Order rejection.

### Work-Order-Specific Evidence (Conditional)

Additional evidence may be required depending on Work Order class, but never instead of the Mandatory Evidence (Core):

- Docs / Governance: file diffs only.
- UI / Frontend: build output (e.g., `npm run build`).
- Backend: tests and/or migration dry-run output as specified by the Work Order.
- Deploy / Migration: explicit environment confirmation plus relevant logs/output as specified by the Work Order.

### Authority Statement

No Work Order may be accepted or closed without a complete Evidence Pack. Evidence is authoritative over narrative description.

### Waiver Rule

- Evidence requirements may be waived only by Robert.
- Any waiver MUST be explicit and recorded in the Work Order.
