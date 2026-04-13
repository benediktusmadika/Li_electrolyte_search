from __future__ import annotations

from typing import Any, Dict

from jsonschema import Draft202012Validator


def assert_matches_schema(payload: Dict[str, Any], schema: Dict[str, Any]) -> None:
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(payload), key=lambda e: e.path)
    if errors:
        messages = []
        for error in errors[:20]:
            path = "/".join(str(part) for part in error.absolute_path)
            messages.append(f"{path or '<root>'}: {error.message}")
        raise ValueError("Schema validation failed: " + " | ".join(messages))