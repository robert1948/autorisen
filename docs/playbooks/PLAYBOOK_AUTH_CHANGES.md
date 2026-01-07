# PLAYBOOK — Auth & CSRF Changes (MVP)

## Purpose
Define governance guardrails for any changes to authentication and CSRF behavior.
This playbook exists to keep the session and CSRF model stable for MVP.

## Spec References
- SYSTEM_SPEC §3 (Authentication & Security Model)
- SYSTEM_SPEC §3.2 (CSRF Policy)
- SYSTEM_SPEC §3.3 (Session Guarantees)
- SYSTEM_SPEC §8 (Change Control)

## Preconditions
- The proposed change is required to satisfy SYSTEM_SPEC scope.
- Auth and CSRF documentation is up to date and used as the baseline.
- The change is reviewed for security impact.
- Any cookie/header name changes are explicitly documented.

## Allowed Actions
- Update SYSTEM_SPEC language to reflect the authoritative behavior.
- Update SECURITY_CSRF.md as the canonical CSRF detail reference.
- Add/adjust tests only in a separately approved engineering task (not in this playbook execution).

## Explicit Stop Conditions
- Stop immediately if the change would weaken CSRF/session protections.
- Stop immediately if the change would introduce a new auth flow not covered by SYSTEM_SPEC.
- Stop immediately if the change requires payment execution work (NEXT-003 remains blocked).
- Stop immediately if change control requirements (SYSTEM_SPEC §8) are not met.
