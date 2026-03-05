# CapeControl Business Plan

**Concise Version — Updated March 2026**

---

## Executive Summary

CapeControl is a workflow-first AI platform that helps compliance-heavy small businesses and operational teams run SOP-driven work with evidence-oriented outputs—calm to use, but governed like an enterprise system behind the scenes. Operated by Cape Craft Projects CC (VAT 4270105119), trading as CapeAIControl / CapeControl.

**Vision:** Empower compliance-heavy SMBs through sovereign, human-centric AI orchestration—delivering calm, secure, transparent workflows.

**Core Promise:**

- **Start calm** — one useful clue at a time
- **Scale powerfully** — secure runs, controlled RAG, orchestration
- **Evidence-oriented security** — approved sources, audit logs, permissions
- **No complexity** — tools off by default; controlled change with rollback

**Differentiation:** Affordable for regulated SMBs; evidence-oriented sovereignty (approved-doc-only answers, "unsupported" policy, exportable evidence logs); tools off by default; controlled change with rollback.

**Stage:** MVP live with enterprise-grade auth, 6 domain AI agents, payment infrastructure, and mature deployment pipeline. Core evidence layer (RAG, citation trace, evidence export) in active development for regulated SMB beta.

**Goal:** R2.8M–R9.3M ARR (~$150K–$500K USD) in 18–24 months via 100–400 active regulated SMB users, plus services revenue and early mid-market pilots once evidence completeness is proven.

**Expansion Path:** After wedge validation (trust + retention + evidence completeness), expand into mid-market regulated ops with stronger reliability posture and optional hybrid/on-prem delivery.

---

## Market Opportunity

Regulated SMBs and operational teams face rising pressure to adopt AI while maintaining control, privacy, and auditability. Many have SOPs, checklists, and compliance demands—but lack systems that produce traceable outcomes instead of "chatty answers."

**Primary focus:** Compliance-heavy SMBs and growing operational teams (5–250 employees) that must manage:

- SOPs / policies / checklists
- Maintenance + incident documentation
- Audit preparation and evidence packs

**Market direction:** Demand is rising for secure workflow automation with clear data boundaries, tool controls, and explainability—without enterprise complexity or cost.

---

## Product & Services

### What's Built (MVP — Live)

| Capability | Detail |
|---|---|
| **AI Agent Framework** | 6 domain agents (Guide, Domain Specialist, Customer, Developer, Finance, Content) with dedicated knowledge bases, agent marketplace with installer/validator |
| **Authentication & Security** | JWT + OAuth (Google, LinkedIn), CSRF protection, rate limiting, login audit trail, role-based gating (Customer / Developer / Admin), admin invite flows |
| **Payment & Subscriptions** | PayFast integration (ZAR), Free / Pro (R529/mo) / Enterprise (R1,799/mo) plans, subscription management |
| **Onboarding & Flows** | Step-tracked onboarding, developer dashboard, support module |
| **Deployment Pipeline** | Multi-stage Docker builds, dual Heroku environments (staging + production), retry logic, deployment certification, evidence-logged releases |
| **Operational Maturity** | 1,400-line Makefile with smoke tests, fixture healing, deployment guards, code quality automation |

### What's In Development (Q1–Q2 2026 — Required for Regulated SMB Beta)

| Capability | Status | Target |
|---|---|---|
| **Controlled RAG Pipeline** | Design phase | Q1 2026 — approved-doc-only retrieval with source provenance |
| **Evidence Output Layer** | Design phase | Q1 2026 — citations, source trace, timestamps, actor identity |
| **"Unsupported" Policy Enforcement** | Not started | Q2 2026 — refuse or flag answers lacking approved-doc backing |
| **Workflow Capsule Engine** | Not started | Q2 2026 — SOP answering, audit summaries, clause-finding templates |
| **Tenant Isolation & Granular Permissions** | Basic role-gating exists | Q2 2026 — resource-level permissions, tenant data boundaries |
| **Audit Export / Evidence Pack Generation** | Login + tool audit exists | Q2 2026 — exportable evidence packs for compliance review |
| **International Payment Rails** | PayFast live (ZAR) | Q3 2026 — Stripe integration for international buyers |

### Core Platform Principles

