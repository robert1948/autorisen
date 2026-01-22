# WO-MIGRATION — Database Migration Work Order Template (Normative)

## Authority Chain (MANDATORY — DO NOT ALTER)

**Robert (final authority)** → **CapeAI (planning & governance)** → **VS_Chat (manager/orchestrator)** → **Codex (worker/implementer)**

> **Sandbox only:** `autorisen` (staging)
> ❌ **No production (`capecraft`) deploys, releases, or migrations unless Robert explicitly instructs it**

---

## Work Order

**WO-MIGRATION-XXX — <Short migration title>**

- Requested by: <name/role>
- Date: <YYYY-MM-DD>
- Target service/app: <e.g., backend>
- Target database: <name>

---

## 1) Authority & Environment

### Environment Selection (choose exactly one)

- [ ] local / dev
- [ ] autorisen (staging)
- [ ] capecraft (production — Robert-only)

### Required Approval Authority (explicit)

- local / dev:
  - Approver(s): <name/role>
- autorisen (staging):
  - Approver(s): <name/role>
- capecraft (production — Robert-only):
  - Approver: **Robert** (mandatory)

> If environment is ambiguous or multiple environments are checked: **STOP** (reject).

---

## 2) Explicit Governance References

This Work Order is governed by, and MUST comply with:

- `SYSTEM_SPEC.md §6.3 Migration Rules`
- `AUTONOMY_PLAYBOOK.md` (migration constraints)

No paraphrasing that weakens authority. If any instruction here conflicts with the above, **STOP** and escalate to **Robert**.

---

## 3) Migration Intent

### What is changing?

- Tables/columns/indexes/constraints affected:
  - <list>
- Data changes (backfill/transform/delete):
  - <list>

### Why is the migration required?

- Problem / requirement:
  - <text>
- Impact if not performed:
  - <text>

### Why no alternative exists?

- Alternatives considered (and rejected):
  - <list>
- Reason alternatives are not viable:
  - <text>

---

## 4) Versioned Migration Declaration

### Migration Identity

- Tooling: <e.g., Alembic>
- Migration ID / revision:
  - <revision>
- Down revision(s):
  - <down_revision>
- Branch labels / dependencies (if any):
  - <values>

### Mandatory Confirmations (must be explicitly answered)

- [ ] No automatic startup migrations exist (no implicit migrations on app/container start).
- [ ] Migration is versioned (checked into the repo) and reviewable.
- [ ] Migration is reversible.
  - If NOT reversible, explain why and provide compensating controls:
    - <text>

---

## 5) Rollback Plan (MANDATORY)

> “No rollback plan” = automatic rejection.

### Exact Rollback Steps

1. <step>
2. <step>
3. <step>

### Rollback Triggers (conditions that force rollback)

- <trigger>
- <trigger>

### Post-Rollback Verification

- Health checks to run:
  - <commands/endpoints>
- Data integrity checks:
  - <queries/criteria>
- Confirmation of restored application behavior:
  - <criteria>

---

## 6) Evidence Pack Checklist (PASTE OUTPUTS)

All items below MUST be attached (paste outputs or provide links to captured logs).

### Required Evidence (pre-approval)

- [ ] Target environment confirmation (from Section 1)
- [ ] Schema diff or clear schema change description
- [ ] Dry-run output (if applicable to the tooling/environment)
- [ ] Backup confirmation (where applicable)

### Evidence Attachments

#### Dry-run / Plan Output (paste)

```text
<paste output here>
```

#### Schema Diff or Change Description (paste)

```text
<paste diff/description here>
```

#### Backup Confirmation (where applicable) (paste)

```text
<paste evidence here>
```

---

## 7) Hard STOP Conditions

If ANY of the following are true, the migration MUST NOT proceed:

- Missing required approval for the selected environment
- Environment ambiguity (multiple environments selected, or not explicitly selected)
- Unversioned migration (not committed/reviewable)
- Implicit or startup-triggered migrations (automatic migrations on app/container start)
- Missing rollback plan
- Evidence pack incomplete or not pasted
- Any instruction conflicts with `SYSTEM_SPEC.md §6.3 Migration Rules` or `AUTONOMY_PLAYBOOK.md`

---

## 8) Final Approval Gate

> “No migration may proceed without this Work Order approved.”

### Approval Sign-Off

- [ ] Approver name / role: <SIGNATURE>
- [ ] Date: <YYYY-MM-DD>

### Robert Approval (mandatory for capecraft)

- [ ] Robert approval (required for capecraft/production): <SIGNATURE>
- [ ] Date: <YYYY-MM-DD>
