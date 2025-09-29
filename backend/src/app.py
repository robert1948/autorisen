"""Application entrypoint wiring routers, middleware, and root handler."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from backend.src.modules.auth.router import router as auth_router
from backend.src.modules.health.router import router as health_router

app = FastAPI(title="Autorisen API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="/api")
app.include_router(auth_router, prefix="/api")


@app.get("/")
def root() -> dict[str, str]:
    """Basic root endpoint for uptime checks."""
    return {"hello": "world"}


@app.get("/favicon.ico", include_in_schema=False)
def favicon() -> RedirectResponse:
    """Redirect browsers and monitors to the canonical favicon."""
    return RedirectResponse(
        "https://lightning-s3.s3.us-east-1.amazonaws.com/static/admin/img/favicon.ico",
        status_code=307,
    )
