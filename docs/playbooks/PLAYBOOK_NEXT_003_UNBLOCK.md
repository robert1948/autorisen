# PLAYBOOK — NEXT-003 Unblock (PayFast Execution Gate)

## Purpose
Define the explicit management gate for unblocking NEXT-003.
This playbook exists to ensure PayFast execution work cannot resume without approved preconditions.

## Spec References
- SYSTEM_SPEC §2.4 (Explicitly Blocked Work)
- SYSTEM_SPEC §4 (Payments — Intent Only)
- SYSTEM_SPEC §4.4 (NEXT-003 Preconditions)
- SYSTEM_SPEC §3 (Authentication & Security Model)

---

## Management Approval Record

| Precondition | Status | Evidence |
|---|---|---|
| SYSTEM_SPEC approved | **MET** | All placeholder sections filled (SPEC-001 through SPEC-011, PRs #42–#59) |
| Auth & CSRF sections frozen in FREEZE_REVIEW | **MET** | GOV-003 / PR #57 — §3 marked FROZEN with sub-section tracking |
| Explicit management approval recorded | **MET** | Owner (`robert1948`) approved 2026-02-13 in VS Code Chat session |
| No scope expansion beyond payments intent | **MET** | No new code required; existing implementation unchanged |

**Approval date:** 2026-02-13
**Approved by:** robert1948 (repository owner)
**Decision:** NEXT-003 is unblocked. Status may change from `blocked` → `planned`.

---

## Preconditions
- ~~SYSTEM_SPEC is approved.~~ ✅ All sections filled.
- ~~Auth and CSRF sections are marked FROZEN in FREEZE_REVIEW.~~ ✅ Confirmed in GOV-003.
- ~~Explicit management approval to resume NEXT-003 is recorded.~~ ✅ Recorded above.
- No scope expansion beyond payments intent constraints.

## Allowed Actions
- Update documentation to record approval and freeze status.
- Update project plan status for NEXT-003 from blocked to planned/in_progress only after all preconditions are satisfied.

## Explicit Stop Conditions
- Stop immediately if ANY precondition is unmet.
- Stop immediately if the work involves payment execution while NEXT-003 is still marked blocked.
- Stop immediately if auth/CSRF stability is not frozen.
- Stop immediately if the proposed work changes payment provider or flow beyond SYSTEM_SPEC intent.

---

## Execution Steps (Post-Unblock)

NEXT-003 is a **configuration + verification** task, not a code task.
All PayFast code (backend endpoints, service, schemas, ITN handler, frontend components,
database models, signature tests) already exists.

### Step 1 — Set production PayFast credentials on Heroku

```bash
heroku config:set \
  PAYFAST_MODE=production \
  PAYFAST_MERCHANT_ID=<real-merchant-id> \
  PAYFAST_MERCHANT_KEY=<real-merchant-key> \
  PAYFAST_PASSPHRASE=<real-passphrase> \
  PAYFAST_RETURN_URL=https://cape-control.com/payments/return \
  PAYFAST_CANCEL_URL=https://cape-control.com/payments/cancel \
  PAYFAST_NOTIFY_URL=https://cape-control.com/api/payments/payfast/itn \
  --app autorisen
```

### Step 2 — Execute R5.00 live verification transaction

Use the built-in `LIVE_VERIFY_R5` product code to confirm end-to-end:
1. Initiate checkout via `POST /api/payments/payfast/checkout` with `product_code: "LIVE_VERIFY_R5"`.
2. Complete payment on PayFast hosted page.
3. Verify ITN callback received and processed (`Invoice` status → `paid`).
4. Confirm `Transaction` record created with PayFast reference.

### Step 3 — Record evidence

Create `docs/evidence/NEXT-003/2026-02-XX/` with:
- Screenshot or log of successful transaction.
- Invoice + Transaction DB records.
- ITN callback payload (redacted if needed).

### Step 4 — Update project-plan.csv

Change NEXT-003 status from `planned` → `done` with completion date.
