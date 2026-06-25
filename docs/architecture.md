# Architecture Notes

Jarvis / Hermes Core is a modular personal assistant concept. The public architecture intentionally avoids secrets, private infrastructure details, and sensitive device information.

## High-Level Layers

```text
User
 │
 ├── Telegram / Chat Interface
 │    └── commands, approvals, notifications
 │
 ├── Assistant Orchestration
 │    └── routing, memory, tools, scheduled jobs
 │
 ├── Workflow Modules
 │    ├── documents and OCR
 │    ├── media and YouTube helpers
 │    ├── weather/news/reminders
 │    ├── smart-home status and actions
 │    └── monitoring/watchdogs
 │
 ├── Local Knowledge
 │    └── notes, references, safe summaries
 │
 └── Dashboard / Jarvis HUD
      └── visual status and control surface
```

## Design Principles

### 1. Separate Public From Private

Public repo content should include:

- documentation
- generic examples
- templates
- non-sensitive architecture notes

Private runtime content should stay outside GitHub:

- API keys
- OAuth tokens
- home network addresses
- personal documents
- chat logs
- device credentials

### 2. Approval Levels

Suggested action categories:

- **Read-only** — status checks, summaries, searches.
- **Low-risk automatic** — routine reminders, safe notifications.
- **Approval-required** — posting, purchasing, booking, deleting, device control.
- **Blocked** — anything involving secrets, payment entry, or irreversible actions without user confirmation.

### 3. Modular Workflows

Each module should have:

- clear purpose
- inputs and outputs
- safety notes
- test command or verification step
- fallback/manual path

### 4. Dashboard Is Not the System

The dashboard should reflect real working services. It should not fake device state or workflow success. If a backend is unavailable, the dashboard should show that clearly.

### 5. Runtime Boundary Contract

Before a public module grows into a private runtime integration, document a small boundary contract:

- **Public surface** — synthetic inputs, schemas, dry-run previews, and generic usage notes that are safe to show in GitHub.
- **Private adapter** — credentials, local paths, account IDs, device identifiers, chat targets, and network details that must stay outside the public repository.
- **Approval path** — whether the module is read-only, preview-only, approval-required, strong-approval-required, private-runtime-only, or blocked.
- **Verification** — a safe test command or checklist that proves the public example works without contacting real services.

This keeps roadmap notes useful without implying that unfinished integrations are already connected to production accounts, devices, or personal data.

## Future Components

- `assistant-gateway/` — chat command entry points
- `workflows/` — reusable automation modules
- `dashboard/` — Jarvis-style visual interface
- `templates/` — prompt and document templates
- `examples/` — safe public examples

These folders can be added when real implementation code is ready.
