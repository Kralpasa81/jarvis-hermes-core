#!/usr/bin/env python3
"""Preview a public-safe escalation path for a channel-fit mismatch.

This is the module proposed in the 2026-07-17 daily note. There is no real
alerting/monitoring system here -- this tool only documents, in a standard
and public-safe way, *which generic escalation step* would apply if a
record/scope/channel combination (see `notification_channel_gate.py`) turns
out to be a mismatch (`is_fit=false`), before any real alerting layer
exists.

Safety rules enforced by this tool:
  - `record_type` must be one of the same small allow-list of already-public
    example record types used by `access_scope_preview.py`,
    `retention_policy_preview.py`, and `notification_channel_gate.py`
    (never an arbitrary free-text label).
  - `visibility_scope` must be one of the same allow-list of generic
    visibility labels defined in `access_scope_preview.py`
    ("local_only", "dashboard_visible", "external_share_approved"). It never
    accepts a real role name, account id, device id, or network location.
  - `channel` must be one of the same small allow-list of generic channel
    labels used by `notification_channel_gate.py` ("local_hud",
    "internal_review_queue", "external_channel"). It never accepts a real
    chat id, webhook URL, phone number, or bot token.
  - This tool sends no alert, triggers no page/call, and makes no network
    call. It only prints/writes an escalation-intent preview.
  - `--output` only accepts a relative path with no ".." segments (no path
    traversal), and writing is opt-in (stdout by default).

Escalation model (intentionally simple and conservative):
  - If the requested channel already matches the fit channel for the given
    visibility scope, no escalation is needed.
  - If the requested channel is *more open* than the fit channel allows
    (an over-exposure mismatch), this is treated as escalation-worthy:
      * a one-step gap escalates to internal review.
      * a two-step gap (e.g. a local-only record requested for the
        external channel) escalates to a human-approval request, since
        it is the most severe generic mismatch shape.
  - If the requested channel is *more restrictive* than the fit channel
    (an under-exposure mismatch, i.e. asking for less reach than allowed),
    this is treated as low-risk and is silently dropped from any
    escalation queue -- it is a missed opportunity, not a safety issue.

Usage:
  python3 examples/escalation_path_preview.py                  # demo preview
  python3 examples/escalation_path_preview.py --format json
  python3 examples/escalation_path_preview.py \\
      --record-type event_log_entry \\
      --visibility-scope local_only \\
      --channel external_channel \\
      --note "Mismatch example: local-only record requested externally."
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

ALLOWED_ESCALATION_ACTIONS = (
    "no_escalation_needed",
    "silently_drop",
    "escalate_to_internal_review",
    "request_human_approval",
)

# Same deterministic scope -> fit-channel mapping used by
# notification_channel_gate.py, kept self-contained here on purpose (this
# repo's convention is small, independently-readable preview modules rather
# than shared runtime imports between examples).
SCOPE_TO_FIT_CHANNEL = {
    "local_only": "local_hud",
    "dashboard_visible": "internal_review_queue",
    "external_share_approved": "external_channel",
}

# Generic openness ranking used only to size the *gap* between the
# requested channel and the fit channel -- never a real severity/priority
# system, just enough to pick a conservative escalation label.
CHANNEL_OPENNESS_RANK = {
    "local_hud": 0,
    "internal_review_queue": 1,
    "external_channel": 2,
}

ESCALATION_DESCRIPTIONS = {
    "no_escalation_needed": (
        "Requested channel already matches the fit channel for this "
        "visibility scope. Nothing to escalate."
    ),
    "silently_drop": (
        "Requested channel is more restrictive than the fit channel would "
        "allow. Treated as a missed-reach note, not a safety escalation."
    ),
    "escalate_to_internal_review": (
        "Requested channel is one step more open than the fit channel "
        "allows. Queue for a human or internal review step before wider "
        "distribution."
    ),
    "request_human_approval": (
        "Requested channel is significantly more open than the fit "
        "channel allows (e.g. a local-only record aimed at an external "
        "channel). Require an explicit human approval before anything "
        "would be sent."
    ),
}


class EscalationPathError(ValueError):
    """Raised when an escalation preview request fails the safety contract."""


@dataclass(frozen=True)
class EscalationPathPreview:
    """One standardized, public-safe escalation-path preview entry."""

    record_type: str
    visibility_scope: str
    requested_channel: str
    fit_channel: str
    is_fit: bool
    escalation_action: str
    escalation_description: str
    note: str


def _validate(record_type: str, visibility_scope: str, channel: str) -> None:
    if record_type not in ALLOWED_RECORD_TYPES:
        raise EscalationPathError(
            f"record_type must be one of {ALLOWED_RECORD_TYPES!r}, got {record_type!r}"
        )
    if visibility_scope not in ALLOWED_VISIBILITY_SCOPES:
        raise EscalationPathError(
            f"visibility_scope must be one of {ALLOWED_VISIBILITY_SCOPES!r}, "
            f"got {visibility_scope!r}"
        )
    if channel not in ALLOWED_CHANNELS:
        raise EscalationPathError(
            f"channel must be one of {ALLOWED_CHANNELS!r}, got {channel!r}"
        )


def _escalation_for_gap(fit_channel: str, requested_channel: str) -> str:
    if requested_channel == fit_channel:
        return "no_escalation_needed"

    gap = CHANNEL_OPENNESS_RANK[requested_channel] - CHANNEL_OPENNESS_RANK[fit_channel]
    if gap < 0:
        return "silently_drop"
    if gap == 1:
        return "escalate_to_internal_review"
    return "request_human_approval"


def build_preview(
    record_type: str, visibility_scope: str, channel: str, note: str
) -> EscalationPathPreview:
    _validate(record_type, visibility_scope, channel)
    fit_channel = SCOPE_TO_FIT_CHANNEL[visibility_scope]
    is_fit = channel == fit_channel
    action = _escalation_for_gap(fit_channel, channel)
    return EscalationPathPreview(
        record_type=record_type,
        visibility_scope=visibility_scope,
        requested_channel=channel,
        fit_channel=fit_channel,
        is_fit=is_fit,
        escalation_action=action,
        escalation_description=ESCALATION_DESCRIPTIONS[action],
        note=note,
    )


def demo_previews() -> list[EscalationPathPreview]:
    """Small embedded demo set, illustrating the preview shape only."""

    return [
        build_preview(
            "status_snapshot",
            "dashboard_visible",
            "internal_review_queue",
            "Fit channel already matches; nothing to escalate.",
        ),
        build_preview(
            "event_log_entry",
            "local_only",
            "internal_review_queue",
            "One-step gap: queue for internal review before wider use.",
        ),
        build_preview(
            "event_log_entry",
            "local_only",
            "external_channel",
            "Two-step gap: local-only record aimed at an external channel.",
        ),
        build_preview(
            "notification_digest",
            "external_share_approved",
            "local_hud",
            "Under-exposure: asking for less reach than approved, low risk.",
        ),
    ]


def to_markdown(previews: list[EscalationPathPreview]) -> str:
    lines = [
        "# Escalation Path Preview (Public-Safe Format Demo)",
        "",
        "This is an escalation-intent preview only -- no alert is sent here.",
        "",
        "| Record type | Visibility scope | Requested channel | Fit channel | Fit? | Escalation action | Note |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for p in previews:
        fit = "yes" if p.is_fit else "no"
        lines.append(
            f"| `{p.record_type}` | `{p.visibility_scope}` | `{p.requested_channel}` | "
            f"`{p.fit_channel}` | {fit} | `{p.escalation_action}` | {p.note} |"
        )
    return "\n".join(lines)


def to_json(previews: list[EscalationPathPreview]) -> str:
    return json.dumps([asdict(p) for p in previews], indent=2, sort_keys=True)


def _safe_output_path(raw: str):
    from pathlib import Path

    path = Path(raw)
    if path.is_absolute() or ".." in path.parts:
        raise EscalationPathError("--output must be a relative path with no '..' segments")
    return path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Preview a public-safe escalation path for a channel-fit mismatch."
    )
    parser.add_argument(
        "--record-type",
        choices=ALLOWED_RECORD_TYPES,
        help="Record type to preview an escalation path for.",
    )
    parser.add_argument(
        "--visibility-scope",
        choices=ALLOWED_VISIBILITY_SCOPES,
        help="Generic visibility scope label (see access_scope_preview.py).",
    )
    parser.add_argument(
        "--channel",
        choices=ALLOWED_CHANNELS,
        help="Generic channel label requested (never a real chat id/webhook).",
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
        except EscalationPathError as exc:
            print(f"escalation_path_error: {exc}")
            return 2
    else:
        previews = demo_previews()

    rendered = to_json(previews) if args.format == "json" else to_markdown(previews)
    print(rendered)

    if args.output:
        try:
            out_path = _safe_output_path(args.output)
        except EscalationPathError as exc:
            print(f"escalation_path_error: {exc}")
            return 2
        out_path.write_text(rendered + "\n", encoding="utf-8")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
