#!/usr/bin/env python3
"""Preview a public-safe visibility/access scope for a known record type.

This is the module proposed in the 2026-07-15 daily note. There is no real
access control or authorization system here -- this tool only documents, in
a standard and public-safe way, *who in general terms* could see a given
type of record (e.g. output from `approval_audit_trail.py` or
`retention_policy_preview.py`) before any real access-control layer exists.

Safety rules enforced by this tool:
  - `record_type` must be one of a small allow-list of already-public
    example record types defined in this repo (never an arbitrary
    free-text label that could describe private data).
  - `visibility_scope` must be one of a small allow-list of generic
    visibility labels ("local_only", "dashboard_visible",
    "external_share_approved"). It never accepts a real role name,
    account id, device id, or network location.
  - This tool performs no authorization check, no file access, and no
    network calls. It only prints/writes a preview description.
  - `--output` only accepts a relative path with no ".." segments (no path
    traversal), and writing is opt-in (stdout by default).

Usage:
  python3 examples/access_scope_preview.py                       # demo preview
  python3 examples/access_scope_preview.py --format json
  python3 examples/access_scope_preview.py \\
      --record-type dashboard_snapshot \\
      --visibility-scope dashboard_visible \\
      --note "Shown on the local HUD only."
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

ALLOWED_VISIBILITY_SCOPES = (
    "local_only",
    "dashboard_visible",
    "external_share_approved",
)

SCOPE_DESCRIPTIONS = {
    "local_only": (
        "Never leaves the local system. Not shown on any dashboard and "
        "not sent through any notification channel."
    ),
    "dashboard_visible": (
        "Safe to display on a local/private status dashboard, but not "
        "pushed to an external channel or third party."
    ),
    "external_share_approved": (
        "May be shared outside the local system, but only after an "
        "explicit approval step (see approval_audit_trail.py)."
    ),
}


class AccessScopeError(ValueError):
    """Raised when a preview request fails the safety contract."""


@dataclass(frozen=True)
class AccessScopePreview:
    """One standardized, public-safe visibility-scope preview entry."""

    record_type: str
    visibility_scope: str
    scope_description: str
    note: str


def _validate(record_type: str, visibility_scope: str) -> None:
    if record_type not in ALLOWED_RECORD_TYPES:
        raise AccessScopeError(
            f"record_type must be one of {ALLOWED_RECORD_TYPES!r}, got {record_type!r}"
        )
    if visibility_scope not in ALLOWED_VISIBILITY_SCOPES:
        raise AccessScopeError(
            f"visibility_scope must be one of {ALLOWED_VISIBILITY_SCOPES!r}, "
            f"got {visibility_scope!r}"
        )


def build_preview(record_type: str, visibility_scope: str, note: str) -> AccessScopePreview:
    _validate(record_type, visibility_scope)
    return AccessScopePreview(
        record_type=record_type,
        visibility_scope=visibility_scope,
        scope_description=SCOPE_DESCRIPTIONS[visibility_scope],
        note=note,
    )


def demo_previews() -> list[AccessScopePreview]:
    """Small embedded demo set, illustrating the preview shape only."""

    return [
        build_preview(
            "status_snapshot",
            "dashboard_visible",
            "General health summary, safe for the local HUD.",
        ),
        build_preview(
            "approval_audit_trail",
            "local_only",
            "Kept for internal review; not surfaced on any dashboard.",
        ),
        build_preview(
            "notification_digest",
            "external_share_approved",
            "Only sent externally after the approval step marks it clear.",
        ),
        build_preview(
            "event_log_entry",
            "local_only",
            "Routine operational detail, not meant for wider visibility.",
        ),
    ]


def to_markdown(previews: list[AccessScopePreview]) -> str:
    lines = [
        "# Access Scope Preview (Public-Safe Format Demo)",
        "",
        "This is a preview only -- no authorization check runs here.",
        "",
        "| Record type | Visibility scope | Description | Note |",
        "| --- | --- | --- | --- |",
    ]
    for p in previews:
        lines.append(
            f"| `{p.record_type}` | `{p.visibility_scope}` | {p.scope_description} | {p.note} |"
        )
    return "\n".join(lines)


def to_json(previews: list[AccessScopePreview]) -> str:
    return json.dumps([asdict(p) for p in previews], indent=2, sort_keys=True)


def _safe_output_path(raw: str):
    from pathlib import Path

    path = Path(raw)
    if path.is_absolute() or ".." in path.parts:
        raise AccessScopeError("--output must be a relative path with no '..' segments")
    return path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Preview a public-safe visibility scope for a known record type."
    )
    parser.add_argument(
        "--record-type",
        choices=ALLOWED_RECORD_TYPES,
        help="Record type to preview a visibility scope for.",
    )
    parser.add_argument(
        "--visibility-scope",
        choices=ALLOWED_VISIBILITY_SCOPES,
        help="Generic visibility scope label (never a real role/account/device id).",
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

    single_fields = (args.record_type, args.visibility_scope)
    if any(single_fields):
        if not all(single_fields):
            print("ERROR: --record-type and --visibility-scope must be given together.")
            return 2
        try:
            previews = [build_preview(args.record_type, args.visibility_scope, args.note)]
        except AccessScopeError as exc:
            print(f"access_scope_error: {exc}")
            return 2
    else:
        previews = demo_previews()

    rendered = to_json(previews) if args.format == "json" else to_markdown(previews)
    print(rendered)

    if args.output:
        try:
            out_path = _safe_output_path(args.output)
        except AccessScopeError as exc:
            print(f"access_scope_error: {exc}")
            return 2
        out_path.write_text(rendered + "\n", encoding="utf-8")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
