"""Common typing helpers shared by dynamic AI providers."""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class Provider(Protocol):
    """Lightweight contract for registry-compatible providers.

    Implementations only need to expose a stable ``name`` attribute so they can
    be addressed in the registry. Optional ``register_routes`` lets providers
    attach their FastAPI routes without forcing an import-cycle dependency on
    FastAPI inside this base module. Additional methods can be implemented as
    needed by concrete providers – typing remains structural.
    """

    name: str

    def register_routes(self, router: Any) -> None:  # pragma: no cover - interface hook
        """Attach provider-specific routes to the supplied router."""
        ...
