#!/usr/bin/env python3
"""Evaluate a public-safe readiness gate for a Jarvis / Hermes workflow.

This example is intentionally offline and dependency-free. It does not read
private config, inspect local devices, call external APIs, send messages, or
require tokens. It only turns generic checklist flags into a small readiness
report that can be printed as Markdown or JSON.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class GateResult:
    """Public-safe readiness result for one workflow idea."""

    workflow: str
    module: str
    readiness: str
    reason: str
    next_action: str
    safe_to_demo_publicly: bool
    requires_private_runtime: bool


def choose_readiness(
    *,
    has_safe_input: bool,
    has_preview: bool,
    approval_rule: str,
    uses_private_runtime: bool,
    has_sensitive_content: bool,
) -> tuple[str, str, str, bool, bool]:
    """Return a readiness label and guidance from public-safe checklist flags."""

    if has_sensitive_content:
        return (
            "blocked_for_public_repo",
            "The workflow description includes private or sensitive content.",
            "Redact the idea to generic placeholders before adding it to public docs.",
            False,
            True,
        )

    if uses_private_runtime:
        return (
            "private_runtime_only",
            "The workflow depends on real credentials, private endpoints, or device state.",
            "Keep implementation details outside the public repo and publish only a safe boundary card.",
            False,
            True,
        )

    if approval_rule in {"external_publish", "device_control", "destructive_or_financial"}:
        return (
            "approval_required",
            "The workflow may affect external systems or produce hard-to-reverse effects.",
            "Add an explicit preview and human confirmation step before any private runtime use.",
            has_safe_input and has_preview,
            False,
        )

    if has_safe_input and has_preview:
        return (
            "preview_ready",
            "The workflow has generic sample input and a non-executing preview path.",
            "Keep the example offline, synthetic, and clearly separated from live integrations.",
            True,
            False,
        )

    return (
        "draft",
        "The workflow is still missing either safe sample input or preview output.",
        "Add placeholder input and expected preview text before building integrations.",
        False,
        False,
    )


def build_result(
    workflow: str,
    module: str,
    has_safe_input: bool,
    has_preview: bool,
    approval_rule: str,
    uses_private_runtime: bool,
    has_sensitive_content: bool,
) -> dict[str, Any]:
    """Build a serializable readiness report for a generic workflow."""

    readiness, reason, next_action, safe_to_demo, private_runtime = choose_readiness(
        has_safe_input=has_safe_input,
        has_preview=has_preview,
        approval_rule=approval_rule,
        uses_private_runtime=uses_private_runtime,
        has_sensitive_content=has_sensitive_content,
    )
    return asdict(
        GateResult(
            workflow=workflow,
            module=module,
            readiness=readiness,
            reason=reason,
            next_action=next_action,
            safe_to_demo_publicly=safe_to_demo,
            requires_private_runtime=private_runtime,
        )
    )


def render_markdown(result: dict[str, Any]) -> str:
    """Render a readiness report as Markdown."""

    return "\n".join(
        [
            "# Jarvis / Hermes Workflow Readiness Gate",
            "",
            f"- **Workflow:** {result['workflow']}",
            f"- **Module:** `{result['module']}`",
            f"- **Readiness:** `{result['readiness']}`",
            f"- **Reason:** {result['reason']}",
            f"- **Next action:** {result['next_action']}",
            f"- **Safe to demo publicly:** `{str(result['safe_to_demo_publicly']).lower()}`",
            f"- **Requires private runtime:** `{str(result['requires_private_runtime']).lower()}`",
        ]
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Print a public-safe readiness gate report for a generic Jarvis/Hermes workflow."
    )
    parser.add_argument(
        "--workflow",
        default="Example assistant workflow",
        help="Public-safe workflow name to display.",
    )
    parser.add_argument(
        "--module",
        choices=("dashboard", "documents", "media", "notifications", "smart_home", "knowledge", "monitoring"),
        default="dashboard",
        help="Generic module category.",
    )
    parser.add_argument(
        "--approval-rule",
        choices=("read_only", "notification", "external_publish", "device_control", "destructive_or_financial"),
        default="read_only",
        help="Generic approval rule for the workflow.",
    )
    parser.add_argument(
        "--has-safe-input",
        action="store_true",
        help="Mark that the workflow has synthetic or placeholder input only.",
    )
    parser.add_argument(
        "--has-preview",
        action="store_true",
        help="Mark that the workflow can show a non-executing preview.",
    )
    parser.add_argument(
        "--uses-private-runtime",
        action="store_true",
        help="Mark that real credentials, endpoints, files, or devices are required outside the public repo.",
    )
    parser.add_argument(
        "--has-sensitive-content",
        action="store_true",
        help="Mark that the draft contains private content and should be blocked from the public repo.",
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
    result = build_result(
        workflow=args.workflow,
        module=args.module,
        has_safe_input=args.has_safe_input,
        has_preview=args.has_preview,
        approval_rule=args.approval_rule,
        uses_private_runtime=args.uses_private_runtime,
        has_sensitive_content=args.has_sensitive_content,
    )
    if args.format == "json":
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(render_markdown(result))


if __name__ == "__main__":
    main()
