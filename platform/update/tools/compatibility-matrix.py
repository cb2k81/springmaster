#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SCHEMA = "springmaster.platform-update-compatibility-matrix.v1"
VERSION_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)(?:[-+].*)?$")
COMPONENT_RE = re.compile(r"^PLATFORM_[A-Z0-9_]+_VERSION$")


class CompatibilityError(RuntimeError):
    pass


def parse_version(value: str) -> tuple[int, int, int]:
    match = VERSION_RE.fullmatch(value)
    if not match:
        raise CompatibilityError(f"unsupported semantic version: {value!r}")
    return tuple(int(part) for part in match.groups())


def read_env(path: Path) -> dict[str, str]:
    if not path.is_file():
        raise CompatibilityError(f"version file missing: {path}")
    values: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    return values


def load_matrix(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CompatibilityError(f"cannot read compatibility matrix {path}: {exc}") from exc
    if data.get("schemaVersion") != SCHEMA:
        raise CompatibilityError(f"unsupported matrix schema: {data.get('schemaVersion')!r}")
    policy = data.get("policy")
    profiles = data.get("profiles")
    if not isinstance(policy, dict) or set(policy) != {"denyCrossMajor", "denyDowngrade"}:
        raise CompatibilityError("matrix policy must define denyCrossMajor and denyDowngrade")
    if not all(isinstance(policy[key], bool) for key in policy):
        raise CompatibilityError("matrix policy flags must be boolean")
    if not isinstance(profiles, dict) or not profiles:
        raise CompatibilityError("matrix profiles must be a non-empty object")
    for profile, rule in profiles.items():
        if not isinstance(rule, dict) or set(rule) != {"allowMissingSource", "minimumSourceVersion", "sourceComponent"}:
            raise CompatibilityError(f"invalid compatibility rule fields for {profile}")
        if not isinstance(rule["allowMissingSource"], bool):
            raise CompatibilityError(f"allowMissingSource must be boolean for {profile}")
        if not isinstance(rule["sourceComponent"], str) or not COMPONENT_RE.fullmatch(rule["sourceComponent"]):
            raise CompatibilityError(f"invalid sourceComponent for {profile}")
        parse_version(rule["minimumSourceVersion"])
    return data


def decision(matrix: dict, profile: str, target_env: Path, master_env: Path) -> dict:
    rules = matrix["profiles"]
    if profile not in rules:
        raise CompatibilityError(f"profile not covered by compatibility matrix: {profile}")
    rule = rules[profile]
    source_key = rule["sourceComponent"]
    target_values = read_env(target_env)
    master_values = read_env(master_env)
    source_raw = target_values.get(source_key)
    source_assumed = False
    if not source_raw:
        if not rule["allowMissingSource"]:
            return {
                "schemaVersion": SCHEMA,
                "status": "FAIL",
                "profile": profile,
                "sourceComponent": source_key,
                "sourceVersion": None,
                "targetVersion": master_values.get(source_key),
                "minimumSourceVersion": rule["minimumSourceVersion"],
                "relation": "MISSING_SOURCE",
                "reason": f"target does not declare {source_key}",
                "sourceAssumed": False,
            }
        source_raw = "0.0.0"
        source_assumed = True
    target_raw = master_values.get(source_key)
    if not target_raw:
        raise CompatibilityError(f"master does not declare {source_key}")
    source = parse_version(source_raw)
    target = parse_version(target_raw)
    minimum = parse_version(rule["minimumSourceVersion"])
    status = "PASS"
    relation = "SAME" if source == target else "FORWARD" if source < target else "DOWNGRADE"
    reason = "supported source-to-target transition"
    if source < minimum:
        status, relation = "FAIL", "SOURCE_TOO_OLD"
        reason = f"source {source_raw} is below minimum {rule['minimumSourceVersion']}"
    elif matrix["policy"]["denyCrossMajor"] and source[0] != target[0]:
        status, relation = "FAIL", "CROSS_MAJOR_BLOCKED"
        reason = f"cross-major transition {source_raw} -> {target_raw} is not supported"
    elif matrix["policy"]["denyDowngrade"] and source > target:
        status, relation = "FAIL", "DOWNGRADE_BLOCKED"
        reason = f"downgrade {source_raw} -> {target_raw} is not supported"
    return {
        "schemaVersion": SCHEMA,
        "status": status,
        "profile": profile,
        "sourceComponent": source_key,
        "sourceVersion": source_raw,
        "targetVersion": target_raw,
        "minimumSourceVersion": rule["minimumSourceVersion"],
        "relation": relation,
        "reason": reason,
        "sourceAssumed": source_assumed,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate Platform-Update source/target version compatibility.")
    parser.add_argument("--matrix", required=True, type=Path)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("validate")
    check = sub.add_parser("check")
    check.add_argument("--profile", required=True)
    check.add_argument("--target-env", required=True, type=Path)
    check.add_argument("--master-env", required=True, type=Path)
    check.add_argument("--output", type=Path)
    check.add_argument("--json", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    matrix = load_matrix(args.matrix.resolve())
    if args.command == "validate":
        print("PLATFORM_UPDATE_COMPATIBILITY_MATRIX=PASS")
        print(f"PROFILE_COUNT={len(matrix['profiles'])}")
        return 0
    result = decision(matrix, args.profile, args.target_env.resolve(), args.master_env.resolve())
    if args.output:
        output = args.output.resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(result, sort_keys=True))
    else:
        print(f"PLATFORM_UPDATE_COMPATIBILITY={result['status']}")
        print(f"PROFILE={result['profile']}")
        print(f"COMPONENT={result['sourceComponent']}")
        print(f"SOURCE_VERSION={result['sourceVersion'] or ''}")
        print(f"TARGET_VERSION={result['targetVersion'] or ''}")
        print(f"RELATION={result['relation']}")
        print(f"REASON={result['reason']}")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except CompatibilityError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        raise SystemExit(1)