- Calm onboarding ("felt calm before powerful")
- Evidence-oriented outputs: citations, source trace, timestamps, actor identity, versions
- Gated tools (off by default), model tiering, audit logs / permissions
- Sovereignty-ready posture (tenant isolation roadmap, RBAC, export, BYOK-ready trajectory)

**Target usage:** Tiered runs with quotas (e.g., 10–30 runs/user/month typical for regulated SMB workflows).

### Add-ons / Services

- Custom workflow capsules (SOP answering, audit summaries, clause finding)
- Compliance setup assistance (policies, controls, onboarding, documentation)
- Paid onboarding for "first audit pack" success

---

## Technical Readiness

### Architecture

- **Backend:** FastAPI (Python 3.12), 16 modules, ~17,500 lines of backend code
- **Frontend:** React + TypeScript + Vite + Tailwind, served as static build
- **Database:** PostgreSQL (production), Alembic migrations, SQLite (test isolation)
- **AI Provider:** Anthropic Claude 3.5 Haiku, abstracted via provider layer for future model flexibility
- **Infrastructure:** Gunicorn + Uvicorn workers, Redis (rate limiting/caching), containerised deployment

### Production-Ready

- Enterprise-grade auth stack (JWT, OAuth, CSRF, rate limiting, login audit)
- Dual-environment deployment with certification flow and retry logic
- Automated test suite with CI/CD (GitHub Actions), fixture healing
- PayFast payment processing with plan management
- Health monitoring endpoints (`/api/health`, `/api/version`)

### Needs Hardening for Regulated SMB Beta

- RAG pipeline with approved-document-only retrieval (core prerequisite)
- Evidence output layer with citation provenance
- Granular RBAC beyond current 3-role gating
- Tenant data isolation
- Monitoring and alerting infrastructure (runbooks, backups)
- Security posture documentation for buyer due diligence

---

## Business Model & Financials

### Revenue Model: Freemium → Pro → Enterprise + Services

| Tier | Price (ZAR) | Includes |
|---|---|---|
| **Free** | R0/mo | 3 AI agents, 50 executions/mo, community support, basic integrations |
| **Pro** | R529/mo (R4,990/yr) | 50 AI agents, 2,000 executions/mo, all integrations, priority email support (24h), advanced analytics |
| **Enterprise** | R1,799/mo (R17,190/yr) | 500 AI agents, 8,000 executions/mo, custom integrations, priority account support (4h SLA), SSO & advanced security |
| **Services** | Project-based | Onboarding, workflow/capsule setup, compliance assistance |

### Projections (Assumption-Based)

All figures in ZAR. Exchange rate assumption: R18.50/USD.

| | Conservative | Optimistic |
|---|---|---|
| **Year 1** | 50–150 users → R1.8M–R4.6M ARR | 200–400 users → R5.5M–R9.3M ARR |
| **Year 2** | 200–500 users → R9.3M–R22M ARR | 500–1,000 users → R28M–R55M ARR |

**Key assumptions:**
- Monthly churn modelled at 5–7% (typical early-stage SMB SaaS)
- Services revenue = 20–30% of total in Year 1 (de-risks platform revenue)
- Blended ARPU ~R830/user/month after free tier dilution (~$45 USD)
- Plan limits enforced server-side: Free 50 exec/mo, Pro 2,000 exec/mo, Enterprise 8,000 exec/mo

### Unit Economics

- **Gross margin target:** 55–65% initially (AI inference + embedding costs compress margins until caching/tiering mature); target 70%+ at scale
- **CAC:** Low — founder-led content marketing + pilot cohorts; target <R3,700 (~$200 USD) blended CAC
- **LTV:** At R830 ARPU and 6% monthly churn, ~R13,830 LTV (~$750 USD) → LTV:CAC >3x required before scaling spend
- **Per-execution AI cost:** ~R0.12–R0.20 blended (Claude 3.5 Haiku primary). Enterprise at full utilisation: R1,632/mo AI cost on R1,799 revenue — margin-positive at all realistic utilisation levels

### Funding / Runway

Bootstrap initially. Optional R18M–R55M (~$1–3M USD) raise to accelerate growth, security posture, and certifications (SOC 2 trajectory) once demand signal is validated through:
- 30+ paying users with >3 month retention
- Evidence completeness confirmed by pilot customers
- Positive unit economics on Pro tier

