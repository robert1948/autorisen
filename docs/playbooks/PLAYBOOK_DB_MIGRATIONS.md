# PLAYBOOK — DB Migrations (MVP)

## Purpose

Define the authoritative, management-approved process for database schema changes
in CapeControl MVP. This playbook enforces that migrations are explicit, reviewed,
and never run implicitly.

**PostgreSQL scope is FROZEN** (FREEZE_REVIEW.md, §2.6). All schema changes must
follow this playbook without exception.

## Spec References

| Reference | Scope |
|---|---|
| SYSTEM_SPEC §2.6.1 | MVP data responsibilities |
| SYSTEM_SPEC §2.6.2 | MVP core tables (conceptual) |
| SYSTEM_SPEC §2.6.3 | Migration & schema management (incl. SPEC-009 rules) |
| SYSTEM_SPEC §2.6.4 | Environments (local/test/production) |
| SYSTEM_SPEC §6.3 | Operational migration rules |
| SYSTEM_SPEC §8 | Change control authority |
| FREEZE_REVIEW.md | Management freeze status for §2.6 |

## Scope — What Counts as a Migration

This playbook applies to any modification that:

1. **Creates or alters a database table, column, index, or constraint.**
2. **Creates or modifies an Alembic revision file** under `backend/migrations/versions/`.
3. **Changes the database connection or session configuration** in `backend/src/db/session.py`
   or `backend/src/core/config.py` (database-related settings).
4. **Modifies the migration runner** (`backend/src/db/migrations_runner.py`).
5. **Runs `alembic upgrade`, `alembic downgrade`, or equivalent** against any environment.

Changes that do **not** trigger this playbook:
- Read-only queries or ORM model additions that don't require schema changes.
- Test fixture changes using the test SQLite database.
- Pure documentation corrections with no migration artifacts.

## Preconditions (ALL must be true before starting)

- [ ] The schema change is **required** to satisfy SYSTEM_SPEC §2.6 scope.
- [ ] The change does NOT expand scope beyond MVP core tables (§2.6.2).
- [ ] A migration plan exists (upgrade path + rollback/downgrade where feasible).
- [ ] **Explicit management approval** is recorded (PR comment, issue, or chat log).
- [ ] Deploy and migrate are treated as **separate steps** (never coupled).
- [ ] `RUN_DB_MIGRATIONS_ON_STARTUP=0` remains the default in staging and production.

## Allowed Actions

| Action | Constraint |
|---|---|
| Draft an Alembic revision | Must be part of an approved engineering work order |
| Review migration files | Code review required before merge |
| Run migration locally | Safe; Docker Compose PostgreSQL on `:5433` |
| Run migration in CI/test | Uses isolated SQLite (`/tmp/autolocal_test.db`) |
| Run migration on staging | Only with evidence pack and verification (see Procedure) |
| Run migration on production | **Forbidden** unless Robert explicitly instructs and approval is recorded |
| Update migration documentation | Always allowed |

## Explicit Stop Conditions

**Stop immediately and escalate** if any of these are true:

1. The migration would **run implicitly on deploy** (auto-upgrade on startup is disabled
   via `RUN_DB_MIGRATIONS_ON_STARTUP=0` — this must never be changed in staging/production).
2. The migration requires **manual production schema edits** (direct SQL against production).
3. **Approval is missing or ambiguous** — no recorded go/no-go decision.
4. The migration would **expand scope beyond SYSTEM_SPEC §2.6** (e.g., adding analytics
   tables, media storage, or entities not in the MVP core tables list).
5. The migration is **irreversible** and no recovery approach is documented.
6. The migration would **drop data** in a non-empty table without explicit data
   migration strategy.

## Procedure

### Step 1 — Plan the migration

Before writing any code:

- [ ] Identify the schema change needed and which MVP core table(s) are affected.
- [ ] Confirm the change is within §2.6 scope.
- [ ] Document the upgrade path and downgrade/rollback approach.
- [ ] Record management approval (link to PR comment, issue, or chat log).

### Step 2 — Create the Alembic revision

```bash
# Create a new revision (local only)
make migrate-revision message="<description>"

# This generates a file under backend/migrations/versions/
# Review the generated upgrade() and downgrade() functions
```

