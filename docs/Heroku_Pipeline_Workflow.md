# Heroku Pipeline Workflow Guide

This document explains how our **Staging → Production** workflow is set up using Heroku Pipelines, GitHub Actions, and the apps **Autorisen** (Staging) and **Capecraft** (Production).

---

## 📦 Apps Overview

- **Autorisen (Staging)**

  - Connected to: [robert1948/autorisen](https://github.com/robert1948/autorisen)
  - Deployment: Auto-deploys from `main` branch via **GitHub Actions** (buildpack-based, Python 3.12, FastAPI 0.110.0)
  - Purpose: Safe environment for development, testing, and QA

- **Capecraft (Production)**
  - Deployment: Promoted from **Staging (Autorisen)**
  - Purpose: Live, customer-facing application

---

## 🔄 Workflow Summary

1. **Develop on GitHub (Staging)**
  - Push changes to `main` branch in `robert1948/autorisen`
  - GitHub Actions runs build, test, and deployment jobs using buildpack-based deployment (Procfile, requirements.txt, runtime.txt at backend root)
  - If successful → changes automatically deployed to **Autorisen (Staging)**

2. **Test on Staging**
  - Verify new features and bug fixes on **Autorisen**
  - Run manual and automated QA
  - Ensure integration with backend services (DB, APIs, etc.) is stable

3. **Promote to Production**
  - When satisfied, use the **Heroku Pipeline “Promote to Production”** button
  - The Staging build (Autorisen) is promoted directly to **Capecraft (Production)**
  - This avoids rebuilding and guarantees Production runs the **exact same build tested in Staging**

---

## ✅ Best Practices

- **Staging First** → Always deploy to Staging before Production
- **Automated Checks** → Ensure CI tests (lint, unit, integration) pass in GitHub Actions (see cicd.yml)
- **Manual QA** → Test critical flows (login, payments, onboarding) on Staging
- **Promotions Only** → Do not deploy directly to Production; always promote from Staging
- **Rollback Plan** →
  - Use `heroku releases -a capecraft` to view prior releases
  - Roll back if a Production issue is detected

---

## ⚙️ Developer Workflow

1. Make changes locally (Python 3.12, FastAPI 0.110.0)
2. Commit & push to `main` → triggers GitHub Actions (buildpack-based deployment)
3. Confirm workflow success in **GitHub → Actions tab**
4. Verify deployment on **Autorisen (Staging)**
5. If approved, promote to **Capecraft (Production)** via the Heroku Pipeline

---

## 🔍 Rollback Commands

```bash
# List recent releases
heroku releases -a capecraft

# Inspect details of a specific release
heroku releases:info v90 -a capecraft

# Roll back to a previous release
heroku rollback v90 -a capecraft
```
