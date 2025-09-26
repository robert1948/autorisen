# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

# Routers
from app.routes.auth_tokens import router as auth_tokens_router         # /api/auth (login w/ cookie, refresh, logout)
from app.routes.auth_db import router as auth_db_router                 # /api/auth (DB-backed register, login, me)
from app.routes.auth_verify import router as auth_verify_router         # /api/auth (verify request/confirm)
from app.routes.auth_reset import router as auth_reset_router         # /api/auth (reset request/confirm)
try:
    # Modular health router (backend/src/modules/health/router.py)
    from src.modules.health.router import router as health_router
except Exception:  # pragma: no cover - defensive import for dev environments
    health_router = None

app = FastAPI(title="Autorisen API")

# --- CORS (cookies need allow_credentials=True) ---
default_origins = {
    "http://localhost:5173",  # container internal 5173; host-facing dev at http://localhost:3000
    "http://localhost:3000",
}
env_frontend = os.getenv("FRONTEND_ORIGIN")
if env_frontend:
    default_origins.add(env_frontend)

# Optional: comma-separated overrides via CORS_ALLOW_ORIGINS
csv = os.getenv("CORS_ALLOW_ORIGINS")
if csv:
    for item in csv.split(","):
        item = item.strip()
        if item:
            default_origins.add(item)

app.add_middleware(
    CORSMiddleware,
    allow_origins=sorted(default_origins),
    allow_credentials=True,                 # send/receive refresh cookie
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

# --- Routers ---
# Use token/refresh dev routes first, then DB-backed auth routes
env = os.getenv("ENVIRONMENT", "development")

# In development we mount the token dev routes (convenience helpers). In production
# we avoid mounting these so the DB-backed auth in `auth_db` is authoritative.
if env == "development":
    app.include_router(auth_tokens_router)

# Always mount DB-backed auth and verify/reset flows
app.include_router(auth_db_router)
app.include_router(auth_verify_router)
app.include_router(auth_reset_router)

# Mount modular health endpoints (exposes /alive and /ping)
if health_router is not None:
    app.include_router(health_router)

# --- Basics / Health ---
@app.get("/", include_in_schema=False)
def root():
    return {"ok": True, "name": "autorisen", "docs": "/docs"}

@app.get("/api/status")
def status():
    return {"ok": True}

@app.get("/api/health", include_in_schema=False)
def health_alias():
    return {"ok": True}

# Back-compat: if modular health wasn't imported, ensure /alive exists
if health_router is None:
    @app.get("/alive", include_in_schema=False)
    def alive_fallback():
        return {"status": "ok"}
