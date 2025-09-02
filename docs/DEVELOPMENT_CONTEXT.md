# DEVELOPMENT_CONTEXT.md  

**Version:** v0.1-agents-mvp  

## Environments

- Localhost: Docker Compose setup with FastAPI, React, PostgreSQL, Redis
- Staging: Heroku app `autorisen` with PostgreSQL, Redis
- Production: Heroku app `capecraft` with PostgreSQL, Redis

---

## Architecture

### Backend

- FastAPI app structured with modular routes (`/auth`, `/ai`, `/analytics`, `/integrations`)
- Middleware stack: logging, monitoring, DDoS protection, sanitization, content moderation
- JWT authentication with role-based access control
- Database: PostgreSQL with SQLAlchemy ORM
- Redis: used for caching and background tasks
- AI Provider Integration: OpenAI, Anthropic Claude, Google Gemini
- Containerized with Docker, deployed to Heroku Container Registry

### Frontend

- React + Vite + Tailwind CSS
- Auth flows: login, register, logout
- Onboarding wizard with guided steps
- Dashboard with agent cards and analytics
- Deployed to Heroku, assets stored on S3 (`lightning-s3`)

---

## Security

- JWT-based authentication (short-lived access + refresh tokens)
- Rate limiting and DDoS protection middleware
- Input sanitization middleware
- Audit logging middleware
- GDPR-lite privacy compliance (minimal data retention, clear consent)

---

## AI Agents (Core Feature – MVP Scope)

**Status:** 🚧 In Progress  

### Overview

AI Agents provide context-aware automation and assistance within CapeControl.  
The MVP scope limits functionality to **FAQ answering** and **basic scheduling**, ensuring the feature is testable and stable without scope creep.

### Capabilities

- **Customer Service Agent**
  - Answers FAQs using `/api/agents/faq` (FastAPI route).
  - Powered by OpenAI GPT-4o-mini for cost-effective inference.
- **Scheduling Agent**
  - Parses simple scheduling commands (e.g., “book meeting Tuesday 10”).
  - Stores events in PostgreSQL via `/api/agents/scheduler`.
- **Adaptive Context Handling**
  - Retains the last 5 messages per session in DB for context-aware replies.

### Implementation

- **Backend**
  - Routes:
    - `/api/agents/faq`
    - `/api/agents/scheduler`
  - Service Layer: `services/ai_provider.py` (modular AI provider integration).
  - Database Models:
    - `AgentSession` → tracks user/role and session context
    - `AgentMessage` → query/response history
    - `ScheduledEvent` → lightweight event storage

- **Frontend**
  - React dashboard card for “AI Agents”
  - FAQ form and Scheduling form linked to backend routes

### Out of Scope for MVP

- Multi-step reasoning chains
- External integrations (CRM, Google Calendar, etc.)
- Long-term learning or ML retraining beyond simple session storage

### Deliverables for Completion

- FAQ agent functional end-to-end (UI → API → AI → response)
- Scheduling agent functional end-to-end (UI → API → DB)
- Context storage tested and verified
- Documentation (Checklist + Development Context) updated accordingly
