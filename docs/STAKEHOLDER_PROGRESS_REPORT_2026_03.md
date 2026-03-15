# CapeControl — Stakeholder Progress Report

**Cape Craft Projects CC** | Trading as CapeControl / CapeAIControl
**VAT:** 4270105119

---

**Report Date:** 9 March 2026
**Prepared by:** Robert Kleyn, Founder & CEO
**Platform Version:** 0.2.5 (Build 539)
**Period Covered:** Project inception (August 2025) to present

---

## 1. Our Objective

CapeControl is a **workflow-first AI platform** purpose-built for compliance-heavy small and medium businesses (5–250 employees). Our mission is to enable SOP-driven workflows with **evidence-oriented outputs** — citations, audit trails, and exportable evidence packs — governed like an enterprise system but calm and intuitive to use.

**Core promise to customers:**

- **Start calm** — one useful clue at a time, no complexity upfront
- **Scale powerfully** — secure workflow runs, controlled RAG, agent orchestration
- **Evidence-oriented security** — approved sources only, full audit logs, granular permissions
- **No surprises** — tools off by default; controlled change with rollback capability

**Target market:** Regulated SMBs that manage SOPs, policies, checklists, maintenance documentation, incident logs, and audit preparation — and need AI that produces traceable, defensible outcomes rather than unverifiable answers.

---

## 2. What We Have Achieved

### 2.1 Platform — Production-Live

The MVP is **live in production** across two environments (staging and production), representing over **6 months of intensive development** — 438 commits, 25,080 lines of backend code, and 5,095 lines of frontend code.

| Capability | Status | Detail |
|---|---|---|
| **Backend API** | Production | FastAPI (Python 3.12), 16 domain modules |
| **Frontend** | Production | React + TypeScript + Vite + Tailwind |
| **AI Agent Framework** | Production | 6 domain agents (Guide, Domain Specialist, Customer, Developer, Finance, Content) with dedicated knowledge bases |
| **Authentication & Security** | Production | JWT + OAuth (Google, LinkedIn), CSRF protection, reCAPTCHA, rate limiting, DDoS protection, MFA, login audit trail |
| **Payment Processing** | Production | PayFast integration (ZAR), Free / Pro (R529/mo) / Enterprise (R1,799/mo), ITN webhook handling, subscription lifecycle |
| **RAG Pipeline** | Initial | Approved-doc-only retrieval with source provenance |
| **Evidence Layer** | Initial | Citations, source trace, timestamps, actor identity |
| **Capsule Engine** | Initial | SOP answering, audit summaries, clause-finding templates |
| **Tenant Isolation** | Initial | Resource-level permissions, tenant data boundaries |
| **Audit & Evidence Export** | Initial | Exportable evidence pack PDF generation |
| **DevOps Pipeline** | Production | Multi-stage Docker builds, dual Heroku environments, 13 CI/CD workflows, automated deployment certification |
| **Test Suite** | Production | 266+ automated tests with fixture healing |
| **Database** | Production | PostgreSQL with 36+ Alembic migrations |
| **Monitoring** | Production | Sentry error tracking, database backup scheduling, health endpoints |

### 2.2 Project Plan Completion

| Metric | Value |
|---|---|
| Total planned tasks | 76 |
| Tasks completed | 74 (97%) |
| Tasks remaining | 1 (Stripe international payments — planned Q3 2026) |
| Total commits | 438 |
| Current build | 539 |

### 2.3 Development Investment

| Metric | Value |
|---|---|
| Founder time invested | ~450–600 hours over 6+ months |
| Development investment value | R750,000–R1,370,000 ($41K–$74K USD) |
| Active coding days | 57+ |
| Work sessions | 91+ |

---

## 3. What We Are Currently Working On

### 3.1 Strategic Shift: Build → Sell

With 97% of planned platform tasks complete and 42 additional commits delivered since the February Board Report, **we have shifted from platform building to pilot acquisition and first commercial proof.**

Three operating guardrails now govern all founder time:

1. **Lead with trust** — evidence packs, traceability, approved-source retrieval, calm UX, strong reliability, and cost discipline. Product work is limited to beta-enabling items only.
2. **Measure by pilots, not internal completion** — progress is now tracked by usage, trust feedback, and conversion signals — not feature count.
3. **Launch a closed beta** with qualified compliance-heavy SMB pilots, validate evidence completeness in real workflows, and prepare the first pilot-to-paid conversion path.

### 3.2 Recent Deliverables (Since February Board Report)

Before entering GTM mode, 42 commits completed the following production-hardening work:

