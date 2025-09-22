# CapeControl — Guiding Principles & How We Achieve Them

> This playbook turns our five principles into day‑to‑day engineering, product, and ops practice. Use it as a living doc alongside `DEVELOPMENT_CONTEXT.md`, our KPI dashboard, and sprint planning board.

---

## 1) Accessibility for All

**Definition**  
Anyone can onboard, understand what to do next, and get value without prior AI expertise or a large budget.

**Why it matters**  
If users can’t reach value quickly, they churn before discovering the platform’s depth. Accessibility compounds adoption and word‑of‑mouth.

**Key Outcomes (KPIs)**  

- **Activation Rate** = activated users / sign‑ups (target ≥ 60%)  
- **Time‑to‑Value (TTV)** = minutes from signup → first successful agent run (target ≤ 10 min)  
- **Free→Paid Conversion** (target ≥ 5%)

**How we obtain it (practices & deliverables)**  

- **Onboarding UX**: Welcome layer → role selection → “show me value now” checklist (3‑step maximum).  
- **Guided First Run**: Pre‑filled example prompts/tasks per persona; one‑click “Run demo” for FAQ/Scheduler agents.  
- **Friction Removal**: Sign up with email only (verify later), progressive profiling, explain pricing in‑product (no hidden costs).  
- **Help in the Flow**: Inline tips, tooltips, and short empty‑state copy; avoid docs wall.  
- **Pricing**: Free tier with safe but useful limits; clear upgrade prompts only after value.

**Engineering hooks**  

- Feature flags for onboarding experiments (e.g., `onboarding.variant=a|b`).  
- `GET /api/examples` for persona‑specific starter tasks.  
- Telemetry events: `user_signed_up`, `user_activated`, `first_agent_run` with timestamps to compute TTV.

**Anti‑patterns**  

- Walls of documentation before first action.  
- Mandatory billing before first successful run.  
- Multi‑page forms with non‑essential fields.

**Weekly checklist**  

- [ ] Median TTV ≤ 10 min.  
- [ ] ≥ 2 live onboarding A/B tests.  
- [ ] Free tier demo runs ≥ 1 per new user.

---

## 2) Contextual Intelligence

**Definition**  
Agents use the user’s goal, history, and context to produce better answers and fewer clarification loops.

**Why it matters**  
Context reduces cognitive load, increases trust, and improves task completion quality and speed.

**Key Outcomes (KPIs)**  

- **Contextual Success** ≥ 70% (tasks using context that complete / total)  
- **Clarifying Turns** ≤ 1.5 average per task  
- **CSAT** ≥ 4.3/5 post‑task

**How we obtain it**  

- **Lightweight Profiles**: Store role, industry, and last 5 tasks; respect privacy consent.  
- **Context Packets**: Standard schema injected into each agent call (goal, constraints, preferences).  
- **Memory Controls**: “Use last session context” toggle and “Forget” button.  
- **Clarify‑then‑Act**: Single targeted follow‑up question when confidence is low.

**Engineering hooks**  

- `ContextEnvelope` type (goal, persona, recent_tasks[], prefs{}).  
- Middleware to attach envelope to `/api/agents/*` requests.  
- Signals: `context_used=true/false`, `clarifying_question_shown`.

**Anti‑patterns**  

- Over‑collection of data without opt‑in.  
- Hidden context influencing outputs without transparency.

**Weekly checklist**  

- [ ] Clarifying turns trending down or stable.  
- [ ] Opt‑in rate to context features ≥ 50%.

---

## 3) Adaptive by Design

**Definition**  
The system learns from interactions and personalizes recommendations and defaults over time.

**Why it matters**  
Adaptive systems increase success rates and reduce time‑to‑outcome as users return.

**Key Outcomes (KPIs)**  

- **Personalization Lift** ≥ +15% (success on vs off)  
- **Recommendation Uptake** ≥ 35%  
- **30‑day Churn** ≤ 15%

**How we obtain it**  

- **Recommendation Engine**: “Next best task” based on persona + recent activity.  
- **Smart Defaults**: Auto‑fill fields (e.g., timezone, typical task length) from prior usage.  
- **Non‑disruptive Learning**: Update profiles incrementally; allow “reset personalization.”  
- **Controlled Experiments**: AB tests for suggestion cards, ranking, and timing.

**Engineering hooks**  

- `suggestion_generated` / `suggestion_accepted` events with context tags.  
- Feature store (simple DB table) for per‑user defaults.  
- Shadow experiments with safe fallbacks.

**Anti‑patterns**  

- Unexplainable personalization; no “why this?” transparency.  
- Aggressive pop‑ups that interrupt work.

**Weekly checklist**  

- [ ] Uptake ≥ 35% (or rising).  
- [ ] “Reset personalization” tested & functional.

