"""Manifest validation using JSON Schema."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from jsonschema import Draft7Validator

_SCHEMA_CACHE: Draft7Validator | None = None


def _schema_path() -> Path:
    return (
        Path(__file__).resolve().parents[4] / "docs" / "agents" / "manifest.schema.json"
    )


def _load_validator() -> Draft7Validator:
    global _SCHEMA_CACHE
    if _SCHEMA_CACHE is not None:
        return _SCHEMA_CACHE

    path = _schema_path()
    schema = json.loads(path.read_text(encoding="utf-8"))
    _SCHEMA_CACHE = Draft7Validator(schema)
    return _SCHEMA_CACHE


def validate_manifest(manifest: Dict[str, Any]) -> None:
    validator = _load_validator()
    errors: List[str] = []
    for error in sorted(validator.iter_errors(manifest), key=lambda err: err.path):
        location = ".".join([str(item) for item in error.path]) or "$"
        errors.append(f"{location}: {error.message}")

    if errors:
        raise ValueError("manifest invalid: " + "; ".join(errors))
