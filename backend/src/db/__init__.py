"""Database package wiring base and models."""

from . import models  # noqa: F401
from .base import Base  # noqa: F401

__all__ = ["Base", "models"]
