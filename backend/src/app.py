"""Application factory for the autorisen backend."""

from __future__ import annotations

import logging
import os
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Optional, TYPE_CHECKING, cast

from dotenv import load_dotenv
from fastapi import APIRouter, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import (
    FileResponse,
    HTMLResponse,
    JSONResponse,
    PlainTextResponse,
    Response,
)

from backend.src.core.config import settings
from backend.src.core.rate_limit import configure_rate_limit
from backend.src.db.session import SessionLocal
from backend.src.modules.auth.csrf import csrf_middleware

try:
    from app.middleware.ddos_protection import DDoSProtectionMiddleware  # type: ignore
except Exception:  # pragma: no cover
    DDoSProtectionMiddleware = None  # type: ignore[assignment]

try:
    from app.utils.input_sanitization import InputSanitizationMiddleware  # type: ignore
except Exception:  # pragma: no cover
    InputSanitizationMiddleware = None  # type: ignore[assignment]

load_dotenv()

# ------------------------------------------------------------------------------
# Optional imports should never break app boot
# ------------------------------------------------------------------------------
try:
    from .middleware.bot_hardening import (  # type: ignore
        BlockProbesMiddleware,
        SecurityHeadersMiddleware,
    )
except Exception:
    BlockProbesMiddleware = None  # type: ignore[assignment]
    SecurityHeadersMiddleware = None  # type: ignore[assignment]

try:
    from .core.log_filters import AccessPathSuppressFilter  # type: ignore
except Exception:
    AccessPathSuppressFilter = None  # type: ignore[assignment]

try:
    from .db.migrations_runner import run_migrations_on_startup  # type: ignore
except Exception:
    run_migrations_on_startup = None  # type: ignore[assignment]

if TYPE_CHECKING:  # pragma: no cover
    from backend.src.agents.mcp_host import MCPHost

try:
    from backend.src.agents.mcp_host import (  # type: ignore
        MCPConfigError as MCPConfigError_,
        mcp_host as _imported_mcp_host,
    )
except Exception:  # pragma: no cover
    MCPConfigError_ = RuntimeError  # type: ignore[assignment]
    _imported_mcp_host = None  # type: ignore[assignment]

mcp_host = cast(Optional["MCPHost"], _imported_mcp_host)

log = logging.getLogger("uvicorn.error")


# ------------------------------------------------------------------------------
# Router safe-loader
# ------------------------------------------------------------------------------
def _safe_import(description: str, dotted_path: str, attr: str):
    try:
        module = __import__(dotted_path, fromlist=[attr])
        router = getattr(module, attr, None)
        if router is None:
            raise AttributeError(attr)
        log.info("Loaded %s router from %s", description, dotted_path)
        return router
    except Exception as exc:  # pragma: no cover
        log.warning("%s router unavailable: %s", description, exc)
        return None


auth_router = _safe_import("auth", "backend.src.modules.auth.router", "router")
auth_v2_router = _safe_import("auth_v2", "app.routes.auth_v2", "router")
agents_router = _safe_import("agents", "backend.src.modules.agents.router", "router")
chatkit_router = _safe_import("chatkit", "backend.src.modules.chatkit.router", "router")
flows_router = _safe_import("flows", "backend.src.modules.flows.router", "router")
marketplace_router = _safe_import(
    "marketplace", "backend.src.modules.marketplace.router", "router"
)
ops_router = _safe_import("ops", "backend.src.modules.ops.router", "router")

# ------------------------------------------------------------------------------
# Constants / paths
# ------------------------------------------------------------------------------
APP_ORIGIN = os.getenv("APP_ORIGIN", "").strip()
BOT_HARDEN = os.getenv("BOT_HARDEN", "1").lower() in {"1", "true", "yes"}
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
CLIENT_DIST = PROJECT_ROOT / "client" / "dist"
SPA_INDEX = CLIENT_DIST / "index.html"

EXPECTED_ROUTES = [
    "/",
    "/about",
    "/login",
    "/register",
    "/register?role=user",
    "/register?role=developer",
    "/subscribe",
]


# ------------------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------------------
def _inline_sitemap(base_url: str, routes: list[str]) -> str:
    today = date.today().isoformat()
    priorities = {
        "/": "1.00",
        "/about": "0.80",
        "/login": "0.80",
        "/register": "0.80",
        "/subscribe": "0.64",
    }
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for route in routes:
        priority = priorities.get(route, "0.64")
        lines.append(
            f"  <url><loc>{base_url.rstrip('/')}{route}</loc>"
            f"<lastmod>{today}</lastmod><priority>{priority}</priority></url>"
        )
    lines.append("</urlset>")
    return "\n".join(lines)


