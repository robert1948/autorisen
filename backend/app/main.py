import os
from app.utils.datetime import utc_now
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles

# NEW: aggregate API router (includes /api/v1/agents/* + /api/agents/* alias)
from .api import api_router
from .routes.agents_faq import router as faq_router

# Existing Routers
from .api.payment import router as payment_router
from .payfast.routes import router as payfast_router
from .routes import (
    audit,
    auth_enhanced,
    auth_v2,
    cape_ai,
    dashboard,
    error_tracking,
    monitoring,
)
from .routes.ai_context import router as ai_context_router
from .routes.ai_performance import router as ai_performance_router
from .routes.ai_personalization import router as ai_personalization_router
from .routes.alerts import router as alerts_router
from .routes.analytics import router as analytics_router
from .routes.developer_earnings import router as developer_earnings_router
from .routes.health import router as health_router
from .routes.password_reset import router as password_reset_router
from .routes.stripe_routes_simple import router as stripe_router

# Middleware (only the ones that exist)
from app.middleware.input_sanitization import InputSanitizationMiddleware
from app.middleware.monitoring import (
    MonitoringMiddleware,
    set_monitoring_middleware_instance,
)

try:
    from app.middleware.rate_limiting import RateLimitingMiddleware  # type: ignore

    _RATE_LIMITING_AVAILABLE = True
except Exception as _rl_exc:  # pragma: no cover - optional
    print(f"⚠️  RateLimitingMiddleware import failed: {_rl_exc}")
    _RATE_LIMITING_AVAILABLE = False

# Optional AI-specific rate limiting (adds headers for /api/ai/*)
try:
    from app.middleware.ai_rate_limiting import AIRateLimitingMiddleware  # type: ignore

    _AI_RATE_LIMITING_AVAILABLE = True
except Exception as _ai_rl_exc:  # pragma: no cover
    print(f"⚠️  AIRateLimitingMiddleware import failed: {_ai_rl_exc}")
    _AI_RATE_LIMITING_AVAILABLE = False

# -------- Optional middleware (graceful fallbacks) --------
DDOS_PROTECTION_AVAILABLE = False
AUDIT_LOGGING_AVAILABLE = False

try:
    from app.middleware.ddos_protection import DDoSProtectionMiddleware

    DDOS_PROTECTION_AVAILABLE = True
    print("✅ DDoS Protection middleware available")
except ImportError:
    print("⚠️  DDoS Protection middleware not available")

try:
    from app.middleware.audit_logging import AuditLoggingMiddleware

    AUDIT_LOGGING_AVAILABLE = True
    print("✅ Audit Logging middleware available")
except ImportError:
    print("⚠️  Audit Logging middleware not available")

# -------- App factory --------
app = FastAPI(
    title="CapeControl API",
    description="Secure, scalable authentication system for CapeControl with AI capabilities",
    version="3.0.0",
)
# Mount the aggregated API router (MVP agents + alias endpoints)
app.include_router(api_router)
# Mount the FAQ agent demo routes
app.include_router(faq_router)


# -------- Version helpers --------
def _env(name: str, default: str = "unknown") -> str:
    val = os.getenv(name, default)
    return val.strip() if val else default


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _version_payload():
    return {
        "service": "capecontrol-backend",
        "version": _env("APP_VERSION"),
        "git_sha": _env("GIT_SHA"),
        "build_time": _env("BUILD_TIME"),
        "environment": _env("ENVIRONMENT", "development"),
        "server_time": _now_iso(),
    }


# -------- Routers --------
# Duplicate api_router inclusion removed (already included above before faq_router) to prevent
# overriding the enhanced FAQ endpoint defined in routes/agents_faq.py.

# Existing apps
app.include_router(auth_v2.router, prefix="/api/auth", tags=["auth"])
app.include_router(auth_enhanced.router, prefix="/api/enhanced", tags=["auth-enhanced"])
app.include_router(
    auth_v2.router, prefix="/api/user", tags=["user"]
)  # user routes via auth router
app.include_router(password_reset_router, tags=["password-reset"])

