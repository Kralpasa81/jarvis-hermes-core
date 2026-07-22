#!/usr/bin/env python3
"""Digest of module registry health, grouped by status and approval level.

This is the module proposed in the 2026-07-20 daily note. It is **not** a
real CI/monitoring integration and it never reads a real module registry,
event log, or daily note. It works only on a small, fully static/synthetic
set of `module_registry_builder.py`-shaped sample entries and counts how
many of them are `ok`, `due-soon`, or `overdue` (using the same review-date
logic as `module_health_review.py`), grouped by `status` and by
`approval_level`.

This mirrors what `weekly_ledger_digest.py` does for escalation-ledger
previews, but for module-registry health instead -- and like
`weekly_ledger_digest.py`, it does not read any file from disk by default;
the sample registry is embedded directly in this script so the "digest
shape" can be reviewed before a real registry-health integration exists.

Safety rules enforced by this tool:
  - The embedded sample registry reuses only the field names and
    allow-listed label values already defined in `module_registry_builder.py`
    (`status`, `approval_level`) and the health labels already defined in
    `module_health_review.py` (`ok`, `due-soon`, `overdue`, `unparseable`).
    No free-text or real values are accepted anywhere in this tool.
  - The tool never reads a real module registry, event log, or daily note
    file; the embedded sample entries are fixed and synthetic only.
  - Health is computed only from the *sample* `next_review` dates compared
    against the real current date (same logic as `module_health_review.py`)
    -- no private runtime state, credentials, or device data is read.
  - `--output` only accepts a relative path with no ".." segments (no path
    traversal), and writing is opt-in (stdout by default).
  - No network call is made and nothing is auto-resolved -- this tool only
    counts and groups, it never changes a module's real status.

Usage:
  python3 examples/module_registry_health_digest.py                 # markdown digest
  python3 examples/module_registry_health_digest.py --format json
  python3 examples/module_registry_health_digest.py --due-soon-days 14
  python3 examples/module_registry_health_digest.py --output out.md
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from datetime import date
from typing import Optional

ALLOWED_STATUSES = ("planned", "prototype", "preview-ready")
ALLOWED_APPROVAL_LEVELS = ("read-only", "approval-required", "private-runtime-only")
ALLOWED_HEALTHS = ("ok", "due-soon", "overdue", "unparseable")


@dataclass(frozen=True)
class SampleModuleEntry:
    """A fully synthetic module-registry-shaped sample used only for counting."""

    slug: str
    title: str
    status: str
    approval_level: str
    next_review: str


# A fixed, synthetic sample registry. These rows mirror the shape of
# `module_registry_builder.py` output but are not read from any real
# registry file -- they exist only so this digest's grouping logic can be
# demonstrated deterministically.
SAMPLE_REGISTRY: tuple[SampleModuleEntry, ...] = (
    SampleModuleEntry("assistant-gateway", "Assistant Gateway", "prototype", "approval-required", "2026-07-11"),
    SampleModuleEntry("document-workflows", "Document Workflows", "planned", "private-runtime-only", "2026-07-18"),
    SampleModuleEntry("dashboard-status", "Dashboard Status", "preview-ready", "read-only", "2026-07-25"),
    SampleModuleEntry("media-helpers", "Media Helpers", "planned", "private-runtime-only", "2026-08-05"),
    SampleModuleEntry("monitoring-watchdogs", "Monitoring Watchdogs", "prototype", "approval-required", "2026-07-23"),
)


class ModuleRegistryHealthDigestError(ValueError):
    """Raised when an embedded sample entry breaks the safety contract."""


def _validate(entry: SampleModuleEntry) -> None:
    if entry.status not in ALLOWED_STATUSES:
        raise ModuleRegistryHealthDigestError(f"status must be one of {ALLOWED_STATUSES!r}, got {entry.status!r}")
    if entry.approval_level not in ALLOWED_APPROVAL_LEVELS:
        raise ModuleRegistryHealthDigestError(
            f"approval_level must be one of {ALLOWED_APPROVAL_LEVELS!r}, got {entry.approval_level!r}"
        )


def _health_for(next_review_raw: str, today: date, due_soon_days: int) -> tuple[str, Optional[int]]:
    """Same health-bucket logic as module_health_review.py, kept self-contained."""
    try:
        next_review_date = date.fromisoformat(next_review_raw)
    except ValueError:
        return "unparseable", None

    delta = (next_review_date - today).days
    if delta < 0:
        return "overdue", delta
    if delta <= due_soon_days:
        return "due-soon", delta
    return "ok", delta


def build_digest(entries: tuple[SampleModuleEntry, ...], today: date, due_soon_days: int) -> dict:
    """Validate every sample entry, then return a deterministic grouped digest."""

    for entry in entries:
        _validate(entry)

    by_health: dict[str, int] = {h: 0 for h in ALLOWED_HEALTHS}
    by_status: dict[str, dict[str, int]] = {s: {h: 0 for h in ALLOWED_HEALTHS} for s in ALLOWED_STATUSES}
    by_approval: dict[str, dict[str, int]] = {a: {h: 0 for h in ALLOWED_HEALTHS} for a in ALLOWED_APPROVAL_LEVELS}

    rows = []
    for entry in entries:
        health, days = _health_for(entry.next_review, today, due_soon_days)
        by_health[health] += 1
        by_status[entry.status][health] += 1
        by_approval[entry.approval_level][health] += 1
        rows.append({**asdict(entry), "health": health, "days_until_review": days})

    return {
        "digest_name": "jarvis_hermes_module_registry_health_digest_demo",
        "source": "synthetic_example_data",
        "privacy_note": "No real module registry, environment variable, or account identifier is read or produced.",
        "evaluated_as_of": today.isoformat(),
        "due_soon_days": due_soon_days,
        "total_entries": len(entries),
        "by_health": by_health,
        "by_status": {s: c for s, c in by_status.items() if sum(c.values()) > 0},
        "by_approval_level": {a: c for a, c in by_approval.items() if sum(c.values()) > 0},
        "entries": rows,
    }


def to_markdown(digest: dict) -> str:
    lines = [
        "# Module Registry Health Digest (Public-Safe, Synthetic Data)",
        "",
        "This groups a fixed, embedded sample module registry by health bucket --",
        "no real registry file, event log, or daily note is read.",
        "",
        f"- Evaluated as of: `{digest['evaluated_as_of']}` (due-soon threshold: {digest['due_soon_days']} days)",
        f"- Total sample entries: {digest['total_entries']}",
        f"- 🟢 `ok`: {digest['by_health']['ok']}",
        f"- 🟡 `due-soon`: {digest['by_health']['due-soon']}",
        f"- 🔴 `overdue`: {digest['by_health']['overdue']}",
        f"- ⚪ `unparseable`: {digest['by_health']['unparseable']}",
        "",
        "## By Status",
        "",
        "| Status | OK | Due soon | Overdue | Unparseable |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for status, counts in digest["by_status"].items():
        lines.append(
            f"| `{status}` | {counts['ok']} | {counts['due-soon']} | {counts['overdue']} | {counts['unparseable']} |"
        )
    lines += [
        "",
        "## By Approval Level",
        "",
        "| Approval level | OK | Due soon | Overdue | Unparseable |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for approval, counts in digest["by_approval_level"].items():
        lines.append(
            f"| `{approval}` | {counts['ok']} | {counts['due-soon']} | {counts['overdue']} | {counts['unparseable']} |"
        )
    return "\n".join(lines)


def to_json(digest: dict) -> str:
    return json.dumps(digest, indent=2, sort_keys=True)


def _safe_output_path(raw: str):
    from pathlib import Path

    path = Path(raw)
    if path.is_absolute() or ".." in path.parts:
        raise ModuleRegistryHealthDigestError("--output must be a relative path with no '..' segments")
    return path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Group a fixed, synthetic sample module registry by review-date health bucket."
    )
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    parser.add_argument(
        "--due-soon-days",
        type=int,
        default=7,
        help="Days-until-review threshold for 'due-soon' status (default: 7).",
    )
    parser.add_argument(
        "--output",
        help="Optional relative file path to also write the rendered output to (no '..' allowed).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        digest = build_digest(SAMPLE_REGISTRY, date.today(), args.due_soon_days)
    except ModuleRegistryHealthDigestError as exc:
        print(f"module_registry_health_digest_error: {exc}")
        return 2

    rendered = to_json(digest) if args.format == "json" else to_markdown(digest)
    print(rendered)

    if args.output:
        try:
            out_path = _safe_output_path(args.output)
        except ModuleRegistryHealthDigestError as exc:
            print(f"module_registry_health_digest_error: {exc}")
            return 2
        out_path.write_text(rendered + "\n", encoding="utf-8")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
