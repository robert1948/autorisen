# 📚 Documentation Index

This index provides an overview of all documentation files under `/docs/` and their purpose.  
Use this as a quick entry point for development, deployment, and project context.

---

## 🔧 Development

- **DEVELOPMENT_CONTEXT.md** — Canonical reference for architecture, tech stack, and environment setup.  
- **DEVELOPMENT_CONTEXT_Old.md** — Archived earlier context (keep for history only).  
- **CONTEXT_UPDATE_README.md** — Notes and updates to context alignment.  
- **DEVELOPMENT_LOG.md** — Running log of development activities and decisions.  
- **DEVELOPMENT_WORKFLOW.md** — Day-to-day dev workflow (local + remote).  
- **LOCAL_DEVELOPMENT.md** — How to run and test locally.  
- **LOCAL_DEVELOPMENT_AND_HEROKU.md** — Hybrid guide for local work + Heroku integration.  
- **C Control Development.md** — Component-level breakdown of Control module. *(check if name should be `CapeControl_Development.md` for consistency)*

---

## 🚀 Deployment

- **DEPLOYMENT.md** — General deployment guide.  
- **DEPLOYMENT_GUIDE_2025.md** — Updated deployment instructions (replace `DEPLOYMENT.md` going forward).  
- **Heroku_Pipeline_Workflow.md** — End-to-end Heroku pipeline (staging → production).  
- **Release Runbook.md** — Manual steps and checks before a production release.  
- **PreDeployment_Sanity_Checklist.md** — Quick validation steps before deploying.  

---

## 📊 Analytics & Integrations

- **ANALYTICS_DASHBOARD_COMPLETE.md** — Finalized analytics dashboard documentation.  
- **CAPECRAFT_INTEGRATION_UPDATE.md** — Integration notes for CapeCraft components.  
- **COMPREHENSIVE_FILE_DIAGRAM.md** — Full system/file structure diagram.  
- **Integration Plan.md** — Roadmap for external system integrations.  

---

## 🔐 Authentication & API

- **AUTH_TROUBLESHOOTING_GUIDE.md** — Common auth issues + fixes.  
- **API_DOCUMENTATION_2025.md** — Up-to-date API endpoints and usage.  

---

## 🌍 Vision & Planning

- **CapeControlVision.md** — High-level vision and mission statement.  
- **WORKFLOW_IMPLEMENTATION_SUMMARY.md** — Summary of workflow changes and improvements.  
- **Integration Plan.md** — System integration roadmap.  
- **DUMMY_REGISTRATION_CHECKLIST.md** *(optional new file)* — Local dummy registration + email verification flow.  

---

## ✅ TODO: Documentation Cleanup

- [ ] **Unify naming conventions**  
  - Rename `C Control Development.md` → `CapeControl_Development.md`  
  - Standardize file names (use Title_Case or kebab-case consistently)  

- [ ] **Merge overlapping docs**  
  - `DEPLOYMENT.md` → mark as legacy, keep `DEPLOYMENT_GUIDE_2025.md` as source of truth  
  - `DEVELOPMENT_CONTEXT_Old.md` → archive officially  
  - Clarify overlap between `CONTEXT_UPDATE_README.md` and `DEVELOPMENT_CONTEXT.md`  

- [ ] **Add missing guides**  
  - `TESTING_GUIDE.md` — unit, integration, and smoke testing workflow  
  - `SECURITY_NOTES.md` — authentication, secrets, compliance checklist  
  - `ENVIRONMENT_SETUP.md` — unify local/Heroku setup instructions  

- [ ] **Add cross-references**  
  - Each doc should link back to `INDEX.md` at the top  
  - Deployment docs should reference `Release Runbook.md` and `PreDeployment_Sanity_Checklist.md`  

- [ ] **Versioning & archiving**  
  - Tag legacy docs with `[ARCHIVED]` in filename or front matter  
  - Keep only current year’s API/Deployment guides active  

---
