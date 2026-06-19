#!/usr/bin/env python3
"""Generate a public-safe handoff checklist for a Jarvis / Hermes module.

This example is intentionally offline and dependency-free. It does not read local
configuration, inspect private files, call APIs, send messages, control devices,
or require credentials. Use it before attaching a real private adapter.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass


ACTION_LEVELS = (
    "read-only",
    "preview-only",
    "approval-required",
    "private-runtime-only",
    "blocked",
)


@dataclass(frozen=True)
class HandoffChecklist:
    """Serializable checklist for public-safe module handoff review."""

    module: str
    action_level: str
    public_contract: tuple[str, ...]
    synthetic_test_path: tuple[str, ...]
    approval_questions: tuple[str, ...]
    private_boundaries: tuple[str, ...]
    done_definition: tuple[str, ...]


def build_checklist(module: str, action_level: str) -> HandoffChecklist:
    """Build a conservative checklist for a generic module name."""

    normalized_module = module.strip().replace(" ", "_").lower()
    if not normalized_module:
        raise ValueError("module name must not be empty")

    if action_level not in ACTION_LEVELS:
        raise ValueError(f"unsupported action level: {action_level}")

    return HandoffChecklist(
        module=normalized_module,
        action_level=action_level,
        public_contract=(
            "Describe the module goal in one sentence using generic wording.",
            "List allowed public inputs such as mock labels, sample timestamps, or redacted field names.",
            "List expected outputs without including real account, device, location, or document data.",
        ),
        synthetic_test_path=(
            "Run the module with hard-coded sample data or CLI arguments only.",
            "Print a preview instead of sending, publishing, purchasing, deleting, or controlling anything.",
            "Keep example output deterministic enough for review and documentation.",
        ),
        approval_questions=(
            "Could this action affect a real person, account, device, file, payment, or public post?",
            "If yes, is there an explicit approval step before the private adapter executes it?",
            "Is there a clear cancel, dry-run, or manual fallback path?",
        ),
        private_boundaries=(
            "No API keys, tokens, OAuth files, webhook URLs, or chat IDs in the public repo.",
            "No home-network addresses, exact device identifiers, personal documents, or private logs.",
            "No production success claims unless verified by real tooling outside this public example.",
        ),
        done_definition=(
            "README or docs explain the safe public contract.",
            "Example command runs without credentials or network access.",
            "Risky actions are labeled with the selected action level and approval expectation.",
        ),
    )


def _markdown_list(items: tuple[str, ...]) -> str:
    return "\n".join(f"- {item}" for item in items)


def render_markdown(checklist: HandoffChecklist) -> str:
    """Render the checklist in Markdown."""

    return "\n".join(
        [
            "# Jarvis / Hermes Module Handoff Checklist",
            "",
            f"- **Module:** `{checklist.module}`",
            f"- **Action level:** `{checklist.action_level}`",
            "",
            "## Public contract",
            _markdown_list(checklist.public_contract),
            "",
            "## Synthetic test path",
            _markdown_list(checklist.synthetic_test_path),
            "",
            "## Approval questions",
            _markdown_list(checklist.approval_questions),
            "",
            "## Private boundaries",
            _markdown_list(checklist.private_boundaries),
            "",
            "## Definition of done",
            _markdown_list(checklist.done_definition),
        ]
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Print a public-safe handoff checklist for a Jarvis/Hermes module."
    )
    parser.add_argument(
        "--module",
        required=True,
        help="Generic module name, for example reminders, dashboard, documents, or smart_home.",
    )
    parser.add_argument(
        "--action-level",
        choices=ACTION_LEVELS,
        default="preview-only",
        help="Safety level to document for the handoff.",
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
    checklist = build_checklist(args.module, args.action_level)
    if args.format == "json":
        print(json.dumps(asdict(checklist), indent=2, sort_keys=True))
    else:
        print(render_markdown(checklist))


if __name__ == "__main__":
    main()
