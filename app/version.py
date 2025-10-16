# backend/app/version.py
from dataclasses import dataclass
import os
from datetime import datetime, timezone

@dataclass(frozen=True)
class AppVersion:
    version: str
    git_sha: str
    build_time: str
    environment: str

def _env(name: str, default: str = "unknown") -> str:
    v = os.getenv(name, default).strip()
    return v if v else default

def get_app_version() -> AppVersion:
    return AppVersion(
        version=_env("APP_VERSION"),
        git_sha=_env("GIT_SHA"),
        build_time=_env("BUILD_TIME"),
        environment=_env("ENVIRONMENT"),
    )

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
