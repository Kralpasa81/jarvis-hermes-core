#!/usr/bin/env python3
"""Weekly ledger digest counter for Jarvis / Hermes escalation ledger previews.

This is the module proposed in the 2026-07-19 daily note. It is **not** a
real weekly reporting system and it never reads a real event log, database,
or `docs/daily/` note. It works only on a small, fully static/synthetic set
of `escalation_history_ledger.py`-shaped sample entries (same field names,
same public-safe allow-listed label values) and counts how many of them are
`logged_pending_review` versus `logged_resolved`, grouped by `record_type`.

This mirrors what `weekly_review_summary.py` does for daily notes, but for
ledger-entry *previews* instead -- and unlike `weekly_review_summary.py`, it
does not read any file from disk by default; the "week" of sample entries is
embedded directly in this script.

Safety rules enforced by this tool:
  - Every embedded sample entry reuses only the allow-listed label values
    already defined in `escalation_history_ledger.py`:
    `record_type`, `escalation_action`, `review_window`, `ledger_status`.
    No free-text or real values are accepted anywhere in this tool.
  - The tool never reads a real ledger, event log, or daily note file; the
    sample "week" is a fixed, embedded, synthetic list only.
  - `--output` only accepts a relative path with no ".." segments (no path
    traversal), and writing is opt-in (stdout by default).
  - No network call is made and nothing is marked "resolved" automatically --
    every `ledger_status` value below is a pre-set example label, not a
    real reviewer decision.

Usage:
  python3 examples/weekly_ledger_digest.py                 # markdown digest
  python3 examples/weekly_ledger_digest.py --format json
  python3 examples/weekly_ledger_digest.py --output out.md
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass

# Reuses the exact allow-listed values from escalation_history_ledger.py.
ALLOWED_RECORD_TYPES = (
    "approval_audit_trail",
    "event_log_entry",
    "dashboard_snapshot",
    "notification_digest",
    "status_snapshot",
)
ALLOWED_ESCALATION_ACTIONS = (
    "escalate_to_internal_review",
    "request_human_approval",
)
ALLOWED_REVIEW_WINDOWS = (
    "same_day",
    "within_7_days",
    "within_30_days",
)
ALLOWED_LEDGER_STATUSES = (
    "logged_pending_review",
    "logged_resolved",
)


@dataclass(frozen=True)
class SampleLedgerEntry:
    """A fully synthetic ledger-entry-shaped sample used only for counting."""

    record_type: str
    escalation_action: str
    review_window: str
    ledger_status: str


# A fixed, synthetic "week" of ledger-entry-shaped samples. These are example
# rows only -- they do not correspond to any real escalation, reviewer, or
# calendar date.
SAMPLE_WEEK_ENTRIES: tuple[SampleLedgerEntry, ...] = (
    SampleLedgerEntry("event_log_entry", "escalate_to_internal_review", "same_day", "logged_pending_review"),
    SampleLedgerEntry("event_log_entry", "request_human_approval", "within_7_days", "logged_pending_review"),
    SampleLedgerEntry("approval_audit_trail", "escalate_to_internal_review", "within_30_days", "logged_resolved"),
    SampleLedgerEntry("dashboard_snapshot", "request_human_approval", "within_7_days", "logged_resolved"),
    SampleLedgerEntry("notification_digest", "escalate_to_internal_review", "same_day", "logged_pending_review"),
    SampleLedgerEntry("status_snapshot", "request_human_approval", "within_30_days", "logged_resolved"),
    SampleLedgerEntry("event_log_entry", "escalate_to_internal_review", "within_7_days", "logged_pending_review"),
)


class WeeklyLedgerDigestError(ValueError):
    """Raised when an embedded sample entry breaks the safety contract."""


def _validate(entry: SampleLedgerEntry) -> None:
    if entry.record_type not in ALLOWED_RECORD_TYPES:
        raise WeeklyLedgerDigestError(f"record_type must be one of {ALLOWED_RECORD_TYPES!r}, got {entry.record_type!r}")
    if entry.escalation_action not in ALLOWED_ESCALATION_ACTIONS:
        raise WeeklyLedgerDigestError(
            f"escalation_action must be one of {ALLOWED_ESCALATION_ACTIONS!r}, got {entry.escalation_action!r}"
        )
    if entry.review_window not in ALLOWED_REVIEW_WINDOWS:
        raise WeeklyLedgerDigestError(f"review_window must be one of {ALLOWED_REVIEW_WINDOWS!r}, got {entry.review_window!r}")
    if entry.ledger_status not in ALLOWED_LEDGER_STATUSES:
        raise WeeklyLedgerDigestError(f"ledger_status must be one of {ALLOWED_LEDGER_STATUSES!r}, got {entry.ledger_status!r}")


def build_digest(entries: tuple[SampleLedgerEntry, ...]) -> dict:
    """Validate every sample entry, then return a deterministic count digest."""

    for entry in entries:
        _validate(entry)

    by_status: dict[str, int] = {status: 0 for status in ALLOWED_LEDGER_STATUSES}
    by_record_type: dict[str, dict[str, int]] = {
        rt: {status: 0 for status in ALLOWED_LEDGER_STATUSES} for rt in ALLOWED_RECORD_TYPES
    }

    for entry in entries:
        by_status[entry.ledger_status] += 1
        by_record_type[entry.record_type][entry.ledger_status] += 1

    return {
        "digest_name": "jarvis_hermes_weekly_ledger_digest_demo",
        "source": "synthetic_example_data",
        "privacy_note": "No real event log, reviewer identity, or calendar date is read or produced.",
        "total_entries": len(entries),
        "by_status": by_status,
        "by_record_type": {
            rt: counts for rt, counts in by_record_type.items() if sum(counts.values()) > 0
        },
        "entries": [asdict(e) for e in entries],
    }


def to_markdown(digest: dict) -> str:
    lines = [
        "# Weekly Ledger Digest Preview (Public-Safe, Synthetic Data)",
        "",
        "This counts a fixed, embedded sample set of ledger-entry previews --",
        "no real event log or daily note is read.",
        "",
        f"- Total sample entries: {digest['total_entries']}",
        f"- `logged_pending_review`: {digest['by_status']['logged_pending_review']}",
        f"- `logged_resolved`: {digest['by_status']['logged_resolved']}",
        "",
        "## By Record Type",
        "",
        "| Record type | Pending review | Resolved |",
        "| --- | ---: | ---: |",
    ]
    for rt, counts in digest["by_record_type"].items():
        lines.append(f"| `{rt}` | {counts['logged_pending_review']} | {counts['logged_resolved']} |")
    return "\n".join(lines)


def to_json(digest: dict) -> str:
    return json.dumps(digest, indent=2, sort_keys=True)


def _safe_output_path(raw: str):
    from pathlib import Path

    path = Path(raw)
    if path.is_absolute() or ".." in path.parts:
        raise WeeklyLedgerDigestError("--output must be a relative path with no '..' segments")
    return path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Count a fixed, synthetic sample set of escalation-ledger-shaped entries."
    )
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    parser.add_argument(
        "--output",
        help="Optional relative file path to also write the rendered output to (no '..' allowed).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        digest = build_digest(SAMPLE_WEEK_ENTRIES)
    except WeeklyLedgerDigestError as exc:
        print(f"weekly_ledger_digest_error: {exc}")
        return 2

    rendered = to_json(digest) if args.format == "json" else to_markdown(digest)
    print(rendered)

    if args.output:
        try:
            out_path = _safe_output_path(args.output)
        except WeeklyLedgerDigestError as exc:
            print(f"weekly_ledger_digest_error: {exc}")
            return 2
        out_path.write_text(rendered + "\n", encoding="utf-8")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
