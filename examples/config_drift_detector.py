#!/usr/bin/env python3
"""Compare two public-safe config *schemas* and report structural drift.

This is the module proposed in the 2026-07-12 daily note. It never compares
real configuration values -- only key names and value *types* -- so it is
safe to run against synthetic examples in a public repository. The intended
real-world use is comparing something like `config/dev.yaml` vs
`config/prod.yaml` structure without ever reading actual secrets, hostnames,
or device data (those files stay private and outside this repo).

Drift categories:
  - missing_in_b   : key exists in schema A but not in schema B
  - missing_in_a   : key exists in schema B but not in schema A
  - type_mismatch  : key exists in both but the value type differs

No external dependencies. No network calls. No file writes (stdout only).
Rejects any key name containing ".." or a path separator to avoid being
pointed at unintended files by a crafted schema.

Usage:
  python3 examples/config_drift_detector.py                     # built-in demo
  python3 examples/config_drift_detector.py a.json b.json       # custom files
  python3 examples/config_drift_detector.py --format json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

UNSAFE_KEY_MARKERS = ("..", "/", "\\")

# ---------------------------------------------------------------------------
# Built-in demo schemas (structure only -- no real values)
# ---------------------------------------------------------------------------
DEMO_SCHEMA_A: dict[str, Any] = {
    "assistant_name": "string",
    "environment": "string",
    "modules": {
        "status_dashboard": {"enabled": "bool", "risk_level": "string"},
        "document_workflow": {"enabled": "bool", "risk_level": "string"},
    },
    "safety": {
        "allow_sensitive_values": "bool",
        "public_safe": "bool",
    },
}

DEMO_SCHEMA_B: dict[str, Any] = {
    "assistant_name": "string",
    "environment": "string",
    "modules": {
        "status_dashboard": {"enabled": "bool", "risk_level": "string"},
        "document_workflow": {"enabled": "string", "risk_level": "string"},
        "local_knowledge": {"enabled": "bool", "risk_level": "string"},
    },
    "safety": {
        "allow_sensitive_values": "bool",
    },
}


class DriftError(ValueError):
    """Raised when a schema file cannot be safely loaded or parsed."""


def _reject_unsafe_keys(node: Any, location: str = "root") -> None:
    """Recursively refuse key names that look like path traversal attempts."""
    if isinstance(node, dict):
        for key, value in node.items():
            key_str = str(key)
            if any(marker in key_str for marker in UNSAFE_KEY_MARKERS):
                raise DriftError(f"{location}.{key_str}: unsafe key name rejected")
            _reject_unsafe_keys(value, f"{location}.{key_str}")


def load_schema(path: Path | None, demo: dict[str, Any]) -> dict[str, Any]:
    if path is None:
        return demo
    if not path.is_file():
        raise DriftError(f"schema file not found: {path}")
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise DriftError(f"{path}: top-level schema must be a JSON object")
    _reject_unsafe_keys(data)
    return data


def _type_label(value: Any) -> str:
    """Return a schema-style type label for a raw JSON value, if needed."""
    if isinstance(value, str):
        return value  # schemas already store type labels as strings
    if isinstance(value, bool):
        return "bool"
    if isinstance(value, (int, float)):
        return "number"
    if isinstance(value, dict):
        return "object"
    if isinstance(value, list):
        return "list"
    return "null"


def diff_schemas(a: dict[str, Any], b: dict[str, Any], prefix: str = "") -> list[dict[str, str]]:
    """Walk both schemas and collect drift entries."""
    drift: list[dict[str, str]] = []
    keys = sorted(set(a.keys()) | set(b.keys()))

    for key in keys:
        path = f"{prefix}.{key}" if prefix else key
        in_a = key in a
        in_b = key in b

        if in_a and not in_b:
            drift.append({"path": path, "kind": "missing_in_b", "detail": _type_label(a[key])})
            continue
        if in_b and not in_a:
            drift.append({"path": path, "kind": "missing_in_a", "detail": _type_label(b[key])})
            continue

        val_a, val_b = a[key], b[key]
        if isinstance(val_a, dict) and isinstance(val_b, dict):
            drift.extend(diff_schemas(val_a, val_b, path))
        else:
            type_a, type_b = _type_label(val_a), _type_label(val_b)
            if type_a != type_b:
                drift.append(
                    {"path": path, "kind": "type_mismatch", "detail": f"{type_a} vs {type_b}"}
                )

    return drift


def to_markdown(drift: list[dict[str, str]], label_a: str, label_b: str) -> str:
    lines = [
        "# Config Drift Report",
        "",
        f"Comparing schema structure only: `{label_a}` vs `{label_b}`.",
        "No real values are read or displayed -- only key names and types.",
        "",
    ]
    if not drift:
        lines.append("No structural drift detected. Schemas match.")
        return "\n".join(lines)

    lines += ["| Path | Kind | Detail |", "| --- | --- | --- |"]
    icon = {"missing_in_b": "➖", "missing_in_a": "➕", "type_mismatch": "⚠️"}
    for item in drift:
        lines.append(
            f"| `{item['path']}` | {icon.get(item['kind'], '')} {item['kind']} | {item['detail']} |"
        )
    lines.append("")
    lines.append(f"Total drift entries: {len(drift)}")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compare two public-safe config schemas and report structural drift."
    )
    parser.add_argument("schema_a", nargs="?", type=Path, help="Path to schema A JSON (optional)")
    parser.add_argument("schema_b", nargs="?", type=Path, help="Path to schema B JSON (optional)")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        schema_a = load_schema(args.schema_a, DEMO_SCHEMA_A)
        schema_b = load_schema(args.schema_b, DEMO_SCHEMA_B)
    except (OSError, json.JSONDecodeError, DriftError) as exc:
        print(f"drift_error: {exc}", file=sys.stderr)
        return 2

    drift = diff_schemas(schema_a, schema_b)
    label_a = str(args.schema_a) if args.schema_a else "demo-schema-a"
    label_b = str(args.schema_b) if args.schema_b else "demo-schema-b"

    if args.format == "json":
        print(json.dumps({"a": label_a, "b": label_b, "drift": drift}, indent=2))
    else:
        print(to_markdown(drift, label_a, label_b))

    return 1 if drift else 0


if __name__ == "__main__":
    raise SystemExit(main())
