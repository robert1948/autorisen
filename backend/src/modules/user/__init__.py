"""User module init."""

from .router import router
from . import schemas, service

__all__ = ["router", "schemas", "service"]
