#!/usr/bin/env python3
"""Preview a public-safe data retention policy for a record type.

This is the module proposed in the 2026-07-14 daily note. There is no real
retention/deletion job here -- this tool only documents, in a synchronized
and public-safe way, how long a given *type* of record (e.g. output from
`approval_audit_trail.py`, input to `event_log_formatter.py`) would be kept
before it is expected to be reviewed or removed.

Safety rules enforced by this tool:
  - `record_type` must be one of a small allow-list of already-public
    example record types defined in this repo (never an arbitrary free-text
    label that could describe private data).
  - `retention_policy` must be one of a small allow-list of generic policy
    labels (e.g. "30_days", "90_days", "indefinite_local_only"). It never
    accepts a real deletion date, real file path, or real storage location.
  - This tool performs no deletion, no file removal, and no network calls.
    It only prints/writes a preview description of a policy.
  - `--output` only accepts a relative path with no ".." segments (no path
    traversal), and writing is opt-in (stdout by default).

Usage:
  python3 examples/retention_policy_preview.py                       # demo preview
  python3 examples/retention_policy_preview.py --format json
  python3 examples/retention_policy_preview.py \\
      --record-type approval_audit_trail \\
      --retention-policy 90_days \\
      --note "Kept for review, not exported externally."
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

ALLOWED_RETENTION_POLICIES = (
    "7_days",
    "30_days",
    "90_days",
    "indefinite_local_only",
)

POLICY_DESCRIPTIONS = {
    "7_days": "Short-lived debug/preview data. Safe to discard quickly.",
    "30_days": "Default working window for routine logs and digests.",
    "90_days": "Extended window for audit-style records needing later review.",
    "indefinite_local_only": (
        "Kept indefinitely, but only on a local/private system -- "
        "never assumed to be synced or backed up to a public location."
    ),
}


class RetentionPreviewError(ValueError):
    """Raised when a preview request fails the safety contract."""


@dataclass(frozen=True)
class RetentionPreview:
    """One standardized, public-safe retention policy preview entry."""

    record_type: str
    retention_policy: str
    policy_description: str
    note: str


def _validate(record_type: str, retention_policy: str) -> None:
    if record_type not in ALLOWED_RECORD_TYPES:
        raise RetentionPreviewError(
            f"record_type must be one of {ALLOWED_RECORD_TYPES!r}, got {record_type!r}"
        )
    if retention_policy not in ALLOWED_RETENTION_POLICIES:
        raise RetentionPreviewError(
            f"retention_policy must be one of {ALLOWED_RETENTION_POLICIES!r}, "
            f"got {retention_policy!r}"
        )


def build_preview(record_type: str, retention_policy: str, note: str) -> RetentionPreview:
    _validate(record_type, retention_policy)
    return RetentionPreview(
        record_type=record_type,
        retention_policy=retention_policy,
        policy_description=POLICY_DESCRIPTIONS[retention_policy],
        note=note,
    )


def demo_previews() -> list[RetentionPreview]:
    """Small embedded demo set, illustrating the preview shape only."""

    return [
        build_preview(
            "approval_audit_trail",
            "90_days",
            "Kept for later review of approval decisions.",
        ),
        build_preview(
            "event_log_entry",
            "30_days",
            "Routine operational log, rotated after the window.",
        ),
        build_preview(
            "dashboard_snapshot",
            "7_days",
            "Preview-only snapshot, not meant for long-term storage.",
        ),
        build_preview(
            "status_snapshot",
            "indefinite_local_only",
            "Kept locally for trend comparison, never published externally.",
        ),
    ]


def to_markdown(previews: list[RetentionPreview]) -> str:
    lines = [
        "# Retention Policy Preview (Public-Safe Format Demo)",
        "",
        "This is a preview only -- no deletion or storage job runs here.",
        "",
        "| Record type | Retention policy | Description | Note |",
        "| --- | --- | --- | --- |",
    ]
    for p in previews:
        lines.append(
            f"| `{p.record_type}` | `{p.retention_policy}` | {p.policy_description} | {p.note} |"
        )
    return "\n".join(lines)


def to_json(previews: list[RetentionPreview]) -> str:
    return json.dumps([asdict(p) for p in previews], indent=2, sort_keys=True)


def _safe_output_path(raw: str):
    from pathlib import Path

    path = Path(raw)
    if path.is_absolute() or ".." in path.parts:
        raise RetentionPreviewError("--output must be a relative path with no '..' segments")
    return path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Preview a public-safe data retention policy for a known record type."
    )
    parser.add_argument(
        "--record-type",
        choices=ALLOWED_RECORD_TYPES,
        help="Record type to preview a retention policy for.",
    )
    parser.add_argument(
        "--retention-policy",
        choices=ALLOWED_RETENTION_POLICIES,
        help="Generic retention policy label (never a real deletion date/path).",
    )
    parser.add_argument("--note", default="", help="Optional public-safe note for a single preview.")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    parser.add_argument(
        "--output",
        help="Optional relative file path to also write the rendered output to (no '..' allowed).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    single_fields = (args.record_type, args.retention_policy)
    if any(single_fields):
        if not all(single_fields):
            print("ERROR: --record-type and --retention-policy must be given together.")
            return 2
        try:
            previews = [build_preview(args.record_type, args.retention_policy, args.note)]
        except RetentionPreviewError as exc:
            print(f"retention_preview_error: {exc}")
            return 2
    else:
        previews = demo_previews()

    rendered = to_json(previews) if args.format == "json" else to_markdown(previews)
    print(rendered)

    if args.output:
        try:
            out_path = _safe_output_path(args.output)
        except RetentionPreviewError as exc:
            print(f"retention_preview_error: {exc}")
            return 2
        out_path.write_text(rendered + "\n", encoding="utf-8")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
