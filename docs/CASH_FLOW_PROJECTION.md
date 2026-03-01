# CapeControl — 24-Month Cash Flow Projection

> **Version:** 1.0 · **Last Updated:** 2026-02-24
> **Entity:** Cape Craft Projects CC (VAT 4270105119)
> **Currency:** ZAR primary, USD equivalent shown where relevant
> **Exchange Rate Assumption:** R18.50 / USD

---

## 1. Key Assumptions

| Assumption | Value | Source |
|---|---|---|
| Pro plan price | R529/mo (~$29 USD) | FEAT-PAY-ALIGN-001 |
| Enterprise plan price | R1,799/mo (~$97 USD) | FEAT-PAY-ALIGN-001 |
| Free tier | R0 | Business Plan v2 |
| Blended ARPU (after free dilution) | R830/mo (~$45 USD) | Business Plan v2 |
| Monthly churn | 6% | Business Plan v2 |
| Services revenue share (Year 1) | 25% of total | Business Plan v2 |
| Gross margin target | 55–65% (Year 1), 70%+ at scale | Business Plan v2 |
| CAC (blended) | <R3,700 (~$200 USD) | Business Plan v2 — founder-led, low-cost |
| LTV (at 6% churn, R830 ARPU) | ~R13,830 (~$750 USD) | Business Plan v2 |
| Team | Founder only → scale to 4–7 | Business Plan v2 |
| Payment rails | PayFast (ZAR) → Stripe (Q3 2026) | Business Plan v2 |

### User Growth Model

| Month | Phase | Net New Users | Cumulative Paying | Notes |
|---|---|---|---|---|
| 1–2 | Pre-beta build | 0 | 0 | RAG + evidence layer development |
| 3 | Closed beta | 10–20 (free) | 0 | 14-day pilot window |
| 4–5 | Beta iteration | 5 | 5 | Early conversions from pilot |
| 6 | First paid cohort | 15 | 18 | Target 30–50 signups, ~35% convert |
| 7–9 | Early traction | 12/mo | 45 | Organic + content marketing |
| 10–12 | Growth phase | 18/mo | 85 | GTM scaling begins |
| 13–18 | Scaling | 25/mo | 200 | Mid-market pilots start |
| 19–24 | Maturity | 30/mo | 350 | Stripe live, international revenue |

*Churn applied monthly: cumulative = (prev × 0.94) + new*

---

## 2. Monthly Fixed Costs (Operating Expenses)

### Infrastructure

| Line Item | Monthly (ZAR) | Monthly (USD) | Notes |
|---|---|---|---|
| Heroku Staging (autorisen) | R370 | $20 | Basic dyno + Postgres Mini |
| Heroku Production (capecraft) | R1,480 | $80 | Standard-2x dyno + Postgres Standard-0 |
| Heroku Redis | R555 | $30 | Rate limiting / caching |
| Domain & DNS | R55 | $3 | cape-control.com |
| **Infrastructure Subtotal** | **R2,460** | **~$133** | |

### AI / API Costs (Variable — scales with usage)

| Line Item | Per-Unit | Monthly Estimate (Early) | Monthly Estimate (Scale) |
|---|---|---|---|
| Anthropic Claude 3.5 Haiku (inference) | ~$0.25/1K input + $1.25/1K output | R1,850 ($100) | R18,500 ($1,000) |
| Embedding API (RAG pipeline) | ~$0.02/1K tokens | R370 ($20) | R3,700 ($200) |
| OpenAI fallback | Variable | R185 ($10) | R1,850 ($100) |
| **AI Subtotal** | | **R2,405 ($130)** | **R24,050 ($1,300)** |

### SaaS & Tooling

| Line Item | Monthly (ZAR) | Monthly (USD) | Notes |
|---|---|---|---|
| GitHub (Team) | R185 | $10 | CI/CD, Actions minutes |
| Sentry / monitoring | R555 | $30 | Error tracking (when added) |
| Email (transactional) | R185 | $10 | SMTP for login notifications, invites |
| Typeform / survey | R555 | $30 | Beta feedback collection |
| Misc SaaS | R370 | $20 | Analytics, misc |
| **SaaS Subtotal** | **R1,850** | **~$100** | |

