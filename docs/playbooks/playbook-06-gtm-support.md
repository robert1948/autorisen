# Playbook 06: GTM & Support Readiness

**Owner**: GTM Steward
**Supporting Agents**: Release Captain, Onboarding Maestro
**Status**: Planned
**Priority**: P2

---

## 1) Outcome

Prepare the CapeControl platform for public release and early customer adoption. This includes aligning marketing promises with product delivery, ensuring basic documentation and support structures exist, and establishing analytics and feedback loops.

**Definition of Done (DoD):**

* Landing page messaging and visuals aligned with MVP functionality.
* Support mailbox and contact channels configured and tested.
* Basic user docs, FAQs, and onboarding help published.
* Feedback loop active (email or form integration).
* Analytics instrumentation in place (traffic, engagement, onboarding metrics).

---

## 2) Scope (In / Out)

**In Scope:**

* Website messaging and visuals consistency check.
* Support mailbox setup (`support@cape-control.com`).
* Feedback collection form and dashboard logging.
* Analytics setup (Google Analytics, Plausible, or similar).
* Documentation updates (README, FAQs, onboarding guides).

**Out of Scope:**

* Paid advertising campaigns.
* Dedicated CRM or helpdesk system.
* Localization or multi-language support.

---

## 3) Dependencies

**Upstream:**

* Playbook 01 – MVP Launch (product must be live).
* Playbook 03 – Frontend Onboarding (UX flow reference).

**Downstream:**

* Future Growth phase (agent marketplace + payments).

---

## 4) Milestones

| Milestone | Description                          | Owner              | Status     |
| --------- | ------------------------------------ | ------------------ | ---------- |
| M1        | Messaging + visuals review complete  | GTM Steward        | 🔄 Pending |
| M2        | Support mailbox + contact tested     | Release Captain    | 🔄 Pending |
| M3        | Feedback form + analytics live       | Onboarding Maestro | 🔄 Pending |
| M4        | Public documentation + FAQ published | GTM Steward        | 🔄 Pending |
| M5        | Launch announcement prepared         | Release Captain    | 🔄 Pending |

---

## 5) Checklist (Executable)

* [ ] Review landing promises vs MVP delivery.
* [ ] Setup and test `support@cape-control.com` mailbox.
* [ ] Add feedback form on landing or dashboard.
* [ ] Enable analytics dashboard.
* [ ] Write `docs/FAQ.md` and link from footer.
* [ ] Draft launch communication (LinkedIn + project log).

---

## 6) Runbook / Commands

```bash
## Check domain mail records
nslookup -type=MX cape-control.com

## Run analytics verification (example for Plausible)
curl -I https://plausible.io/api/event

## Build docs locally
mkdocs serve
```text
---

## 7) Risks & Mitigations

| Risk                                     | Mitigation                                      |
| ---------------------------------------- | ----------------------------------------------- |
| Messaging misaligned with MVP features   | Cross-check with MVP Launch checklist           |
| Support mailbox not monitored            | Auto-forward to team shared inbox               |
| Missing analytics due to script blockers | Provide fallback logging via server-side events |
| Feedback ignored                         | Weekly triage in project log                    |

---

## 8) Links

* [`docs/PLAYBOOKS_OVERVIEW.md`](../PLAYBOOKS_OVERVIEW.md)
* [`docs/FAQ.md`](../FAQ.md)
* Landing Page: [https://cape-control.com](https://cape-control.com)
* Support Email: [support@cape-control.com](mailto:support@cape-control.com)

---

## ✅ Next Actions

1. Align landing visuals and messaging (M1).
1. Set up support mailbox and test responses (M2).
1. Implement feedback + analytics systems (M3).
1. Prepare documentation and launch announcement (M4–M5).
