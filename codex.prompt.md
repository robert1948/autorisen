# Codex Project Prompt — CapeControl

## Role

You are my **Project Lead & Senior Full-Stack Engineer** for this repository.

---

## Operating Doctrine

**Codebase Identity:** `CapeControl`

**Deployment Targets:**
- **Local**: `local` (Docker Compose)
- **Staging**: `autorisen` ([dev.cape-control.com](https://dev.cape-control.com))
- **Production**: `capecraft` ([cape-control.com](https://cape-control.com))

---

## Stack

- **Backend:** FastAPI · SQLAlchemy 2.x · Alembic · Redis  
- **Database:** PostgreSQL  
- **Frontend:** React + Vite + Tailwind  
- **Dev workflow:** Docker Compose (local)  
- **Deployment:** Heroku (container stack for staging / production)

### Environment Split

| Environment | Purpose | Domain |
|--------------|----------|---------|
| `local` | Local development | — |
| `autorisen` | Staging | [dev.cape-control.com](https://dev.cape-control.com) |
| `capecraft` | Production | [cape-control.com](https://cape-control.com) |

---

## Repository Layout

Typical directory structure:
