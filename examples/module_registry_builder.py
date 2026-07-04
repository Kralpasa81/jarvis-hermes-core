#!/usr/bin/env python3
"""Build a public-safe synthetic Jarvis / Hermes module registry.

This example is dependency-free, local-only, and uses demo metadata only. It is
intended for roadmap, dashboard, and review planning without reading private
configuration, environment variables, account identifiers, device addresses, or
runtime credentials.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from typing import Literal

ApprovalLevel = Literal["read-only", "approval-required", "private-runtime-only"]
ModuleStatus = Literal["planned", "prototype", "preview-ready"]


@dataclass(frozen=True)
class ModuleRegistryEntry:
    """One public-safe module registry entry."""

    slug: str
    title: str
    status: ModuleStatus
    approval_level: ApprovalLevel
    public_contract: str
    private_boundary: str
    manual_fallback: str
    next_review: str


DEFAULT_REGISTRY = [
    ModuleRegistryEntry(
        slug="assistant-gateway",
        title="Assistant Gateway",
        status="prototype",
        approval_level="approval-required",
        public_contract="Accepts synthetic command labels and returns a non-executing routing preview.",
        private_boundary="Real chat tokens, user IDs, webhook URLs, and delivery credentials stay private.",
        manual_fallback="Use the provider UI directly if the gateway is unavailable.",
        next_review="2026-07-11",
    ),
    ModuleRegistryEntry(
        slug="document-workflows",
        title="Document Workflows",
        status="planned",
        approval_level="private-runtime-only",
        public_contract="Documents expected OCR steps and redacted sample checklist output.",
        private_boundary="Personal files, scans, extracted text, and storage paths stay out of the public repo.",
        manual_fallback="Run OCR manually on local files and review results before sharing.",
        next_review="2026-07-18",
    ),
    ModuleRegistryEntry(
        slug="dashboard-status",
        title="Dashboard Status",
        status="preview-ready",
        approval_level="read-only",
        public_contract="Publishes synthetic status cards and mock module health values.",
        private_boundary="Live service URLs, device names, and personal monitoring data remain private.",
        manual_fallback="Read the underlying service dashboards directly.",
        next_review="2026-07-25",
    ),
]


def registry_as_dicts(entries: list[ModuleRegistryEntry]) -> list[dict[str, str]]:
    """Return registry entries as JSON-serializable dictionaries."""

    return [asdict(entry) for entry in entries]


def to_markdown(entries: list[ModuleRegistryEntry]) -> str:
    """Render the registry as a compact Markdown table."""

    lines = [
        "# Jarvis / Hermes Public Module Registry",
        "",
        "Synthetic planning data only. Do not place private adapter details, credentials, personal files, or real device endpoints in this registry.",
        "",
        "| Module | Status | Approval | Public contract | Private boundary | Manual fallback | Next review |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for entry in entries:
        lines.append(
            "| "
            f"{entry.title} (`{entry.slug}`) | "
            f"`{entry.status}` | "
            f"`{entry.approval_level}` | "
            f"{entry.public_contract} | "
            f"{entry.private_boundary} | "
            f"{entry.manual_fallback} | "
            f"{entry.next_review} |"
        )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Print a public-safe synthetic module registry for Jarvis/Hermes planning."
    )
    parser.add_argument(
        "--format",
        choices=("markdown", "json"),
        default="markdown",
        help="Output format.",
    )
    parser.add_argument(
        "--status",
        choices=("planned", "prototype", "preview-ready"),
        help="Optionally show only entries with this status.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    entries = DEFAULT_REGISTRY
    if args.status:
        entries = [entry for entry in entries if entry.status == args.status]

    if args.format == "json":
        print(json.dumps({"modules": registry_as_dicts(entries)}, indent=2, sort_keys=True))
    else:
        print(to_markdown(entries))


if __name__ == "__main__":
    main()