---

## Go-to-Market & Operations

### Positioning

> "AI that feels calm first—evidence-oriented, secure, and powerful for compliance-heavy teams."

### Channels

| Channel | Approach |
|---|---|
| **LinkedIn / X** | Founder-led content for compliance-heavy SMB operators |
| **Pilot cohorts** | "First evidence pack in 14 days" program |
| **Partnerships** | Tools regulated SMBs already use (accounting, property ops, scheduling, maintenance, ticketing) |

### Team

Founder-led (Robert Kleyn / @Zeonita). Scale to 4–7 (engineering, growth, security/ops) as paid traction increases.

### Milestones

| Timeframe | Target | Dependency |
|---|---|---|
| **Month 1–2** | RAG pipeline + evidence output layer complete | Technical prerequisite for beta |
| **Month 3** | Closed beta with 10–20 compliance-heavy SMBs | Evidence layer must be functional |
| **Month 4–5** | Iterate on evidence completeness + "unsupported" policy | Pilot feedback loop |
| **Month 6** | First paying cohort — target 30–50 users | Conversion from beta |
| **Month 9** | 100+ actives, retention >25%, evidence completeness tracked | GTM scaling begins |
| **Month 12** | $150–300K ARR (conservative), mid-market pilot evaluation | Expansion decision point |

---

## Risks & Mitigation

| Risk | Severity | Mitigation |
|---|---|---|
| **Core feature gap** — RAG and evidence layer are not yet built; the plan's moat depends on features in development | High | Months 1–2 focused exclusively on technical prerequisites before any GTM push |
| **Adoption speed** — regulated buyers have long sales cycles (demos → security review → procurement) | High | Strong freemium hooks + capsule-driven onboarding; services revenue bridges the gap |
| **Single-founder risk** — bus factor of 1 for a platform targeting compliance-sensitive buyers who value organisational stability | High | Document architecture decisions; modular codebase enables contractor onboarding; hire #2 engineer as first priority after revenue |
| **Trust / security posture** — calling the product "evidence-grade" before audit validation invites liability | Medium | Use "evidence-oriented" and "sovereignty-ready" language; seek pilot customer validation before stronger claims; target SOC 2 readiness as funded milestone |
| **LLM cost volatility** — inference and embedding costs may compress margins | Medium | Quotas, response caching, model tiering, guardrails; gross margin modelled conservatively at 55–65% |
| **Payment rails** — PayFast (ZAR only) limits international reach; plan states "worldwide" | Medium | Stripe integration planned for Q3 2026; initial wedge market is South African regulated SMBs |
| **Regulatory compliance claims** — "sovereignty-compatible" implies certifications that don't yet exist | Low | Position as "sovereignty-ready posture" with explicit caveats; pursue certifications after funding |
| **Documentation–code drift** — some documented features (middleware agents, monitoring) don't match codebase | Low | Audit docs quarterly; align `docs/agents.md` with actual module inventory |

---

## Competitive Advantages (Underplayed in Previous Version)

These genuine technical assets support the "governed like an enterprise system" claim and should be highlighted in sales conversations:

1. **Deployment discipline** — Multi-stage Docker, dual environments, retry logic, deployment certification, evidence-logged releases. Unusually mature for a bootstrap MVP.
2. **Auth depth** — JWT + OAuth (Google/LinkedIn) + CSRF + rate limiting + login audit + admin invites. Enterprise-grade auth from day one.
3. **Agent architecture** — 6 domain agents with dedicated knowledge bases and an agent marketplace/installer. Extensible by design.
4. **Operational automation** — Smoke tests, fixture healing, deployment guards, code quality automation. Signals the engineering discipline compliance buyers care about.

---

## Legal & Entity

Operated by **Cape Craft Projects CC** (VAT 4270105119) — Trading as CapeAIControl / CapeControl.

This plan preserves the existing technical foundation while sharpening focus on regulated SMB workflows—building a defensible moat around sovereignty, evidence, and controlled change, then expanding into mid-market regulated operations after trust and reliability are proven.

---

*Last updated: March 2026*
