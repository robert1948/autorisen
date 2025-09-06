# Cape Control MVP Launch Checklist

**Last updated:** 2025-09-06

Status note (engineering): v3.1.0 tagged and pushed. Health endpoints enhanced and standardized; deployment to Heroku container pending smoke test of /api/health and /api/health/status.

This checklist ensures that our MVP launch delivers on the promises outlined in **About Cape Control** while staying aligned with our development context.

---

## 1. Technical Foundation

- [ ] **AI Agents (Core Feature)**  
  **Status:** 🚧 In Progress  
  **Deliverables (MVP Scope):**  
  - [ ] Customer Service Agent  
    - Basic FAQ answering via `/api/agents/faq` route.  
    - Backed by OpenAI GPT-4o-mini.  
  - [ ] Scheduling Agent  
    - Interpret simple scheduling commands.  
    - Store events in PostgreSQL via `/api/agents/scheduler`.  
    **Status:** ✅ Completed  
    **Notes:** Scheduling endpoint implemented at `/api/v1/agents/scheduler`; persists events in `scheduled_events` table with demo provider.
  - [ ] Adaptive Context Handling  
    - Store last 5 messages in DB for context.  

  **Notes:**  
  - AI provider logic modularized in `services/ai_provider.py`.  
  - Basic FAQ agent implemented as `/api/agents/faq` (demo `CapeAIService` used for local/dev responses).  
  - Status: ✅ Basic FAQ endpoint implemented (records conversation and messages, returns demo answer).  
  - Database models: `AgentSession`, `AgentMessage`, `ScheduledEvent`.  
  - Frontend card in React: FAQ + Schedule Task forms.  
  - Out of scope for MVP: multi-step reasoning, external integrations (CRM, Google Calendar), and advanced ML retraining.  

- [ ] **Custom Integrations**
  - At least 1–2 working integrations (e.g., CRM, POS, Google Calendar).
  - No workflow breakage during integration.

- [ ] **Performance Analytics**
  - Real-time dashboards with:
    - Usage stats (tasks completed, response times).
    - Business insights (basic trends, performance metrics).

- [ ] **Secure Architecture**
  - Authentication with role-based access control.
  - Privacy compliance (GDPR-lite principles).

- [ ] **Streamlined Setup**
  - Guided onboarding wizard (no tech skills required).
  - Self-service registration.

---

## 2. Business & Value Alignment

- [ ] **Mission Validation**
  - Messaging emphasizes empowering SMEs with simplicity, speed, and elegance.
  - Focus on local and regional business needs.

- [ ] **Why Cape Control Demonstration**
  - ✅ Purpose-built for SMEs.  
  - ✅ AI agents adapting to needs.  
  - ✅ Easy setup, no tech skills required.  
  - ✅ Live usage analytics.  
  - ✅ Secure and privacy-respecting.  

---

## 3. Operations & Support

- [ ] **24/7 Support Simulation**
  - AI-powered chat with human fallback.
  - Escalation flow defined (AI → email → phone).

- [ ] **Customer Feedback Loop**
  - In-app feedback capture (ratings, surveys).
  - Iterative update plan based on pilot users.

---

## 4. Go-To-Market Preparation

- [ ] **MVP Marketing Assets**
  - Finalized landing page with mission + value.
  - Demo video or product walkthrough.

- [ ] **Early Adopter Program**
  - 5–10 pilot businesses onboarded.
  - Free/discounted trial for feedback.

- [ ] **Launch Playbook**
  - Rollout timeline (beta → limited release → public).
  - Success metrics: *10 active SMEs onboarded in 30 days*.

---

## 5. Post-Launch Iteration

- [ ] **Performance Review**
  - Analytics monitoring: adoption, usage, support needs.

- [ ] **Feature Roadmap**
  - Prioritize enhancements (integrations, analytics depth, AI personalization).

- [ ] **Scale Strategy**
  - Regional expansion readiness (multi-language, wider CRM/POS support).

---

📌 **Reminder:** This checklist evolves with each sprint. Update items in sync with [DEVELOPMENT_CONTEXT.md](./DEVELOPMENT_CONTEXT.md) to keep documentation consistent across staging (Autorisen) and production (Capecraft).
