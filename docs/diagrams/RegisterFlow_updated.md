# Register Flow - SSOT

Canonical: `docs/diagrams/RegisterFlow_updated.mm`

## Invariants
- Email uniqueness enforced at DB layer (case-insensitive, race-safe).
- Registration creates user (+ related rows if used) in a single DB transaction.
- `confirm_password` is validation-only; never stored or returned.
- Terms acceptance tracked with `terms_accepted_at` and `terms_version` (when gated).
- Post-register route: `/onboarding/welcome` (unless terms gate forces `/terms`).