def _ensure_email_config(test_mode: bool) -> None:
    """Email config gate — call this early in create_app()."""
    email_enabled = os.getenv("EMAIL_ENABLED", "1").lower() in {"1", "true", "yes"}

    required_env = {
        "EMAIL_TOKEN_SECRET": getattr(settings, "email_token_secret", None),
        "FROM_EMAIL": getattr(settings, "from_email", None),
        "SMTP_USERNAME": getattr(settings, "smtp_username", None),
        "SMTP_PASSWORD": getattr(settings, "smtp_password", None),
        "SMTP_HOST": getattr(settings, "smtp_host", None),
        "SMTP_PORT": getattr(settings, "smtp_port", None),
    }

    # In test/dev or when EMAIL_ENABLED=0, don't hard-fail — just log what’s missing.
    if test_mode or not email_enabled:
        missing = [name for name, value in required_env.items() if not value]
        if missing:
            reasons = []
            if test_mode:
                reasons.append("test mode active")
            if not email_enabled:
                reasons.append("EMAIL_ENABLED=0")
            reason_text = " and ".join(reasons) or "development settings"
            log.info(
                "%s: skipping strict email configuration checks (missing: %s)",
                reason_text,
                ", ".join(sorted(missing)),
            )
        if not email_enabled:
            log.info("EMAIL_ENABLED=0 — transactional email disabled for this run")
        return

    # In non-test envs with email enabled, enforce strictly
    missing = [name for name, value in required_env.items() if not value]
    if missing:
        raise RuntimeError(
            "Missing required auth email configuration: " + ", ".join(sorted(missing))
        )


def _is_test_mode() -> bool:
    env = (
        os.getenv("APP_ENV") or os.getenv("ENVIRONMENT") or os.getenv("ENV") or ""
    ).lower()
    settings_env = str(getattr(settings, "env", "")).lower()
    flag = os.getenv("AUTH_TEST_MODE", "0").lower() in {"1", "true", "yes"}
    settings_flag = bool(getattr(settings, "auth_test_mode", False))
    pytest_active = "pytest" in sys.modules
    return (
        env == "test"
        or settings_env == "test"
        or flag
        or settings_flag
        or pytest_active
    )


