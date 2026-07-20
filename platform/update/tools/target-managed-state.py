#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SCHEMA = "springmaster.managed-target-state.v1"
VERSION_KEYS = (
    "PLATFORM_VERSION",
    "PLATFORM_CORE_VERSION",
    "PLATFORM_TOOLING_VERSION",
    "PLATFORM_TEMPLATE_VERSION",
    "PLATFORM_DEMO_VERSION",
    "PLATFORM_UPDATE_VERSION",
)
ARTIFACT_RE = re.compile(r"^urn:uuid:[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$")
PATCH_RE = re.compile(r"^\d{6}_[A-Za-z0-9][A-Za-z0-9._-]*$")


class StateError(RuntimeError):
    pass


def fail(message: str) -> None:
    raise StateError(message)


def read_env(path: Path) -> tuple[list[str], dict[str, str]]:
    if not path.is_file():
        fail(f"platform version file missing: {path}")
    lines = path.read_text(encoding="utf-8").splitlines()
    values: dict[str, str] = {}
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        values[key.strip()] = value.strip()
    return lines, values


def write_env(lines: list[str], values: dict[str, str], output: Path) -> None:
    emitted: set[str] = set()
    rendered: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and "=" in stripped:
            key = stripped.split("=", 1)[0].strip()
            if key in values:
                rendered.append(f"{key}={values[key]}")
                emitted.add(key)
                continue
        rendered.append(line)
    for key in (
        "PLATFORM_TEMPLATE_VERSION",
        "PLATFORM_UPDATE_VERSION",
        "PLATFORM_STATE_PATCH",
        "PLATFORM_BASELINE_KIND",
    ):
        if key in values and key not in emitted:
            rendered.append(f"{key}={values[key]}")
            emitted.add(key)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(rendered).rstrip("\n") + "\n", encoding="utf-8")


def validate_identity(artifact_id: str, patch_id: str) -> None:
    if not ARTIFACT_RE.fullmatch(artifact_id):
        fail(f"invalid artifact id: {artifact_id}")
    if not PATCH_RE.fullmatch(patch_id):
        fail(f"invalid patch id: {patch_id}")


def component_keys(profile: str, rules_path: Path) -> tuple[str, ...]:
    try:
        rules = json.loads(rules_path.read_text(encoding="utf-8"))
        values = rules["profiles"][profile]["versionComponents"]
    except (OSError, json.JSONDecodeError, KeyError, TypeError) as exc:
        fail(f"cannot resolve versionComponents for profile {profile}: {exc}")
    if not isinstance(values, list) or not values or any(value not in VERSION_KEYS for value in values):
        fail(f"invalid versionComponents for profile {profile}")
    return tuple(values)


