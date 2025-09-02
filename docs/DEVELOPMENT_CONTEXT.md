# DEVELOPMENT_CONTEXT.md

## Project Overview
Cape Control (staging: **Autorisen**, production: **Capecraft**) is a full-stack platform designed to empower local and regional businesses with **AI agents**, seamless automation, and real-time insights. The project is built with:

- **Frontend:** React (Vite + Tailwind)
- **Backend:** FastAPI (Python 3.11)
- **Database:** PostgreSQL
- **Deployment:** Docker, Docker Compose, Heroku (staging + production pipelines)
- **Version Control:** GitHub (with Actions for CI/CD)
- **AI Providers:** OpenAI, Anthropic Claude, Google Gemini (multi-provider)

The platform emphasizes:
- Accessibility and simplicity for SMEs
- Context-aware AI agents
- Secure, privacy-respecting architecture
- Real-time analytics and dashboards
- Seamless integrations with existing tools

---

## Environments
- **Local Development**: Docker Compose with API + DB for dev; lightweight setup to simulate staging.  
- **Staging (Autorisen)**: Always ahead of production; experimental features tested here.  
- **Production (Capecraft)**: Stable environment for live users; updated only after successful staging validation.  

Environment-specific configuration is managed with `.env` files and secrets, ensuring portability and minimal downtime during deployment.

---

## Architecture
- **Backend**
  - FastAPI app structured with modular routes (`/auth`, `/ai`, `/analytics`, `/integrations`)
  - Middleware stack: logging, monitoring, DDoS protection, sanitization, content moderation
  - JWT authentication with role-based access control
- **Frontend**
  - React with Vite + Tailwind for responsive, modern UI
  - Pages organized under `client/src/pages/`
  - Auth components under `client/src/components/auth/`
- **Database**
  - PostgreSQL with clearly defined schemas (users, developers, agents, analytics)
  - Alembic migrations for version control
- **DevOps**
  - Docker + Docker Compose for local and CI/CD parity
  - GitHub Actions for automated build, test, and deploy
  - Heroku pipeline with staging → production promotion flow

---

## MVP Phase

The MVP phase focuses on delivering a functional platform that demonstrates Cape Control’s mission:
- AI agents for SMEs
- Streamlined onboarding
- Core integrations
- Analytics dashboards
- Secure, privacy-respecting foundation

### 📋 Checklist Reference
For a detailed, step-by-step launch checklist aligned with our mission and promises, see:
- [Checklist_MVP.md](./Checklist_MVP.md)

This checklist should be updated in sync with MVP development progress and used as the **source of truth** for technical + business readiness before moving to production rollout.

---

## Scaling & Roadmap
- **Phase 2 (Enhancements)**: Broader integrations, deeper analytics, enterprise-grade features.  
- **Phase 3 (Advanced Features)**: Developer marketplace, regional expansion, AI personalization, and multi-tenant architecture.  
- **Future Goals**: Establish Cape Control as the leading AI-powered business automation suite for SMEs in emerging markets.  

---

## Notes
- **Autorisen** must always stay ahead of **Capecraft** in development.  
- Deployments follow the runbook in `Release_Runbook.md` to minimize downtime.  
- Documentation (this file, integration plan, checklist, runbook) is living and must remain aligned across repos.  
