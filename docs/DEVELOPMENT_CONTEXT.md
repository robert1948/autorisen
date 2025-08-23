# 🛠 DEVELOPMENT CONTEXT

**Last Updated**: August 23, 2025  
**Source of truth**: CapeControl / Capecraft project (synchronized with `C_Control_Development.md`)  
**Project Status**: Production Ready — Registration fixed, AI Security Suite deployed, Payment & Developer Earnings live  
**Current Version**: v648 (Heroku, deployed Aug 11, 2025) ✅ RUNNING

---

## Executive Summary

This document captures the authoritative development and deployment context for the CapeControl / Capecraft project, incorporating `autorisen` features into the main CapeControl platform.

- **Production App**: `capecraft` (Heroku, version v648)
- **Staging Source**: `autorisen` repo, feature integration validated here
- **Goal**: Feature-flagged integration of `autorisen` modules into CapeControl, with validation gates before production promotion.

---

## 1. Company Information

- **Legal Entity**: Cape Craft Projects CC
- **Trading Name**: Cape Control
- **VAT Number**: 4270105119

---

## 2. Project Status & Versions

- Production Heroku app: `capecraft` (v648, deployed Aug 11, 2025)
- Source app (pre-merge staging): `autorisen`
- Backend: FastAPI 0.104.1 on Python 3.11
- Frontend: React 18 + Vite, served by FastAPI
- Stripe payment integration: ✅ Test-ready, stable at `stripe==7.7.0`

---

## 3. Repositories & Structure

- **Production Repo**: `localstorm` / `capecontrol` (contains `backend/` and `client/`)
- **Staging Repo**: `autorisen` (feature source, to be merged under `apps/autorisen` or `backend/app/routes/autorisen`)

---

## 4. Development Workflow

### Local Development

```bash
# Backend (port 8000)
cd backend
python -m uvicorn app.main:app --reload --port 8000

# Frontend (port 3000)
cd client
npm run dev

# DB migrations
cd backend
alembic upgrade head
```