---

## 4) Simplicity & Trust

**Definition**  
Users feel in control. The UI is clear; privacy‑first defaults, transparent data use, and minimal surprises.

**Why it matters**  
Trust increases willingness to try and pay; simplicity reduces support burden.

**Key Outcomes (KPIs)**  

- **Help‑Free Completion** ≥ 75%  
- **Privacy Incidents (sev‑1/2)** = 0  
- **Trust Score** ≥ 4.4/5

**How we obtain it**  

- **Design Rules**: One primary action per view, sensible defaults, descriptive button labels.  
- **Transparent Data Use**: “Why we ask” notes near inputs; privacy summary page.  
- **Error States**: Actionable errors with retry or contact path.  
- **Security**: Rate limiting, input sanitization, structured audit logs.

**Engineering hooks**  

- Security middleware: DDoS, sanitization, content moderation (already in stack).  
- Audit log service with route name, actor, outcome, latency.  
- UI copy guidelines and component library for consistent patterns.

**Anti‑patterns**  

- Dark patterns; auto‑opt‑in to marketing or data sharing.  
- Cryptic errors without recovery steps.

**Weekly checklist**  

- [ ] No sev‑1/2 privacy incidents.  
- [ ] Help‑free completion ≥ 75%.

---

## 5) Productivity & Impact

**Definition**  
We deliver measurable time/cost savings and quality improvements for real workflows.

**Why it matters**  
Sustained retention and monetization depend on real, felt value—not novelty.

**Key Outcomes (KPIs)**  

- **Time Saved/User/Week** ≥ 2 hrs (logs + survey)  
- **Automation Coverage** ≥ 30% of steps in target workflows  
- **Positive ROI** for ≥ 50% of active users

**How we obtain it**  

- **Workflow Mapping**: Pick 2–3 high‑value flows (e.g., FAQ handling, scheduling). Identify steps and automate ≥30%.  
- **Templates & Checklists**: Opinionated templates that reduce cognitive load (“Do it for me” options).  
- **Insight Loops**: Post‑task summary with estimated time saved and recommended next step.  
- **Quality Gates**: Simple acceptance criteria per feature; user‑visible result checks.

**Engineering hooks**  

- Instrument “minutes saved” via baseline vs assisted time.  
- `task_completed` payload includes estimated time saved, steps automated[].  
- Weekly ROI report by segment (free vs paid).

**Anti‑patterns**  

- Automations that create rework or require extensive manual validation.  
- Vanity metrics without user corroboration.

**Weekly checklist**  

- [ ] Median time saved ≥ 2 hrs/wk among actives.  
- [ ] At least one automation >30% coverage live.

---

## Cross‑Cutting Implementation Plan (90‑Day MVP)

**Weeks 1–2: Foundations**  

- Ship onboarding v1 (personas, guided first run).  
- Health, telemetry event schema, and KPI dashboards live.  
- Free tier & pricing copy in product.

**Weeks 3–6: Agents & Context**  

- FAQ Agent MVP + Scheduler Agent MVP.  
- ContextEnvelope middleware; consent & memory controls.  
- First personalization defaults (timezone, typical task duration).

**Weeks 7–9: Adaptation & Productivity**  

- Suggestion cards (next best task) with attribution.  
- Instrumentation for time‑saved and coverage.  
- Accessibility pass and trust copy polish.

**Weeks 10–12: Hardening & Preview**  

- Rate limits, error budgets, and performance pass (P95 < 400ms).  
- Docs & runbooks, staging deploy, preview landing assets.  
- Go/No‑Go with rollback plan and release notes.

---

## Operating Cadence

- **Weekly Metrics Review**: Activation, TTV, Contextual Success, Clarifying Turns, Incidents.  
- **Monthly Review**: Free→Paid, Churn, Personalization Lift, ROI Proxy.  
- **Improvement Sprints**: Any metric missing target for 2 consecutive periods triggers a focused sprint.

---

## Appendices

**Event Names (telemetry)**  
`user_signed_up`, `user_activated`, `first_agent_run`, `agent_run_success`, `agent_run_failed`, `context_used`, `clarifying_question_shown`, `suggestion_generated`, `suggestion_accepted`, `task_completed`, `help_opened`, `survey_submitted`.

**Data Privacy Shortlist**  

- Minimize by default, encrypt at rest, redact logs, support right‑to‑forget.  
- Clear retention policy; document data processors.  
- Security headers and dependency scanning in CI.

**References**  

- `DEVELOPMENT_CONTEXT.md` — ports, quickstart, environments.  
- `AUTH_TROUBLESHOOTING_GUIDE.md` — auth flows.  
- `DEPLOYMENT_GUIDE_2025.md` — ops & release.
