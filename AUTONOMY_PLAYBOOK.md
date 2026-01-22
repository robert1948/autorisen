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
