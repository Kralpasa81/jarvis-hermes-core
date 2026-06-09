#!/usr/bin/env python3
"""Generate a public-safe OCR workflow checklist.

The checklist is meant for planning Jarvis / Hermes document workflows without
processing real files or exposing private paths, document names, IDs, tokens, or
personal data. It prints Markdown so the output can be pasted into an issue,
lab note, or dashboard card.
"""

from __future__ import annotations

import argparse
from datetime import date

DEFAULT_STEPS = [
    (
        "intake",
        "Use a local input folder that is ignored by Git; never commit source scans.",
    ),
    (
        "classification",
        "Label the document type with generic names such as invoice, form, or note.",
    ),
    (
        "ocr",
        "Run OCR locally or through an approved private service; keep raw text private.",
    ),
    (
        "redaction",
        "Remove names, addresses, IDs, account numbers, and signatures before sharing.",
    ),
    (
        "summary",
        "Export only a short safe summary, status flag, and next action.",
    ),
    (
        "approval",
        "Require human approval before sending, deleting, uploading, or filing documents.",
    ),
]

SAFETY_RULES = [
    "No real document paths, filenames, IDs, or personal details in public output.",
    "No API keys, OAuth files, bot tokens, or service credentials in examples.",
    "No claim that OCR succeeded unless a real private runtime verified it.",
    "Public demos should use synthetic text or placeholders only.",
]


def build_checklist(workflow_label: str, include_owner_placeholders: bool) -> str:
    """Return a Markdown checklist for a safe OCR workflow."""
    lines = [
        f"# OCR Workflow Checklist — {workflow_label}",
        "",
        f"Generated: {date.today().isoformat()}",
        "",
        "## Steps",
    ]

    for name, description in DEFAULT_STEPS:
        lines.append(f"- [ ] **{name}** — {description}")

    lines.extend(["", "## Public-safety rules"])
    for rule in SAFETY_RULES:
        lines.append(f"- {rule}")

    if include_owner_placeholders:
        lines.extend(
            [
                "",
                "## Private-runtime placeholders",
                "- `<PRIVATE_INPUT_DIR>` stays outside Git.",
                "- `<PRIVATE_OUTPUT_DIR>` stores local OCR text and redacted summaries.",
                "- `<APPROVAL_CHANNEL>` is configured privately, not in this repo.",
            ]
        )

    lines.extend(
        [
            "",
            "## Safe exported status shape",
            "```json",
            '{"workflow":"ocr","status":"planned","public_safe":true,"needs_approval":true}',
            "```",
        ]
    )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Print a public-safe Markdown checklist for OCR workflow planning."
    )
    parser.add_argument(
        "--workflow-label",
        default="public-demo",
        help="Non-sensitive label shown in the checklist title.",
    )
    parser.add_argument(
        "--include-placeholders",
        action="store_true",
        help="Include generic private-runtime placeholder names.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    print(build_checklist(args.workflow_label, args.include_placeholders))


if __name__ == "__main__":
    main()
