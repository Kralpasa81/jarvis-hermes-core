#!/usr/bin/env python3
"""Generate a public-safe notification digest for Jarvis / Hermes planning.

This helper uses only synthetic items. It does not read messages, tokens,
chat IDs, local files, calendars, device state, or network resources. The goal
is to prototype how a daily assistant digest might group low-risk updates while
marking items that should wait for explicit human approval.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class DigestItem:
    """A synthetic notification item suitable for public documentation."""

    area: str
    title: str
    summary: str
    severity: str
    needs_approval: bool
    safe_next_step: str


SYNTHETIC_ITEMS = (
    DigestItem(
        area="assistant",
        title="Morning command center check",
        summary="Confirm that planned read-only summaries are separated from action requests.",
        severity="info",
        needs_approval=False,
        safe_next_step="Show the digest preview before any external message is sent.",
    ),
    DigestItem(
        area="documents",
        title="OCR queue reminder",
        summary="Use placeholder document names in public notes and keep real files local.",
        severity="notice",
        needs_approval=False,
        safe_next_step="Prepare a checklist with synthetic filenames only.",
    ),
    DigestItem(
        area="smart_home",
        title="Control action requested",
        summary="Any physical-world action must be reviewed instead of running silently.",
        severity="approval_required",
        needs_approval=True,
        safe_next_step="Ask for confirmation in the private runtime before execution.",
    ),
    DigestItem(
        area="publishing",
        title="External share boundary",
        summary="Generated content should be redacted and reviewed before leaving the local system.",
        severity="approval_required",
        needs_approval=True,
        safe_next_step="Run a public-safe preview and require explicit approval.",
    ),
)


def build_digest() -> dict[str, Any]:
    """Return a deterministic public-safe digest payload."""

    items = [asdict(item) for item in SYNTHETIC_ITEMS]
    return {
        "digest_name": "jarvis_hermes_public_demo_digest",
        "source": "synthetic_example_data",
        "privacy_note": "No private messages, credentials, device IDs, addresses, or live logs are included.",
        "items": items,
        "counts": {
            "total": len(items),
            "approval_required": sum(1 for item in items if item["needs_approval"]),
            "informational": sum(1 for item in items if not item["needs_approval"]),
        },
    }


def render_markdown(digest: dict[str, Any]) -> str:
    """Render the digest as a compact Markdown report."""

    lines = [
        "# Jarvis / Hermes Notification Digest Preview",
        "",
        f"- Digest: `{digest['digest_name']}`",
        f"- Source: `{digest['source']}`",
        f"- Privacy note: {digest['privacy_note']}",
        "",
        "| Area | Title | Severity | Approval? | Safe next step |",
        "| --- | --- | --- | --- | --- |",
    ]
    for item in digest["items"]:
        approval = "yes" if item["needs_approval"] else "no"
        lines.append(
            f"| `{item['area']}` | {item['title']} | `{item['severity']}` | {approval} | {item['safe_next_step']} |"
        )
    lines.extend(
        [
            "",
            "## Counts",
            "",
            f"- Total items: {digest['counts']['total']}",
            f"- Approval required: {digest['counts']['approval_required']}",
            f"- Informational: {digest['counts']['informational']}",
        ]
    )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Print a public-safe synthetic notification digest for Jarvis/Hermes planning."
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
    digest = build_digest()
    if args.format == "json":
        print(json.dumps(digest, indent=2, sort_keys=True))
    else:
        print(render_markdown(digest))


if __name__ == "__main__":
    main()
