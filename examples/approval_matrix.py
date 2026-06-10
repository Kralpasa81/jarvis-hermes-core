#!/usr/bin/env python3
"""Generate a public-safe approval matrix for Jarvis / Hermes actions.

The matrix is intentionally generic. It does not call APIs, read local
configuration, inspect devices, or require credentials. Use it as a small
planning aid for deciding which assistant actions can be automatic and which
must wait for explicit human confirmation.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class ApprovalRule:
    """Describe a generic assistant action safety rule."""

    action_type: str
    examples: tuple[str, ...]
    default_policy: str
    reason: str


RULES = (
    ApprovalRule(
        action_type="read_only",
        examples=("status summary", "weather check", "documentation lookup"),
        default_policy="allow",
        reason="No external state is changed and no private data is published.",
    ),
    ApprovalRule(
        action_type="low_risk_notification",
        examples=("routine reminder", "safe dashboard alert", "scheduled checklist"),
        default_policy="allow_with_rate_limit",
        reason="Notifications are useful but should avoid spam and sensitive text.",
    ),
    ApprovalRule(
        action_type="external_publish",
        examples=("send message", "post update", "share generated file"),
        default_policy="require_approval",
        reason="Anything leaving the local system can expose private information.",
    ),
    ApprovalRule(
        action_type="device_or_home_control",
        examples=("toggle device", "start routine", "change environment setting"),
        default_policy="require_approval",
        reason="Physical-world actions need a clear confirmation and fallback path.",
    ),
    ApprovalRule(
        action_type="irreversible_or_financial",
        examples=("delete data", "purchase", "book appointment", "payment step"),
        default_policy="block_or_require_strong_approval",
        reason="High-impact actions should never run silently from a public template.",
    ),
)


def build_matrix() -> list[dict[str, Any]]:
    """Return the approval matrix as serializable dictionaries."""

    return [asdict(rule) for rule in RULES]


def render_markdown(rows: list[dict[str, Any]]) -> str:
    """Render the approval matrix as a Markdown table."""

    lines = [
        "# Jarvis / Hermes Approval Matrix",
        "",
        "| Action type | Example actions | Default policy | Why |",
        "| --- | --- | --- | --- |",
    ]
    for row in rows:
        examples_value = row["examples"]
        examples = ", ".join(str(item) for item in examples_value)
        lines.append(
            f"| `{row['action_type']}` | {examples} | `{row['default_policy']}` | {row['reason']} |"
        )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Print a public-safe approval matrix for Jarvis/Hermes action planning."
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
    rows = build_matrix()
    if args.format == "json":
        print(json.dumps(rows, indent=2, sort_keys=True))
    else:
        print(render_markdown(rows))


if __name__ == "__main__":
    main()
