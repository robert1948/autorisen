from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from backend.src.modules.agents.router import router as agents_router
from backend.src.modules.auth.router import router as auth_router
from backend.src.modules.chatkit.router import router as chatkit_router
from backend.src.modules.flows.router import router as flows_router
from backend.src.modules.health.router import router as health_router
from backend.src.modules.marketplace.router import router as marketplace_router

CLIENT_DIST = Path(__file__).resolve().parents[2] / "client" / "dist"

app = FastAPI(title="Autorisen API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if CLIENT_DIST.exists():
    assets_path = CLIENT_DIST / "assets"
    if assets_path.exists():
        app.mount("/assets", StaticFiles(directory=assets_path), name="assets")
    app.mount("/client-static", StaticFiles(directory=CLIENT_DIST), name="client-static")


@app.get("/", include_in_schema=False)
def read_root():
    """Serve the SPA landing page if built; otherwise return JSON hint."""
    if CLIENT_DIST.exists():
        index_file = CLIENT_DIST / "index.html"
        if index_file.exists():
            return FileResponse(index_file)
    return JSONResponse(
        content={
            "message": "Autorisen API root",
            "docs_url": "/docs",
            "health_url": "/api/health",
        }
    )


app.include_router(health_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(chatkit_router, prefix="/api")
app.include_router(flows_router, prefix="/api")
app.include_router(agents_router, prefix="/api")
app.include_router(marketplace_router, prefix="/api")


@app.get("/{full_path:path}", include_in_schema=False)
def spa_fallback(full_path: str):
    """Fallback to index.html for client-side routes (excluding API paths)."""
    if full_path.startswith("api/"):
        raise HTTPException(status_code=404, detail="Not Found")
    if CLIENT_DIST.exists():
        index_file = CLIENT_DIST / "index.html"
        if index_file.exists():
            return FileResponse(index_file)
    raise HTTPException(status_code=404, detail="Not Found")
