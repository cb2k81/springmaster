#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SCHEMA = "springmaster.platform-update-profile-rules.v1"
PROFILE_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
FIELDS = {
    "scope": str,
    "payloadMode": str,
    "summary": str,
    "documentFamily": str,
    "requiresCorePom": bool,
    "synthesizeToolingCutoverConfig": bool,
    "acceptProfile": str,
    "fullTest": bool,
    "payloadPaths": list,
    "versionComponents": list,
}
ALLOWED_SCOPES = {"root", "core", "docs", "tooling", "demo", "platform-update"}
ALLOWED_ACCEPT = {"docs", "tooling", "code"}
ALLOWED_FAMILIES = {"core", "tooling", "platform-update", "general"}
ALLOWED_MODES = {"payload", "generated-document", "reserved"}
VERSION_KEYS = {
    "PLATFORM_CORE_VERSION",
    "PLATFORM_TOOLING_VERSION",
    "PLATFORM_TEMPLATE_VERSION",
    "PLATFORM_DEMO_VERSION",
    "PLATFORM_UPDATE_VERSION",
}


class RuleError(RuntimeError):
    pass


def load_rules(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuleError(f"cannot read profile rules {path}: {exc}") from exc
    if data.get("schemaVersion") != SCHEMA:
        raise RuleError(f"unsupported schemaVersion: {data.get('schemaVersion')!r}")
    profiles = data.get("profiles")
    if not isinstance(profiles, dict) or not profiles:
        raise RuleError("profiles must be a non-empty object")
    for name, rule in profiles.items():
        if not PROFILE_RE.fullmatch(name):
            raise RuleError(f"invalid profile name: {name!r}")
        if not isinstance(rule, dict):
            raise RuleError(f"profile {name} must be an object")
        missing = sorted(set(FIELDS) - set(rule))
        unknown = sorted(set(rule) - set(FIELDS))
        if missing or unknown:
            raise RuleError(f"profile {name} field mismatch: missing={missing} unknown={unknown}")
        for field, expected_type in FIELDS.items():
            if not isinstance(rule[field], expected_type):
                raise RuleError(f"profile {name}.{field} must be {expected_type.__name__}")
        if rule["scope"] not in ALLOWED_SCOPES:
            raise RuleError(f"profile {name} has unsupported scope {rule['scope']!r}")
        if rule["acceptProfile"] not in ALLOWED_ACCEPT:
            raise RuleError(f"profile {name} has unsupported acceptProfile")
        if rule["documentFamily"] not in ALLOWED_FAMILIES:
            raise RuleError(f"profile {name} has unsupported documentFamily")
        if rule["payloadMode"] not in ALLOWED_MODES:
            raise RuleError(f"profile {name} has unsupported payloadMode")
        for item in rule["payloadPaths"]:
            if not isinstance(item, str) or not item or item.startswith(("/", "~")) or ".." in Path(item).parts:
                raise RuleError(f"profile {name} contains unsafe payload path: {item!r}")
        if not rule["versionComponents"] or any(item not in VERSION_KEYS for item in rule["versionComponents"]):
            raise RuleError(f"profile {name} has invalid versionComponents")
        if rule["payloadMode"] == "payload" and not rule["payloadPaths"]:
            raise RuleError(f"profile {name} payload mode requires payloadPaths")
        if rule["payloadMode"] != "payload" and rule["payloadPaths"]:
            raise RuleError(f"profile {name} non-payload mode must not declare payloadPaths")
    return data


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Read and validate declarative Platform-Update profile rules.")
    parser.add_argument("--rules", required=True, type=Path)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("validate")
    sub.add_parser("profiles")
    get = sub.add_parser("get")
    get.add_argument("--profile", required=True)
    get.add_argument("--field", required=True, choices=sorted(FIELDS))
    paths = sub.add_parser("paths")
    paths.add_argument("--profile", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    data = load_rules(args.rules.resolve())
    profiles = data["profiles"]
    if args.command == "validate":
        print("PLATFORM_UPDATE_PROFILE_RULES=PASS")
        print(f"PROFILE_COUNT={len(profiles)}")
        return 0
    if args.command == "profiles":
        print("\n".join(sorted(profiles)))
        return 0
    if args.profile not in profiles:
        raise RuleError(f"unsupported update profile: {args.profile}")
    rule = profiles[args.profile]
    if args.command == "paths":
        print("\n".join(rule["payloadPaths"]))
        return 0
    value = rule[args.field]
    if isinstance(value, bool):
        print("true" if value else "false")
    elif isinstance(value, list):
        print("\n".join(value))
    else:
        print(value)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuleError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        raise SystemExit(1)
