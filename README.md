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
│   ├── action_review.py
│   ├── approval_matrix.py
│   ├── config_template_validator.py
│   ├── dashboard_mock_data.py
│   ├── module_boundary_card.py
│   ├── module_handoff_checklist.py
│   ├── module_preview_manifest.py
│   ├── module_registry_builder.py
│   ├── notification_digest.py
│   ├── ocr_workflow_checklist.py
│   ├── public_payload_redactor.py
│   ├── public_safety_scan.py
│   ├── safe_command_router.py
│   ├── status_snapshot.py
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

- [`examples/action_review.py`](examples/action_review.py) reviews a generic assistant action and prints a public-safe approval/risk preview without executing anything.
- [`examples/approval_matrix.py`](examples/approval_matrix.py) prints a public-safe action approval matrix as Markdown or JSON.
- [`examples/status_snapshot.py`](examples/status_snapshot.py) generates public-safe example status JSON for dashboards or assistant messages.
- [`examples/config_template_validator.py`](examples/config_template_validator.py) checks a public-safe JSON config template shape without requiring secrets or private machine details.
- [`examples/dashboard_mock_data.py`](examples/dashboard_mock_data.py) prints synthetic dashboard cards as JSON or Markdown for public-safe UI prototypes.
- [`examples/integration_readiness_report.py`](examples/integration_readiness_report.py) evaluates a synthetic module description and prints a pass / warn / block integration readiness summary without calling APIs or reading private configuration.
- [`examples/module_boundary_card.py`](examples/module_boundary_card.py) generates a public-safe module boundary card that documents allowed inputs, blocked private data, approval policy, and safe preview behavior.
- [`examples/module_handoff_checklist.py`](examples/module_handoff_checklist.py) prints a public-safe handoff checklist for a proposed module before private adapters are attached.
- [`examples/module_preview_manifest.py`](examples/module_preview_manifest.py) generates a synthetic public contract for a future module, including mock inputs, blocked private data, preview outputs, and approval level.
- [`examples/module_registry_builder.py`](examples/module_registry_builder.py) prints a synthetic public-safe module registry for roadmap, dashboard, and review planning without reading private runtime configuration.
- [`examples/notification_digest.py`](examples/notification_digest.py) prints a synthetic notification digest preview and marks items that require approval before external delivery.
- [`examples/ocr_workflow_checklist.py`](examples/ocr_workflow_checklist.py) prints a public-safe Markdown checklist for OCR/document workflow planning.
- [`examples/public_payload_redactor.py`](examples/public_payload_redactor.py) redacts risky key-name fields from synthetic JSON payloads before they are copied into public docs or dashboard mockups.
- [`examples/public_safety_scan.py`](examples/public_safety_scan.py) scans local repo files for high-signal public-safety risk patterns without printing matched secret-like values.
- [`examples/safe_command_router.py`](examples/safe_command_router.py) classifies a generic command into a module and approval level without executing actions or echoing private input text.
- [`examples/workflow_readiness_gate.py`](examples/workflow_readiness_gate.py) evaluates whether a generic workflow is draft, preview-ready, approval-required, private-runtime-only, or blocked for public use.
- [`docs/schemas/status_snapshot.md`](docs/schemas/status_snapshot.md) documents the example payload shape and its safety boundaries.

---

**Simple. Useful. Reliable.**
