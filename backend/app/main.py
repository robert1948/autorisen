from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import FileResponse, Response, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# Import only EXISTING middleware
from app.middleware.input_sanitization import InputSanitizationMiddleware
from app.middleware.content_moderation import ContentModerationMiddleware
from app.middleware.monitoring import MonitoringMiddleware, set_monitoring_middleware_instance
import os

from app.routes import cape_ai, audit, monitoring, error_tracking, dashboard
from app.routes.health import router as health_router
from app.routes.alerts import router as alerts_router
from app.routes.ai_performance import router as ai_performance_router
from app.routes.ai_context import router as ai_context_router
from app.routes.ai_personalization import router as ai_personalization_router
from app.routes import auth_v2
from app.routes import auth_enhanced
from app.routes.password_reset import router as password_reset_router
from app.routes.developer_earnings import router as developer_earnings_router
from app.routes.analytics import router as analytics_router
from app.api.payment import router as payment_router
from app.routes.stripe_routes_simple import router as stripe_router
from app.payfast.routes import router as payfast_router
from fastapi import FastAPI
from app.routes import payfast  # add this

app = FastAPI()
app.include_router(payfast.router)  # add this


# Optional routes with graceful fallbacks
try:
    from app.routes.usage_analytics import router as usage_analytics_router
    USAGE_ANALYTICS_AVAILABLE = True
except ImportError:
    USAGE_ANALYTICS_AVAILABLE = False
    print("⚠️  Usage Analytics routes not available - Task 2.2.5 not deployed")

try:
    from app.routes.preference_management import router as preference_management_router
    PREFERENCE_MANAGEMENT_AVAILABLE = True
except ImportError:
    PREFERENCE_MANAGEMENT_AVAILABLE = False
    print("⚠️  Preference Management routes not available - Task 2.2.6 not deployed")

# Optional middleware with graceful fallbacks
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

app = FastAPI(
    title="CapeControl API",
    description="Secure, scalable authentication system for CapeControl with AI capabilities",
    version="3.0.0"
)

# Include routers
app.include_router(auth_v2.router, prefix="/api/auth", tags=["auth"])
app.include_router(auth_enhanced.router, prefix="/api/enhanced", tags=["auth-enhanced"])
app.include_router(auth_v2.router, prefix="/api/user", tags=["user"])  # Add user routes using auth router
app.include_router(password_reset_router, tags=["password-reset"])
app.include_router(developer_earnings_router, tags=["developer-earnings"])
app.include_router(analytics_router, prefix="/api/analytics", tags=["analytics"])  # Performance Analytics Dashboard
app.include_router(payment_router, prefix="", tags=["payment"])  # No extra prefix as router already has /api/payment
app.include_router(stripe_router, prefix="/api/stripe", tags=["stripe"])  # Stripe payment integration
app.include_router(payfast_router)  # router already has prefix "/api/payfast" and tags
app.include_router(cape_ai.router, prefix="/api/cape_ai", tags=["cape-ai"])
app.include_router(audit.router, prefix="/api/audit", tags=["audit"])
app.include_router(monitoring.router, prefix="/api/monitoring", tags=["monitoring"])
app.include_router(error_tracking.router, prefix="/api/error_tracking", tags=["error-tracking"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])
app.include_router(health_router, prefix="/api/health", tags=["health"])
app.include_router(alerts_router, prefix="/api/alerts", tags=["alerts"])
app.include_router(ai_performance_router, prefix="/api/ai_performance", tags=["ai-performance"])
app.include_router(ai_context_router, prefix="/api/ai_context", tags=["ai-context"])
app.include_router(ai_personalization_router, prefix="/api/ai_personalization", tags=["ai-personalization"])

if USAGE_ANALYTICS_AVAILABLE:
    app.include_router(usage_analytics_router, prefix="/api/v1/analytics", tags=["usage-analytics"])
    print("✅ Usage Analytics routes enabled (Task 2.2.5)")

if PREFERENCE_MANAGEMENT_AVAILABLE:
    app.include_router(preference_management_router, prefix="/api/v1/preferences", tags=["preferences"])
    print("✅ Preference Management routes enabled (Task 2.2.6)")

# Initialize monitoring middleware (REQUIRED)
monitoring_middleware = MonitoringMiddleware(app)
set_monitoring_middleware_instance(monitoring_middleware)

# Add middleware in correct order (reverse order of execution)
# CORS should be last (executed first)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add REQUIRED middleware
# Temporarily disable ContentModerationMiddleware to fix timeout issues
# try:
#     app.add_middleware(ContentModerationMiddleware, strict_mode=False)
#     print("✅ ContentModerationMiddleware added successfully")
# except Exception as e:
#     print(f"❌ Failed to add ContentModerationMiddleware: {e}")
print("⚠️  ContentModerationMiddleware temporarily disabled")

try:
    app.add_middleware(InputSanitizationMiddleware, max_content_length=10*1024*1024)
    print("✅ InputSanitizationMiddleware added successfully")
except Exception as e:
    print(f"❌ Failed to add InputSanitizationMiddleware: {e}")

# Add OPTIONAL middleware only if available
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

# Static files configuration with Heroku-compatible fallbacks
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIST = os.path.join(BASE_DIR, "static")
INDEX_HTML = os.path.join(FRONTEND_DIST, "index.html")