### Personnel

| Role | Monthly (ZAR) | When | Notes |
|---|---|---|---|
| Founder (Robert) | R0 | Month 1–6 | Unpaid / bootstrapping |
| Founder draw | R25,000 | Month 7+ | Modest draw once revenue starts |
| Contract engineer #1 | R37,000 | Month 6+ | Part-time, critical path features |
| Contract engineer #2 | R37,000 | Month 10+ | Scale team as revenue grows |
| Growth / marketing | R18,500 | Month 12+ | Content + partnerships |
| **Personnel Subtotal** | **R0 → R117,500** | | Ramp over 24 months |

---

## 3. One-Time / Periodic Costs

| Item | Cost (ZAR) | Timing | Notes |
|---|---|---|---|
| PayFast setup & integration | R0 | Done | Already integrated |
| Stripe integration | R18,500 | Month 8–9 | Developer time + fees |
| SOC 2 readiness assessment | R93,000 | Month 12–15 | If pursuing certification |
| Legal (terms, privacy, DPA) | R18,500 | Month 3 | Pre-beta legal review |
| Branding / design refresh | R9,250 | Month 5 | Before public launch |
| Security penetration test | R37,000 | Month 9 | Pre-mid-market |
| **One-Time Total** | **~R176,250** | | Spread across Year 1–2 |

---

## 4. Revenue Projections

### Subscription Revenue (Conservative)

| Month | Paying Users | Blended ARPU (R) | Subscription Rev (R) | Services Rev (R) | **Total Rev (R)** |
|---|---|---|---|---|---|
| 1 | 0 | — | 0 | 0 | **0** |
| 2 | 0 | — | 0 | 0 | **0** |
| 3 | 0 | — | 0 | 0 | **0** |
| 4 | 3 | 529 | 1,587 | 0 | **1,587** |
| 5 | 5 | 600 | 3,000 | 0 | **3,000** |
| 6 | 18 | 700 | 12,600 | 9,250 | **21,850** |
| 7 | 28 | 750 | 21,000 | 9,250 | **30,250** |
| 8 | 37 | 780 | 28,860 | 9,250 | **38,110** |
| 9 | 45 | 800 | 36,000 | 13,875 | **49,875** |
| 10 | 58 | 810 | 46,980 | 13,875 | **60,855** |
| 11 | 72 | 820 | 59,040 | 13,875 | **72,915** |
| 12 | 85 | 830 | 70,550 | 18,500 | **89,050** |
| **Year 1 Total** | | | **R279,617** | **R87,875** | **R367,492** |

| Month | Paying Users | Blended ARPU (R) | Subscription Rev (R) | Services Rev (R) | **Total Rev (R)** |
|---|---|---|---|---|---|
| 13 | 100 | 830 | 83,000 | 18,500 | **101,500** |
| 14 | 118 | 830 | 97,940 | 18,500 | **116,440** |
| 15 | 135 | 850 | 114,750 | 18,500 | **133,250** |
| 16 | 155 | 850 | 131,750 | 23,125 | **154,875** |
| 17 | 175 | 860 | 150,500 | 23,125 | **173,625** |
| 18 | 200 | 870 | 174,000 | 23,125 | **197,125** |
| 19 | 225 | 880 | 198,000 | 27,750 | **225,750** |
| 20 | 250 | 890 | 222,500 | 27,750 | **250,250** |
| 21 | 275 | 900 | 247,500 | 27,750 | **275,250** |
| 22 | 300 | 910 | 273,000 | 27,750 | **300,750** |
| 23 | 325 | 920 | 299,000 | 32,375 | **331,375** |
| 24 | 350 | 930 | 325,500 | 32,375 | **357,875** |
| **Year 2 Total** | | | **R2,317,440** | **R300,625** | **R2,618,065** |

