## Implementation Steps (Propose First)

1. Confirm the task ID corresponds to a row in `docs/project-plan.csv`.
1. Propose a step-by-step implementation plan.
1. After approval:
   1. Implement code changes.
   1. Update the matching row in `docs/project-plan.csv` with new `status`, `completion_date`, and `notes`.
   1. Update relevant documentation if required.
1. Provide a unified git diff for review.

---

## Output Format

1. Restate your understanding.
1. Propose the implementation plan.
1. Wait for approval.
1. After approval: show the unified diff, including all CSV updates.

---

## Linked Project Plan Row

- **id**: AUTH-004
- **task**: MFA system (TOTP)
- **owner**: backend
- **status**: completed
- **priority**: P0
- **completion_date**: 2025-11-07
- **notes**: 6-digit TOTP with QR code enrollment
- **artifacts**: backend/src/modules/auth/mfa.py
- **verification_commands**: Manual test MFA flow on staging