| Area | Delivered |
|---|---|
| AI Cost Optimisation | Usage tracking, circuit breaker, LLM cache, admin cost dashboard, 9-gap mandate |
| Billing & Subscriptions | Automated billing cycles, missed payment logging, reminder emails, Free→Pro conversion flow |
| Performance | GZip middleware, lazy-loaded routes, Lighthouse score 98 |
| Production Wiring | Marketplace, onboarding checklist, dashboard V2, evidence pack PDF export — all connected to real APIs |
| Security | Enterprise reCAPTCHA, per-customer usage tracking, MFA, privacy policy page |
| Chat | Backend threads, events, WebSocket, Anthropic AI integration |
| GTM Foundations | LinkedIn content calendar, SEO, social share assets, instructional video script, beta contact list |

### 3.3 12-Week Founder Execution Plan

The following week-by-week plan governs execution from 9 March 2026 through late May 2026. We are currently in **Week 1–2**.

| Week | Focus | Key Activity |
|---|---|---|
| **W1–2** | **Sharpen the message** | Define one plain-language promise: *CapeControl helps compliance-heavy SMBs run SOP-driven workflows with traceable, audit-ready AI outputs.* Pick one primary beta use case. |
| **W3** | **Package the demo** | Build one trust-centred demo: question/work item → cited answer → evidence trail → exportable proof. |
| **W4** | **Build the pilot pipeline** | Rank the 20 beta slots by urgency and fit. Start founder-led outreach using a simple pilot invitation and sector priority list. |
| **W5–6** | **Qualify and recruit pilots** | Run discovery calls. Select pilots by urgency, clarity of use case, and suitability for evidence-first value. Refine the pitch from live objections. |
| **W7** | **Tighten onboarding** | Make first value easy: upload/connect, try the first workflow, understand evidence output, and follow a short quick-start path. |
| **W8** | **Launch first cohort** | Move from preparation to real-world use. Watch citations, source clarity, evidence completeness, usability, and speed. |
| **W9** | **Validate evidence completeness** | Ask pilots whether outputs feel defensible, traceable, and usable in real compliance settings. Capture structured trust feedback. |
| **W10** | **Strengthen reliability and proof assets** | Fix highest-friction issues. Capture anonymised before/after examples, screenshots, and sample evidence packs. |
| **W11** | **Prepare the conversion path** | Define what marks a pilot as conversion-ready. Align the pilot-to-paid path with Free, Pro, and Enterprise offers already in place. |

---

## 4. Our End Goal

### 4.1 Near-Term (Next 6 Months)

| Milestone | Target |
|---|---|
| **Closed beta launch** | 10–20 compliance-heavy SMB pilots |
| **Evidence completeness validation** | Pilot customer feedback confirms audit-grade outputs |
| **First paying cohort** | 30–50 converted users from beta |
| **Stripe integration** | International payment capability (Q3 2026) |

### 4.2 Financial Targets

| Period | Revenue Target (ZAR) | User Target |
|---|---|---|
| **Year 1** | R367,000 (~$20K USD) | 50–150 active users |
| **Year 2** | R2,618,000 (~$141K USD) | 200–500 active users |
| **Break-even** | Month 18–20 | ~200 paying users |
| **Steady-state ARR** | R2.8M–R9.3M (~$150K–$500K USD) | 100–400 regulated SMB users |

### 4.3 Long-Term Vision

**Become the trusted AI workflow platform for compliance-heavy SMBs** — where every AI output is traceable, every action is auditable, and every workflow runs with enterprise governance at SMB simplicity.

**Expansion path after wedge validation:**

1. **Deepen the wedge** — prove trust, retention, and evidence completeness with initial regulated SMB cohort
2. **Expand to mid-market** — stronger reliability posture, optional hybrid/on-prem delivery, SOC 2 trajectory
3. **Platform ecosystem** — marketplace of community and third-party workflow capsules, agent templates, and compliance packs
4. **International reach** — Stripe-powered global billing, multi-currency support, region-specific compliance modules

### 4.4 Funding Position

The platform is bootstrapped. Optional raise of R18M–R55M (~$1–3M USD) to accelerate growth once demand signal is validated through:

- 30+ paying users with >3 month retention
- Evidence completeness confirmed by pilot customers
- Positive unit economics on Pro tier

---

## 5. Summary

| Area | Status |
|---|---|
| **Platform** | Production-live with enterprise-grade infrastructure |
| **Task completion** | 97% (74 of 76 planned tasks complete) |
| **Current focus** | Go-to-market execution, beta recruitment, cost optimisation |
| **Key risk** | Adoption speed in regulated buyer segment (mitigated by pilot approach and services revenue) |
| **Next major milestone** | Closed beta launch with 10–20 pilot companies |

---

*This report was prepared from verified project data, git history, and current project plan records.*
