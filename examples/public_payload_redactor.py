#!/usr/bin/env python3
"""Redact risky fields from a public-demo Jarvis / Hermes JSON payload.

This example is intentionally offline and dependency-free. It does not inspect
private files unless the user explicitly passes a JSON input path, and it never
calls external services. It is meant for synthetic demo payloads before they are
copied into public docs, screenshots, dashboard mockups, or README examples.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REDACTION = "<redacted-for-public-demo>"
RISKY_KEY_PARTS = (
    "api_key",
    "apikey",
    "auth",
    "authorization",
    "bearer",
    "chat_id",
    "client_secret",
    "credential",
    "device_id",
    "email",
    "home_ip",
    "host",
    "ip_address",
    "latitude",
    "local_url",
    "longitude",
    "oauth",
    "password",
    "payment",
    "phone",
    "private_url",
    "refresh_token",
    "secret",
    "session",
    "token",
    "webhook",
)


@dataclass(frozen=True)
class RedactionReport:
    """Summary of fields changed during redaction."""

    redacted_paths: list[str]
    unchanged_leaf_count: int


def default_payload() -> dict[str, Any]:
    """Return a synthetic payload containing safe and intentionally risky sample keys."""

    return {
        "module": "dashboard",
        "status": "preview",
        "summary": "Synthetic assistant dashboard payload for documentation.",
        "safe_cards": [
            {"name": "weather", "state": "placeholder", "visible": True},
            {"name": "documents", "state": "queue-demo", "visible": True},
        ],
        "private_adapter_example": {
            "api_key": "placeholder_value",
            "webhook_url": "https://example.invalid/webhook-placeholder",
            "device_id": "placeholder_value",
            "chat_id": "placeholder_value",
        },
    }


def risky_key(key: str) -> bool:
    """Return True when a JSON key name is unsafe for public demo output."""

    normalized = key.lower().replace("-", "_").replace(" ", "_")
    return any(part in normalized for part in RISKY_KEY_PARTS)


def redact_payload(value: Any, path: str = "$") -> tuple[Any, RedactionReport]:
    """Recursively redact risky-key values while preserving public-safe structure."""

    redacted_paths: list[str] = []
    unchanged_leaf_count = 0

    if isinstance(value, dict):
        clean: dict[str, Any] = {}
        for key, item in value.items():
            child_path = f"{path}.{key}"
            if risky_key(str(key)):
                clean[key] = REDACTION
                redacted_paths.append(child_path)
                continue
            child_value, child_report = redact_payload(item, child_path)
            clean[key] = child_value
            redacted_paths.extend(child_report.redacted_paths)
            unchanged_leaf_count += child_report.unchanged_leaf_count
        return clean, RedactionReport(redacted_paths, unchanged_leaf_count)

    if isinstance(value, list):
        clean_list: list[Any] = []
        for index, item in enumerate(value):
            child_value, child_report = redact_payload(item, f"{path}[{index}]")
            clean_list.append(child_value)
            redacted_paths.extend(child_report.redacted_paths)
            unchanged_leaf_count += child_report.unchanged_leaf_count
        return clean_list, RedactionReport(redacted_paths, unchanged_leaf_count)

    return value, RedactionReport(redacted_paths, 1)


def load_payload(input_path: str | None) -> Any:
    """Load JSON from a path, or return the built-in synthetic demo payload."""

    if input_path is None:
        return default_payload()

    path = Path(input_path)
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def render_markdown(clean_payload: Any, report: RedactionReport) -> str:
    """Render a redaction result as a short Markdown report."""

    redacted = report.redacted_paths or ["none"]
    lines = [
        "# Jarvis / Hermes Public Payload Redaction Preview",
        "",
        f"- **Redacted fields:** `{len(report.redacted_paths)}`",
        f"- **Unchanged leaf values:** `{report.unchanged_leaf_count}`",
        "- **Reminder:** review output manually before publishing docs or screenshots.",
        "",
        "## Redacted paths",
    ]
    lines.extend(f"- `{path}`" for path in redacted)
    lines.extend(
        [
            "",
            "## Clean payload",
            "",
            "```json",
            json.dumps(clean_payload, indent=2, sort_keys=True),
            "```",
        ]
    )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Redact risky key names from a public-demo Jarvis/Hermes JSON payload."
    )
    parser.add_argument(
        "--input",
        help="Optional path to a JSON payload. If omitted, a synthetic demo payload is used.",
    )
    parser.add_argument(
        "--format",
        choices=("json", "markdown"),
        default="markdown",
        help="Output format.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = load_payload(args.input)
    clean_payload, report = redact_payload(payload)

    if args.format == "json":
        print(
            json.dumps(
                {
                    "redacted_paths": report.redacted_paths,
                    "unchanged_leaf_count": report.unchanged_leaf_count,
                    "payload": clean_payload,
                },
                indent=2,
                sort_keys=True,
            )
        )
    else:
        print(render_markdown(clean_payload, report))


if __name__ == "__main__":
    main()
