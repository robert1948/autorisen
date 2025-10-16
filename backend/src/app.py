# backend/src/app.py
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Do NOT import get_current_user here.
from backend.src.modules.auth.router import router as auth_router

# --- App ---
app = FastAPI(
    title="CapeControl API",
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

# --- CORS (safe defaults; tighten via env/settings later) ---
try:
    # If you have settings, we’ll use them; otherwise fall back to permissive dev CORS
    from backend.src.settings import settings  # type: ignore[attr-defined]

    allow_origins = getattr(settings, "CORS_ALLOW_ORIGINS", ["*"])
except Exception:
    allow_origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Lightweight health endpoint (no DB/auth at import time) ---
@app.get("/api/health")
def health():
    return {"ok": True}


# Optional landing
@app.get("/")
def root():
    return {"service": "CapeControl API", "docs": "/docs", "health": "/api/health"}


# --- Routers (protect endpoints inside their own modules) ---
# NOTE: Do not pass global dependencies=... here.
app.include_router(auth_router)

__all__ = ["app"]
