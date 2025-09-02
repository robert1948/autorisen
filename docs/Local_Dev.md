# Local Dev (Autorisen / CapeControl)

This one-pager explains how to run the full stack locally with Docker Compose using environment-specific `.env` files and the provided `Makefile` shortcuts.

---

## Prereqs

- Docker + Docker Compose
- Git
- Make (for shortcuts)

---

## Env Files

- **Checked in (templates / safe defaults):**
  - `/.env.example` – master template (no secrets)
  - `/client/.env.development` – safe Vite defaults

- **Gitignored (real secrets):**
  - `/.env.development.local` – main local secrets for compose
  - `/client/.env.development.local` – Vite overrides (only `VITE_*`)
  - `/backend/.env.development.local` – backend-only overrides (rarely needed)

> Start by copying:  
> `cp .env.example .env.development.local` and fill values.

---

## How to Run

### Start services

```bash
make up
