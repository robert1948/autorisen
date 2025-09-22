from fastapi import FastAPI
import os

app = FastAPI(title="Autorisen API", version="0.0.1")

@app.get("/api/health")
def health():
    return {"status": "ok", "env": os.getenv("APP_ENV", "development")}
