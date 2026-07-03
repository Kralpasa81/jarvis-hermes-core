#!/usr/bin/env python3
"""Generate a public-safe integration readiness report for Jarvis / Hermes modules.

This example is intentionally offline and dependency-free. It evaluates only
explicit checklist flags for a synthetic module description; it does not read
private configuration, inspect local devices, call APIs, send notifications, or
require tokens.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from typing import Literal

Status = Literal["pass", "warn", "block"]


@dataclass(frozen=True)
class CheckResult:
    """One public-safe integration readiness check."""

    name: str
    status: Status
    detail: str


@dataclass(frozen=True)
class IntegrationReadinessReport:
    """Summary for a synthetic future module integration."""

    module: str
    summary: Status
    checks: list[CheckResult]
    next_action: str
    safe_for_public_repo: bool


def check_flag(name: str, enabled: bool, pass_detail: str, warn_detail: str) -> CheckResult:
    """Convert a checklist flag into a pass/warn result."""

    return CheckResult(
        name=name,
        status="pass" if enabled else "warn",
        detail=pass_detail if enabled else warn_detail,
    )


def build_report(
    *,
    module: str,
    has_public_contract: bool,
    has_approval_rule: bool,
    has_private_boundary: bool,
    has_manual_fallback: bool,
    contains_sensitive_detail: bool,
) -> IntegrationReadinessReport:
    """Build a deterministic readiness report from public-safe flags."""

    normalized_module = module.strip().replace("_", "-").lower() or "sample-module"

    if contains_sensitive_detail:
        return IntegrationReadinessReport(
            module=normalized_module,
            summary="block",
            checks=[
                CheckResult(
                    name="public safety",
                    status="block",
                    detail=(
                        "The draft is marked as containing sensitive details; redact it "
                        "before committing anything to the public repository."
                    ),
                )
            ],
            next_action="Replace real identifiers, credentials, endpoints, files, and account details with placeholders.",
            safe_for_public_repo=False,
        )

    checks = [
        check_flag(
            "public contract",
            has_public_contract,
            "Synthetic inputs and preview outputs are documented.",
            "Add a public contract that lists mock inputs and non-executing preview output.",
        ),
        check_flag(
            "approval rule",
            has_approval_rule,
            "Human confirmation policy is documented for non-read-only actions.",
            "Define whether the module is read-only, approval-required, private-runtime-only, or blocked.",
        ),
        check_flag(
            "private boundary",
            has_private_boundary,
            "Runtime secrets, device details, and personal data are explicitly excluded from the public layer.",
            "Document which implementation details must stay in private runtime configuration.",
        ),
        check_flag(
            "manual fallback",
            has_manual_fallback,
            "A safe manual fallback or rollback path is described.",
            "Add a fallback path so the module does not imply irreversible automation.",
        ),
    ]

    warning_count = sum(1 for check in checks if check.status == "warn")
    if warning_count == 0:
        summary: Status = "pass"
        next_action = "Ready for a public-safe demo manifest or dry-run example."
    else:
        summary = "warn"
        next_action = "Resolve the warning items before attaching any private runtime adapter."

    return IntegrationReadinessReport(
        module=normalized_module,
        summary=summary,
        checks=checks,
        next_action=next_action,
        safe_for_public_repo=True,
    )


def to_markdown(report: IntegrationReadinessReport) -> str:
    """Render the report as Markdown."""

    lines = [
        "# Jarvis / Hermes Integration Readiness Report",
        "",
        f"- **Module:** `{report.module}`",
        f"- **Summary:** `{report.summary}`",
        f"- **Safe for public repo:** `{str(report.safe_for_public_repo).lower()}`",
        f"- **Next action:** {report.next_action}",
        "",
        "| Check | Status | Detail |",
        "| --- | --- | --- |",
    ]
    lines.extend(
        f"| {check.name} | `{check.status}` | {check.detail} |" for check in report.checks
    )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Print a public-safe integration readiness report for a synthetic Jarvis/Hermes module."
    )
    parser.add_argument(
        "--module",
        default="notification-digest",
        help="Synthetic module slug to evaluate.",
    )
    parser.add_argument(
        "--has-public-contract",
        action="store_true",
        help="Mark that mock inputs and preview outputs are documented.",
    )
    parser.add_argument(
        "--has-approval-rule",
        action="store_true",
        help="Mark that the module has a documented approval policy.",
    )
    parser.add_argument(
        "--has-private-boundary",
        action="store_true",
        help="Mark that private runtime boundaries are documented.",
    )
    parser.add_argument(
        "--has-manual-fallback",
        action="store_true",
        help="Mark that a manual fallback or rollback path is documented.",
    )
    parser.add_argument(
        "--contains-sensitive-detail",
        action="store_true",
        help="Block the report because the draft contains private or sensitive details.",
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
    report = build_report(
        module=args.module,
        has_public_contract=args.has_public_contract,
        has_approval_rule=args.has_approval_rule,
        has_private_boundary=args.has_private_boundary,
        has_manual_fallback=args.has_manual_fallback,
        contains_sensitive_detail=args.contains_sensitive_detail,
    )
    if args.format == "json":
        print(json.dumps(asdict(report), indent=2, sort_keys=True))
    else:
        print(to_markdown(report))


if __name__ == "__main__":
    main()
