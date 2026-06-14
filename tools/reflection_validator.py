"""Reflection validator — перевірка артефакту рефлексії за JSON Schema."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

SCHEMA_DIR = Path(__file__).resolve().parent.parent / "schemas"


def load_schema(name: str) -> dict[str, Any]:
    schema: dict[str, Any] = json.loads((SCHEMA_DIR / name).read_text(encoding="utf-8"))
    return schema


def _validate(obj: dict[str, Any], schema_name: str) -> list[str]:
    validator = Draft202012Validator(load_schema(schema_name))
    errors = sorted(validator.iter_errors(obj), key=lambda e: list(e.path))
    return [f"{'/'.join(map(str, e.path)) or '<root>'}: {e.message}" for e in errors]


def validate_reflection(obj: dict[str, Any]) -> list[str]:
    """Повертає список помилок; порожній список = валідно."""
    return _validate(obj, "reflection.schema.json")


def validate_intent(obj: dict[str, Any]) -> list[str]:
    return _validate(obj, "intent.schema.json")


def validate_inference_trace(obj: dict[str, Any]) -> list[str]:
    return _validate(obj, "inference_trace.schema.json")