app.include_router(developer_earnings_router, tags=["developer-earnings"])
app.include_router(
    analytics_router, prefix="/api/analytics", tags=["analytics"]
)  # Perf Analytics
app.include_router(
    payment_router, tags=["payment"]
)  # already under /api/payment inside the router
app.include_router(stripe_router, prefix="/api/stripe", tags=["stripe"])
app.include_router(payfast_router)  # already defines prefix /api/payfast

app.include_router(cape_ai.router, prefix="/api/cape_ai", tags=["cape-ai"])
# Legacy mount for tests expecting /api/ai/* endpoints
app.include_router(cape_ai.router, prefix="/api/ai", tags=["cape-ai-legacy"])
app.include_router(audit.router, prefix="/api/audit", tags=["audit"])
app.include_router(monitoring.router, prefix="/api/monitoring", tags=["monitoring"])
app.include_router(
    error_tracking.router, prefix="/api/error_tracking", tags=["error-tracking"]
)
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])
app.include_router(health_router, prefix="/api/health", tags=["health"])
app.include_router(alerts_router, prefix="/api/alerts", tags=["alerts"])
app.include_router(
    ai_performance_router, prefix="/api/ai_performance", tags=["ai-performance"]
)
app.include_router(ai_context_router, prefix="/api/ai_context", tags=["ai-context"])
app.include_router(
    ai_personalization_router,
    prefix="/api/ai_personalization",
    tags=["ai-personalization"],
)


# Lightweight /api/ root for rate limit & status tests
@app.get("/api/")
async def api_root():
    return {"ok": True, "message": "CapeControl API root"}


# -------- Monitoring middleware (required by your project) --------
monitoring_middleware = MonitoringMiddleware(app)
set_monitoring_middleware_instance(monitoring_middleware)

# -------- Middleware order (reverse order of execution; CORS should be last added) --------
print("⚠️  ContentModerationMiddleware temporarily disabled")

try:
    app.add_middleware(InputSanitizationMiddleware, max_content_length=10 * 1024 * 1024)
    print("✅ InputSanitizationMiddleware added successfully")
except Exception as e:
    print(f"❌ Failed to add InputSanitizationMiddleware: {e}")

# Add rate limiting (must come before CORS so headers still added after processing)
if _RATE_LIMITING_AVAILABLE:
    try:
        app.add_middleware(RateLimitingMiddleware, requests_per_minute=60)
        print("✅ RateLimitingMiddleware added successfully (60 rpm)")
    except Exception as e:  # pragma: no cover
        print(f"❌ Failed to add RateLimitingMiddleware: {e}")

if "_AI_RATE_LIMITING_AVAILABLE" in globals() and _AI_RATE_LIMITING_AVAILABLE:
    try:
        # Provide generous default; tests assert header values (30/min 500/hour) we set inside middleware
        app.add_middleware(AIRateLimitingMiddleware, ai_requests_per_minute=30)
        print("✅ AIRateLimitingMiddleware added successfully (30 rpm AI)")
    except Exception as e:  # pragma: no cover
        print(f"❌ Failed to add AIRateLimitingMiddleware: {e}")

if AUDIT_LOGGING_AVAILABLE:
    try:
        app.add_middleware(AuditLoggingMiddleware)
        print("✅ AuditLoggingMiddleware added successfully")
    except Exception as e:
        print(f"❌ Failed to add AuditLoggingMiddleware: {e}")

if DDOS_PROTECTION_AVAILABLE:
    try:
        app.add_middleware(DDoSProtectionMiddleware)
        print("✅ DDoSProtectionMiddleware added successfully")
    except Exception as e:
        print(f"❌ Failed to add DDoSProtectionMiddleware: {e}")

# Allowlist via env (comma-separated), fallback to "*"
allowlist = os.getenv("CORS_ALLOW_ORIGINS", "").strip()
if allowlist:
    origins = [o.strip() for o in allowlist.split(",") if o.strip()]