# Add a StaticFiles subclass to control cache headers
class CustomStaticFiles(StaticFiles):
    async def get_response(self, path, scope):
        response = await super().get_response(path, scope)
        try:
            # Never cache index.html (prevents mismatched chunk hashes)
            if path == "index.html" or path == "":
                response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
            # Aggressively cache versioned assets (immutable)
            elif path.startswith("assets/") and (path.endswith(".js") or path.endswith(".css") or path.endswith(".svg") or path.endswith(".png") or path.endswith(".jpg") or path.endswith(".woff2")):
                response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
            else:
                # Default sane caching for other static files
                response.headers.setdefault("Cache-Control", "public, max-age=3600")
        except Exception:
            pass
        return response

# Create missing static files for Heroku deployment
if not os.path.exists(INDEX_HTML):
    print(f"⚠️  Frontend build not found: {INDEX_HTML}")
    print("ℹ️  Creating minimal index.html for Heroku deployment")
    os.makedirs(FRONTEND_DIST, exist_ok=True)
    with open(INDEX_HTML, 'w') as f:
        f.write("""<!DOCTYPE html>
<html lang=\"en\">
<head>
    <meta charset=\"UTF-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
    <title>CapeControl API</title>
</head>
<body>
    <h1>CapeControl API</h1>
    <p>API is running successfully!</p>
    <p><a href=\"/docs\">View API Documentation</a></p>
    <p><a href=\"/health\">Health Check</a></p>
</body>
</html>""")

# Ensure static directories exist
os.makedirs(os.path.join(FRONTEND_DIST, "assets"), exist_ok=True)

# Mount static files with proper asset serving
try:
    # Mount the main static directory for all files
    app.mount("/static", CustomStaticFiles(directory=FRONTEND_DIST), name="static")
    # Mount assets directory specifically for frontend assets
    app.mount("/assets", CustomStaticFiles(directory=os.path.join(FRONTEND_DIST, "assets")), name="assets")
    print("✅ Static file directories mounted successfully")
    print(f"ℹ️  Static files: {FRONTEND_DIST}")
    print(f"ℹ️  Assets directory: {os.path.join(FRONTEND_DIST, 'assets')}")
except Exception as e:
    print(f"❌ Failed to mount static directories: {e}")
    print(f"ℹ️  FRONTEND_DIST: {FRONTEND_DIST}")

# Serve Web App Manifest explicitly to avoid SPA fallback catching it
@app.get("/manifest.json")
async def web_manifest():
    manifest_path = os.path.join(FRONTEND_DIST, "manifest.json")
    if os.path.exists(manifest_path):
        try:
            return FileResponse(manifest_path, media_type="application/manifest+json")
        except Exception:
            pass
    # Minimal valid PWA manifest fallback
    return JSONResponse(
        content={
            "name": "CapeControl",
            "short_name": "CapeControl",
            "start_url": "/",
            "display": "standalone",
            "background_color": "#ffffff",
            "theme_color": "#2563eb",
            "icons": []
        },
        media_type="application/manifest+json"
    )

@app.get("/favicon.ico")
async def favicon():
    fav_path = os.path.join(FRONTEND_DIST, "favicon.ico")
    if os.path.exists(fav_path):
        return FileResponse(fav_path, media_type="image/x-icon")
    # 204 if not present
    return Response(status_code=204)

# SPA fallback: serve index.html for non-API routes (fixes hard refresh and deep links)
@app.get("/{full_path:path}")
async def spa_fallback(full_path: str):
    if (
        full_path.startswith("api/") or
        full_path.startswith("docs") or
        full_path.startswith("redoc") or
        full_path == "manifest.json" or
        full_path == "favicon.ico" or
        full_path.startswith("assets/") or
        full_path.startswith("static/")
    ):
        raise HTTPException(status_code=404, detail="Not Found")
    return FileResponse(INDEX_HTML)

@app.get("/robots.txt")
async def robots_txt():
    try:
        return FileResponse(os.path.join(FRONTEND_DIST, "robots.txt"), media_type="text/plain")
    except:
        # Fallback robots.txt content for production safety
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
        return FileResponse(os.path.join(FRONTEND_DIST, "sitemap.xml"), media_type="application/xml")
    except:
        return '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"></urlset>'

@app.get("/site.webmanifest")
async def site_webmanifest():
    try:
        return FileResponse(os.path.join(FRONTEND_DIST, "site.webmanifest"), media_type="application/manifest+json")
    except:
        return {"name": "CapeControl API", "short_name": "CapeControl", "start_url": "/"}

@app.get("/apple-touch-icon.png")
async def apple_touch_icon():
    try:
        return FileResponse(os.path.join(FRONTEND_DIST, "apple-touch-icon.png"), media_type="image/png")
    except:
        return Response("", media_type="image/png")

# DISABLED: S3 proxy route - now serving assets locally via StaticFiles mount
# @app.get("/assets/{asset_path:path}")
# async def proxy_s3_assets(asset_path: str):
#     # S3 proxy logic disabled in favor of local static file serving
#     pass

@app.get("/api/status")
async def api_status():
    return {
        "message": "CapeControl API is running successfully!",
        "version": "3.0.0",
        "docs": "/docs",
        "health": "/health",
        "middleware_status": {
            "monitoring": True,
            "input_sanitization": True,
            "content_moderation": True,
            "ddos_protection": DDOS_PROTECTION_AVAILABLE,
            "audit_logging": AUDIT_LOGGING_AVAILABLE
        },
        "routes_status": {
            "usage_analytics": USAGE_ANALYTICS_AVAILABLE,
            "preference_management": PREFERENCE_MANAGEMENT_AVAILABLE
        }
    }

@app.get("/")
async def serve_react_app():
    return FileResponse(INDEX_HTML)
