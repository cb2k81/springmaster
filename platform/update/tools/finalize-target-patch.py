#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import stat
import sys
import uuid
from pathlib import Path

PATCH_MANIFEST_SCHEMA = "springmaster.patch-manifest.v2"
ARTIFACT_ID_PREFIX = "urn:uuid:"
PATCH_ID_RE = re.compile(r"^\d{6}_[A-Za-z0-9][A-Za-z0-9._-]*$")
CHANGELOG_RE = re.compile(r"^CHANGELOG-[A-Za-z0-9._-]+\.md$")


class FinalizeError(RuntimeError):
    pass


def validate_artifact_id(value: str) -> str:
    try:
        parsed = uuid.UUID(value.removeprefix(ARTIFACT_ID_PREFIX))
    except (ValueError, AttributeError) as exc:
        fail(f"invalid artifact id: {value!r}: {exc}")
    canonical = f"{ARTIFACT_ID_PREFIX}{parsed}"
    if value != canonical or parsed.int == 0:
        fail(f"artifact id must be canonical lowercase UUID URN: {value!r}")
    return value


def fail(message: str) -> None:
    raise FinalizeError(message)


def sha256_file(path: Path) -> str | None:
    if not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def executable(path: Path) -> bool:
    return bool(stat.S_IMODE(path.stat().st_mode) & 0o111)


def validate_relpath(raw: str) -> str:
    value = raw.replace("\\", "/")
    while value.startswith("./"):
        value = value[2:]
    parts = [part for part in value.split("/") if part]
    if not parts or value.startswith(("/", "~")) or any(part == ".." for part in parts):
        fail(f"unsafe relative path: {raw}")
    return "/".join(parts)


def scope_log_dir(scope: str) -> str:
    known = {
        "root": "root",
        "bin": "bin",
        "tooling": "tooling",
        "platform": "platform",
        "core": "core",
        "demo": "demo",
        "app": "app",
        "resources": "resources",
        "tests": "tests",
        "docs": "docs",
        "db": "db",
        "templates": "templates",
        "planning": "planning",
        "target-registry": "target-registry",
        "platform-update": "platform-update",
    }
    return known.get(scope, scope)


def collect_operations(root: Path, target_root: Path, scope: str) -> list[dict]:
    operations: list[dict] = []
    files_root = root / "files"
    logs_root = root / "logs"

    for candidate in sorted(root.rglob("*")):
        if candidate.is_symlink():
            fail(f"symlinks are forbidden in generated target patches: {candidate.relative_to(root)}")

    if files_root.is_dir():
        for source in sorted(files_root.rglob("*")):
            if not source.is_file():
                continue
            rel = validate_relpath(source.relative_to(files_root).as_posix())
            operations.append({"source": source, "target": rel, "kind": "file"})

    changelog_count = 0
    if logs_root.is_dir():
        for source in sorted(logs_root.rglob("*")):
            if not source.is_file():
                continue
            if not CHANGELOG_RE.fullmatch(source.name):
                fail(f"invalid changelog filename: {source.relative_to(root)}")
            target = f"patches/logs/{scope_log_dir(scope)}/{source.name}"
            operations.append({"source": source, "target": target, "kind": "file"})
            changelog_count += 1

    if changelog_count == 0:
        fail("generated target patch requires logs/CHANGELOG-*.md")
    if not operations:
        fail("generated target patch contains no operations")

    seen: set[str] = set()
    for operation in operations:
        if operation["target"] in seen:
            fail(f"duplicate target operation: {operation['target']}")
        seen.add(operation["target"])

    effective: list[dict] = []
    for operation in operations:
        source: Path = operation["source"]
        target = target_root / operation["target"]
        if target.exists() and not target.is_file():
            fail(f"target path is not a regular file: {operation['target']}")
        same = (
            target.is_file()
            and sha256_file(source) == sha256_file(target)
            and executable(source) == executable(target)
        )
        if same:
            source.unlink()
            continue
        effective.append(operation)

    if not effective:
        fail("all generated operations are unchanged")
    if not any(op["target"].startswith(f"patches/logs/{scope_log_dir(scope)}/CHANGELOG-") for op in effective):
        fail("effective target patch lost its changelog operation")
    return effective


