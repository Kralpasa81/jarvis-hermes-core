# Jarvis / Hermes Core

**Personal AI command center for automation, smart-home workflows, Telegram tools, document/media helpers, and local knowledge systems.**

This repository is a public showcase and planning hub for a practical Jarvis-style assistant setup. It is intentionally safe for public GitHub: no tokens, private configuration, personal documents, API keys, chat exports, or home-network secrets should be committed here.

---

## Vision

Jarvis / Hermes Core is designed as a real-world personal automation layer, not just a demo dashboard.

The long-term goal is to connect useful everyday workflows into one reliable command center:

- Telegram-based assistant control
- smart-home status and action panels
- reminders, weather, news, and monitoring jobs
- document/PDF/OCR workflows
- media and YouTube automation helpers
- local knowledge search and personal notes
- safe integrations with APIs, devices, and home services

## Core Ideas

- **Practical first** — build things that actually help daily life.
- **Local-first where possible** — keep personal files, notes, and automation state under user control.
- **Safe by design** — public code stays separate from private tokens, device addresses, and personal data.
- **Modular** — each workflow should be understandable and replaceable.
- **Reliable over flashy** — dashboards are useful only when the underlying actions work.

## Planned Modules

| Area | Purpose |
| --- | --- |
| Assistant Gateway | Telegram and chat-based command interface |
| Smart Home | Device status, scenes, routines, safe control flows |
| Knowledge Base | Local notes, memories, search, summaries, references |
| Documents | OCR, PDFs, forms, translation support, admin workflows |
| Media Tools | YouTube/video helpers, Shorts ideas, transcripts, publishing support |
| Monitoring | Weather, news, services, reminders, watchdogs |
| Dashboard | Jarvis-style visual status and control overlay |

## Repository Structure

```text
.
├── README.md
├── docs/
│   ├── architecture.md
│   ├── daily/
│   │   └── YYYY-MM-DD.md
│   ├── roadmap.md
│   └── schemas/
│       └── status_snapshot.md
├── examples/
│   ├── access_scope_preview.py
│   ├── action_review.py
│   ├── approval_matrix.py
│   ├── config_template_validator.py
│   ├── daily_note_health_check.py
│   ├── dashboard_mock_data.py
│   ├── escalation_history_ledger.py
│   ├── escalation_path_preview.py
│   ├── example_catalog_indexer.py
│   ├── module_boundary_card.py
│   ├── module_handoff_checklist.py
│   ├── module_health_review.py
│   ├── module_preview_manifest.py
│   ├── module_registry_builder.py
│   ├── module_registry_health_digest.py
│   ├── notification_channel_gate.py
│   ├── notification_digest.py
│   ├── ocr_workflow_checklist.py
│   ├── public_payload_redactor.py
│   ├── public_safety_scan.py
│   ├── retention_policy_preview.py
│   ├── safe_command_router.py
│   ├── status_snapshot.py
│   ├── weekly_ledger_digest.py
│   └── workflow_readiness_gate.py
└── .gitignore
```

## What This Repo Is

- A public roadmap and documentation hub
- A clean showcase for the Jarvis / Hermes concept
- A place to collect safe examples and architecture notes
- A foundation for future code modules

## What This Repo Is Not

- It is not a dump of private Hermes configuration.
- It is not a place for API keys or tokens.
- It is not a place for personal documents or home network details.
- It is not claiming to be a finished commercial product.

## Safety Rules

Before committing anything, check:

- no `.env` files
- no tokens or API keys
- no private chat logs
- no personal documents
- no exact home-network secrets
- no device credentials

## Roadmap

See [`docs/roadmap.md`](docs/roadmap.md).

## Architecture Notes

See [`docs/architecture.md`](docs/architecture.md).

## Daily Lab Notes

Safe daily planning notes live in [`docs/daily/`](docs/daily/). They record goals, architecture thoughts, small next actions, future module ideas, and secret-safety reminders without exposing private data.

## Safe Examples

