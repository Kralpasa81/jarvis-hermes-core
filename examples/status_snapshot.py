#!/usr/bin/env python3
"""Generate a public-safe mock Jarvis / Hermes status snapshot.

This script intentionally uses fake/example data only. It is useful for
front-end dashboard experiments without exposing real devices, tokens,
home-network details, or personal documents.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone

DEFAULT_MODULES = [
    {"name": "telegram_gateway", "status": "ready", "risk": "low"},
    {"name": "weather_briefing", "status": "scheduled", "risk": "low"},
    {"name": "document_workflows", "status": "planned", "risk": "approval-required"},
    {"name": "smart_home", "status": "planned", "risk": "approval-required"},
    {"name": "local_knowledge", "status": "planned", "risk": "private-data"},
]


def build_snapshot(profile: str, modules: list[dict[str, str]]) -> dict[str, object]:
    """Return a safe mock snapshot for dashboard prototypes."""
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "profile": profile,
        "assistant": {
            "name": "Jarvis / Hermes Core",
            "mode": "demo",
            "status": "online",
        },
        "modules": modules,
        "rules": [
            "No tokens in public repos",
            "No real home-network details in examples",
            "Approval required for posting, buying, deleting, booking, or device control",
        ],
        "safety": {
            "public_safe": True,
            "contains_real_devices": False,
            "contains_secrets": False,
            "data_source": "example-only",
        },
    }


def parse_module(value: str) -> dict[str, str]:
    """Parse NAME:STATUS:RISK into a module dictionary."""
    parts = value.split(":")
    if len(parts) != 3 or not all(parts):
        raise argparse.ArgumentTypeError("module must use NAME:STATUS:RISK format")
    name, status, risk = parts
    return {"name": name, "status": status, "risk": risk}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a public-safe example status JSON for Jarvis/Hermes dashboards."
    )
    parser.add_argument(
        "--profile",
        default="public-demo",
        help="Non-sensitive label for the generated snapshot.",
    )
    parser.add_argument(
        "--module",
        action="append",
        type=parse_module,
        default=[],
        help="Add a module as NAME:STATUS:RISK. Can be passed multiple times.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    modules = args.module or DEFAULT_MODULES
    print(json.dumps(build_snapshot(args.profile, modules), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
