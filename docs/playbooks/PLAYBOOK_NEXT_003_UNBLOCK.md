# PLAYBOOK — NEXT-003 Unblock (PayFast Execution Gate)

## Purpose
Define the explicit management gate for unblocking NEXT-003.
This playbook exists to ensure PayFast execution work cannot resume without approved preconditions.

## Spec References
- SYSTEM_SPEC §2.4 (Explicitly Blocked Work)
- SYSTEM_SPEC §4 (Payments — Intent Only)
- SYSTEM_SPEC §4.4 (NEXT-003 Preconditions)
- SYSTEM_SPEC §3 (Authentication & Security Model)

## Preconditions
- SYSTEM_SPEC is approved.
- Auth and CSRF sections are marked FROZEN in FREEZE_REVIEW.
- Explicit management approval to resume NEXT-003 is recorded.
- No scope expansion beyond payments intent constraints.

## Allowed Actions
- Update documentation to record approval and freeze status.
- Update project plan status for NEXT-003 from blocked to planned/in_progress only after all preconditions are satisfied.

## Explicit Stop Conditions
- Stop immediately if ANY precondition is unmet.
- Stop immediately if the work involves payment execution while NEXT-003 is still marked blocked.
- Stop immediately if auth/CSRF stability is not frozen.
- Stop immediately if the proposed work changes payment provider or flow beyond SYSTEM_SPEC intent.
