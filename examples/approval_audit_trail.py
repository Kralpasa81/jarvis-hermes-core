#!/usr/bin/env python3
"""Standardize a public-safe approval audit trail entry format.

This is the module proposed in the 2026-07-13 daily note. There is no real
approval mechanism here -- this tool only defines and validates the *shape*
of an approval-history record (who/what level approved an action and when),
so that if a real approval workflow is added later, its stored data is
consistent from day one.

Safety rules enforced by this tool:
  - `approved_by` must be one of a small set of generic role labels
    (never a real name, email, username, or account id).
  - `approval_level` must be one of the levels already documented in
    docs/architecture.md ("Approval Levels").
  - `action_title` is treated as opaque display text; the tool does not
    execute, schedule, or otherwise act on it.

No network calls. No default file writes -- entries are printed to stdout
unless --output is given, and --output only accepts a path inside the
current working directory (no path traversal).

Usage:
  python3 examples/approval_audit_trail.py                     # demo trail
  python3 examples/approval_audit_trail.py --format json
  python3 examples/approval_audit_trail.py \\
      --title "Send weekly digest" \\
      --action-type notification \\
      --approval-level not_required \\
      --approved-by automated-policy
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ALLOWED_APPROVAL_LEVELS = (
    "not_required",
    "usually_not_required",
    "required",
    "strong_approval_or_block",
)

ALLOWED_APPROVED_BY = (
    "automated-policy",
    "user",
    "reviewer",
)


class AuditTrailError(ValueError):
    """Raised when a record or trail entry fails the safety contract."""


@dataclass(frozen=True)
class ApprovalRecord:
    """One standardized, public-safe approval-history entry."""

    action_title: str
    action_type: str
    approval_level: str
    approved_by: str
    recorded_at: str  # UTC ISO-8601 timestamp
    note: str


def _validate(action_title: str, action_type: str, approval_level: str, approved_by: str) -> None:
    if approval_level not in ALLOWED_APPROVAL_LEVELS:
        raise AuditTrailError(
            f"approval_level must be one of {ALLOWED_APPROVAL_LEVELS!r}, got {approval_level!r}"
        )
    if approved_by not in ALLOWED_APPROVED_BY:
        raise AuditTrailError(
            f"approved_by must be a generic role label {ALLOWED_APPROVED_BY!r}, "
            f"not a real name/email/account id; got {approved_by!r}"
        )
    if not action_title.strip():
        raise AuditTrailError("action_title must not be empty")
    if not action_type.strip():
        raise AuditTrailError("action_type must not be empty")


def build_record(action_title: str, action_type: str, approval_level: str, approved_by: str, note: str) -> ApprovalRecord:
    _validate(action_title, action_type, approval_level, approved_by)
    recorded_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    return ApprovalRecord(
        action_title=action_title,
        action_type=action_type,
        approval_level=approval_level,
        approved_by=approved_by,
        recorded_at=recorded_at,
        note=note,
    )


def demo_trail() -> list[ApprovalRecord]:
    """Small embedded demo trail, illustrating the record shape only."""

    fixed_time = "2026-07-14T09:00:00+00:00"
    return [
        ApprovalRecord(
            action_title="Print status dashboard preview",
            action_type="read_only",
            approval_level="not_required",
            approved_by="automated-policy",
            recorded_at=fixed_time,
            note="Read-only preview, no state change.",
        ),
        ApprovalRecord(
            action_title="Send weekly digest notification",
            action_type="notification",
            approval_level="usually_not_required",
            approved_by="automated-policy",
            recorded_at=fixed_time,
            note="Rate-limited, low-risk notification.",
        ),
        ApprovalRecord(
            action_title="Publish generated summary externally",
            action_type="external_publish",
            approval_level="required",
            approved_by="user",
            recorded_at=fixed_time,
            note="Explicit confirmation required before leaving local system.",
        ),
    ]


def to_markdown(records: list[ApprovalRecord]) -> str:
    lines = [
        "# Approval Audit Trail (Public-Safe Format Demo)",
        "",
        "This is a format demonstration only -- no real approval workflow runs here.",
        "",
        "| Recorded at (UTC) | Action | Type | Approval level | Approved by | Note |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for r in records:
        lines.append(
            f"| {r.recorded_at} | {r.action_title} | `{r.action_type}` | "
            f"`{r.approval_level}` | `{r.approved_by}` | {r.note} |"
        )
    return "\n".join(lines)


def to_json(records: list[ApprovalRecord]) -> str:
    return json.dumps([asdict(r) for r in records], indent=2, sort_keys=True)


def _safe_output_path(raw: str) -> Path:
    path = Path(raw)
    if path.is_absolute() or ".." in path.parts:
        raise AuditTrailError("--output must be a relative path with no '..' segments")
    return path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build or preview a public-safe approval audit trail entry/record set."
    )
    parser.add_argument("--title", help="Action title for a single new record.")
    parser.add_argument("--action-type", help="Generic action type, e.g. read_only, notification.")
    parser.add_argument(
        "--approval-level",
        choices=ALLOWED_APPROVAL_LEVELS,
        help="Approval level for a single new record.",
    )
    parser.add_argument(
        "--approved-by",
        choices=ALLOWED_APPROVED_BY,
        help="Generic role label that approved the action (never a real identity).",
    )
    parser.add_argument("--note", default="", help="Optional public-safe note for a single new record.")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    parser.add_argument(
        "--output",
        help="Optional relative file path to also write the rendered output to (no '..' allowed).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    single_record_fields = (args.title, args.action_type, args.approval_level, args.approved_by)
    if any(single_record_fields):
        if not all(single_record_fields):
            print(
                "ERROR: --title, --action-type, --approval-level, and --approved-by "
                "must all be given together to build a single record.",
            )
            return 2
        try:
            records = [build_record(args.title, args.action_type, args.approval_level, args.approved_by, args.note)]
        except AuditTrailError as exc:
            print(f"audit_trail_error: {exc}")
            return 2
    else:
        records = demo_trail()

    rendered = to_json(records) if args.format == "json" else to_markdown(records)
    print(rendered)

    if args.output:
        try:
            out_path = _safe_output_path(args.output)
        except AuditTrailError as exc:
            print(f"audit_trail_error: {exc}")
            return 2
        out_path.write_text(rendered + "\n", encoding="utf-8")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
