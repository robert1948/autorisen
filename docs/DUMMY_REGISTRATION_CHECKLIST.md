# Dummy Registration & Email Verification (Localhost)

This checklist ensures we can simulate user registration and email verification flow locally, without hitting production services.

---

## 1. Prerequisites

- [ ] Local backend running (FastAPI/Django/etc.)
- [ ] Local DB migrated with `users` table
- [ ] SMTP test server (e.g. MailHog, Papercut, or Python `smtpd`) installed

---

## 2. Registration Endpoint

- [ ] Confirm `/auth/register` (or equivalent) route exists
- [ ] Accepts `email`, `password`, and `confirm_password`
- [ ] Validates password length and email format
- [ ] Creates DB user in `pending` state (verified=false)

---

## 3. Verification Token

- [ ] Generate token (UUID/JWT) tied to user
- [ ] Store token + expiry in DB
- [ ] Build `/auth/verify?token=XYZ` endpoint

---

## 4. Email Sending (Dummy)

- [ ] Configure SMTP to point at local MailHog (port 1025)
- [ ] Template: “Click here to verify: [Verify Account](http://localhost:8000/auth/verify?token=XYZ)”
- [ ] Log email to console as fallback

---

## 5. Local Test

- [ ] Run backend and SMTP dummy server
- [ ] Register a test user (`test@example.com`)
- [ ] Confirm email appears in MailHog inbox
- [ ] Click verification link → user state flips to `verified=true`

---

## 6. Cleanup

- [ ] Document dummy credentials in `README.md`
- [ ] Reset DB between tests (`make db-reset`)
- [ ] Mark feature as ✅ in `Checklist_MVP.md`
