# Payments Security Notes (PayFast)

To enable the PayFast-backed `PaymentsAgent`, configure the following environment
variables in the backend deployment (no secret values should be committed):

- `PAYFAST_MERCHANT_ID`
- `PAYFAST_MERCHANT_KEY`
- `PAYFAST_PASSPHRASE`
- `PAYFAST_MODE` (e.g., `sandbox`, `production`)
- `PAYFAST_RETURN_URL`, `PAYFAST_CANCEL_URL`
- `PAYFAST_NOTIFY_URL` (public ITN endpoint)

Security requirements:

1. **Signed ITN enforcement** – verify the PayFast signature for every Instant
   Transaction Notification before persisting events or triggering workflows.
2. **Server-to-server validation** – perform a server-side validation call back to
   PayFast for each ITN payload and reject mismatches.
3. **No PAN storage** – only handle payment references and tokens that PayFast
   returns; never store raw card data in CapeControl systems.
4. **Least-privilege webhooks** – expose the ITN endpoint under
   `/api/payments/payfast/itn` with minimal middleware and strict IP filtering when
   possible.