def load_managed_state(root: Path, args: argparse.Namespace) -> dict:
    path = root / "files/platform/update/managed-state.json"
    if not path.is_file():
        fail("generated target patch requires files/platform/update/managed-state.json")
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"invalid managed target state: {exc}")
    expected = {
        "schemaVersion": "springmaster.managed-target-state.v1",
        "target": args.target_name,
        "artifactId": args.artifact_id,
        "patchId": args.patch_id,
        "profile": args.profile,
    }
    for key, value in expected.items():
        if state.get(key) != value:
            fail(f"managed target state mismatch for {key}: expected={value!r} actual={state.get(key)!r}")
    return state


def build_manifest(args: argparse.Namespace, operations: list[dict]) -> dict:
    expected: dict[str, str | None] = {}
    for operation in sorted(operations, key=lambda item: item["target"]):
        expected[operation["target"]] = sha256_file(args.target_root / operation["target"])

    managed_state = load_managed_state(args.root, args)

    return {
        "schemaVersion": PATCH_MANIFEST_SCHEMA,
        "artifactId": args.artifact_id,
        "id": args.patch_id,
        "patchId": args.patch_id,
        "name": args.name,
        "scope": args.scope,
        "description": (
            f"Generated Springmaster platform-update patch for target {args.target_name} "
            f"and profile {args.profile}."
        ),
        "type": "platform-update",
        "baseline": {"expectedBeforeSha256": expected},
        "requires": {
            "target": args.target_name,
            "profile": args.profile,
            "masterPlatformVersion": args.master_platform_version,
            "masterCoreVersion": args.master_core_version,
            "masterToolingVersion": args.master_tooling_version,
            "masterPlatformUpdateVersion": args.master_platform_update_version,
            "managedState": managed_state,
        },
        "changes": [
            "Uses a target-bound six-digit patch identity",
            "Contains complete live target baseline hashes",
            "Omits byte- and mode-identical payload files",
            "Requires producer artifact preflight before delivery",
            "Updates target component versions and provenance atomically with the payload",
        ],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Finalize a target-bound Springmaster platform-update patch.")
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--target-root", required=True, type=Path)
    parser.add_argument("--patch-id", required=True)
    parser.add_argument("--artifact-id", default=None)
    parser.add_argument("--name", required=True)
    parser.add_argument("--scope", required=True)
    parser.add_argument("--target-name", required=True)
    parser.add_argument("--profile", required=True)
    parser.add_argument("--master-platform-version", default="")
    parser.add_argument("--master-core-version", default="")
    parser.add_argument("--master-tooling-version", default="")
    parser.add_argument("--master-platform-update-version", default="")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    args.root = args.root.resolve()
    args.target_root = args.target_root.resolve()
    args.artifact_id = validate_artifact_id(args.artifact_id or f"urn:uuid:{uuid.uuid4()}")
    if not args.root.is_dir():
        fail(f"patch staging root missing: {args.root}")
    if not args.target_root.is_dir():
        fail(f"target root missing: {args.target_root}")
    if not PATCH_ID_RE.fullmatch(args.patch_id):
        fail(f"invalid target patch id: {args.patch_id}")
    expected_id = f"{args.patch_id.split('_', 1)[0]}_{args.name}"
    if args.patch_id != expected_id:
        fail(f"patch id/name mismatch: expected {expected_id}, got {args.patch_id}")

    operations = collect_operations(args.root, args.target_root, args.scope)
    manifest = build_manifest(args, operations)
    manifest_path = args.root / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    summary = {
        "artifactId": args.artifact_id,
        "patchId": args.patch_id,
        "scope": args.scope,
        "operationCount": len(operations),
        "new": sum(1 for op in operations if not (args.target_root / op["target"]).exists()),
        "modified": sum(1 for op in operations if (args.target_root / op["target"]).is_file()),
        "expectedBeforeSha256Count": len(manifest["baseline"]["expectedBeforeSha256"]),
        "operations": [op["target"] for op in sorted(operations, key=lambda item: item["target"])],
    }
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except FinalizeError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        raise SystemExit(1)
