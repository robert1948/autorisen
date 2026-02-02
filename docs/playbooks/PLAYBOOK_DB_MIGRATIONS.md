# PLAYBOOK — DB Migrations (MVP)

## Purpose
Define the authoritative, management-approved process for database schema changes in CapeControl MVP.
This playbook exists to ensure migrations are explicit, reviewed, and never run implicitly or without approval.

## Scope
- **Applies to:** MVP schema changes managed via Alembic in this repo.
- **Does not include:** Any production execution, emergency hotfixes, or scope expansion beyond SYSTEM_SPEC.
- **Non-goal:** Running migrations by default (deploy and migrate are separate steps).

## Spec References
- SYSTEM_SPEC §2.6.3 (Migration & Schema Management)
- SYSTEM_SPEC §6.3 (Migration Rules)
- SYSTEM_SPEC §2.6.4 (Environments)

## Golden Rules
- **Least privilege:** changes must be minimal and necessary to satisfy SYSTEM_SPEC.
- **Evidence-first:** all steps must be logged with commands, outputs, and approvals.
- **Rollback mindset:** every migration must consider downgrade/rollback impact.
- **No implicit execution:** migrations never run automatically on deploy.

## Preconditions
- The change is required to satisfy SYSTEM_SPEC scope.
- A migration plan exists (upgrade + rollback/downgrade where feasible).
- Explicit management approval is recorded **before any migration is executed**.
- Deploy and migrate are treated as separate steps.

## Allowed Actions
- Draft and review Alembic migration files (only as part of an approved engineering task).
- Update migration documentation and runbook steps.
- Validate migration safety in local/dev and test environments.

## Blocked Actions
- **No production migrations** in this playbook.
- **No manual production schema edits** under any circumstance.
- **No implicit migration execution** during deploy/startup.
- **No scope expansion** beyond SYSTEM_SPEC.

## Step-by-Step Workflow
1. **Prep**
	- Confirm the WO is approved and within SYSTEM_SPEC scope.
	- Identify data risks and rollback considerations.
2. **Generate (draft only)**
	- Create Alembic migration files with clear intent and minimal changes.
3. **Review**
	- Peer review of migration logic (upgrade + downgrade path).
	- Validate compatibility with current schema and data constraints.
4. **Authorize**
	- Record explicit management approval **before** execution.
5. **Apply (only when authorized)**
	- Run migrations **only** in approved non-prod environments.
6. **Verify**
	- Confirm schema state and app health in the target environment.
7. **Record Evidence**
	- Save command outputs, approvals, and verification results with the WO.

## Evidence Checklist
- WO link + approval reference
- `alembic revision --autogenerate -m "..."` (or equivalent) output
- Migration file diff (upgrade/downgrade sections)
- `alembic upgrade head` output (non-prod only, when authorized)
- Post-migration verification command outputs (health checks, targeted queries)
- Rollback plan or downgrade test evidence (if applicable)

## Verification Commands (Examples)
- `alembic current`
- `alembic history -i`
- `alembic upgrade head` (non-prod only, with approval)
- `alembic downgrade -1` (if rollback test is required)

## Explicit Stop Conditions
- Stop immediately if the change requires manual production schema edits.
- Stop immediately if the migration would run implicitly on deploy.
- Stop immediately if approval is missing or ambiguous.
- Stop immediately if the change expands scope beyond SYSTEM_SPEC §2.6.
- Stop immediately if tests/verification fail in the approved environment.
- Stop immediately if any production boundary is touched.
