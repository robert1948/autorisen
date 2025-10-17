# backend/src/app.py
from __future__ import annotations

import logging
import os

from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse, Response, PlainTextResponse
from dotenv import load_dotenv

# Load .env for local dev (safe in prod; no-op if vars already set)
load_dotenv()

# ------------------------------------------------------------------------------
# Soft imports — never fail app boot if an optional module/file is missing
# ------------------------------------------------------------------------------

# Security middleware (bot probe blocking + headers)
try:
    from .middleware.bot_hardening import (  # type: ignore
        BlockProbesMiddleware,
        SecurityHeadersMiddleware,
    )
except Exception:
    BlockProbesMiddleware = None  # type: ignore[assignment]
    SecurityHeadersMiddleware = None  # type: ignore[assignment]

# Access-log noise suppression (hide wp/xmlrpc scans)
try:
    from .core.log_filters import AccessPathSuppressFilter  # type: ignore
except Exception:
    AccessPathSuppressFilter = None  # type: ignore[assignment]

# Routers (auth/agents/chatkit)
try:
    from .modules.auth.router import router as auth_router  # type: ignore
except Exception:
    auth_router = None
try:
    from .modules.agents.router import router as agents_router  # type: ignore
except Exception:
    agents_router = None
try:
    from .modules.chatkit.router import router as chatkit_router  # type: ignore
except Exception:
    chatkit_router = None

# ------------------------------------------------------------------------------
APP_ORIGIN = os.getenv("APP_ORIGIN", "").strip()
BOT_HARDEN = os.getenv("BOT_HARDEN", "1").lower() in {"1", "true", "yes"}


def create_app() -> FastAPI:
    app = FastAPI(title="autorisen", version=os.getenv("APP_VERSION", "dev"))

    # -------------------- Middlewares --------------------
    if BlockProbesMiddleware and BOT_HARDEN:
        app.add_middleware(BlockProbesMiddleware)  # type: ignore[arg-type]
    if SecurityHeadersMiddleware:
        app.add_middleware(SecurityHeadersMiddleware)  # type: ignore[arg-type]

    # CORS (same-origin + localhost dev; allow explicit origin if provided)
    allow_origins = ["http://localhost:3000", "http://127.0.0.1:3000"]
    if APP_ORIGIN:
        allow_origins.append(APP_ORIGIN)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"],
        allow_headers=["Authorization", "Content-Type"],
        expose_headers=["Content-Length"],
        max_age=86400,
    )

    # Trim access-log spam from known bot probes
    if AccessPathSuppressFilter:
        logging.getLogger("uvicorn.access").addFilter(AccessPathSuppressFilter())

    # -------------------- Health & utility --------------------
    @app.get("/", include_in_schema=False)
    def root_ok():
        return {"ok": True}

    @app.get("/api/health", include_in_schema=False)
    def api_health():
        return {"ok": True}

    # Silence favicon 404 noise
    @app.get("/favicon.ico", include_in_schema=False)
    def favicon():
        return Response(
            content=b"",
            media_type="image/x-icon",
            headers={"Cache-Control": "public, max-age=31536000"},
        )

    # Polite hint to good crawlers (bad ones ignore this)
    @app.get("/robots.txt", include_in_schema=False)
    def robots():
        body = "User-agent: *\nDisallow: /wp-\nDisallow: /xmlrpc.php\n"
        return Response(
            content=body,
            media_type="text/plain",
            headers={"Cache-Control": "public, max-age=86400"},
        )

    # Explicit short-circuits for common WP probes
    @app.get("/xmlrpc.php", include_in_schema=False)
    def _bots_xmlrpc():
        return PlainTextResponse("Not found", status_code=404, headers={"Cache-Control": "no-store"})

    @app.get("/{prefix:path}/wp-includes/wlwmanifest.xml", include_in_schema=False)
    def _bots_wlw(prefix: str):
        return PlainTextResponse("Not found", status_code=404, headers={"Cache-Control": "no-store"})

    # -------------------- API Routers --------------------
    api = APIRouter()
    if auth_router:
        api.include_router(auth_router, prefix="/auth", tags=["auth"])
    if agents_router:
        api.include_router(agents_router, prefix="/agents", tags=["agents"])
    if chatkit_router:
        api.include_router(chatkit_router, prefix="/chatkit", tags=["chatkit"])

    # Namespace all app routes under /api
    app.include_router(api, prefix="/api")

    # -------------------- Error handling --------------------
    @app.exception_handler(Exception)
    async def _unhandled_error(_, exc: Exception):
        logging.getLogger("uvicorn.error").exception("Unhandled exception")
        return JSONResponse({"detail": "Internal Server Error"}, status_code=500)

    return app


# Uvicorn entrypoint
app = create_app()

# Concise boot log (helps when tailing Heroku logs)
logging.getLogger("uvicorn.error").info(
    "autorisen boot: origin=%s harden=%s version=%s",
    APP_ORIGIN or "(unset)",
    BOT_HARDEN,
    os.getenv("APP_VERSION", "dev"),
)