- [`examples/access_scope_preview.py`](examples/access_scope_preview.py) previews who, in generic terms, could see a known public-safe record type (e.g. an audit trail or dashboard snapshot) using visibility labels only — no real role, account id, or device address.
- [`examples/action_review.py`](examples/action_review.py) reviews a generic assistant action and prints a public-safe approval/risk preview without executing anything.
- [`examples/approval_audit_trail.py`](examples/approval_audit_trail.py) standardizes a public-safe approval-history record shape (who/what level approved an action and when) using only generic role labels, never real identities.
- [`examples/approval_matrix.py`](examples/approval_matrix.py) prints a public-safe action approval matrix as Markdown or JSON.
- [`examples/status_snapshot.py`](examples/status_snapshot.py) generates public-safe example status JSON for dashboards or assistant messages.
- [`examples/config_drift_detector.py`](examples/config_drift_detector.py) compares two config *schemas* (key names and value types only, never real values) and reports structural drift such as missing keys or type mismatches between environments.
- [`examples/config_template_validator.py`](examples/config_template_validator.py) checks a public-safe JSON config template shape without requiring secrets or private machine details.
- [`examples/daily_note_health_check.py`](examples/daily_note_health_check.py) is a keyword-based static check that reports, per `docs/daily/*.md` note, whether each expected section (focus, architecture note, actionable task, future module idea, security reminder) appears to be present — no note content is judged or modified, only section presence.
- [`examples/dashboard_mock_data.py`](examples/dashboard_mock_data.py) prints synthetic dashboard cards as JSON or Markdown for public-safe UI prototypes.
- [`examples/dependency_graph_reporter.py`](examples/dependency_graph_reporter.py) reads a module dependency definition and prints both a JSON report and a Mermaid.js diagram of the dependency graph.
- [`examples/escalation_history_ledger.py`](examples/escalation_history_ledger.py) previews how an escalation-worthy outcome from `escalation_path_preview.py` (`escalate_to_internal_review` or `request_human_approval`) would be recorded as a standard ledger entry, using only generic review-window and ledger-status labels — no real event log is written and no real date/reviewer is recorded.
- [`examples/escalation_path_preview.py`](examples/escalation_path_preview.py) previews which generic escalation step (e.g. silently drop, escalate to internal review, request human approval) fits a channel-fit mismatch from `notification_channel_gate.py`, using only public-safe labels — no real alert, page, or notification is sent.
- [`examples/example_catalog_indexer.py`](examples/example_catalog_indexer.py) cross-checks every `examples/*.py` docstring title and `Usage:` block against the README "Safe Examples" table and reports `ok` / `missing-usage` / `missing-readme` / `no-docstring` / `readme-only` per file — it never edits the README or any example file, only reports drift.
- [`examples/event_log_formatter.py`](examples/event_log_formatter.py) converts structured event log entries into human-readable text output.
- [`examples/capability_matrix_builder.py`](examples/capability_matrix_builder.py) evaluates a sample module list against safe capability categories and prints a capability matrix report.
- [`examples/integration_readiness_report.py`](examples/integration_readiness_report.py) evaluates a synthetic module description and prints a pass / warn / block integration readiness summary without calling APIs or reading private configuration.
- [`examples/module_boundary_card.py`](examples/module_boundary_card.py) generates a public-safe module boundary card that documents allowed inputs, blocked private data, approval policy, and safe preview behavior.
- [`examples/module_handoff_checklist.py`](examples/module_handoff_checklist.py) prints a public-safe handoff checklist for a proposed module before private adapters are attached.
- [`examples/module_health_review.py`](examples/module_health_review.py) reads a JSON module registry (file, stdin, or embedded demo data) and flags entries whose `next_review` date is overdue or due soon, using only safe status/date metadata.
- [`examples/module_preview_manifest.py`](examples/module_preview_manifest.py) generates a synthetic public contract for a future module, including mock inputs, blocked private data, preview outputs, and approval level.
- [`examples/module_registry_builder.py`](examples/module_registry_builder.py) prints a synthetic public-safe module registry for roadmap, dashboard, and review planning without reading private runtime configuration.
- [`examples/module_registry_health_digest.py`](examples/module_registry_health_digest.py) groups a fixed, embedded sample set of `module_registry_builder.py`-shaped entries into `ok` / `due-soon` / `overdue` review-health buckets, broken down by `status` and `approval_level` — no real module registry or daily note is read.
- [`examples/notification_channel_gate.py`](examples/notification_channel_gate.py) previews which generic notification channel (e.g. local HUD, internal review queue, external channel) fits a known record type and visibility scope, using only public-safe labels — no real chat id, webhook, or bot token.
- [`examples/notification_digest.py`](examples/notification_digest.py) prints a synthetic notification digest preview and marks items that require approval before external delivery.
- [`examples/ocr_workflow_checklist.py`](examples/ocr_workflow_checklist.py) prints a public-safe Markdown checklist for OCR/document workflow planning.
- [`examples/public_payload_redactor.py`](examples/public_payload_redactor.py) redacts risky key-name fields from synthetic JSON payloads before they are copied into public docs or dashboard mockups.
- [`examples/public_safety_scan.py`](examples/public_safety_scan.py) scans local repo files for high-signal public-safety risk patterns without printing matched secret-like values.
- [`examples/retention_policy_preview.py`](examples/retention_policy_preview.py) previews how long a known public-safe record type (e.g. an audit trail or dashboard snapshot) would be kept, using generic policy labels only — no real deletion job, deletion date, or storage location.
- [`examples/safe_command_router.py`](examples/safe_command_router.py) classifies a generic command into a module and approval level without executing actions or echoing private input text.
- [`examples/weekly_ledger_digest.py`](examples/weekly_ledger_digest.py) counts a fixed, embedded sample set of `escalation_history_ledger.py`-shaped entries and reports how many are `logged_pending_review` versus `logged_resolved`, grouped by record type — no real event log or daily note is read.
- [`examples/weekly_review_summary.py`](examples/weekly_review_summary.py) reads all Markdown daily notes from `docs/daily/` and prints a summary table (or JSON) showing each note's date, focus line, and whether a future-module idea or security reminder was mentioned. Supports `--week` to filter to the current calendar week.
- [`examples/workflow_readiness_gate.py`](examples/workflow_readiness_gate.py) evaluates whether a generic workflow is draft, preview-ready, approval-required, private-runtime-only, or blocked for public use.
- [`docs/schemas/status_snapshot.md`](docs/schemas/status_snapshot.md) documents the example payload shape and its safety boundaries.

---

**Simple. Useful. Reliable.**
