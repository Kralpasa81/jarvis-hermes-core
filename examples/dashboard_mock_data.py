#!/usr/bin/env python3
"""Generate public-safe mock dashboard cards for Jarvis / Hermes prototypes.

The output is synthetic and deterministic by default. It is intended for UI
layout experiments, documentation screenshots, and tests that should not depend
on real devices, private documents, API keys, home-network details, or live
service state.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class DashboardCard:
    """Represent a safe dashboard card with no private runtime data."""

    title: str
    category: str
    status: str
    priority: str
    message: str
    next_action: str


DEFAULT_CARDS = (
    DashboardCard(
        title="Assistant Gateway",
        category="communications",
        status="demo-ready",
        priority="normal",
        message="Command intake pattern is documented with approval boundaries.",
        next_action="Connect only through a private adapter that keeps tokens outside git.",
    ),
    DashboardCard(
        title="Document Workflow",
        category="documents",
        status="planned",
        priority="normal",
        message="OCR and checklist flows can be tested with sample-only filenames.",
        next_action="Add redaction checks before processing private files.",
    ),
    DashboardCard(
        title="Smart Home Layer",
        category="environment",
        status="approval-required",
        priority="high",
        message="Device control should never run from a public demo payload.",
        next_action="Keep real device identifiers in private configuration only.",
    ),
    DashboardCard(
        title="Knowledge Base",
        category="local-notes",
        status="private-adapter-needed",
        priority="high",
        message="Search results may contain personal context and must be sanitized.",
        next_action="Expose summaries only after a local privacy filter approves them.",
    ),
)


def build_payload(profile: str, cards: tuple[DashboardCard, ...]) -> dict[str, Any]:
    """Return a serializable dashboard mock payload."""

    return {
        "profile": profile,
        "data_source": "synthetic-example-only",
        "public_safe": True,
        "cards": [asdict(card) for card in cards],
        "safety_rules": [
            "Do not include tokens or API keys.",
            "Do not include exact home-network addresses or device credentials.",
            "Do not publish private document names, chat logs, or screenshots.",
            "Require approval before external posts, deletions, purchases, bookings, or device control.",
        ],
    }


def render_markdown(payload: dict[str, Any]) -> str:
    """Render dashboard cards as a compact Markdown table."""

    lines = [
        "# Jarvis / Hermes Dashboard Mock Data",
        "",
        f"Profile: `{payload['profile']}`",
        f"Data source: `{payload['data_source']}`",
        "",
        "| Card | Category | Status | Priority | Next action |",
        "| --- | --- | --- | --- | --- |",
    ]
    for card in payload["cards"]:
        lines.append(
            "| {title} | `{category}` | `{status}` | `{priority}` | {next_action} |".format(
                **card
            )
        )
    lines.extend(["", "## Safety rules"])
    lines.extend(f"- {rule}" for rule in payload["safety_rules"])
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Print synthetic Jarvis/Hermes dashboard cards for public-safe prototypes."
    )
    parser.add_argument(
        "--profile",
        default="public-demo",
        help="Non-sensitive label to include in the mock payload.",
    )
    parser.add_argument(
        "--format",
        choices=("json", "markdown"),
        default="json",
        help="Output format.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = build_payload(args.profile, DEFAULT_CARDS)
    if args.format == "markdown":
        print(render_markdown(payload))
    else:
        print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
