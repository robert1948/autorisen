from fastapi import FastAPI
import os

app = FastAPI(title="Autorisen API", version="0.0.1")


@app.get("/api/health")
def health():
    return {"status": "ok", "env": os.getenv("APP_ENV", "development")}


@app.get("/alive")
def alive():
    """Lightweight health endpoint used by CI smoke tests."""
    return {"alive": True}


@app.get("/")
def root():
    """Simple root route so platform-level health checks (/) return 200."""
    return {"ok": True}
