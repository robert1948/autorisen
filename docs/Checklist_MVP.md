# ✅ AutoLocal MVP Checklist — Linked to `MVP_SCOPE.md`

**Project:** AutoLocal (CapeControl MVP)  
**Owner:** Robert Kleyn  
**Version:** 1.0 — October 2025  
**Reference:** See `docs/MVP_SCOPE.md` for full scope and success metrics.

---

## 📊 Overview

| Total Codex Quota | Used | Remaining | Strategy |
|-------------------:|------:|-----------:|-----------|
| ~120 medium-equivalent | ~72 (≈60%) | ~48 | Use medium by default, low for docs/small edits, high only for refactors |

---

## 🚀 Stage Summary

| Stage | Area | Goal | Est. Codex Use | Priority | Status |
|:------|:------|:------|:---------------:|:----------:|:--------:|
| **S0** | Planning | Finalize MVP scope + checklist | 5 low | P1 | ✅ |
| **S1** | Backend Core | Stable Auth + Health + Version | 25 med | P1 | ⏳ |
| **S2** | Frontend Auth | Login + Register flows | 25 med | P1 | ⏳ |
| **S3** | Agent Stub | Agent list + “Run” stub | 15 med | P2 | ⏳ |
| **S4** | CI & Tests | Smoke tests + GH Action | 15 med | P2 | ⏳ |
| **S5** | Deploy Polish | Landing + release health | 10 low | P3 | ⏳ |
| **Buffer** | — | Bugs + refinements | 15–25 | — | ⏳ |

### Latest Notes

- 2025-10-20 — AUTH-005 security tests still timing out under SQLite; migration 202502191200 patched for CURRENT_TIMESTAMP, next step is finishing the CSRF/AsyncClient fixture refactor before FE-004 can resume.
- 2026-02-07 — Added Playwright UI visual smoke tests with evidence capture for onboarding welcome and dashboard preview.
