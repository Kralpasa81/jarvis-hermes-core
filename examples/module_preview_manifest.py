#!/usr/bin/env python3
"""Generate a public-safe module preview manifest for Jarvis / Hermes planning.

The manifest is intentionally synthetic: it documents a proposed module's public
contract, mock input boundary, approval level, and private-data blocks without
reading secrets, device identifiers, personal files, or network settings.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from typing import Literal

ApprovalLevel = Literal["none", "confirm", "private-runtime-only", "blocked"]


@dataclass(frozen=True)
class ModulePreviewManifest:
    """A safe, shareable preview contract for a future assistant module."""

    module: str
    public_purpose: str
    safe_demo_command: str
    allowed_mock_inputs: list[str]
    blocked_private_inputs: list[str]
    preview_outputs: list[str]
    approval_level: ApprovalLevel
    operator_warning: str


def build_manifest(module: str, approval_level: ApprovalLevel) -> ModulePreviewManifest:
    normalized = module.strip().replace("_", "-").lower() or "sample-module"
    title = normalized.replace("-", " ").title()
    return ModulePreviewManifest(
        module=normalized,
        public_purpose=f"Public planning contract for a future {title} workflow.",
        safe_demo_command=f"jarvis preview {normalized} --mock",
        allowed_mock_inputs=[
            "synthetic status labels",
            "example timestamps",
            "placeholder module names",
            "non-personal checklist items",
        ],
        blocked_private_inputs=[
            "API keys, tokens, OAuth files, or webhook URLs",
            "real home-network addresses or device credentials",
            "personal documents, chat exports, or payment details",
            "production claims that have not been verified",
        ],
        preview_outputs=[
            "dry-run action summary",
            "approval requirement",
            "redacted public-safe payload shape",
        ],
        approval_level=approval_level,
        operator_warning=(
            "Keep this manifest in the public layer only. Attach private adapters "
            "in a separate runtime that is excluded from Git."
        ),
    )


def to_markdown(manifest: ModulePreviewManifest) -> str:
    rows = [
        ("Module", manifest.module),
        ("Purpose", manifest.public_purpose),
        ("Safe demo command", f"`{manifest.safe_demo_command}`"),
        ("Approval level", manifest.approval_level),
        ("Operator warning", manifest.operator_warning),
    ]
    lines = ["# Module Preview Manifest", "", "| Field | Value |", "| --- | --- |"]
    lines.extend(f"| {field} | {value} |" for field, value in rows)
    lines.extend(["", "## Allowed mock inputs"])
    lines.extend(f"- {item}" for item in manifest.allowed_mock_inputs)
    lines.extend(["", "## Blocked private inputs"])
    lines.extend(f"- {item}" for item in manifest.blocked_private_inputs)
    lines.extend(["", "## Preview outputs"])
    lines.extend(f"- {item}" for item in manifest.preview_outputs)
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Print a synthetic, public-safe module preview manifest."
    )
    parser.add_argument(
        "--module",
        default="notification-digest",
        help="Public module slug to describe with mock boundaries.",
    )
    parser.add_argument(
        "--approval",
        choices=["none", "confirm", "private-runtime-only", "blocked"],
        default="confirm",
        help="Approval level required before a real private adapter may act.",
    )
    parser.add_argument(
        "--format",
        choices=["json", "markdown"],
        default="json",
        help="Output format for the generated manifest.",
    )
    args = parser.parse_args()

    manifest = build_manifest(args.module, args.approval)
    if args.format == "markdown":
        print(to_markdown(manifest))
    else:
        print(json.dumps(asdict(manifest), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