In the revision file:
- [ ] `upgrade()` implements the schema change.
- [ ] `downgrade()` reverses the change where feasible.
- [ ] The revision message clearly describes what changes.
- [ ] The revision chain is linear (`alembic heads` returns exactly one head).

### Step 3 — Validate locally

```bash
# Apply the migration locally
make migrate-up

# Verify the schema
./.venv/bin/python -m alembic -c backend/alembic.ini current
./.venv/bin/python -m alembic -c backend/alembic.ini history --verbose | head -20

# Run tests to confirm nothing broke
make codex-test
```

### Step 4 — PR with evidence

The migration PR must include:

- [ ] Alembic revision file (reviewed).
- [ ] Rollback plan documented in the PR description.
- [ ] Verification commands included (examples below).
- [ ] Evidence artifacts captured under `docs/evidence/<WO_ID>/logs/`.
- [ ] Security impact noted if the migration touches auth-related tables (cross-ref PLAYBOOK_AUTH_CHANGES.md).

PR description template:
```
## Migration: <description>

### Schema change
- Table: ...
- Change: ADD COLUMN / CREATE TABLE / ALTER ... / etc.

### Upgrade path
- `alembic upgrade head` (revision: <hash>)

### Rollback path
- `alembic downgrade <previous_hash>`
- OR: recovery approach if downgrade is not feasible

### Verification
alembic current
alembic history | head -5
SELECT column_name FROM information_schema.columns WHERE table_name = '<table>';

### Approval
- [ ] Management approval recorded: <link>
```

### Step 5 — Deploy to staging (separate from migration)

Deploy and migrate are **always separate steps**:

```bash
# Step A: Deploy the code (no migration runs)
make deploy-heroku  # deploys to autorisen (staging)

# Step B: Run the migration explicitly
make heroku-run-migrate
# Equivalent to: heroku run --app autorisen -- python -m alembic -c backend/alembic.ini upgrade head

# Step C: Verify
heroku pg:psql -a autorisen -c "SELECT version_num FROM alembic_version;"
```

### Step 6 — Production (gated)

Production migrations on capecraft are **forbidden by default**.

They may only proceed when:
- [ ] Robert explicitly instructs the migration.
- [ ] Approval is recorded in writing (PR, issue, or chat log).
- [ ] The migration has been verified on staging first.
- [ ] A rollback plan is confirmed feasible.

```bash
# Only when explicitly approved:
heroku run --app capecraft -- python -m alembic -c backend/alembic.ini upgrade head
heroku pg:psql -a capecraft -c "SELECT version_num FROM alembic_version;"
```

## Rollback

If a migration causes issues:

### Staging (autorisen)
```bash
# Downgrade to previous revision
heroku run --app autorisen -- python -m alembic -c backend/alembic.ini downgrade -1

# Verify
heroku pg:psql -a autorisen -c "SELECT version_num FROM alembic_version;"
```

### Production (capecraft)
- Same commands with `--app capecraft`, but **only with explicit approval**.
- If downgrade is not feasible, document the recovery approach and escalate.

### If rollback fails
1. Restore from Heroku Postgres backup.
2. Document the incident in a post-mortem work order.
3. Revert the code PR on `main` and redeploy.

## Execution Guard

The system enforces migration safety via:

| Guard | Setting | Where |
|---|---|---|
| App startup | `RUN_DB_MIGRATIONS_ON_STARTUP=0` | `backend/src/core/config.py` (default: `False`) |
| Staging deploy | `RUN_DB_MIGRATIONS_ON_STARTUP=0` | Heroku config var |
| Production deploy | `RUN_DB_MIGRATIONS_ON_STARTUP=0` | Heroku config var |
| CI tests | `RUN_DB_MIGRATIONS_ON_STARTUP=0` | `tests/conftest.py` |
| CI deploy workflow | `RUN_DB_MIGRATIONS_ON_STARTUP=0` | `.github/workflows/deploy-staging.yml` |

**Never change these values.** Migrations are always run as an explicit manual step.

## Audit Trail

Every migration must produce:
- A PR with the migration revision file and rollback plan.
- Evidence of local validation (test results, `alembic current` output).
- Staging verification log (after `heroku-run-migrate`).
- Entry in `docs/project-plan.csv` linking to the work order and artifacts.
