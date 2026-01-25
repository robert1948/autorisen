# WO-NAV-TRUST-ALIGN-001 — Align all navigation and footer links to trust states and accessibility standards

## Status

Approved — Pending Post-Freeze Execution

## Blocker

MVP Freeze ends 2026-01-31 (inclusive)

## Earliest Start

2026-02-01

## Purpose

Align all user-facing navigation and footer links to a single trust-preserving standard so the UI never presents dead ends, ambiguous destinations, or misleading affordances.

## Canonical Rule

- 3-State Rule: `docs/spec/3_state_rule.md`

## Scope (Post-freeze execution only)

- Navigation (top nav, side nav, in-app nav)
- Footer links
- Primary CTAs that function as navigation
- Trust/clarity copy where needed to explain unavailable destinations

## Non-goals

- No feature expansion
- No backend changes
- No deployments as part of this WO definition
- No migrations

## Acceptance Criteria

- Every visible navigation item conforms to exactly one 3-State outcome:
  - Works
  - Explains
  - Hidden
- No dead links remain in navigation or footer.
- Any auth-gated destinations present a truthful UX path (e.g., login/register soft-gate) rather than silent redirects.
- Accessibility check: focus order, aria-labels where appropriate, and link semantics preserved.

## Evidence

- Manual verification in autorisen
- Record any exceptions as separate planned WOs (do not bundle unrelated gaps)
