# backend/src/app.py
from __future__ import annotations

import logging
import os
from pathlib import Path
from datetime import date

from dotenv import load_dotenv
from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.responses import (
    FileResponse,
    HTMLResponse,
    JSONResponse,
    PlainTextResponse,
    Response,
)

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

# Database migrations auto-runner (optional)
try:
    from .db.migrations_runner import run_migrations_on_startup  # type: ignore
except Exception:
    run_migrations_on_startup = None  # type: ignore[assignment]

# Routers (auth/agents/chatkit/flows/marketplace)
log = logging.getLogger("uvicorn.error")


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
agents_router = _safe_import("agents", "backend.src.modules.agents.router", "router")
chatkit_router = _safe_import("chatkit", "backend.src.modules.chatkit.router", "router")
flows_router = _safe_import("flows", "backend.src.modules.flows.router", "router")
marketplace_router = _safe_import(
    "marketplace", "backend.src.modules.marketplace.router", "router"
)

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
    landing_html = """<!doctype html><html lang='en'><head><meta charset='utf-8'/><meta name='viewport' content='width=device-width,initial-scale=1'/><title>autorisen</title><style>body{font-family:system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;margin:0;padding:0;background:#0f172a;color:#e2e8f0;display:flex;align-items:center;justify-content:center;min-height:100vh;}main{max-width:640px;padding:3rem 1.5rem;text-align:center;background:rgba(15,23,42,0.85);border-radius:16px;box-shadow:0 25px 50px -12px rgba(15,23,42,0.6);}h1{font-size:2.5rem;margin-bottom:0.75rem;}p{line-height:1.6;margin:0.75rem 0;}a{color:#38bdf8;text-decoration:none;font-weight:600;}a:hover{text-decoration:underline;}footer{margin-top:2rem;font-size:0.875rem;color:#94a3b8;}nav{display:flex;flex-wrap:wrap;gap:1rem;justify-content:center;margin-top:1.5rem;}nav a{padding:0.75rem 1.5rem;border-radius:999px;background:#1e293b;transition:background 0.2s ease;}nav a:hover{background:#334155;}</style></head><body><main><h1>autorisen Platform API</h1><p>Welcome! This deployment powers authentication, agent tooling, and ChatKit capabilities for the autorisen platform.</p><p>Use the quick links below to inspect the live API and health checks.</p><nav><a href="/docs">Interactive Docs</a><a href="/redoc">ReDoc Spec</a><a href="/api/health">API Health</a></nav><footer>Release: {version} · Origin: {origin}</footer></main></body></html>"""

    spa_index = SPA_INDEX if SPA_INDEX.exists() else None

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

    @app.get("/api/health", include_in_schema=False)
    def api_health():
        version = os.getenv("APP_VERSION", "dev")
        env_name = (
            os.getenv("APP_ENV")
            or os.getenv("ENVIRONMENT")
            or os.getenv("ENV")
            or "local"
        )
        return {"status": "ok", "version": version, "env": env_name}

    @app.get("/api/health/alive", include_in_schema=False)
    def api_health_alive():
        return {"alive": True}

    @app.get("/api/health/ping", include_in_schema=False)
    def api_health_ping():
        return {"ping": "pong", "version": os.getenv("APP_VERSION", "dev")}

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

    # Explicit short-circuits for common WP probes
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

    # -------------------- API Routers --------------------
    api = APIRouter()
    if auth_router:
        api.include_router(auth_router, prefix="/auth")
    if agents_router:
        api.include_router(agents_router)
    if chatkit_router:
        api.include_router(chatkit_router)
    if flows_router:
        api.include_router(flows_router)
    if marketplace_router:
        api.include_router(marketplace_router)

    # Namespace all app routes under /api
    app.include_router(api, prefix="/api")

    # -------------------- Error handling --------------------
    @app.exception_handler(Exception)
    async def _unhandled_error(_, exc: Exception):
        logging.getLogger("uvicorn.error").exception("Unhandled exception")
        return JSONResponse({"detail": "Internal Server Error"}, status_code=500)

    if run_migrations_on_startup:

        @app.on_event("startup")
        def _apply_db_migrations() -> None:
            try:
                run_migrations_on_startup()
            except Exception:
                log.exception("Database migrations failed during startup")
                raise

    if spa_index:
        app.mount(
            "/", StaticFiles(directory=str(CLIENT_DIST), html=True), name="frontend"
        )

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
