#!/usr/bin/env python3
"""Generate a public-safe mock Jarvis / Hermes status snapshot.

This script intentionally uses fake/example data only. It is useful for
front-end dashboard experiments without exposing real devices, tokens,
home-network details, or personal documents.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone


def build_snapshot() -> dict:
    """Return a safe mock snapshot for dashboard prototypes."""
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "assistant": {
            "name": "Jarvis / Hermes Core",
            "mode": "demo",
            "status": "online",
        },
        "modules": [
            {"name": "telegram_gateway", "status": "ready", "risk": "low"},
            {"name": "weather_briefing", "status": "scheduled", "risk": "low"},
            {"name": "document_workflows", "status": "planned", "risk": "approval-required"},
            {"name": "smart_home", "status": "planned", "risk": "approval-required"},
            {"name": "local_knowledge", "status": "planned", "risk": "private-data"},
        ],
        "rules": [
            "No tokens in public repos",
            "No real home-network details in examples",
            "Approval required for posting, buying, deleting, booking, or device control",
        ],
    }


def main() -> None:
    print(json.dumps(build_snapshot(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
