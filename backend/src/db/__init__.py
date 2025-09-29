"""Database package wiring base and models."""

from .base import Base  # noqa: F401
from . import models  # noqa: F401

__all__ = ["Base", "models"]
