# Cape Craft Projects CC — Board Report

**Trading as CapeControl / CapeAIControl**
**VAT 4270105119**

---

**Report Date:** 24 February 2026
**Prepared by:** Robert Kleyn, Founder & CEO
**Platform Version:** 0.2.5 (Build 489)
**Period Covered:** Project inception (August 2025) to present

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Platform Status & Technical Assets](#2-platform-status--technical-assets)
3. [Founder Development Investment](#3-founder-development-investment)
4. [IP Valuation Summary](#4-ip-valuation-summary)
5. [Financial Projections — 24-Month Cash Flow](#5-financial-projections--24-month-cash-flow)
6. [Unit Economics](#6-unit-economics)
7. [Go-to-Market Readiness](#7-go-to-market-readiness)
8. [Funding Position & Scenarios](#8-funding-position--scenarios)
9. [Risk Register](#9-risk-register)
10. [Key Decisions Required](#10-key-decisions-required)
11. [Appendices](#11-appendices)

---

## 1. Executive Summary

CapeControl is a workflow-first AI platform targeting compliance-heavy SMBs (5–250 employees). It enables SOP-driven workflows with evidence-oriented outputs — citations, audit trails, and exportable evidence packs — governed like an enterprise system but calm to use.

**Current position:**

- The MVP is **live in production** with enterprise-grade authentication, 6 AI domain agents, payment processing (PayFast/ZAR), and a mature CI/CD pipeline.
- Core differentiating features — RAG pipeline, evidence output layer, workflow capsules, tenant isolation, and audit export — have reached initial implementation status.
- The platform is **technically ready for closed beta** with 10–20 compliance-heavy SMB pilot companies.

**Financial headline:**

| Metric | Value |
|---|---|
| Founder time invested | ~450–600 hours over 6 months |
| Development investment value | **R750,000–R1,370,000** ($41K–$74K USD) |
| Projected Year 1 revenue | R367,000 (~$20K USD) |
| Projected Year 2 revenue | R2,618,000 (~$141K USD) |
| Break-even target | Month 18–20 |
| Cumulative funding required | R464,000–R510,000 ($25K–$28K USD) |

---

## 2. Platform Status & Technical Assets

### 2.1 What Has Been Built

The platform represents a substantial, production-grade software asset developed over 6 months of intensive founder-led engineering.

| Asset | Detail | Maturity |
|---|---|---|
| **Backend API** | FastAPI (Python 3.12), 16 modules, 25,080 lines | Production |
| **Frontend** | React + TypeScript + Vite + Tailwind, 5,095 lines | Production |
| **AI Agent Framework** | 6 domain agents with dedicated knowledge bases | Production |
| **RAG Pipeline** | Approved-doc-only retrieval with source provenance | Initial |
| **Evidence Layer** | Citations, source trace, timestamps, actor identity | Initial |
| **Capsule Engine** | SOP answering, audit summaries, clause finding | Initial |
| **Auth & Security** | JWT + OAuth (Google/LinkedIn) + CSRF + rate limiting + DDoS protection | Production |
| **Payment Processing** | PayFast integration (ZAR), Free/Pro/Enterprise tiers | Production |
| **Tenant Isolation** | Resource-level permissions, tenant data boundaries | Initial |
| **Audit & Evidence Export** | Exportable evidence packs for compliance review | Initial |
| **DevOps Pipeline** | Multi-stage Docker, dual Heroku environments, 13 CI/CD workflows | Production |
| **Test Suite** | 26,111 lines of tests with fixture healing | Production |
| **Documentation** | 15,769 lines — specs, playbooks, architecture docs | Current |
| **Database** | PostgreSQL with 36 Alembic migrations | Production |

### 2.2 Codebase Metrics

| Metric | Value |
|---|---|
| Total tracked files | 995 |
| Total code churn | 400,845 lines (284K insertions / 117K deletions) |
| Completed project tasks | 52 of 54 |
| Active deployment environments | 2 (staging + production) |
| Makefile automation | 1,406 lines (build, test, deploy, smoke-test) |

### 2.3 Production Environments

| Environment | URL | Purpose |
|---|---|---|
| Staging | `https://dev.cape-control.com` | Beta pilots, QA |
| Production | `https://autorisen-dac8e65796e7.herokuapp.com` | Live platform |

---

## 3. Founder Development Investment

### 3.1 Effort Analysis

All figures are derived from verified git history (396 total commits, 1,004 author-attributed commits including merges and CI).

| Metric | Value |
|---|---|
| **Project duration** | 6 months (29 August 2025 – 24 February 2026) |
| **Unique active coding days** | 57 days across the period |
| **Identified work sessions** | 91 sessions |
| **Commit-measured hours** | 181 hours (lower bound — inter-commit time only) |
| **Adjusted total hours** | **450–600 hours** (includes planning, design, research, debugging, vendor management) |
| **Average per active day** | 6.8 commits / day; ~8–10 hours estimated |

**Adjustment rationale:** Git commits capture only the moment code is saved, not the significant time spent on architecture decisions, API research, security design, debugging sessions, deployment troubleshooting, infrastructure configuration, business planning, or documentation authored outside the repository. The industry-standard multiplier for solo-founder SaaS development is 2.5–3.3× commit-measured time.

### 3.2 Monthly Effort Distribution

| Month | Active Days | Commits | Key Work |
|---|---|---|---|
| Sep 2025 | 7 | 73 | Project foundation, repo setup, CI/CD, Docker |
| Oct 2025 | 18 | 66 | Core backend modules, auth stack, database design |
| Nov 2025 | 6 | 47 | Production deployment, payment integration, security hardening |
| Dec 2025 | 3 | 7 | Maintenance, planning |
| Jan 2026 | 6 | 39 | Spec authoring, migration rules, management artifacts |
| Feb 2026 | 17 | 163 | Feature sprint — OAuth, dashboard, RAG, capsules, beta prep |

### 3.3 Work Category Breakdown

| Category | Commits | % of Effort | Description |
|---|---|---|---|
| Feature development | 155 | 24% | New capabilities, UI, agents, payments |
| Documentation & specs | 132 | 21% | System spec, playbooks, architecture docs |
| Chores & refactoring | 114 | 18% | Code quality, repo hygiene, restructuring |
| DevOps & infrastructure | 105 | 17% | Docker, Heroku, CI/CD, migrations |
| Bug fixes | 102 | 16% | Debugging, corrections, production fixes |
| Testing | 27 | 4% | Test suite, fixtures, CI validation |

### 3.4 Working Pattern

The commit timestamp analysis shows a founder working in two primary blocks:
- **Early morning:** 03:00–11:00 (62% of commits) — deep engineering work
- **Afternoon:** 14:00–18:00 (32% of commits) — features, fixes, deployment

This pattern is consistent across all 6 months and represents sustained, full-time-equivalent effort on the project.

---

## 4. IP Valuation Summary

Three independent valuation methods were applied to determine the monetary worth of the development investment.

### 4.1 Method 1 — Hourly Replacement Cost

*What would it cost to hire a developer with equivalent skills to perform this work?*

The work spans fullstack engineering, DevOps, security architecture, database design, CI/CD automation, AI integration, and product/business design. This maps to a senior fullstack engineer with DevOps and AI specialisation.

| Rate Tier | Hourly Rate | At 450 hrs | At 600 hrs |
|---|---|---|---|
| Mid-level SA fullstack | R650/hr | R292,500 | R390,000 |
| **Senior SA fullstack + DevOps** | **R1,100/hr** | **R495,000** | **R660,000** |
| Contract specialist (international) | R1,850/hr | R832,500 | R1,110,000 |

**Applicable range: R495,000–R660,000** (senior rate, most representative of actual skill applied).

### 4.2 Method 2 — Cost to Recreate

*What would an agency or team charge to build this platform from a blank repository?*

| Component | Estimated Cost (ZAR) |
|---|---|
| FastAPI backend (16 modules, auth, agents, payments, RAG) | R300,000–R450,000 |
| React + TypeScript frontend (dashboard, onboarding, billing) | R120,000–R180,000 |
| DevOps pipeline (Docker, Heroku, CI/CD, 13 workflows) | R80,000–R120,000 |
| Database design + 36 Alembic migrations | R40,000–R60,000 |
| Security stack (JWT, OAuth, CSRF, rate limiting, DDoS) | R60,000–R90,000 |
| AI agent framework (6 agents + marketplace) | R80,000–R120,000 |
| RAG pipeline + evidence layer + capsule engine | R100,000–R150,000 |
| Payment integration (PayFast + plan management) | R40,000–R60,000 |
| Test suite (26K lines) | R60,000–R80,000 |
| Documentation (16K lines, playbooks, specs) | R40,000–R60,000 |
| **Total** | **R920,000–R1,370,000** |
| **USD equivalent** | **$50,000–$74,000** |

### 4.3 Method 3 — Opportunity Cost

*What salary has the founder foregone during the development period?*

| Scenario | Annual Equivalent | 6-Month Cost |
|---|---|---|
| Senior developer (SA market) | R850,000–R1,200,000 | R425,000–R600,000 |
| Tech lead / architect (SA market) | R1,200,000–R1,800,000 | R600,000–R900,000 |

### 4.4 Consolidated Valuation

| Method | Range (ZAR) | Range (USD) |
|---|---|---|
| Hourly replacement cost | R495,000–R660,000 | $27,000–$36,000 |
| Cost to recreate (agency quote) | R920,000–R1,370,000 | $50,000–$74,000 |
| Opportunity cost (senior dev) | R425,000–R900,000 | $23,000–$49,000 |

| | ZAR | USD |
|---|---|---|
| **Conservative estimate** | **R750,000** | **$41,000** |
| **IP / recreation value (investor-relevant)** | **R920,000–R1,370,000** | **$50,000–$74,000** |

**Board recommendation:** For funding conversations and balance sheet purposes, the development investment should be valued at **R750,000** (conservative mid-point), with the cost-to-recreate range of **R920K–R1.37M** cited as the IP replacement value.

---

## 5. Financial Projections — 24-Month Cash Flow

### 5.1 Revenue Model

| Tier | Monthly Price | Target Segment |
|---|---|---|
| Free | R0 | Trial / evaluation |
| Pro | R529/mo (~$29 USD) | Individual compliance practitioners |
| Enterprise | R1,799/mo (~$97 USD) | Teams with governance requirements |
| Services | Project-based | Onboarding, capsule setup, compliance assistance |

Blended ARPU after free-tier dilution: **R830/mo (~$45 USD)**.

### 5.2 Year 1 Cash Flow (Month-by-Month)

| Month | Phase | Revenue (R) | Costs (R) | Net (R) | Cumulative (R) |
|---|---|---|---|---|---|
| 1 | Pre-beta | 0 | 5,790 | -5,790 | -5,790 |
| 2 | Pre-beta | 0 | 5,790 | -5,790 | -11,580 |
| 3 | Beta launch | 0 | 24,845 | -24,845 | -36,425 |
| 4 | Early conversion | 1,587 | 6,530 | -4,943 | -41,368 |
| 5 | Iteration | 3,000 | 15,965 | -12,965 | -54,333 |
| 6 | First paid cohort | 21,850 | 70,010 | -48,160 | -102,493 |
| 7 | Traction | 30,250 | 70,935 | -40,685 | -143,178 |
| 8 | Growth | 38,110 | 81,110 | -43,000 | -186,178 |
| 9 | Growth | 49,875 | 110,710 | -60,835 | -247,013 |
| 10 | Scaling | 60,855 | 113,800 | -52,945 | -299,958 |
| 11 | Scaling | 72,915 | 115,650 | -42,735 | -342,693 |
| 12 | Scaling | 89,050 | 210,500 | -121,450 | -464,143 |
| **Year 1** | | **R367,492** | **R831,635** | **-R464,143** | |

### 5.3 Year 2 Cash Flow (Quarterly)

| Quarter | Revenue (R) | Costs (R) | Net (R) | Cumulative (R) |
|---|---|---|---|---|
| Q1 (M13–15) | 351,190 | 393,000 | -41,810 | -505,953 |
| Q2 (M16–18) | 525,625 | 430,000 | **+95,625** | -410,328 |
| Q3 (M19–21) | 751,250 | 475,000 | **+276,250** | -134,078 |
| Q4 (M22–24) | 990,000 | 510,000 | **+480,000** | **+345,922** |
| **Year 2** | **R2,618,065** | **R1,808,000** | **+R810,065** | |

### 5.4 Visual — Cumulative Cash Position

```
  R ('000)
   +400 │                                                                    ████
   +300 │                                                               ████
   +200 │                                                          ████
   +100 │                                                     ████
      0 │───┐                                            ████
  -100 │   │                                       ████
  -200 │   └──┐                                ▓▓▓▓
  -300 │      └───┐                        ▓▓▓▓
  -400 │          └────┐               ▓▓▓▓
  -500 │               └──────── ▓▓▓▓▓▓
        └──────────────────────────────────────────────────────────────────────
         M1  M3  M5  M7  M9  M11  M13  M15  M17  M19  M21  M23
                Year 1 (▓ burn)          Year 2 (█ growth)
```

### 5.5 Year-End ARR

| | Conservative | Optimistic |
|---|---|---|
| End of Year 1 | R1,069,000 (~$58K ARR) | R2,500,000 (~$135K ARR) |
| End of Year 2 | R4,295,000 (~$232K ARR) | R9,250,000 (~$500K ARR) |

---

## 6. Unit Economics

| Metric | Current / Projected | Target | Status |
|---|---|---|---|
| **ARPU** | R830/mo ($45) | R900+/mo | On track via enterprise upsell |
| **Monthly churn** | Modelled at 6% | <5% | To be validated in beta |
| **LTV** | R13,830 ($750) | R18,000+ | Dependent on churn reduction |
| **CAC** | <R3,700 ($200) | <R3,700 | Founder-led, low for now |
| **LTV:CAC** | 3.7:1 | >3:1 | Healthy — supports scaling spend |
| **Gross margin** | 55–65% (Year 1) | 70%+ (Year 2) | AI cost management critical |
| **Payback period** | ~4 months | <6 months | Strong for SaaS |

### Break-Even Point

| Metric | Value |
|---|---|
| Monthly break-even revenue | ~R130,000/mo |
| Users at break-even | ~155–165 paying users |
| Expected break-even month | Month 18–20 |
| Cumulative cash to break-even | R464,000–R510,000 |
| Full cumulative payback | Month 22–24 |

---

## 7. Go-to-Market Readiness

### 7.1 Immediate Next Step: Closed Beta

A detailed Beta Pilot Playbook has been prepared for a 14-day evaluation with 10–20 compliance-heavy SMBs.

| Phase | Timeline | Activity |
|---|---|---|
| Pre-launch | T-7 days | Staging verification, RAG seeding, invite setup |
| Onboarding | Day 1–3 | Invite, register, first query, first capsule |
| Active evaluation | Day 3–12 | Daily usage, weekly check-ins, monitoring |
| Wrap-up | Day 12–14 | NPS survey, evidence pack export, conversion offers |

**Success criteria:** ≥85% relevant-answer rate, ≥3 companies export evidence packs, NPS ≥40, zero cross-tenant leaks.

### 7.2 Pricing Tiers (Live)

| Tier | Price (ZAR) | Price (USD) | Includes |
|---|---|---|---|
| Free | R0 | $0 | Limited runs, single agent, basic onboarding |
| Pro | R529/mo | $29/mo | Full agent access, evidence exports, quota runs |
| Enterprise | R1,799/mo | $97/mo | Governance controls, priority support |

### 7.3 GTM Channels

| Channel | Status |
|---|---|
| Founder-led LinkedIn/X content | Ready — pending beta results for content |
| "First Evidence Pack in 14 Days" pilot program | Playbook complete |
| Partner integrations (accounting, property, maintenance) | Roadmap |
| Stripe for international buyers | Q3 2026 |

---

## 8. Funding Position & Scenarios

### 8.1 Current Position

| Item | Value |
|---|---|
| Capital raised to date | R0 (bootstrapped) |
| Founder sweat equity invested | R750,000–R1,370,000 (at valuation) |
| Monthly burn rate (current) | ~R5,800/mo (infrastructure only) |
| Monthly burn rate (at scale, M12) | ~R210,000/mo |
| Cash required to break-even | R464,000–R510,000 |

### 8.2 Funding Scenarios

#### Scenario A — Continue Bootstrap

| | Detail |
|---|---|
| Capital required | ~R500,000 ($27K) personal funding |
| Risk | Slower team growth, no SOC 2, tighter runway |
| Break-even | Month 18–20 |
| Equity retained | 100% |
| **Recommended if:** | Personal capital available; willing to accept slower scaling |

#### Scenario B — Seed Raise (R1–3M / $55–165K)

| | Detail |
|---|---|
| Use of funds | Engineer #2 (Month 4), marketing, SOC 2 readiness |
| Impact | Break-even accelerated to Month 14–16 |
| Dilution | 10–20% (SAFE or convertible note) |
| **Trigger:** | 30+ paying users with >3-month retention |
| **Recommended if:** | Beta validates demand; want to move fast on mid-market |

#### Scenario C — Growth Raise (R5–10M / $270–540K)

| | Detail |
|---|---|
| Use of funds | Full team (5–7), security certs, mid-market push |
| Impact | Aggressive ARR scaling, earlier market position |
| Dilution | 15–25% |
| **Trigger:** | 100+ users, proven unit economics, mid-market pull |
| **Recommended if:** | Strong beta signal + mid-market demand confirmed |

---

## 9. Risk Register

| # | Risk | Severity | Likelihood | Mitigation |
|---|---|---|---|---|
| 1 | **Core feature gap** — RAG/evidence layer quality insufficient for regulated buyers | High | Medium | Months 1–2 focused on technical prerequisites; beta validates before GTM |
| 2 | **Adoption speed** — regulated buyers have long sales cycles | High | High | Freemium hooks + capsule onboarding; services revenue bridges gap |
| 3 | **Single-founder risk** — bus factor of one for compliance-targeting platform | High | Medium | Modular codebase; comprehensive docs; hire engineer #2 as first priority |
| 4 | **AI cost volatility** — inference/embedding costs may compress margins | Medium | Medium | Quotas, caching, model tiering; margin modelled conservatively at 55–65% |
| 5 | **Payment rails** — PayFast ZAR-only limits international reach | Medium | Low | Stripe integration planned Q3 2026; initial wedge is SA market |
| 6 | **Trust/security posture** — "evidence-grade" claims before third-party audit | Medium | Medium | Use "evidence-oriented" language; target SOC 2 after funding |
| 7 | **Churn** — SMB churn historically high in SaaS | Medium | Medium | Evidence lock-in, workflow stickiness, capsule templates |

---

## 10. Key Decisions Required

The board is asked to consider and resolve the following:

### Decision 1: Beta Launch Timing

**Recommendation:** Approve closed beta launch within 30 days (target: late March 2026).
- Technical prerequisites (RAG, evidence layer, capsules) have reached initial implementation.
- Beta Pilot Playbook is complete and ready for execution.
- 10–20 target companies to be identified and invited.

### Decision 2: Funding Strategy

**Recommendation:** Proceed with bootstrap (Scenario A) through beta, then evaluate Scenario B based on beta results.
- Current infrastructure costs are manageable (~R5,800/mo).
- Defer fundraising decision until Month 6 with conversion data from beta cohort.
- Prepare SAFE/convertible note terms in parallel so raise can execute quickly if triggered.

### Decision 3: Founder Compensation

**Recommendation:** Begin modest founder draw of R25,000/mo from Month 7 (first revenue month), contingent on cumulative revenue exceeding R30,000.

### Decision 4: First Hire Priority

**Recommendation:** Approve budget for contract engineer #1 (R37,000/mo part-time) from Month 6, focused on RAG quality and evidence completeness — the core differentiating capability.

---

## 11. Appendices

| Document | Location |
|---|---|
| Full Business Plan | `docs/CapeControl_Business_Plan_v2.md` |
| 24-Month Cash Flow Model | `docs/CASH_FLOW_PROJECTION.md` |
| Beta Pilot Playbook | `docs/playbooks/BETA_PILOT_PLAYBOOK.md` |
| System Specification | `docs/SYSTEM_SPEC.md` |
| Project Plan (task tracker) | `docs/project-plan.csv` |
| Security Posture | `docs/SECURITY_POSTURE.md` |
| Agent Registry | `docs/agents.md` |
| Deployment Environments | `docs/deployment-environments.md` |

---

**Submitted by:**
Robert Kleyn
Founder & CEO, Cape Craft Projects CC
24 February 2026

---

*This report contains forward-looking projections based on stated assumptions. Actual results may vary. Financial projections should be refreshed quarterly as actuals become available.*
