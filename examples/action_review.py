#!/usr/bin/env python3
"""Review a proposed Jarvis / Hermes action without executing it.

This example is intentionally public-safe: it does not call APIs, inspect the
host machine, read private config, control devices, or publish messages. It only
turns a generic action category into a small review record that can be printed
as Markdown or JSON.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class ActionPolicy:
    """Safety policy for one generic action category."""

    action_type: str
    approval: str
    risk_level: str
    state_change: str
    preview_guidance: str


POLICIES: dict[str, ActionPolicy] = {
    "read_only": ActionPolicy(
        action_type="read_only",
        approval="not_required",
        risk_level="low",
        state_change="none",
        preview_guidance="Summarize the information that would be read; do not include private data.",
    ),
    "notification": ActionPolicy(
        action_type="notification",
        approval="usually_not_required",
        risk_level="low_to_medium",
        state_change="sends a local or user-facing notice",
        preview_guidance="Show recipient class and message purpose, then apply rate limits.",
    ),
    "external_publish": ActionPolicy(
        action_type="external_publish",
        approval="required",
        risk_level="medium",
        state_change="shares content outside the local assistant context",
        preview_guidance="Show the exact public-safe text that would be sent or posted.",
    ),
    "device_control": ActionPolicy(
        action_type="device_control",
        approval="required",
        risk_level="medium_to_high",
        state_change="changes a physical or environmental system",
        preview_guidance="Describe the intended control action and confirm a manual fallback exists.",
    ),
    "destructive_or_financial": ActionPolicy(
        action_type="destructive_or_financial",
        approval="strong_approval_or_block",
        risk_level="high",
        state_change="may delete data, spend money, or create hard-to-reverse effects",
        preview_guidance="Prefer blocking in public templates; require explicit confirmation in private systems.",
    ),
}


def build_review(action_type: str, title: str) -> dict[str, Any]:
    """Build a serializable action review from a generic action type."""

    policy = POLICIES[action_type]
    return {
        "title": title,
        "action_type": policy.action_type,
        "approval": policy.approval,
        "risk_level": policy.risk_level,
        "state_change": policy.state_change,
        "safe_preview": policy.preview_guidance,
        "executes_action": False,
        "secret_safety": "No tokens, credentials, private endpoints, or personal data are required.",
    }


def render_markdown(review: dict[str, Any]) -> str:
    """Render an action review as Markdown."""

    return "\n".join(
        [
            "# Jarvis / Hermes Action Review",
            "",
            f"- **Title:** {review['title']}",
            f"- **Action type:** `{review['action_type']}`",
            f"- **Risk level:** `{review['risk_level']}`",
            f"- **Approval:** `{review['approval']}`",
            f"- **State change:** {review['state_change']}",
            f"- **Safe preview:** {review['safe_preview']}",
            f"- **Executes action:** `{str(review['executes_action']).lower()}`",
            f"- **Secret safety:** {review['secret_safety']}",
        ]
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Print a public-safe review for a generic Jarvis/Hermes action."
    )
    parser.add_argument(
        "action_type",
        choices=tuple(POLICIES),
        help="Generic action category to review.",
    )
    parser.add_argument(
        "--title",
        default="Example assistant action",
        help="Public-safe action title to display in the review.",
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
    review = build_review(args.action_type, args.title)
    if args.format == "json":
        print(json.dumps(review, indent=2, sort_keys=True))
    else:
        print(render_markdown(review))


if __name__ == "__main__":
    main()