# ------------------------------------------------------------------------------
# App factory
# ------------------------------------------------------------------------------
def create_app() -> FastAPI:
    app = FastAPI(title="autorisen", version=os.getenv("APP_VERSION", "dev"))
    test_mode = _is_test_mode()

    # Enforce/relax email settings according to ENV and EMAIL_ENABLED
    _ensure_email_config(test_mode)

    # Warn if optional OAuth config not set
    optional_env = {
        "GOOGLE_CLIENT_ID": getattr(settings, "google_client_id", None),
        "GOOGLE_CLIENT_SECRET": getattr(settings, "google_client_secret", None),
        "GOOGLE_CALLBACK_URL": getattr(settings, "google_callback_url", None),
        "LINKEDIN_CLIENT_ID": getattr(settings, "linkedin_client_id", None),
        "LINKEDIN_CLIENT_SECRET": getattr(settings, "linkedin_client_secret", None),
        "LINKEDIN_CALLBACK_URL": getattr(settings, "linkedin_callback_url", None),
    }
    for name, value in optional_env.items():
        if not value:
            log.warning("Optional OAuth configuration %s is not set", name)

    # Security middleware (order matters)
    if BlockProbesMiddleware and BOT_HARDEN:
        app.add_middleware(BlockProbesMiddleware)  # type: ignore[arg-type]
    if SecurityHeadersMiddleware:
        app.add_middleware(SecurityHeadersMiddleware)  # type: ignore[arg-type]
    if DDoSProtectionMiddleware:
        app.add_middleware(DDoSProtectionMiddleware)  # type: ignore[arg-type]
    if InputSanitizationMiddleware:
        app.add_middleware(InputSanitizationMiddleware)  # type: ignore[arg-type]

    # CSRF middleware (Starlette BaseHTTPMiddleware dispatch)
    app.add_middleware(BaseHTTPMiddleware, dispatch=csrf_middleware)

    # CORS
    allow_origins = {
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        getattr(settings, "frontend_origin", "").rstrip("/"),
        "https://dev.cape-control.com",
        "https://cape-control.com",
    }
    if APP_ORIGIN:
        allow_origins.add(APP_ORIGIN.rstrip("/"))
    allow_origins = [o for o in allow_origins if o]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"],
        allow_headers=[
            "Authorization",
            "Content-Type",
            "X-CSRF-Token",
            "X-CSRFToken",
            "X-XSRF-Token",
            "X-Requested-With",
        ],
        expose_headers=["Content-Length"],
        max_age=86400,
    )

    # Rate limiting (idempotent even if slowapi is absent/falls back)
    try:
        configure_rate_limit(app)
    except Exception:  # pragma: no cover
        log.exception("Failed to configure rate limiting middleware")

    # Quieter access logs
    if AccessPathSuppressFilter:
        logging.getLogger("uvicorn.access").addFilter(AccessPathSuppressFilter())

    # Minimal landing (served if SPA isn't built yet)
    landing_html = (
        "<!doctype html><html lang='en'><head><meta charset='utf-8'/>"
        "<meta name='viewport' content='width=device-width,initial-scale=1'/>"
        "<title>autorisen</title><style>body{font-family:system-ui,-apple-system,"
        "BlinkMacSystemFont,'Segoe UI',sans-serif;margin:0;padding:0;background:#0f172a;"
        "color:#e2e8f0;display:flex;align-items:center;justify-content:center;min-height:100vh;}"
        "main{max-width:640px;padding:3rem 1.5rem;text-align:center;background:rgba(15,23,42,0.85);"
        "border-radius:16px;box-shadow:0 25px 50px -12px rgba(15,23,42,0.6);}"
        "h1{font-size:2.5rem;margin-bottom:0.75rem;}"
        "p{line-height:1.6;margin:0.75rem 0;}"
        "a{color:#38bdf8;text-decoration:none;font-weight:600;}"
        "a:hover{text-decoration:underline;}"
        "footer{margin-top:2rem;font-size:0.875rem;color:#94a3b8;}"
        "nav{display:flex;flex-wrap:wrap;gap:1rem;justify-content:center;margin-top:1.5rem;}"
        "nav a{padding:0.75rem 1.5rem;border-radius:999px;background:#1e293b;transition:background 0.2s ease;}"
        "nav a:hover{background:#334155;}"
        "</style></head><body><main><h1>autorisen Platform API</h1>"
        "<p>Welcome! This deployment powers authentication, agent tooling, and ChatKit capabilities for the autorisen platform.</p>"
        "<p>Use the quick links below to inspect the live API and health checks.</p>"
        "<nav><a href='/docs'>Interactive Docs</a><a href='/redoc'>ReDoc Spec</a>"
        "<a href='/api/health'>API Health</a></nav>"
        "<footer>Release: {version} · Origin: {origin}</footer></main></body></html>"
    )

    spa_index = SPA_INDEX if SPA_INDEX.exists() else None

    # ----------------------------- Root/Meta ------------------------------
    @app.get("/", include_in_schema=False)
    def root_ok():
        if spa_index:
            return FileResponse(spa_index)
        return HTMLResponse(
            landing_html.format(
                version=os.getenv("APP_VERSION", "dev"),
                origin=APP_ORIGIN or "default",
            )
        )

    @app.get("/favicon.ico", include_in_schema=False)
    def favicon():
        return Response(
            content=b"",
            media_type="image/x-icon",
            headers={"Cache-Control": "public, max-age=31536000"},
        )

    @app.get("/robots.txt", include_in_schema=False)
    def robots_txt():
        base = os.getenv("PUBLIC_BASE_URL", "https://dev.cape-control.com").rstrip("/")
        body = f"User-agent: *\nAllow: /\nSitemap: {base}/sitemap.xml\n"
        return Response(
            content=body,
            media_type="text/plain",
            headers={"Cache-Control": "public, max-age=86400"},
        )

    @app.get("/sitemap.xml", include_in_schema=False)
    def sitemap_xml():
        static_path = CLIENT_DIST / "sitemap.xml"
        if static_path.exists():
            return FileResponse(static_path, media_type="application/xml")
        base = os.getenv("PUBLIC_BASE_URL", "https://dev.cape-control.com")
        return Response(
            _inline_sitemap(base, EXPECTED_ROUTES),
            media_type="application/xml",
            headers={"Cache-Control": "public, max-age=3600"},
        )

    # Honeypots / bot probes
    @app.get("/xmlrpc.php", include_in_schema=False)
    def _bots_xmlrpc():
        return PlainTextResponse(
            "Not found", status_code=404, headers={"Cache-Control": "no-store"}
        )

    @app.get("/{prefix:path}/wp-includes/wlwmanifest.xml", include_in_schema=False)
    def _bots_wlw(prefix: str):
        return PlainTextResponse(
            "Not found", status_code=404, headers={"Cache-Control": "no-store"}
        )

    # Simple alias for external uptime checks
    @app.get("/health")
    def health_alias():
        return {"status": "ok"}

    # ----------------------------- API: health/version --------------------
    @app.get("/api/", include_in_schema=False)
    def api_root():
        return {
            "status": "ok",
            "message": "CapeControl API root",
            "services": ["auth_v1", "auth_v2", "agents", "marketplace"],
        }

    @app.get("/api/health", include_in_schema=False)
    def api_health():
        version = os.getenv("APP_VERSION", "dev")
        env_name = (
            os.getenv("APP_ENV")
            or os.getenv("ENVIRONMENT")
            or os.getenv("ENV")
            or "local"
        )
        db_ok = False
        try:
            with SessionLocal() as session:  # type: ignore[call-arg]
                session.execute(text("SELECT 1"))
            db_ok = True
        except Exception:
            log.exception("Database connectivity check failed for /api/health")
        return {
            "status": "healthy" if db_ok else "degraded",
            "version": version,
            "env": env_name,
            "database_connected": db_ok,
            "input_sanitization": "enabled (Task 1.2.4)",
            "rate_limiting": "active"
            if getattr(app.state, "rate_limit_configured", False)
            else "inactive",
        }

    @app.get("/api/health/alive", include_in_schema=False)
    def api_health_alive():
        return {"alive": True}

    @app.get("/api/health/ping", include_in_schema=False)
    def api_health_ping():
        return {"ping": "pong", "version": os.getenv("APP_VERSION", "dev")}

    @app.get("/api/version", include_in_schema=False)
    def api_version():
        git_sha = os.getenv("GIT_SHA", "").strip()
        app_version = os.getenv("APP_VERSION", "").strip()
        version_value = (
            git_sha or app_version or datetime.utcnow().strftime("%Y%m%d%H%M%S")
        )
        return {"version": version_value}

    @app.get("/api/security/stats")
    def api_security_stats():
        now = datetime.utcnow().replace(tzinfo=None).isoformat() + "Z"
        rate_limit_state = (
            "active" if getattr(app.state, "rate_limit_configured", False) else "inactive"
        )
        return {
            "security_systems": {
                "ddos_protection": "active",
                "input_sanitization": "enabled (Task 1.2.4)",
                "rate_limiting": rate_limit_state,
            },
            "timestamp": now,
        }

    # ----------------------------- API Routers ----------------------------
    api = APIRouter()
    if auth_router:
        # → /api/auth/*
        api.include_router(auth_router, prefix="/auth")
    if auth_v2_router:
        api.include_router(auth_v2_router, prefix="/auth/v2")
    if agents_router:
        api.include_router(agents_router)
    if chatkit_router:
        api.include_router(chatkit_router)
    if flows_router:
        api.include_router(flows_router)
    if marketplace_router:
        api.include_router(marketplace_router)
    if ops_router:
        api.include_router(ops_router)

    # Mount all versioned routes under /api
    app.include_router(api, prefix="/api")

    # ----------------------------- Errors --------------------------------
    @app.exception_handler(Exception)
    async def _unhandled_error(_, exc: Exception):
        logging.getLogger("uvicorn.error").exception("Unhandled exception")
        return JSONResponse({"detail": "Internal Server Error"}, status_code=500)

    # ----------------------------- Startup hooks --------------------------
    enable_migrations = bool(getattr(settings, "run_db_migrations_on_startup", False))
    if enable_migrations and callable(run_migrations_on_startup):

        @app.on_event("startup")
        def _apply_db_migrations() -> None:
            try:
                run_migrations_on_startup()  # type: ignore[misc]
                log.info("Database migrations applied during startup")
            except Exception:
                log.exception("Database migrations failed during startup")
                raise

    else:
        log.info(
            "Startup migrations skipped (enabled=%s, callable=%s)",
            enable_migrations,
            callable(run_migrations_on_startup),
        )

    if mcp_host is not None and os.getenv("ENABLE_MCP_HOST", "0") == "1":

        @app.on_event("startup")
        def _start_mcp_host() -> None:
            host = mcp_host
            if host is None:
                log.warning("ENABLE_MCP_HOST=1 but MCP host import failed")
                return
            try:
                host.start()
            except MCPConfigError_ as exc:  # type: ignore[misc]
                log.error("MCP host disabled: %s", exc)
            except Exception:  # pragma: no cover
                log.exception("Unexpected MCP host start failure")

        log.info("MCP host startup hook registered")

    # ----------------------------- SPA mount ------------------------------
    if spa_index:
        app.mount(
            "/", StaticFiles(directory=str(CLIENT_DIST), html=True), name="frontend"
        )

        @app.get("/{client_path:path}", include_in_schema=False)
        def _spa_fallback(client_path: str):
            # Let API and asset requests fall through normally.
            if client_path.startswith("api/") or client_path.startswith("assets/"):
                raise HTTPException(status_code=404)
            if SPA_INDEX.exists():
                return FileResponse(SPA_INDEX)
            raise HTTPException(status_code=404)

    return app


app = create_app()

logging.getLogger("uvicorn.error").info(
    "autorisen boot: origin=%s harden=%s version=%s",
    APP_ORIGIN or "(unset)",
    BOT_HARDEN,
    os.getenv("APP_VERSION", "dev"),
)
