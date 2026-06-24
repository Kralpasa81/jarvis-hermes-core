#!/usr/bin/env python3
"""Classify a proposed Jarvis / Hermes command without executing it.

This example is intentionally offline and dependency-free. It does not call APIs,
read private files, inspect devices, send messages, publish content, or require
credentials. It turns a generic command phrase into a public-safe routing preview
so module boundaries and approval levels can be reviewed before a private runtime
is connected.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class RouteRule:
    """Keyword-based routing rule for public-safe command planning."""

    module: str
    action_level: str
    approval: str
    keywords: tuple[str, ...]
    preview_guidance: str


@dataclass(frozen=True)
class RoutePreview:
    """Serializable preview for one proposed command."""

    module: str
    action_level: str
    approval: str
    matched_keywords: tuple[str, ...]
    safety_flags: tuple[str, ...]
    executes_action: bool
    input_echo: str
    next_step: str


ROUTE_RULES: tuple[RouteRule, ...] = (
    RouteRule(
        module="dashboard",
        action_level="read_only",
        approval="not_required",
        keywords=("dashboard", "status", "hud", "overview", "summary"),
        preview_guidance="Show synthetic or redacted status only; do not claim live state.",
    ),
    RouteRule(
        module="documents",
        action_level="preview_only",
        approval="required_before_private_files",
        keywords=("document", "pdf", "ocr", "scan", "form", "translate"),
        preview_guidance="Use placeholder document names in public examples; private files stay outside GitHub.",
    ),
    RouteRule(
        module="notifications",
        action_level="preview_only",
        approval="required_before_external_delivery",
        keywords=("notify", "remind", "alert", "message", "digest"),
        preview_guidance="Print a draft notification; do not send to real channels from the example.",
    ),
    RouteRule(
        module="media",
        action_level="approval_required",
        approval="required_before_publish",
        keywords=("youtube", "video", "upload", "publish", "post", "shorts"),
        preview_guidance="Prepare a checklist or draft only; publishing needs explicit approval.",
    ),
    RouteRule(
        module="smart_home",
        action_level="approval_required",
        approval="required_before_device_control",
        keywords=("device", "light", "thermostat", "lock", "scene", "routine"),
        preview_guidance="Describe intended control and manual fallback; never touch devices in public examples.",
    ),
    RouteRule(
        module="monitoring",
        action_level="read_only",
        approval="not_required",
        keywords=("weather", "news", "monitor", "watchdog", "health"),
        preview_guidance="Return generic monitoring summaries without private endpoints or account IDs.",
    ),
    RouteRule(
        module="knowledge",
        action_level="read_only",
        approval="not_required",
        keywords=("note", "knowledge", "search", "reference", "memory"),
        preview_guidance="Use public placeholder notes only; private knowledge bases stay local.",
    ),
)

SENSITIVE_TERMS = (
    "api key",
    "apikey",
    "token",
    "secret",
    "password",
    "oauth",
    "credential",
    "webhook",
    "chat id",
    "private ip",
    "address",
    "payment",
    "card number",
)

HIGH_IMPACT_TERMS = (
    "delete",
    "buy",
    "purchase",
    "pay",
    "book",
    "transfer",
    "unlock",
    "shutdown",
)


def _normalize(text: str) -> str:
    return " ".join(text.lower().strip().split())


def _matching_terms(text: str, terms: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(term for term in terms if term in text)


def choose_rule(command: str) -> tuple[RouteRule | None, tuple[str, ...]]:
    """Choose the first matching route rule and return matched keywords."""

    normalized = _normalize(command)
    for rule in ROUTE_RULES:
        matches = _matching_terms(normalized, rule.keywords)
        if matches:
            return rule, matches
    return None, ()


def build_preview(command: str) -> dict[str, Any]:
    """Build a public-safe routing preview without echoing the full command."""

    normalized = _normalize(command)
    if not normalized:
        raise ValueError("command must not be empty")

    sensitive_matches = _matching_terms(normalized, SENSITIVE_TERMS)
    high_impact_matches = _matching_terms(normalized, HIGH_IMPACT_TERMS)
    rule, matched_keywords = choose_rule(normalized)

    safety_flags: list[str] = []
    if sensitive_matches:
        safety_flags.append("contains_sensitive_terms_redact_before_public_use")
    if high_impact_matches:
        safety_flags.append("contains_high_impact_action_requires_strong_approval")

    if sensitive_matches:
        preview = RoutePreview(
            module="blocked",
            action_level="blocked_for_public_repo",
            approval="do_not_commit_private_details",
            matched_keywords=matched_keywords,
            safety_flags=tuple(safety_flags),
            executes_action=False,
            input_echo="omitted_by_design",
            next_step="Remove secrets or private identifiers and replace them with generic placeholders.",
        )
        return asdict(preview)

    if high_impact_matches:
        preview = RoutePreview(
            module=rule.module if rule else "automation",
            action_level="strong_approval_required",
            approval="block_in_public_example_until_reviewed",
            matched_keywords=matched_keywords + high_impact_matches,
            safety_flags=tuple(safety_flags),
            executes_action=False,
            input_echo="omitted_by_design",
            next_step="Keep this as a dry-run preview and require explicit approval in a private runtime.",
        )
        return asdict(preview)

    if rule is None:
        preview = RoutePreview(
            module="orchestration",
            action_level="draft",
            approval="review_needed",
            matched_keywords=(),
            safety_flags=tuple(safety_flags),
            executes_action=False,
            input_echo="omitted_by_design",
            next_step="Add a module boundary card and safe sample input before implementation.",
        )
        return asdict(preview)

    preview = RoutePreview(
        module=rule.module,
        action_level=rule.action_level,
        approval=rule.approval,
        matched_keywords=matched_keywords,
        safety_flags=tuple(safety_flags) or ("public_safe_preview_only",),
        executes_action=False,
        input_echo="omitted_by_design",
        next_step=rule.preview_guidance,
    )
    return asdict(preview)


def render_markdown(preview: dict[str, Any]) -> str:
    """Render a route preview as Markdown."""

    matched = ", ".join(preview["matched_keywords"]) or "none"
    flags = ", ".join(preview["safety_flags"]) or "none"
    return "\n".join(
        [
            "# Jarvis / Hermes Safe Command Route Preview",
            "",
            f"- **Module:** `{preview['module']}`",
            f"- **Action level:** `{preview['action_level']}`",
            f"- **Approval:** `{preview['approval']}`",
            f"- **Matched keywords:** {matched}",
            f"- **Safety flags:** {flags}",
            f"- **Executes action:** `{str(preview['executes_action']).lower()}`",
            f"- **Input echo:** `{preview['input_echo']}`",
            f"- **Next step:** {preview['next_step']}",
        ]
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Print a public-safe route preview for a proposed Jarvis/Hermes command."
    )
    parser.add_argument(
        "--command",
        default="show dashboard status summary",
        help="Generic command phrase to classify. The full text is never echoed in output.",
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
    preview = build_preview(args.command)
    if args.format == "json":
        print(json.dumps(preview, indent=2, sort_keys=True))
    else:
        print(render_markdown(preview))


if __name__ == "__main__":
    main()