### Year-End ARR

| | Conservative | Optimistic |
|---|---|---|
| **End of Year 1** | R1,069,000 (~$58K ARR) | R2,500,000 (~$135K ARR) |
| **End of Year 2** | R4,295,000 (~$232K ARR) | R9,250,000 (~$500K ARR) |

---

## 5. Monthly Cash Flow Summary

### Year 1 — Month-by-Month

| Month | Revenue (R) | Infrastructure (R) | AI Costs (R) | SaaS (R) | Personnel (R) | One-Time (R) | **Net Cash Flow (R)** | **Cumulative (R)** |
|---|---|---|---|---|---|---|---|---|
| 1 | 0 | 2,460 | 1,850 | 1,480 | 0 | 0 | **-5,790** | **-5,790** |
| 2 | 0 | 2,460 | 1,850 | 1,480 | 0 | 0 | **-5,790** | **-11,580** |
| 3 | 0 | 2,460 | 2,035 | 1,850 | 0 | 18,500 | **-24,845** | **-36,425** |
| 4 | 1,587 | 2,460 | 2,220 | 1,850 | 0 | 0 | **-4,943** | **-41,368** |
| 5 | 3,000 | 2,460 | 2,405 | 1,850 | 0 | 9,250 | **-12,965** | **-54,333** |
| 6 | 21,850 | 2,460 | 3,700 | 1,850 | 62,000 | 0 | **-48,160** | **-102,493** |
| 7 | 30,250 | 2,460 | 4,625 | 1,850 | 62,000 | 0 | **-40,685** | **-143,178** |
| 8 | 38,110 | 2,460 | 5,550 | 1,850 | 62,000 | 9,250 | **-43,000** | **-186,178** |
| 9 | 49,875 | 2,460 | 7,400 | 1,850 | 62,000 | 37,000 | **-60,835** | **-247,013** |
| 10 | 60,855 | 3,700 | 9,250 | 1,850 | 99,000 | 0 | **-52,945** | **-299,958** |
| 11 | 72,915 | 3,700 | 11,100 | 1,850 | 99,000 | 0 | **-42,735** | **-342,693** |
| 12 | 89,050 | 3,700 | 12,950 | 1,850 | 99,000 | 93,000 | **-121,450** | **-464,143** |
| **Year 1** | **R367,492** | **R33,240** | **R64,935** | **R21,460** | **R545,000** | **R167,000** | **-R464,143** | |

### Year 2 — Quarterly Summary

| Quarter | Revenue (R) | Total Costs (R) | **Net Cash Flow (R)** | **Cumulative (R)** |
|---|---|---|---|---|
| Q1 (M13–15) | 351,190 | 393,000 | **-41,810** | **-505,953** |
| Q2 (M16–18) | 525,625 | 430,000 | **+95,625** | **-410,328** |
| Q3 (M19–21) | 751,250 | 475,000 | **+276,250** | **-134,078** |
| Q4 (M22–24) | 990,000 | 510,000 | **+480,000** | **+345,922** |
| **Year 2** | **R2,618,065** | **R1,808,000** | **+R810,065** | |

---

## 6. Cash Flow Waterfall (Visual)

```
  Revenue ──────────────────────────────────────────────►
  Month:  1   2   3   4   5   6   7   8   9  10  11  12  │ 13─15  16─18  19─21  22─24
         ─── ─── ─── ─── ─── ─── ─── ─── ─── ─── ─── ──── │ ────── ────── ────── ──────
  Rev R:  0   0   0   2K  3K  22K 30K 38K 50K 61K 73K 89K │ 351K   526K   751K   990K

  Cumulative Cash Position (R '000):
   +400 │                                                              ─────────── ████
   +200 │                                                         ████
      0 │───                                                 ████
   -100 │   ───                                         ████
   -200 │      ────                                ████
   -300 │          ─────────                  ████
   -400 │                   ───────      ████
   -500 │                          ██████
```

