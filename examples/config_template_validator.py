#!/usr/bin/env python3
"""Validate a public-safe Jarvis / Hermes config template.

The validator is intentionally small and dependency-free. It checks the shape of
an example configuration without requiring real tokens, hostnames, device names,
or private paths. It is meant for public documentation and CI-style smoke tests,
not for loading private production configuration.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

ALLOWED_RISK_LEVELS = {"low", "approval-required", "private-data"}
FORBIDDEN_KEY_PATTERNS = (
    "api_key",
    "apikey",
    "auth",
    "credential",
    "oauth",
    "password",
    "secret",
    "token",
)
SECRET_LIKE_VALUE = re.compile(
    r"(?i)(ghp_[a-z0-9_]{20,}|xox[baprs]-|sk-[a-z0-9]{20,}|bot[0-9]{6,}:)"
)

SAFE_EXAMPLE: dict[str, Any] = {
    "assistant_name": "Jarvis / Hermes Core",
    "environment": "public-demo",
    "modules": [
        {"name": "status_dashboard", "enabled": True, "risk_level": "low"},
        {"name": "document_workflow", "enabled": False, "risk_level": "approval-required"},
        {"name": "local_knowledge", "enabled": False, "risk_level": "private-data"},
    ],
    "safety": {
        "allow_sensitive_values": False,
        "public_safe": True,
        "requires_human_approval_for_risky_actions": True,
    },
}


class ValidationError(ValueError):
    """Raised when a config template fails public-safety validation."""


def load_config(path: Path | None) -> dict[str, Any]:
    """Load config JSON from a file, or return the embedded safe example."""
    if path is None:
        return SAFE_EXAMPLE
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValidationError("top-level config must be a JSON object")
    return data


def scan_for_secret_like_content(value: Any, location: str = "config") -> list[str]:
    """Return public-safety issues found in keys or string values."""
    issues: list[str] = []
    if isinstance(value, dict):
        for key, nested in value.items():
            key_lower = str(key).lower()
            if any(pattern in key_lower for pattern in FORBIDDEN_KEY_PATTERNS):
                issues.append(f"{location}.{key}: secret-like key name is not allowed")
            issues.extend(scan_for_secret_like_content(nested, f"{location}.{key}"))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            issues.extend(scan_for_secret_like_content(item, f"{location}[{index}]"))
    elif isinstance(value, str) and SECRET_LIKE_VALUE.search(value):
        issues.append(f"{location}: value looks like a real secret/token")
    return issues


def validate_config(config: dict[str, Any]) -> list[str]:
    """Validate required fields and public-safety boundaries."""
    issues = scan_for_secret_like_content(config)

    if not isinstance(config.get("assistant_name"), str) or not config["assistant_name"].strip():
        issues.append("assistant_name must be a non-empty string")

    if not isinstance(config.get("environment"), str) or not config["environment"].strip():
        issues.append("environment must be a non-empty, non-sensitive label")

    modules = config.get("modules")
    if not isinstance(modules, list) or not modules:
        issues.append("modules must be a non-empty list")
    else:
        for index, module in enumerate(modules):
            prefix = f"modules[{index}]"
            if not isinstance(module, dict):
                issues.append(f"{prefix} must be an object")
                continue
            if not isinstance(module.get("name"), str) or not module["name"].strip():
                issues.append(f"{prefix}.name must be a non-empty string")
            if not isinstance(module.get("enabled"), bool):
                issues.append(f"{prefix}.enabled must be true or false")
            if module.get("risk_level") not in ALLOWED_RISK_LEVELS:
                allowed = ", ".join(sorted(ALLOWED_RISK_LEVELS))
                issues.append(f"{prefix}.risk_level must be one of: {allowed}")

    safety = config.get("safety")
    if not isinstance(safety, dict):
        issues.append("safety must be an object")
    else:
        if safety.get("allow_sensitive_values") is not False:
            issues.append("safety.allow_sensitive_values must be false for public templates")
        if safety.get("public_safe") is not True:
            issues.append("safety.public_safe must be true for public templates")
        if safety.get("requires_human_approval_for_risky_actions") is not True:
            issues.append(
                "safety.requires_human_approval_for_risky_actions must be true"
            )

    return issues


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate a public-safe Jarvis/Hermes JSON config template."
    )
    parser.add_argument(
        "--file",
        type=Path,
        help="Optional JSON file to validate. Uses an embedded safe example when omitted.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        config = load_config(args.file)
        issues = validate_config(config)
    except (OSError, json.JSONDecodeError, ValidationError) as exc:
        print(f"validation_error: {exc}", file=sys.stderr)
        return 2

    if issues:
        print("config_template_valid=false")
        for issue in issues:
            print(f"- {issue}")
        return 1

    print("config_template_valid=true")
    print(f"modules_checked={len(config['modules'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
