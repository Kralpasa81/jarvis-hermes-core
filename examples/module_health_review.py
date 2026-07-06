#!/usr/bin/env python3
"""Flag stale entries in a public-safe Jarvis / Hermes module registry.

This example reads a small JSON module registry (as produced by
`module_registry_builder.py --format json`) and flags any entry whose
`next_review` date is overdue or due soon. It only inspects safe metadata
fields -- status, approval_level, and next_review -- and never reads private
runtime configuration, tokens, device addresses, or account data.

Usage:
    python3 examples/module_registry_builder.py --format json \\
        | python3 examples/module_health_review.py
    python3 examples/module_health_review.py --registry registry.json --format json
    python3 examples/module_health_review.py            # embedded demo data
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Optional


@dataclass(frozen=True)
class HealthResult:
    slug: str
    title: str
    status: str
    approval_level: str
    next_review: str
    health: str  # "ok" | "due-soon" | "overdue" | "unparseable"
    days_until_review: Optional[int]


def _demo_registry() -> list[dict]:
    """Small embedded demo, used only when no registry file/stdin is given."""
    return [
        {
            "slug": "assistant-gateway",
            "title": "Assistant Gateway",
            "status": "prototype",
            "approval_level": "approval-required",
            "next_review": "2026-07-11",
        },
        {
            "slug": "document-workflows",
            "title": "Document Workflows",
            "status": "planned",
            "approval_level": "private-runtime-only",
            "next_review": "2026-07-18",
        },
        {
            "slug": "dashboard-status",
            "title": "Dashboard Status",
            "status": "preview-ready",
            "approval_level": "read-only",
            "next_review": "2026-07-25",
        },
    ]


def load_registry(source: Optional[str]) -> list[dict]:
    """Load registry entries from a JSON file, stdin, or embedded demo data."""
    if source:
        path = Path(source)
        if not path.is_file():
            sys.exit(f"ERROR: registry file not found: {source}")
        payload = json.loads(path.read_text(encoding="utf-8"))
    elif not sys.stdin.isatty():
        raw = sys.stdin.read().strip()
        payload = json.loads(raw) if raw else {"modules": _demo_registry()}
    else:
        payload = {"modules": _demo_registry()}

    if isinstance(payload, list):
        modules = payload
    else:
        modules = payload.get("modules", [])

    if not isinstance(modules, list):
        sys.exit("ERROR: registry JSON must contain a 'modules' list.")
    return modules


def evaluate(entries: list[dict], today: date, due_soon_days: int) -> list[HealthResult]:
    results: list[HealthResult] = []
    for entry in entries:
        slug = str(entry.get("slug", "unknown"))
        title = str(entry.get("title", slug))
        status = str(entry.get("status", "unknown"))
        approval_level = str(entry.get("approval_level", "unknown"))
        next_review_raw = str(entry.get("next_review", ""))

        try:
            next_review_date = date.fromisoformat(next_review_raw)
        except ValueError:
            results.append(
                HealthResult(slug, title, status, approval_level, next_review_raw, "unparseable", None)
            )
            continue

        delta = (next_review_date - today).days
        if delta < 0:
            health = "overdue"
        elif delta <= due_soon_days:
            health = "due-soon"
        else:
            health = "ok"

        results.append(
            HealthResult(slug, title, status, approval_level, next_review_raw, health, delta)
        )
    return results


def to_markdown(results: list[HealthResult]) -> str:
    lines = [
        "# Module Health Summary",
        "",
        "Review-date check only, based on safe registry metadata. No private "
        "runtime configuration, tokens, or device data is read.",
        "",
        "| Module | Status | Approval | Next review | Health | Days |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    icon = {"ok": "🟢", "due-soon": "🟡", "overdue": "🔴", "unparseable": "⚪"}
    for r in results:
        days = "" if r.days_until_review is None else str(r.days_until_review)
        lines.append(
            f"| {r.title} (`{r.slug}`) | `{r.status}` | `{r.approval_level}` | "
            f"{r.next_review} | {icon.get(r.health, '')} {r.health} | {days} |"
        )
    return "\n".join(lines)


def to_json(results: list[HealthResult]) -> str:
    return json.dumps([r.__dict__ for r in results], indent=2, sort_keys=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Flag stale entries in a public-safe module registry by next_review date."
    )
    parser.add_argument(
        "--registry",
        help="Path to a registry JSON file (see module_registry_builder.py --format json).",
    )
    parser.add_argument(
        "--due-soon-days",
        type=int,
        default=7,
        help="Days-until-review threshold for 'due-soon' status (default: 7).",
    )
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    entries = load_registry(args.registry)
    results = evaluate(entries, date.today(), args.due_soon_days)

    if args.format == "json":
        print(to_json(results))
    else:
        print(to_markdown(results))

    overdue = sum(1 for r in results if r.health == "overdue")
    if overdue:
        print(f"\n{overdue} module(s) overdue for review.")


if __name__ == "__main__":
    main()
