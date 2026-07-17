#!/usr/bin/env python3
"""Preview which public-safe notification channel fits a known record/scope pair.

This is the module proposed in the 2026-07-16 daily note. There is no real
notification delivery here -- this tool only documents, in a standard and
public-safe way, *which generic channel* a given record type and visibility
scope (see `access_scope_preview.py`) would be appropriate for, before any
real notification-sending layer exists.

Safety rules enforced by this tool:
  - `record_type` must be one of the same small allow-list of already-public
    example record types used by `access_scope_preview.py` and
    `retention_policy_preview.py` (never an arbitrary free-text label).
  - `visibility_scope` must be one of the same allow-list of generic
    visibility labels defined in `access_scope_preview.py`
    ("local_only", "dashboard_visible", "external_share_approved"). It never
    accepts a real role name, account id, device id, or network location.
  - `channel` must be one of a small allow-list of generic channel labels
    ("local_hud", "internal_review_queue", "external_channel"). It never
    accepts a real chat id, webhook URL, phone number, or bot token.
  - This tool sends no notification, makes no network call, and reads no
    private configuration. It only prints/writes a routing preview.
  - `--output` only accepts a relative path with no ".." segments (no path
    traversal), and writing is opt-in (stdout by default).

Usage:
  python3 examples/notification_channel_gate.py                  # demo preview
  python3 examples/notification_channel_gate.py --format json
  python3 examples/notification_channel_gate.py \\
      --record-type notification_digest \\
      --visibility-scope external_share_approved \\
      --note "Weekly summary, already approved for external delivery."
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

ALLOWED_CHANNELS = (
    "local_hud",
    "internal_review_queue",
    "external_channel",
)

# Deterministic mapping from visibility scope to the single channel this
# preview considers "fit" for that scope. This is intentionally simple and
# conservative: nothing routes to `external_channel` unless the scope is
# already `external_share_approved`.
SCOPE_TO_FIT_CHANNEL = {
    "local_only": "local_hud",
    "dashboard_visible": "internal_review_queue",
    "external_share_approved": "external_channel",
}

CHANNEL_DESCRIPTIONS = {
    "local_hud": (
        "Stays on the local status surface only. No message leaves the "
        "local system through this channel."
    ),
    "internal_review_queue": (
        "Queued for a human or internal review step before any wider "
        "distribution is considered."
    ),
    "external_channel": (
        "May be delivered through an external notification channel, but "
        "only for records already marked external_share_approved."
    ),
}


class ChannelGateError(ValueError):
    """Raised when a routing preview request fails the safety contract."""


@dataclass(frozen=True)
class ChannelGatePreview:
    """One standardized, public-safe channel-routing preview entry."""

    record_type: str
    visibility_scope: str
    requested_channel: str
    fit_channel: str
    is_fit: bool
    channel_description: str
    note: str


def _validate(record_type: str, visibility_scope: str, channel: str) -> None:
    if record_type not in ALLOWED_RECORD_TYPES:
        raise ChannelGateError(
            f"record_type must be one of {ALLOWED_RECORD_TYPES!r}, got {record_type!r}"
        )
    if visibility_scope not in ALLOWED_VISIBILITY_SCOPES:
        raise ChannelGateError(
            f"visibility_scope must be one of {ALLOWED_VISIBILITY_SCOPES!r}, "
            f"got {visibility_scope!r}"
        )
    if channel not in ALLOWED_CHANNELS:
        raise ChannelGateError(
            f"channel must be one of {ALLOWED_CHANNELS!r}, got {channel!r}"
        )


def build_preview(
    record_type: str, visibility_scope: str, channel: str, note: str
) -> ChannelGatePreview:
    _validate(record_type, visibility_scope, channel)
    fit_channel = SCOPE_TO_FIT_CHANNEL[visibility_scope]
    return ChannelGatePreview(
        record_type=record_type,
        visibility_scope=visibility_scope,
        requested_channel=channel,
        fit_channel=fit_channel,
        is_fit=(channel == fit_channel),
        channel_description=CHANNEL_DESCRIPTIONS[channel],
        note=note,
    )


def demo_previews() -> list[ChannelGatePreview]:
    """Small embedded demo set, illustrating the preview shape only."""

    return [
        build_preview(
            "status_snapshot",
            "dashboard_visible",
            "internal_review_queue",
            "General health summary, held for internal review before wider use.",
        ),
        build_preview(
            "approval_audit_trail",
            "local_only",
            "local_hud",
            "Kept for internal review; never sent through any channel.",
        ),
        build_preview(
            "notification_digest",
            "external_share_approved",
            "external_channel",
            "Weekly digest, already cleared for external delivery.",
        ),
        build_preview(
            "event_log_entry",
            "local_only",
            "external_channel",
            "Mismatch example: a local-only record requested for an external channel.",
        ),
    ]


def to_markdown(previews: list[ChannelGatePreview]) -> str:
    lines = [
        "# Notification Channel Gate Preview (Public-Safe Format Demo)",
        "",
        "This is a routing preview only -- no notification is sent here.",
        "",
        "| Record type | Visibility scope | Requested channel | Fit channel | Fit? | Note |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for p in previews:
        fit = "yes" if p.is_fit else "no"
        lines.append(
            f"| `{p.record_type}` | `{p.visibility_scope}` | `{p.requested_channel}` | "
            f"`{p.fit_channel}` | {fit} | {p.note} |"
        )
    return "\n".join(lines)


def to_json(previews: list[ChannelGatePreview]) -> str:
    return json.dumps([asdict(p) for p in previews], indent=2, sort_keys=True)


def _safe_output_path(raw: str):
    from pathlib import Path

    path = Path(raw)
    if path.is_absolute() or ".." in path.parts:
        raise ChannelGateError("--output must be a relative path with no '..' segments")
    return path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Preview a public-safe notification channel fit for a known record/scope pair."
    )
    parser.add_argument(
        "--record-type",
        choices=ALLOWED_RECORD_TYPES,
        help="Record type to preview a channel fit for.",
    )
    parser.add_argument(
        "--visibility-scope",
        choices=ALLOWED_VISIBILITY_SCOPES,
        help="Generic visibility scope label (see access_scope_preview.py).",
    )
    parser.add_argument(
        "--channel",
        choices=ALLOWED_CHANNELS,
        help="Generic channel label to check fitness for (never a real chat id/webhook).",
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

    single_fields = (args.record_type, args.visibility_scope, args.channel)
    if any(single_fields):
        if not all(single_fields):
            print(
                "ERROR: --record-type, --visibility-scope and --channel must be given together."
            )
            return 2
        try:
            previews = [
                build_preview(
                    args.record_type, args.visibility_scope, args.channel, args.note
                )
            ]
        except ChannelGateError as exc:
            print(f"channel_gate_error: {exc}")
            return 2
    else:
        previews = demo_previews()

    rendered = to_json(previews) if args.format == "json" else to_markdown(previews)
    print(rendered)

    if args.output:
        try:
            out_path = _safe_output_path(args.output)
        except ChannelGateError as exc:
            print(f"channel_gate_error: {exc}")
            return 2
        out_path.write_text(rendered + "\n", encoding="utf-8")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
