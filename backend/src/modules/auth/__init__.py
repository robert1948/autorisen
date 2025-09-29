"""Authentication module wiring schemas, services, and API router."""

from . import router, schemas, service  # noqa: F401

__all__ = ["router", "schemas", "service"]
