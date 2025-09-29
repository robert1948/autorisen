from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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
app.include_router(health_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
