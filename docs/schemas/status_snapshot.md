# Status Snapshot Schema

`examples/status_snapshot.py` produces a small JSON payload that can be used by dashboard mockups, Telegram message previews, or monitoring UI experiments.

The schema is intentionally public-safe and example-only. It must not include real tokens, exact device identifiers, personal documents, chat logs, home-network details, or credentials.

## Top-level fields

| Field | Type | Purpose |
| --- | --- | --- |
| `generated_at` | string | UTC timestamp for when the example payload was generated. |
| `profile` | string | Non-sensitive label such as `public-demo` or `dashboard-test`. |
| `assistant` | object | Generic assistant metadata for demos. |
| `modules` | array | List of example module states. |
| `rules` | array | Human-readable safety rules shown with the payload. |
| `safety` | object | Explicit flags documenting that the payload is public-safe. |

## Module object

| Field | Type | Example | Note |
| --- | --- | --- | --- |
| `name` | string | `weather_briefing` | Use generic names, not private hostnames or device IDs. |
| `status` | string | `planned` | Keep statuses honest: `planned`, `scheduled`, `ready`, or `blocked`. |
| `risk` | string | `approval-required` | Helps separate read-only work from actions needing confirmation. |

## Verification

Run the example without secrets:

```bash
python3 examples/status_snapshot.py --profile dashboard-test --module dashboard:planned:low
```

Expected behavior: valid JSON is printed to stdout, and the payload declares `contains_secrets: false`.
