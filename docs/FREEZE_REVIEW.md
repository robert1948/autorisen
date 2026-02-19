# CapeControl — Management Freeze Review

Derived strictly from SYSTEM_SPEC.
Initial review: 2026-01-06
**Updated review: 2026-02-19** (GOV-003, session refresh)

---

## Review Purpose

This document records the formal management assessment of which SYSTEM_SPEC
sections are FROZEN (no changes without playbook + approval), FLEXIBLE (may
evolve within guardrails), or DEFERRED (not yet actionable). It is the
capstone governance artifact that other playbooks and work orders reference.

---

## Section Statuses

| SYSTEM_SPEC section | Status | Rationale | Evidence (since 2026-01-06) |
| --- | --- | --- | --- |
| §1 Purpose & Scope | FLEXIBLE | May evolve as the spec matures, without changing MVP guardrails. | No changes needed. |
| §2 System Boundaries | FROZEN | Defines responsibility split and blocked work constraints. | NEXT-003 unblocked 2026-02-15; PayFast in-progress. |
| §2.5 MVP Pages & Navigation | FROZEN | Authoritative MVP page list; out-of-list pages are out of scope. | MVP-ROUTES-001 checklist published (PR #54). Onboarding gate rules added (MVP-ROUTES-002). ROUTING-SPA-API-001 fixed SPA fallback (PR #44). SPA fallback now blocks .php/.asp probes (2026-02-19). |
| §2.6 Data & PostgreSQL | FROZEN | Authoritative MVP data scope and migration guardrails. | DB-001 established scope (2026-01-06). SPEC-009 added normative migration rules (PR #53). DB-002 playbook published (PR #56). 32 migration files in versions/. |
| §3 Authentication & Security Model | FROZEN | Stability required; auth/CSRF must not churn during MVP. | SPEC-001 filled §3.1 auth flows (PR #42). SPEC-002 filled §3.2 CSRF policy (PR #52). GOV-001 playbook published (PR #55). Google & LinkedIn OAuth fully activated (2026-02-18). OAuth state uses HMAC-signed token for domain mismatch resilience. |
| §3.1 Auth Flows | FROZEN | Fully specified: login, refresh, logout, me, csrf bootstrap, OAuth (Google/LinkedIn). | SPEC-001 completed 2026-02-10. FEAT-OAUTH-001 activated Google & LinkedIn (2026-02-18). |
| §3.2 CSRF Policy | FROZEN | Fully specified: double-submit pattern, cookie/header requirements, exemptions. | SPEC-002 completed 2026-02-12. SECURITY_CSRF.md is canonical detail reference. Note: /checkout exemption was removed from code (now requires CSRF + JWT). |
| §3.3 Session Guarantees | PLACEHOLDER | Section exists but content is placeholder ("What the system guarantees / does not guarantee"). | SPEC-003 is planned (P1). |
| §3.4 Frozen vs Flexible Areas | PLACEHOLDER | Section exists but content is placeholder ("Frozen: to be defined / Flexible: to be defined"). | SPEC-004 is planned (P1). This freeze review partially satisfies the intent. |
| §4 Payments — Intent Only | IN PROGRESS | Intent constraints defined; PayFast integration unblocked and in-progress. | PAY-INTENT-001 confirmed intent-only scope (2026-01-06). NEXT-003 unblocked 2026-02-15; PayFast checkout endpoint active. |
| §4.4 NEXT-003 Preconditions | UNBLOCKED | All preconditions met as of 2026-02-15. | Auth/CSRF frozen. Management approval granted. PayFast feature flag enabled. |
| §5 Testing Strategy | FLEXIBLE | Strategy can be refined while staying within determinism guardrails. | §5.1 and §5.2 remain placeholder. SPEC-005, SPEC-006 are planned (P1). |
| §6 Operational Guardrails | FROZEN | Deployment/migration separation and approvals are enforced. | §6.1–§6.3 remain high-level. SPEC-008 (deploy rules) planned (P1). Migration rules detailed in §2.6.3 via SPEC-009. |
| §7 Roadmap & Unlock Criteria | DEFERRED | Unlock criteria published; execution blocked until gates met. | SPEC-010 published §7.2 normative unlock criteria (2026-02-03). Stage A–D gates defined. |
| §8 Change Control | FROZEN | Governs edits and authority to prevent drift. | §8.1 remains placeholder. SPEC-011 planned (P1). §8.2 authority statement is present. |

---

## Freeze Integrity Assessment

### Fully Frozen and Specified (safe to build against)

| Area | Key artifacts |
|---|---|
| §3.1 Auth Flows | SYSTEM_SPEC §3.1, PLAYBOOK_AUTH_CHANGES.md |
| §3.2 CSRF Policy | SYSTEM_SPEC §3.2, SECURITY_CSRF.md, PLAYBOOK_AUTH_CHANGES.md |
| §2.5 MVP Pages & Navigation | MVP_PAGES_AND_ROUTES.md, onboarding gate in §2.5.7 |
| §2.6.3 Migration Rules | SYSTEM_SPEC §2.6.3 (SPEC-009), PLAYBOOK_DB_MIGRATIONS.md |

### Frozen but Incomplete (placeholder sections within frozen areas)

| Section | Gap | Planned WO |
|---|---|---|
| §3.3 Session Guarantees | Content is placeholder | SPEC-003 (P1) |
| §3.4 Frozen vs Flexible Areas | Content is placeholder | SPEC-004 (P1) |
| §6.1 Development Rules | High-level only | SPEC-007 (P2) |
| §6.2 Deployment Rules | High-level only | SPEC-008 (P1) |
| §6.3 Migration Rules | High-level only (detail is in §2.6.3) | — (covered by SPEC-009) |
| §8.1 How This Spec Is Updated | Content is placeholder | SPEC-011 (P1) |

These placeholders do not block current work but should be filled before
Stage A unlock (§7.2.2).

### Deferred (explicitly not actionable)

| Area | Reason |
|---|---|
| §7 Roadmap progression | Gates defined but execution blocked until met |

---

## Required Confirmations

All confirmations are valid as of 2026-02-19:

- [x] **Auth flows are FROZEN** — §3.1 fully specified (SPEC-001, PR #42). Google & LinkedIn OAuth activated (FEAT-OAUTH-001).
- [x] **CSRF policy is FROZEN** — §3.2 fully specified (SPEC-002, PR #52). SECURITY_CSRF.md is canonical.
- [x] **MVP page list is FROZEN** — §2.5 checklist published (MVP-ROUTES-001, PR #54).
- [x] **PostgreSQL scope is FROZEN** — §2.6 scope established (DB-001). Migration rules defined (SPEC-009, PR #53).
- [x] **Payments in-progress** — §4 PayFast integration unblocked (NEXT-003, 2026-02-15). Feature flag enabled.
- [x] **NEXT-003 is UNBLOCKED** — §4.4 all preconditions met. In-progress since 2026-02-15.
- [x] **Operational guardrails are FROZEN** — §6 enforces deploy/migrate separation.
- [x] **Change control is FROZEN** — §8.2 authority statement is present.
- [x] **Auth changes playbook exists** — PLAYBOOK_AUTH_CHANGES.md (GOV-001, PR #55). Updated 2026-02-19 with OAuth section.
- [x] **Migration playbook exists** — PLAYBOOK_DB_MIGRATIONS.md (DB-002, PR #56).

---

## NEXT-003 Status

NEXT-003 (PayFast production transaction) is **IN PROGRESS**.

| Precondition (§4.4) | Status |
|---|---|
| Specification is approved | MET — frozen sections are stable; spec is authoritative |
| Auth and CSRF sections are frozen | MET — §3.1 and §3.2 fully specified and frozen |
| Explicit management approval recorded | MET — unblocked 2026-02-15 per PLAYBOOK_NEXT_003_UNBLOCK.md |

PayFast feature flag is enabled. Checkout endpoint is active with JWT auth + CSRF.
Live R5 verification pending.

---

## Risks and Recommendations

1. **Placeholder sections within frozen areas** — §3.3, §3.4, §6.1–§6.3, §8.1
   are frozen but contain placeholder text. Recommend completing SPEC-003, SPEC-004,
   and SPEC-011 before Stage A unlock to avoid ambiguity.

2. **§6.3 duplication** — Migration rules are detailed in §2.6.3 (SPEC-009) but §6.3
   still has placeholder text. Recommend either filling §6.3 with a cross-reference
   or merging the sections to eliminate confusion.

3. **CSRF doc/code discrepancy** — `SECURITY_CSRF.md` lists `/api/payments/payfast/checkout`
   as CSRF-exempt, but the code (`csrf.py`) only exempts `/itn`. The checkout endpoint
   now requires CSRF + JWT auth. Update the doc to match code.

4. **OAuth state resilience** — The HMAC-signed state parameter approach works but
   relies on `SECRET_KEY` consistency across environments. Document this dependency
   in the auth playbook (done 2026-02-19).

5. **Two parallel onboarding flows** — MVP onboarding (`/onboarding/*`) and canonical
   app onboarding (`/app/onboarding/*`) coexist. Consolidate when feature flags are
   removed to avoid confusion.

---

## Review History

| Date | Reviewer | Changes |
|---|---|---|
| 2026-01-06 | Management | Initial freeze review — established section statuses |
| 2026-02-12 | GOV-003 | Full review refresh — added evidence, integrity assessment, gap analysis, confirmations, NEXT-003 assessment, risks |
| 2026-02-19 | GOV-003 | Session refresh — NEXT-003 unblocked (in-progress), OAuth activated, auth playbook updated with OAuth section, CSRF discrepancy noted, new risks added (dual onboarding, OAuth state), 11 engineering tasks completed |
