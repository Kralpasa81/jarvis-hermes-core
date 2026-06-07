# Roadmap

This roadmap keeps the Jarvis / Hermes Core idea practical and safe. Each phase should produce something usable before moving to the next one.

## Phase 1 — Public Foundation

- Create a clean public GitHub repository.
- Document the vision and safe boundaries.
- Add roadmap and architecture notes.
- Keep all secrets and private configuration outside the repo.

## Phase 2 — Command Center Design

- Define common assistant commands.
- Map Telegram workflows and notification patterns.
- Decide which actions are read-only, approval-required, or automatic.
- Design a simple dashboard/status view.

## Phase 3 — Automation Modules

Candidate modules:

- weather summaries
- news briefings
- document/PDF/OCR helpers
- reminders and calendar-style prompts
- YouTube/media support workflows
- service watchdogs and health checks

## Phase 4 — Smart Home Layer

- Inventory controllable device categories.
- Separate safe read-only status from real control actions.
- Add confirmation rules for risky actions.
- Document fallback/manual control paths.

## Phase 5 — Local Knowledge System

- Organize notes and references.
- Add local search and summaries.
- Keep personal data private.
- Create reusable templates for tasks and workflows.

## Phase 6 — Dashboard / Jarvis HUD

- Build a visual status overlay.
- Display only safe, non-sensitive data by default.
- Add cards for assistant status, smart home, weather, documents, and media.
- Avoid exposing private tokens, addresses, or personal files.

## Guiding Principle

Every feature should answer one question:

> Does this make daily life easier, safer, or more organized?
