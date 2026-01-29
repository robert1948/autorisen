# docs/project-plan.csv (SSOT)

This repository’s SSOT plan is the machine-parseable CSV file:

- `docs/project-plan.csv`

The CSV is intentionally kept free of blank lines and comment/header blocks so standard CSV tooling (`csv.reader`, spreadsheet imports, etc.) can parse it with a strict 9-column schema.

## Historical commentary (moved from CSV)

The following comment blocks and section headings were previously embedded in the CSV and are preserved here for human context.

### CapeControl MVP Plan

- CapeControl MVP Plan (Derived strictly from `docs/SYSTEM_SPEC.md`)

Rules:
- Every row MUST reference a `SYSTEM_SPEC` section.
- `status` MUST be one of: `planned | in_progress | blocked | done`
- Payments execution work remains out of scope; `NEXT-003` stays blocked.

### System Spec Completion

- SYSTEM SPEC COMPLETION (spec has placeholders that must match implementation)

### MVP Pages & Navigation

- MVP PAGES & NAVIGATION (authoritative route list)

### UX Work Orders

- UX WORK ORDERS (implementation work; execution gated by status)

### Data & PostgreSQL

- DATA & POSTGRESQL (authoritative scope + governance)

### Payments

- PAYMENTS (INTENT ONLY) — EXECUTION BLOCKED

### Governance Playbooks

- GOVERNANCE PLAYBOOKS (derived guardrails)