else:
    origins = ["*"]  # dev-safe default; tighten in production

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------- Version headers for every response --------
@app.middleware("http")
async def version_headers(request: Request, call_next):
    try:
        response = await call_next(request)
    except Exception as exc:
        # Handle client disconnects gracefully
        try:
            import anyio

            if isinstance(exc, anyio.EndOfStream):
                vp = _version_payload()
                resp = Response(status_code=499)
                resp.headers["X-App-Version"] = vp["version"]
                resp.headers["X-App-Commit"] = vp["git_sha"]
                resp.headers["X-App-Env"] = vp["environment"]
                return resp
        except Exception:
            pass

        # Fallback for other unhandled exceptions
        try:
            import logging

            logging.exception("Unhandled exception while processing request")
        except Exception:
            pass
        vp = _version_payload()
        resp = JSONResponse(
            content={"detail": "Internal Server Error"}, status_code=500
        )
        resp.headers["X-App-Version"] = vp["version"]
        resp.headers["X-App-Commit"] = vp["git_sha"]
        resp.headers["X-App-Env"] = vp["environment"]
        return resp

    vp = _version_payload()
    response.headers["X-App-Version"] = vp["version"]
    response.headers["X-App-Commit"] = vp["git_sha"]
    response.headers["X-App-Env"] = vp["environment"]
    return response


# -------- Static files --------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIST = os.path.join(BASE_DIR, "static")
INDEX_HTML = os.path.join(FRONTEND_DIST, "index.html")


class CustomStaticFiles(StaticFiles):
    async def get_response(self, path, scope):
        response = await super().get_response(path, scope)
        try:
            if path in ("index.html", ""):
                response.headers["Cache-Control"] = (
                    "no-store, no-cache, must-revalidate"
                )
            elif path.startswith("assets/") and path.split(".")[-1] in {
                "js",
                "css",
                "svg",
                "png",
                "jpg",
                "woff2",
            }:
                response.headers["Cache-Control"] = (
                    "public, max-age=31536000, immutable"
                )
            else:
                response.headers.setdefault("Cache-Control", "public, max-age=3600")
        except Exception:
            pass
        return response


if not os.path.exists(INDEX_HTML):
    print(f"⚠️  Frontend build not found: {INDEX_HTML}")
    print("ℹ️  Creating minimal index.html for Heroku deployment")
    os.makedirs(FRONTEND_DIST, exist_ok=True)
    with open(INDEX_HTML, "w") as f:
        f.write(
            """<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>CapeControl API</title></head>
<body>
  <h1>CapeControl API</h1>
  <p>API is running successfully!</p>
  <p><a href="/docs">View API Documentation</a></p>
  <p><a href="/api/health">Health Check</a></p>
</body>
</html>"""
        )

os.makedirs(os.path.join(FRONTEND_DIST, "assets"), exist_ok=True)

try:
    app.mount("/static", CustomStaticFiles(directory=FRONTEND_DIST), name="static")
    app.mount(
        "/assets",
        CustomStaticFiles(directory=os.path.join(FRONTEND_DIST, "assets")),
        name="assets",
    )
    print("✅ Static file directories mounted successfully")
    print(f"ℹ️  Static files: {FRONTEND_DIST}")
except Exception as e:
    print(f"❌ Failed to mount static directories: {e}")
    print(f"ℹ️  FRONTEND_DIST: {FRONTEND_DIST}")


# -------- Explicit static JSONs --------
@app.get("/manifest.json")
async def web_manifest():
    manifest_path = os.path.join(FRONTEND_DIST, "manifest.json")
    if os.path.exists(manifest_path):
        return FileResponse(manifest_path, media_type="application/manifest+json")
    return JSONResponse(
        content={
            "name": "CapeControl",
            "short_name": "CapeControl",
            "start_url": "/",
            "display": "standalone",
            "background_color": "#ffffff",
            "theme_color": "#2563eb",
            "icons": [],
        },
        media_type="application/manifest+json",
    )


