#!/bin/bash

echo "📋 Updating ROADMAP.md..."

cat << 'EOF' > ROADMAP.md
# ROADMAP

## ✅ Milestone 1: Project Initialization & Deployment

- [x] Set up FastAPI backend structure
- [x] Configure `.env` with `DATABASE_URL`, `SECRET_KEY`, `DEV_JWT`
- [x] Split schema files: `schemas/user.py`, `schemas/developer.py`
- [x] Implement `GET /developers` and `GET /users` routes
- [x] Add `POST /register-developer` and `POST /register-user`
- [x] Generate Swagger docs with auth hint token
- [x] Deploy backend to Heroku with working root health check
- [x] Test Swagger locally and on Heroku

---

## ✅ Milestone 2: Authentication & Security

- [x] Implement password hashing using `bcrypt`
- [x] Add `POST /login` endpoints for developers and users
- [x] Generate JWT tokens upon successful login
- [x] Protect `/me` routes with `Depends(auth_guard)`
- [x] Extend Swagger auth to use real JWT bearer token

---

## 🚧 Milestone 3: React Frontend Integration

- [ ] Set up React frontend project
- [ ] Create basic pages: Home, Login, Register, Dashboard
- [ ] Add Axios client with JWT token storage
- [ ] Hook frontend forms to backend `/register-*` and `/login` routes
- [ ] Display user data from `/me` after login

---

## 🚧 Milestone 4: Testing & CI/CD

- [x] Add Pytest tests for registration routes
- [ ] Create `test_login.py` and `test_me.py`
- [ ] Create test DB configuration
- [ ] Setup GitHub Actions for test + Heroku deploy
- [ ] Use Black/Flake8 for linting

---

## ✅ Milestone 5: Database Model Enhancements

- [x] Add timestamp fields (created_at, updated_at)
- [x] Add role-based access support (admin, user, developer)
- [x] Index frequently queried columns
- [x] Enable pagination on `GET /users` and `GET /developers`

---

## 📘 Notes

- Prioritize login + JWT protection before frontend integration.
- Code and docs live in `backend/`, `client/`, and `scripts/`.
- Use `ROADMAP.md` to track real-time progress and planning.
EOF

echo "✅ ROADMAP.md updated successfully."
