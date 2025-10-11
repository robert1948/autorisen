from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.src.modules.health.router import router as health_router
from backend.src.modules.auth.router import router as auth_router

app = FastAPI(title="Autorisen API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", include_in_schema=False)
def read_root() -> JSONResponse:
    """Provide a friendly landing response for the root path."""
    payload = {
        "message": "Autorisen API root",
        "docs_url": "/docs",
        "health_url": "/api/health",
    }
    return JSONResponse(content=payload)


app.include_router(health_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