def synthesize(args: argparse.Namespace) -> int:
    validate_identity(args.artifact_id, args.patch_id)
    target_env = args.target_root / "platform/versions/platform.env"
    master_env = args.master_env
    target_lines, target_values = read_env(target_env)
    _, master_values = read_env(master_env)
    updated = dict(target_values)
    for key in VERSION_KEYS:
        updated.setdefault(key, "0.0.0")
    for key in component_keys(args.profile, args.rules):
        value = master_values.get(key)
        if not value:
            fail(f"master version key missing for profile {args.profile}: {key}")
        updated[key] = value
    updated["PLATFORM_STATE_PATCH"] = args.patch_id
    updated["PLATFORM_BASELINE_KIND"] = "managed-target"

    version_output = args.output_root / "platform/versions/platform.env"
    state_output = args.output_root / "platform/update/managed-state.json"
    write_env(target_lines, updated, version_output)

    previous_state_path = args.target_root / "platform/update/managed-state.json"
    previous: dict[str, object] | None = None
    if previous_state_path.is_file():
        try:
            previous_data = json.loads(previous_state_path.read_text(encoding="utf-8"))
            previous = {
                "artifactId": previous_data.get("artifactId"),
                "patchId": previous_data.get("patchId"),
                "profile": previous_data.get("profile"),
            }
        except json.JSONDecodeError as exc:
            fail(f"invalid previous managed state: {previous_state_path}: {exc}")

    installed = {key: updated.get(key, "") for key in VERSION_KEYS}
    source = {key: master_values.get(key, "") for key in VERSION_KEYS}
    try:
        compatibility = json.loads(args.compatibility_file.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"invalid compatibility decision: {exc}")
    if compatibility.get("status") != "PASS" or compatibility.get("profile") != args.profile:
        fail("compatibility decision is not a PASS for the selected profile")

    state = {
        "schemaVersion": SCHEMA,
        "status": "INSTALLED_BY_PATCH",
        "target": args.target_name,
        "artifactId": args.artifact_id,
        "patchId": args.patch_id,
        "profile": args.profile,
        "updatedComponents": list(component_keys(args.profile, args.rules)),
        "sourceMasterVersions": source,
        "installedVersions": installed,
        "platformStatePatch": args.patch_id,
        "previous": previous,
        "compatibility": compatibility,
    }
    state_output.parent.mkdir(parents=True, exist_ok=True)
    state_output.write_text(json.dumps(state, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(state_output)
    return 0


def verify(args: argparse.Namespace) -> int:
    validate_identity(args.artifact_id, args.patch_id)
    state_path = args.target_root / "platform/update/managed-state.json"
    compatibility_path = args.target_root / "platform/update/compatibility-decision.json"
    env_path = args.target_root / "platform/versions/platform.env"
    if not state_path.is_file():
        fail(f"managed state missing: {state_path}")
    if not compatibility_path.is_file():
        fail(f"compatibility decision missing: {compatibility_path}")
    state = json.loads(state_path.read_text(encoding="utf-8"))
    compatibility = json.loads(compatibility_path.read_text(encoding="utf-8"))
    _, env_values = read_env(env_path)
    expected = {
        "schemaVersion": SCHEMA,
        "status": "INSTALLED_BY_PATCH",
        "target": args.target_name,
        "artifactId": args.artifact_id,
        "patchId": args.patch_id,
        "profile": args.profile,
        "platformStatePatch": args.patch_id,
    }
    for key, value in expected.items():
        if state.get(key) != value:
            fail(f"managed state mismatch for {key}: expected={value!r} actual={state.get(key)!r}")
    if state.get("compatibility") != compatibility or compatibility.get("status") != "PASS":
        fail("managed state compatibility decision mismatch")
    installed = state.get("installedVersions")
    if not isinstance(installed, dict):
        fail("managed state installedVersions missing")
    for key in VERSION_KEYS:
        if installed.get(key, "") != env_values.get(key, ""):
            fail(f"installed version mismatch for {key}: state={installed.get(key)!r} env={env_values.get(key)!r}")
    if env_values.get("PLATFORM_STATE_PATCH") != args.patch_id:
        fail("PLATFORM_STATE_PATCH does not match applied patch")
    if env_values.get("PLATFORM_BASELINE_KIND") != "managed-target":
        fail("PLATFORM_BASELINE_KIND is not managed-target")
    print("TARGET_MANAGED_STATE=PASS")
    print(f"STATE={state_path}")
    return 0


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description="Synthesize and verify atomic managed target version/provenance state.")
    sub = root.add_subparsers(dest="command", required=True)
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--target-root", required=True, type=Path)
    common.add_argument("--target-name", required=True)
    common.add_argument("--profile", required=True)
    common.add_argument("--artifact-id", required=True)
    common.add_argument("--patch-id", required=True)
    synth = sub.add_parser("synthesize", parents=[common])
    synth.add_argument("--output-root", required=True, type=Path)
    synth.add_argument("--master-env", required=True, type=Path)
    synth.add_argument("--rules", required=True, type=Path)
    synth.add_argument("--compatibility-file", required=True, type=Path)
    sub.add_parser("verify", parents=[common])
    return root


def main() -> int:
    args = parser().parse_args()
    args.target_root = args.target_root.resolve()
    if args.command == "synthesize":
        args.output_root = args.output_root.resolve()
        args.master_env = args.master_env.resolve()
        args.rules = args.rules.resolve()
        args.compatibility_file = args.compatibility_file.resolve()
        return synthesize(args)
    return verify(args)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (StateError, json.JSONDecodeError) as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        raise SystemExit(1)
