# CapeControl — Closed Beta Pilot Playbook

> **Version:** 1.0 · **Last Updated:** 2026-02-24
> **Target:** 10–20 compliance-heavy SMBs over a 14-day evaluation window

---

## 1. Objectives

| # | Goal | Success Metric |
|---|------|----------------|
| 1 | Validate RAG-backed compliance Q&A accuracy | ≥ 85 % relevant-answer rate (user thumbs-up) |
| 2 | Prove evidence-pack audit trail value | ≥ 3 companies export an evidence pack |
| 3 | Stress-test multi-tenant isolation | Zero cross-tenant data leaks |
| 4 | Collect NPS / qualitative feedback | NPS ≥ 40 across pilot cohort |
| 5 | Validate capsule workflows | ≥ 60 % of pilots run ≥ 2 capsules |

---

## 2. Pilot Phases

### Phase 0 — Pre-Launch (T-7 days)

- [ ] Confirm staging environment (`dev.cape-control.com`) is green
- [ ] Set `BETA_MODE=1` + `BETA_INVITE_TTL_HOURS=336` (14 days) on staging
- [ ] Seed approved documents in RAG (ISO 27001 clauses, POPIA, sample SOPs)
- [ ] Set up a dedicated Slack channel `#cape-beta-pilots`
- [ ] Prepare onboarding guide (see §4)
- [ ] Admin creates beta invites for each pilot company via:
  ```
  POST /api/admin/beta/invite
  { "target_email": "...", "company_name": "...", "plan_override": "pro" }
  ```

### Phase 1 — Onboarding (Day 1–3)

- Invite emails land automatically via `send_beta_invite_email()`
- Each pilot clicks **Accept Invite & Register** link
- 15-min onboarding call per company (screen-share walkthrough)
- Checklist:
  - [ ] User registered and logged in
  - [ ] First compliance query answered
  - [ ] First capsule run (e.g. `compliance-check`)
  - [ ] Company documents uploaded to RAG

### Phase 2 — Active Evaluation (Day 3–12)

- Pilots use the platform daily for real compliance tasks
- Weekly check-in calls (Day 7, Day 12)
- Monitor via `/api/metrics` dashboard and `/api/admin/beta/stats`
- Alert thresholds:
  - < 5 queries/week per company → proactive reach-out
  - Any error rate > 5 % → engineering triage within 4 hours

### Phase 3 — Wrap-up & Conversion (Day 12–14)

- Send NPS/feedback survey (Typeform or similar)
- Export evidence pack for each pilot as proof of audit trail
- 1-on-1 debrief call with each company lead
- Extend or convert beta accounts to paid plans

---

## 3. Invite Management

### Creating invites (Admin API)

```bash
# Single invite
curl -X POST https://dev.cape-control.com/api/admin/beta/invite \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "target_email": "jane@acme.co.za",
    "company_name": "Acme Compliance Ltd",
    "plan_override": "pro",
    "note": "Pilot cohort 1 — ISO 27001 focus"
  }'
```

### Monitoring invites

```bash
# List active invites
GET /api/admin/beta/invites

# Program stats (total, used, active, expired, conversion rate)
GET /api/admin/beta/stats
```

### Revoking an invite

```bash
DELETE /api/admin/beta/invite/{invite_id}
```

---

## 4. Pilot Onboarding Guide (share with each company)

**Subject:** Getting Started with CapeControl Beta

1. **Register** — Click the link in your invite email and create your account.
2. **Upload Documents** — Go to **Documents → Upload** and add your SOPs, policies, or compliance frameworks.
3. **Ask a Question** — Open **ChatKit** and ask something like:
   - _"What does our data retention policy say about backup frequency?"_
   - _"Summarize Section 6.1 of our ISO 27001 SoA."_
4. **Run a Capsule** — Navigate to **Capsules** and try:
   - **Compliance Check** — paste a control requirement to see if your docs cover it.
   - **Clause Finder** — search across your uploaded policies for a specific clause.
5. **Export Evidence** — Use **Audit → Export Evidence Pack** to download a timestamped PDF.
6. **Give Feedback** — Use the in-app feedback button or message us in `#cape-beta-pilots`.

---

## 5. Feedback Collection

| Method | Timing | Tool |
|--------|--------|------|
| In-app thumbs up/down on answers | Continuous | Built-in |
| Weekly pulse survey (3 questions) | Day 7, Day 12 | Typeform |
| NPS + open-ended debrief | Day 14 | Typeform |
| 1-on-1 call notes | Day 7, Day 14 | Notion / Google Doc |

### Key questions to ask:

1. What compliance task did CapeControl help you with that you couldn't do before?
2. What was frustrating or missing?
3. Would you pay for this? At what price point?
4. Who else in your organisation would use it?

---

## 6. Conversion Workflow

```
Beta Pilot (14 days)
  ├── Positive NPS + active usage → Offer Pro plan ($49/mo)
  ├── Moderate engagement → Extend beta 14 days + add training
  └── Low engagement → Thank & close, collect exit feedback
```

### Post-Beta Checklist

- [ ] Remove `BETA_MODE=1` from production when opening registration
- [ ] Migrate pilot accounts to appropriate subscription tier
- [ ] Archive pilot feedback in `docs/pilot-reports/`
- [ ] Update `docs/project-plan.csv` — mark BP-BETA-001 complete

---

## 7. Environment Variables

| Variable | Value | Notes |
|----------|-------|-------|
| `BETA_MODE` | `1` | Enables invite-only registration |
| `BETA_INVITE_TTL_HOURS` | `336` | 14 days for pilot window |
| `ENV` | `staging` | Use staging for pilot |
| `SMTP_*` | configured | Required for invite emails |

---

## 8. Escalation & Support

| Severity | Response SLA | Channel |
|----------|-------------|---------|
| P0 — Platform down | 1 hour | Slack + phone call |
| P1 — Feature broken | 4 hours | Slack `#cape-beta-pilots` |
| P2 — Question / feedback | 24 hours | Slack or email |

---

## 9. Risk Mitigations

| Risk | Mitigation |
|------|------------|
| Low pilot engagement | Proactive weekly check-ins; reduce onboarding friction |
| Data leak between tenants | RAG queries scoped by `organization_id`; audit logs reviewed daily |
| Invite abuse | Tokens time-limited, single-use, email-bound |
| Poor answer quality | Pre-seed high-quality documents; tune capsule prompts before launch |
| Email deliverability | Test SMTP pipeline end-to-end before invites go out |
