# 📍 AutoAgent Project Roadmap

_Last updated: 2025-05-28_

---

## ✅ Milestone 1: Project Initialization

- [x] Set up GitHub repository `autoagent`
- [x] Initialize backend with FastAPI structure
- [x] Add frontend base using React and Bootstrap
- [x] Configure `.env`, CORS, and settings.py
- [x] Add JWT-based authentication

---

## ✅ Milestone 2: Authentication & Core API

- [x] User and Developer registration routes
- [x] JWT login for both roles
- [x] `/me` endpoints for authenticated profiles
- [x] Password hashing with passlib
- [x] Swagger UI with `DEV_JWT` preset for testing
- [x] Role-based auth guards for route protection

---

## ✅ Milestone 3: React Frontend Integration

- [x] Frontend AuthContext with global state
- [x] Login and registration forms (user/dev)
- [x] Protected routes using `RequireAuth`
- [x] Navbar shows login status + dropdown menu
- [x] Dynamic home page (auth-aware)
- [x] Basic profile and dashboard pages
- [x] Global styling via App.css

---

## ✅ Milestone 4: Deployment

- [x] Heroku backend deployed using GitHub integration
- [x] React app built and copied to `backend/static/`
- [x] FastAPI serves frontend with fallback for React Router
- [x] `.env` and config vars matched with Heroku
- [x] Auto-deploy enabled via GitHub main branch
- [x] Verified live deployment:
  - 🌐 https://autorisen-d2ba5f0027e2.herokuapp.com

---

## ⏳ Milestone 5: Onboarding & Agents (In Progress)

- [ ] Developer onboarding controller & routes
- [ ] Smart checklist schema for AI agent guidance
- [ ] Dashboard to show onboarding stage
- [ ] Background task (optional) to track status
- [ ] Timeline visualization

---

## ⏳ Milestone 6: Agent Execution Layer

- [ ] Agent planner & interpreter modules
- [ ] Integration with external tools (e.g., GitHub, Notion)
- [ ] Secure action runner with audit logging
- [ ] Simulated agent demo (frontend + backend)

---

## ⏳ Milestone 7: UI/UX Enhancements

- [ ] Mobile responsive layout
- [ ] Toast alerts and form feedback
- [ ] Animated transitions (Framer Motion)
- [ ] Light/dark mode toggle
- [ ] Accessibility (ARIA, keyboard support)

---

## 🧠 Long-term Vision

- ⌛ AI-assisted workflows with persistent memory
- ⌛ Real-time collaboration
- ⌛ Marketplace for agent templates
- ⌛ SaaS billing + user roles (admin, team, client)

---

## 📦 Project Layout Reference

See `autoplan.md` or run `scripts/project-diagram.sh` for the full directory tree.
