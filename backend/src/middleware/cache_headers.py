from starlette.types import ASGIApp, Scope, Receive, Send, Message
from starlette.datastructures import MutableHeaders

EXPECTED_ROUTES = {
    "/login",
    "/register",
    "/dashboard",
    "/agents",
    "/settings",
    "/chat",
    "/marketplace",
}


class CacheHeadersMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        async def send_wrapper(message: Message) -> None:
            if message["type"] == "http.response.start":
                headers = MutableHeaders(scope=message)
                path = scope.get("path", "")

                # Force clear any existing cache headers first
                if "cache-control" in headers:
                    del headers["cache-control"]
                if "pragma" in headers:
                    del headers["pragma"]

                # Apply our cache-correctness rules
                # 1. Immutable, long cache for hashed assets from Vite
                if path.startswith("/assets/") and any(
                    path.endswith(ext)
                    for ext in (
                        ".js",
                        ".css",
                        ".png",
                        ".jpg",
                        ".jpeg",
                        ".svg",
                        ".webp",
                        ".woff",
                        ".woff2",
                        ".ttf",
                        ".map",
                        ".ico",
                    )
                ):
                    headers["Cache-Control"] = "public, max-age=31536000, immutable"

                # 2. Specific files that should cache for a long time
                elif path in ["/favicon.ico", "/site.webmanifest", "/robots.txt"]:
                    headers["Cache-Control"] = "public, max-age=31536000"

                # 3. Never cache HTML shells or config - always revalidate for new builds
                elif (
                    path == "/"
                    or path.endswith(".html")
                    or path in EXPECTED_ROUTES
                    or path == "/config.json"
                ):
                    headers["Cache-Control"] = "no-cache, must-revalidate"
                    headers["Pragma"] = "no-cache"
                    headers["Expires"] = "0"

                # 4. API endpoints should not be cached by default
                elif path.startswith("/api/"):
                    headers["Cache-Control"] = "no-store"

                # 5. Everything else gets short cache with revalidation
                else:
                    headers["Cache-Control"] = "public, max-age=300, must-revalidate"

            await send(message)

        await self.app(scope, receive, send_wrapper)
