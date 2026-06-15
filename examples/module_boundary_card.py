#!/usr/bin/env python3
"""Generate a public-safe boundary card for a Jarvis / Hermes module.

This example is intentionally offline and dependency-free. It does not read local
configuration, inspect devices, call APIs, publish messages, or require secrets.
Use it to describe what a module may safely accept, what it must block, and which
approval rule should apply before a real private integration is attached.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class BoundaryCard:
    """Public-safe safety boundary for one generic module type."""

    module: str
    purpose: str
    allowed_public_inputs: tuple[str, ...]
    blocked_private_data: tuple[str, ...]
    default_approval: str
    safe_preview: str


CARDS: dict[str, BoundaryCard] = {
    "dashboard": BoundaryCard(
        module="dashboard",
        purpose="Display synthetic or redacted status cards for planning a Jarvis-style HUD.",
        allowed_public_inputs=(
            "mock status labels",
            "sample timestamps",
            "non-sensitive health states",
        ),
        blocked_private_data=(
            "live account identifiers",
            "exact device names",
            "private network addresses",
        ),
        default_approval="allow_read_only_preview",
        safe_preview="Render mock cards only; do not connect to live services.",
    ),
    "documents": BoundaryCard(
        module="documents",
        purpose="Plan OCR or document helper flows without exposing real files.",
        allowed_public_inputs=(
            "generic document type",
            "synthetic checklist step",
            "redacted field name",
        ),
        blocked_private_data=(
            "personal document content",
            "government or payment identifiers",
            "private file paths",
        ),
        default_approval="allow_template_only",
        safe_preview="Show a checklist using placeholder document names.",
    ),
    "notifications": BoundaryCard(
        module="notifications",
        purpose="Describe assistant reminders and alerts before connecting messaging channels.",
        allowed_public_inputs=(
            "sample reminder title",
            "generic recipient class",
            "non-sensitive urgency label",
        ),
        blocked_private_data=(
            "real chat IDs",
            "webhook URLs",
            "private message history",
        ),
        default_approval="allow_with_rate_limit",
        safe_preview="Print a draft notification without sending it.",
    ),
    "smart_home": BoundaryCard(
        module="smart_home",
        purpose="Plan safe smart-home status and control boundaries without touching devices.",
        allowed_public_inputs=(
            "generic room label",
            "synthetic device category",
            "mock on/off state",
        ),
        blocked_private_data=(
            "device credentials",
            "precise home layout",
            "local hub addresses",
        ),
        default_approval="require_confirmation_for_control",
        safe_preview="Show intended action and fallback note; never execute control from this example.",
    ),
    "media": BoundaryCard(
        module="media",
        purpose="Sketch media workflow helpers with public-safe placeholder content.",
        allowed_public_inputs=(
            "sample title idea",
            "synthetic publishing checklist",
            "generic content category",
        ),
        blocked_private_data=(
            "account tokens",
            "unpublished private drafts",
            "creator analytics exports",
        ),
        default_approval="require_approval_before_publish",
        safe_preview="Render a planning checklist only; do not upload or publish anything.",
    ),
}


def build_card(module: str) -> dict[str, Any]:
    """Return a serializable boundary card for a generic module."""

    return asdict(CARDS[module])


def render_markdown(card: dict[str, Any]) -> str:
    """Render a boundary card as Markdown."""

    allowed = "\n".join(f"  - {item}" for item in card["allowed_public_inputs"])
    blocked = "\n".join(f"  - {item}" for item in card["blocked_private_data"])
    return "\n".join(
        [
            "# Jarvis / Hermes Module Boundary Card",
            "",
            f"- **Module:** `{card['module']}`",
            f"- **Purpose:** {card['purpose']}",
            f"- **Default approval:** `{card['default_approval']}`",
            f"- **Safe preview:** {card['safe_preview']}",
            "",
            "## Allowed public inputs",
            allowed,
            "",
            "## Blocked private data",
            blocked,
        ]
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Print a public-safe boundary card for a generic Jarvis/Hermes module."
    )
    parser.add_argument(
        "module",
        choices=tuple(CARDS),
        help="Generic module to describe.",
    )
    parser.add_argument(
        "--format",
        choices=("markdown", "json"),
        default="markdown",
        help="Output format.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    card = build_card(args.module)
    if args.format == "json":
        print(json.dumps(card, indent=2, sort_keys=True))
    else:
        print(render_markdown(card))


if __name__ == "__main__":
    main()