---

## 7. Break-Even Analysis

| Metric | Value |
|---|---|
| **Monthly break-even revenue** | ~R130,000/mo (at scale cost base) |
| **Users needed at break-even** | ~155–165 paying users (at R830 blended ARPU) |
| **Expected break-even month** | Month 18–20 (quarterly cash-flow positive by Q2 Year 2) |
| **Cumulative cash needed to break-even** | R464,000–R510,000 |
| **Full payback month** | Month 22–24 (cumulative positive) |

---

## 8. Funding Scenarios

### Scenario A: Bootstrap Only

- **Runway needed:** ~R500,000 ($27K USD) personal capital
- **Risk:** Tighter timelines, slower hiring, no SOC 2 push
- **Break-even:** Month 18–20
- **Benefit:** Full equity retained

### Scenario B: Small Raise (R1–3M / $55–165K)

- **Use of funds:** Engineer #2 earlier (Month 4), marketing, SOC 2
- **Impact:** Accelerate to break-even by Month 14–16
- **Dilution:** 10–20% (SAFE or convertible note)
- **Trigger:** 30+ paying users with >3 month retention

### Scenario C: Growth Raise (R5–10M / $270–540K)

- **Use of funds:** Full team (5–7), security certifications, mid-market push
- **Impact:** Aggressive scaling, earlier ARR milestones
- **Dilution:** 15–25%
- **Trigger:** 100+ paying users, proven unit economics, mid-market demand signal

---

## 9. Key Sensitivities

| Variable | Impact if +20% worse | Mitigation |
|---|---|---|
| **Churn rate** (6% → 7.2%) | Break-even delays 2–3 months; LTV drops 16% | Onboarding quality, evidence value, sticky workflows |
| **AI costs** | Margin compresses 5–8 points | Response caching, model tiering, quotas |
| **Conversion rate** (beta → paid) | Revenue delays 1–2 months | "First evidence pack" onboarding, capsule value |
| **ARPU** (R830 → R664) | Need 20% more users to break even | Upsell enterprise tier, services bundling |
| **Sales cycle length** | Cash trough deepens R50–100K | Services revenue bridges; free tier hooks |

---

## 10. Payment Processing Fees

| Provider | Fee Structure | Impact |
|---|---|---|
| **PayFast** (ZAR) | 2.5% + R2.00 per transaction | ~R21/transaction on Pro plan |
| **Stripe** (international, from Q3 2026) | 2.9% + $0.30 per transaction | ~$1.65/transaction on $49 plan |
| **Effective revenue reduction** | ~3–4% of gross subscription revenue | Factored into gross margin target |

---

## 11. Tax Obligations

| Obligation | Rate / Notes |
|---|---|
| **VAT** (South Africa) | 15% — mandatory once turnover exceeds R1M/year |
| **Income Tax** (CC) | 27% corporate rate on net profit |
| **Provisional Tax** | Required once trading — two payments per year |
| **Withholding Tax** (international services) | May apply on contractor payments outside ZA |

*Consult a tax practitioner before first VAT registration threshold is reached (approximately Month 12–14 at conservative projections).*

---

## 12. Monthly KPIs to Track

| KPI | Target | Why |
|---|---|---|
| MRR | Growth ≥ 15% m/m (early) | Revenue momentum |
| Net Revenue Retention | ≥ 95% | Churn + expansion balance |
| Gross Margin | ≥ 55% | AI cost discipline |
| Burn Rate | < R100K/mo (pre-revenue) | Runway preservation |
| Months of Runway | ≥ 6 months | Solvency buffer |
| LTV:CAC | ≥ 3:1 | Unit economics health |
| Cash Conversion Score | Revenue / Total Spend | Efficiency signal |

---

*This projection is assumption-based and should be refreshed quarterly as actuals become available. See [CapeControl_Business_Plan_v2.md](CapeControl_Business_Plan_v2.md) for underlying strategy.*
