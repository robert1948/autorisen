"""Authentication module wiring schemas, services, dependencies, and API router."""

from . import deps, router, schemas, service  # noqa: F401

__all__ = ["router", "schemas", "service", "deps"]
