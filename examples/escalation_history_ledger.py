#!/usr/bin/env python3
"""Preview a public-safe escalation-history ledger entry.

This is the module proposed in the 2026-07-18 daily note. There is no real
event/incident ledger here -- this tool only documents, in a standard and
public-safe way, *how* an escalation produced by
`examples/escalation_path_preview.py` would be recorded once it reaches
`escalate_to_internal_review` or `request_human_approval`. It never claims
that a real review happened, and it never invents a real date/time.

Safety rules enforced by this tool:
  - `record_type` must be one of the same small allow-list of already-public
    example record types used by `escalation_path_preview.py`,
    `retention_policy_preview.py`, and `access_scope_preview.py` (never an
    arbitrary free-text label).
  - `escalation_action` only accepts the two escalation-worthy outcomes from
    `escalation_path_preview.py` ("escalate_to_internal_review",
    "request_human_approval"). The non-escalating outcomes
    ("no_escalation_needed", "silently_drop") have nothing to log here by
    design, so they are rejected with a clear message.
  - `review_window` is a small generic label ("same_day", "within_7_days",
    "within_30_days") describing an *expected* review horizon, never a real
    calendar date or deadline.
  - `ledger_status` is one of "logged_pending_review" or "logged_resolved" --
    a status label only. This tool never marks anything as resolved based on
    real events; the caller supplies the status explicitly.
  - This tool writes no real ledger, sends no alert, and makes no network
    call. It only prints/writes a ledger-entry-shape preview.
  - `--output` only accepts a relative path with no ".." segments (no path
    traversal), and writing is opt-in (stdout by default).

Usage:
  python3 examples/escalation_history_ledger.py                 # demo preview
  python3 examples/escalation_history_ledger.py --format json
  python3 examples/escalation_history_ledger.py \\
      --record-type event_log_entry \\
      --escalation-action request_human_approval \\
      --review-window within_7_days \\
      --ledger-status logged_pending_review \\
      --note "Two-step channel gap awaiting human approval."
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass

ALLOWED_RECORD_TYPES = (
    "approval_audit_trail",
    "event_log_entry",
    "dashboard_snapshot",
    "notification_digest",
    "status_snapshot",
)

# Only the two escalation-worthy outcomes from escalation_path_preview.py
# have anything to log here -- "no_escalation_needed" and "silently_drop"
# are intentionally out of scope for a ledger.
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

REVIEW_WINDOW_DESCRIPTIONS = {
    "same_day": "Expected to be looked at the same day it was queued.",
    "within_7_days": "Expected to be looked at within a routine weekly review.",
    "within_30_days": "Expected to be looked at within a routine monthly review.",
}

LEDGER_STATUS_DESCRIPTIONS = {
    "logged_pending_review": "Entry recorded; no reviewer decision yet.",
    "logged_resolved": "Entry recorded and a reviewer decision has already been noted elsewhere.",
}


class EscalationLedgerError(ValueError):
    """Raised when a ledger preview request fails the safety contract."""


@dataclass(frozen=True)
class EscalationLedgerEntry:
    """One standardized, public-safe escalation-history ledger entry."""

    record_type: str
    escalation_action: str
    review_window: str
    review_window_description: str
    ledger_status: str
    ledger_status_description: str
    note: str


def _validate(
    record_type: str, escalation_action: str, review_window: str, ledger_status: str
) -> None:
    if record_type not in ALLOWED_RECORD_TYPES:
        raise EscalationLedgerError(
            f"record_type must be one of {ALLOWED_RECORD_TYPES!r}, got {record_type!r}"
        )
    if escalation_action not in ALLOWED_ESCALATION_ACTIONS:
        raise EscalationLedgerError(
            "escalation_action must be one of the escalation-worthy outcomes "
            f"{ALLOWED_ESCALATION_ACTIONS!r}, got {escalation_action!r} "
            "('no_escalation_needed' and 'silently_drop' have nothing to log)"
        )
    if review_window not in ALLOWED_REVIEW_WINDOWS:
        raise EscalationLedgerError(
            f"review_window must be one of {ALLOWED_REVIEW_WINDOWS!r}, got {review_window!r}"
        )
    if ledger_status not in ALLOWED_LEDGER_STATUSES:
        raise EscalationLedgerError(
            f"ledger_status must be one of {ALLOWED_LEDGER_STATUSES!r}, got {ledger_status!r}"
        )


def build_entry(
    record_type: str,
    escalation_action: str,
    review_window: str,
    ledger_status: str,
    note: str,
) -> EscalationLedgerEntry:
    _validate(record_type, escalation_action, review_window, ledger_status)
    return EscalationLedgerEntry(
        record_type=record_type,
        escalation_action=escalation_action,
        review_window=review_window,
        review_window_description=REVIEW_WINDOW_DESCRIPTIONS[review_window],
        ledger_status=ledger_status,
        ledger_status_description=LEDGER_STATUS_DESCRIPTIONS[ledger_status],
        note=note,
    )


def demo_entries() -> list[EscalationLedgerEntry]:
    """Small embedded demo set, illustrating the ledger entry shape only."""

    return [
        build_entry(
            "event_log_entry",
            "escalate_to_internal_review",
            "same_day",
            "logged_pending_review",
            "One-step channel gap, queued for the next internal review pass.",
        ),
        build_entry(
            "event_log_entry",
            "request_human_approval",
            "within_7_days",
            "logged_pending_review",
            "Two-step channel gap (local-only aimed externally); awaiting approval.",
        ),
        build_entry(
            "approval_audit_trail",
            "escalate_to_internal_review",
            "within_30_days",
            "logged_resolved",
            "Routine review confirmed the original channel choice was correct.",
        ),
    ]


def to_markdown(entries: list[EscalationLedgerEntry]) -> str:
    lines = [
        "# Escalation History Ledger Preview (Public-Safe Format Demo)",
        "",
        "This is a ledger-shape preview only -- no real event log is written here.",
        "",
        "| Record type | Escalation action | Review window | Ledger status | Note |",
        "| --- | --- | --- | --- | --- |",
    ]
    for e in entries:
        lines.append(
            f"| `{e.record_type}` | `{e.escalation_action}` | `{e.review_window}` | "
            f"`{e.ledger_status}` | {e.note} |"
        )
    return "\n".join(lines)


def to_json(entries: list[EscalationLedgerEntry]) -> str:
    return json.dumps([asdict(e) for e in entries], indent=2, sort_keys=True)


def _safe_output_path(raw: str):
    from pathlib import Path

    path = Path(raw)
    if path.is_absolute() or ".." in path.parts:
        raise EscalationLedgerError("--output must be a relative path with no '..' segments")
    return path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Preview a public-safe escalation-history ledger entry."
    )
    parser.add_argument(
        "--record-type",
        choices=ALLOWED_RECORD_TYPES,
        help="Record type the escalation relates to.",
    )
    parser.add_argument(
        "--escalation-action",
        choices=ALLOWED_ESCALATION_ACTIONS,
        help="Escalation-worthy outcome from escalation_path_preview.py.",
    )
    parser.add_argument(
        "--review-window",
        choices=ALLOWED_REVIEW_WINDOWS,
        help="Generic expected-review horizon label (never a real date).",
    )
    parser.add_argument(
        "--ledger-status",
        choices=ALLOWED_LEDGER_STATUSES,
        help="Generic ledger status label for a single entry.",
    )
    parser.add_argument("--note", default="", help="Optional public-safe note for a single entry.")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    parser.add_argument(
        "--output",
        help="Optional relative file path to also write the rendered output to (no '..' allowed).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    single_fields = (
        args.record_type,
        args.escalation_action,
        args.review_window,
        args.ledger_status,
    )
    if any(single_fields):
        if not all(single_fields):
            print(
                "ERROR: --record-type, --escalation-action, --review-window and "
                "--ledger-status must be given together."
            )
            return 2
        try:
            entries = [
                build_entry(
                    args.record_type,
                    args.escalation_action,
                    args.review_window,
                    args.ledger_status,
                    args.note,
                )
            ]
        except EscalationLedgerError as exc:
            print(f"escalation_ledger_error: {exc}")
            return 2
    else:
        entries = demo_entries()

    rendered = to_json(entries) if args.format == "json" else to_markdown(entries)
    print(rendered)

    if args.output:
        try:
            out_path = _safe_output_path(args.output)
        except EscalationLedgerError as exc:
            print(f"escalation_ledger_error: {exc}")
            return 2
        out_path.write_text(rendered + "\n", encoding="utf-8")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
