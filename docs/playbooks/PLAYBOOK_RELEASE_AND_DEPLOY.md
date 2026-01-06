# PLAYBOOK — Release & Deploy (MVP)

## Purpose
Define the minimal, authoritative release and deployment guardrails for MVP.
This playbook ensures deployments are controlled, reversible, and do not implicitly run migrations.

## Spec References
- SYSTEM_SPEC §6.2 (Deployment Rules)
- SYSTEM_SPEC §6.3 (Migration Rules)
- SYSTEM_SPEC §2.6.3 (Migration & Schema Management)

## Preconditions
- The change set is within SYSTEM_SPEC scope.
- Required approvals (as defined in SYSTEM_SPEC §6.2) are recorded.
- Rollback expectations are documented.
- If a migration is involved: explicit approval exists and migration steps are separated from deploy.

## Allowed Actions
- Prepare release notes and a rollback checklist.
- Execute a deployment according to approved workflow (in an engineering task).
- Perform post-deploy validation according to defined health checks.

## Explicit Stop Conditions
- Stop immediately if deploy would include implicit migrations.
- Stop immediately if rollback is not feasible or not documented.
- Stop immediately if deploy would enable payment execution work (NEXT-003 remains blocked).
- Stop immediately if required approvals are missing.
