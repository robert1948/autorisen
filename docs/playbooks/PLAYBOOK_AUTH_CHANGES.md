# PLAYBOOK — Auth & CSRF Changes (MVP)

## Purpose
Define governance guardrails for any changes to authentication and CSRF behavior.
This playbook exists to keep the session and CSRF model stable for MVP.

## Scope
- **Applies to:** Auth and CSRF behavior defined by SYSTEM_SPEC and supporting docs.
- **Does not include:** Implementation changes, migrations, or deploy actions.
- **Non-goal:** Creating new auth flows beyond SYSTEM_SPEC.

## Spec References
- SYSTEM_SPEC §3 (Authentication & Security Model)
- SYSTEM_SPEC §3.2 (CSRF Policy)
- SYSTEM_SPEC §3.3 (Session Guarantees)
- SYSTEM_SPEC §8 (Change Control)

## Golden Rules
- **Stability first:** do not weaken or widen auth/CSRF behavior without explicit approval.
- **Evidence-first:** every change must include rationale, diff, and verification notes.
- **No hidden behavior:** all cookie/header/token changes must be documented.
- **No implicit execution:** no deploys or migrations from this playbook.

## Preconditions
- The proposed change is required to satisfy SYSTEM_SPEC scope.
- Auth and CSRF documentation is up to date and used as the baseline.
- The change is reviewed for security impact.
- Any cookie/header name changes are explicitly documented.

## Allowed Actions
- Update SYSTEM_SPEC language to reflect authoritative behavior.
- Update SECURITY_CSRF.md as the canonical CSRF detail reference.
- Add or refine playbooks/runbooks (docs-only).
- Propose test changes in a separate, approved engineering WO.

## Blocked Actions
- **No new auth flows** not covered by SYSTEM_SPEC.
- **No changes to runtime behavior** (code changes) in this doc-only WO.
- **No migrations or deploys.**
- **No payment execution work** (NEXT-003 remains blocked).

## Step-by-Step Workflow
1. **Prep**
	- Identify the SYSTEM_SPEC section(s) impacted.
	- Verify current behavior aligns with docs (no code changes here).
2. **Draft**
	- Update documentation with precise, testable statements.
3. **Review**
	- Security review of the doc changes for unintended weakening.
4. **Verify**
	- Confirm references and links point to the canonical sources.
5. **Record Evidence**
	- Capture diffs, review notes, and verification outputs.

## Evidence Checklist
- Diff of updated docs (before/after)
- References to SYSTEM_SPEC sections updated
- Notes on impact (what changed, what did not)
- Any required follow-on WO IDs (if code changes are needed)

## Verification Commands (Examples)
- `rg -n "CSRF|auth" docs/SYSTEM_SPEC.md docs/SECURITY_CSRF.md`
- `git diff --stat`
- `git diff`

## Explicit Stop Conditions
- Stop immediately if the change would weaken CSRF/session protections.
- Stop immediately if the change would introduce a new auth flow not covered by SYSTEM_SPEC.
- Stop immediately if the change requires payment execution work (NEXT-003 remains blocked).
- Stop immediately if change control requirements (SYSTEM_SPEC §8) are not met.
- Stop immediately if the change would require code updates in this doc-only WO.
