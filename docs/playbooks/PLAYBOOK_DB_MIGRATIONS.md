# PLAYBOOK — DB Migrations (MVP)

## Purpose
Define the authoritative, management-approved process for database schema changes in CapeControl MVP.
This playbook exists to enforce that migrations are explicit, reviewed, and never run implicitly.

## Spec References
- SYSTEM_SPEC §2.6.3 (Migration & Schema Management)
- SYSTEM_SPEC §6.3 (Migration Rules)
- SYSTEM_SPEC §2.6.4 (Environments)

## Preconditions
- The change is required to satisfy SYSTEM_SPEC scope.
- A migration plan exists (upgrade + rollback/downgrade where feasible).
- Explicit management approval is recorded for running migrations.
- Deploy and migrate are treated as separate steps.

## Allowed Actions
- Draft and review Alembic migration files (only as part of an approved engineering task).
- Update migration documentation and runbook steps.
- Validate migration safety in local/dev and test environments.

## Explicit Stop Conditions
- Stop immediately if the change requires manual production schema edits.
- Stop immediately if the migration would run implicitly on deploy.
- Stop immediately if approval is missing or ambiguous.
- Stop immediately if the change expands scope beyond SYSTEM_SPEC §2.6.