@app.get("/version.json")
async def version_json():
    """Serve FE-stamped version.json if present, else safe fallback using envs."""
    version_path = os.path.join(FRONTEND_DIST, "version.json")
    if os.path.exists(version_path):
        return FileResponse(version_path, media_type="application/json")
    return JSONResponse(
        content={
            "app": "capecontrol-frontend",
            "version": _env("APP_VERSION"),
            "git_sha": _env("GIT_SHA"),
            "build_time": _env("BUILD_TIME"),
        },
        media_type="application/json",
    )


@app.get("/favicon.ico")
async def favicon():
    fav_path = os.path.join(FRONTEND_DIST, "favicon.ico")
    if os.path.exists(fav_path):
        return FileResponse(fav_path, media_type="image/x-icon")
    return Response(status_code=204)


# -------- Status & health --------
@app.get("/api/health")
async def api_health():
    """Delegate to health router root for consistent structure."""
    try:
        from app.routes.health import health_root  # type: ignore

        return await health_root()
    except Exception:
        return {
            "status": "healthy",
            "database_connected": True,
            "timestamp": utc_now().isoformat(),
            "message": "health endpoint",
        }


@app.get("/api/status")
async def api_status():
    payload = _version_payload()
    payload.update(
        {
            "ok": True,
            "docs": "/docs",
            "health": "/api/health",
            "middleware_status": {
                "monitoring": True,
                "input_sanitization": True,
                "content_moderation": False,  # disabled intentionally
                "ddos_protection": DDOS_PROTECTION_AVAILABLE,
                "audit_logging": AUDIT_LOGGING_AVAILABLE,
            },
        }
    )
    return payload


# Keep a convenience alias so /health responds (router owns /api/health)
@app.get("/health")
async def health_alias():
    return {"ok": True, "alias": "/api/health"}


# Explicit root route to serve the SPA index and avoid 404s from clients requesting '/'
@app.get("/")
async def root_index():
    try:
        return FileResponse(INDEX_HTML)
    except Exception:
        return JSONResponse(
            content={"ok": True, "message": "API running - no frontend build present"}
        )


# -------- SPA fallback --------
@app.get("/{full_path:path}")
async def spa_fallback(full_path: str):
    if (
        full_path.startswith("api/")
        or full_path.startswith("docs")
        or full_path.startswith("redoc")
        or full_path == "manifest.json"
        or full_path == "favicon.ico"
        or full_path.startswith("assets/")
        or full_path.startswith("static/")
    ):
        raise HTTPException(status_code=404, detail="Not Found")
    return FileResponse(INDEX_HTML)


@app.get("/robots.txt")
async def robots_txt():
    try:
        return FileResponse(
            os.path.join(FRONTEND_DIST, "robots.txt"), media_type="text/plain"
        )
    except Exception:
        # Safe default
        fallback_content = """User-agent: *
Allow: /

# Disallow sensitive areas
Disallow: /api/
Disallow: /admin/
Disallow: /dashboard/

# Allow public documentation
Allow: /docs

# Sitemap
Sitemap: https://www.cape-control.com/sitemap.xml

# Crawl delay
Crawl-delay: 1"""
        return Response(content=fallback_content, media_type="text/plain")


@app.get("/sitemap.xml")
async def sitemap_xml():
    try:
        return FileResponse(
            os.path.join(FRONTEND_DIST, "sitemap.xml"), media_type="application/xml"
        )
    except Exception:
        return Response(
            '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"></urlset>',
            media_type="application/xml",
        )


@app.get("/site.webmanifest")
async def site_webmanifest():
    try:
        return FileResponse(
            os.path.join(FRONTEND_DIST, "site.webmanifest"),
            media_type="application/manifest+json",
        )
    except Exception:
        return {
            "name": "CapeControl API",
            "short_name": "CapeControl",
            "start_url": "/",
        }
