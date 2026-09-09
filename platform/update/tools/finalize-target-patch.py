#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import os
import re
import stat
import sys
import tempfile
import uuid
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ACTIVATION_CONTRACT = "contracts/governance/tooling/patch-toolkit-activation-contract.json"
ARTIFACT_ID_PREFIX = "urn:uuid:"
PATCH_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
NUMBERED_PATCH_ID_RE = re.compile(r"^\d{6}_[A-Za-z0-9][A-Za-z0-9._-]*$")
CHANGELOG_RE = re.compile(r"^CHANGELOG-[A-Za-z0-9._-]+\.md$")
PATCH_MANIFEST_SCHEMA_RE = re.compile(r'^PATCH_MANIFEST_SCHEMA\s*=\s*["\']([^"\']+)["\']\s*$', re.MULTILINE)
FIXED_ZIP_TIME = (1980, 1, 1, 0, 0, 0)


class FinalizeError(RuntimeError):
    pass


def fail(message: str) -> None:
    raise FinalizeError(message)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str | None:
    if not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def file_mode(path: Path) -> str:
    return "0755" if stat.S_IMODE(path.stat().st_mode) & 0o111 else "0644"


def validate_relpath(raw: str) -> str:
    value = raw.replace("\\", "/")
    while value.startswith("./"):
        value = value[2:]
    parts = value.split("/")
    if not value or value.startswith(("/", "~")) or any(part in ("", ".", "..") for part in parts):
        fail(f"unsafe relative path: {raw}")
    return "/".join(parts)


def validate_artifact_id(value: str) -> str:
    try:
        parsed = uuid.UUID(value.removeprefix(ARTIFACT_ID_PREFIX))
    except (ValueError, AttributeError) as exc:
        fail(f"invalid artifact id: {value!r}: {exc}")
    canonical = f"{ARTIFACT_ID_PREFIX}{parsed}"
    if value != canonical or parsed.int == 0:
        fail(f"artifact id must be canonical lowercase UUID URN: {value!r}")
    return value


def project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def load_artifact_model(root: Path) -> dict[str, Any]:
    contract_path = root / ACTIVATION_CONTRACT
    try:
        contract = json.loads(contract_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"cannot read Toolkit activation contract: {exc}")
    model = contract.get("artifactModel")
    adapter = model.get("platformUpdateLegacyV2Adapter") if isinstance(model, dict) else None
    if not isinstance(model, dict) or not isinstance(adapter, dict):
        fail("Toolkit activation contract has no Platform Update artifact model")
    runtime_rel = model.get("runtimePath")
    if not isinstance(runtime_rel, str):
        fail("Toolkit artifact model runtimePath is invalid")
    runtime = (root / runtime_rel).resolve()
    expected_digest = contract.get("runtimeSha256")
    if not runtime.is_file() or sha256_file(runtime) != expected_digest:
        fail("activation-bound Toolkit runtime is missing or has the wrong digest")
    sys.path.insert(0, str(runtime))
    try:
        manifest_module = importlib.import_module(str(model.get("manifestModule")))
        writer_module = importlib.import_module(str(model.get("writerModule")))
    except Exception as exc:
        fail(f"cannot load activation-bound Toolkit artifact model: {exc}")
    finally:
        if sys.path and sys.path[0] == str(runtime):
            sys.path.pop(0)
    if getattr(manifest_module, "PATCH_SCHEMA", None) != model.get("canonicalSchemaVersion"):
        fail("activation contract and Toolkit canonical schema differ")
    try:
        model["PatchManifest"] = getattr(manifest_module, str(model["manifestClass"]))
        model["PatchOperation"] = getattr(manifest_module, str(model["operationClass"]))
        model["write_patch"] = getattr(writer_module, str(model["writerFunction"]))
        model["inspect_patch"] = getattr(writer_module, str(model["inspectionFunction"]))
    except (AttributeError, KeyError) as exc:
        fail(f"activation-bound Toolkit artifact API is incomplete: {exc}")
    return model


def target_manifest_schema(target_root: Path, model: dict[str, Any]) -> str:
    patch_engine = target_root / "bin/patch.py"
    if not patch_engine.is_file():
        fail(f"target capability cannot be established: patch engine missing: {patch_engine}")
    match = PATCH_MANIFEST_SCHEMA_RE.search(patch_engine.read_text(encoding="utf-8"))
    if not match:
        fail(f"cannot resolve target patch manifest schema from {patch_engine}")
    value = match.group(1)
    suffix = model["platformUpdateLegacyV2Adapter"].get("schemaSuffix")
    if not isinstance(suffix, str) or not value.endswith(suffix):
        fail(f"target does not declare the supported legacy V2 capability: {value}")
    return value


def scope_log_dir(scope: str) -> str:
    known = {
        "root": "root", "bin": "bin", "tooling": "tooling", "platform": "platform",
        "core": "core", "demo": "demo", "app": "app", "resources": "resources",
        "tests": "tests", "docs": "docs", "db": "db", "templates": "templates",
        "planning": "planning", "target-registry": "target-registry",
        "platform-update": "platform-update",
    }
    return known.get(scope, scope)


def staging_candidates(root: Path, scope: str) -> list[tuple[Path | None, str, str]]:
    candidates: list[tuple[Path | None, str, str]] = []
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            fail(f"symlinks are forbidden in generated target patches: {path.relative_to(root)}")
    files_root = root / "files"
    if files_root.is_dir():
        for source in sorted(path for path in files_root.rglob("*") if path.is_file()):
            candidates.append((source, validate_relpath(source.relative_to(files_root).as_posix()), "payload"))
    delete_root = root / "delete"
    if delete_root.is_dir():
        for marker in sorted(path for path in delete_root.rglob("*") if path.is_file()):
            candidates.append((None, validate_relpath(marker.relative_to(delete_root).as_posix()), "delete"))
    logs_root = root / "logs"
    if logs_root.is_dir():
        for source in sorted(path for path in logs_root.rglob("*") if path.is_file()):
            if not CHANGELOG_RE.fullmatch(source.name):
                fail(f"invalid changelog filename: {source.relative_to(root)}")
            candidates.append((source, f"patches/logs/{scope_log_dir(scope)}/{source.name}", "changelog"))
    targets = [target for _source, target, _kind in candidates]
    if len(targets) != len(set(targets)):
        duplicate = next(path for path in targets if targets.count(path) > 1)
        fail(f"duplicate target operation: {duplicate}")
    if not any(kind == "changelog" for _source, _target, kind in candidates):
        fail("generated target patch requires logs/CHANGELOG-*.md")
    return candidates


def collect_canonical_operations(
    root: Path, target_root: Path, scope: str
) -> tuple[list[dict[str, Any]], dict[str, bytes]]:
    operations: list[dict[str, Any]] = []
    payloads: dict[str, bytes] = {}
    for source, target, kind in staging_candidates(root, scope):
        current = target_root / target
        if current.exists() and not current.is_file():
            fail(f"target path is not a regular file: {target}")
        before_hash = sha256_file(current)
        before_mode = file_mode(current) if current.is_file() else None
        if kind == "delete":
            if not current.is_file():
                continue
            operations.append({
                "type": "delete", "path": target, "beforeSha256": before_hash,
                "afterSha256": None, "beforeMode": before_mode, "afterMode": None, "payload": None,
            })
            continue
        assert source is not None
        data = source.read_bytes()
        after_hash = sha256_bytes(data)
        after_mode = file_mode(source)
        if before_hash == after_hash and before_mode == after_mode:
            continue
        op_type = "modify" if current.is_file() else "add"
        payload_name = f"payload/{target}"
        payloads[payload_name] = data
        operations.append({
            "type": op_type, "path": target, "beforeSha256": before_hash,
            "afterSha256": after_hash, "beforeMode": before_mode, "afterMode": after_mode,
            "payload": payload_name,
        })
    operations.sort(key=lambda item: item["path"])
    if not operations:
        fail("generated target patch has an empty effective payload")
    if not any(op["path"].startswith(f"patches/logs/{scope_log_dir(scope)}/CHANGELOG-") for op in operations):
        fail("effective target patch lost its changelog operation")
    return operations, payloads


def load_managed_state(root: Path, args: argparse.Namespace) -> dict[str, Any]:
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


def canonical_manifest(
    args: argparse.Namespace, model: dict[str, Any], operations: list[dict[str, Any]]
) -> dict[str, Any]:
    return {
        "schemaVersion": model["canonicalSchemaVersion"],
        "artifactId": args.artifact_id,
        "patchId": args.patch_id,
        "title": args.description or f"Springmaster Platform Update for {args.target_name}",
        "createdAt": args.created_at,
        "producer": {"name": "cocondo-patch-toolkit", "version": args.toolkit_version},
        "source": {"repositoryId": "springmaster", "baseCommit": None, "headCommit": None, "workspace": None},
        "target": {"requiredProjectId": args.target_name, "allowedScopes": [args.scope]},
        "operations": operations,
        "payloadSha256": "0" * 64,
    }


def legacy_manifest(
    args: argparse.Namespace,
    model: dict[str, Any],
    canonical: Any,
    target_schema: str,
) -> dict[str, Any]:
    adapter = model["platformUpdateLegacyV2Adapter"]
    expected = {op.path: op.before_sha256 for op in canonical.manifest.operations}
    requires: dict[str, Any] = {
        "target": args.target_name,
        "profile": args.profile,
        "masterPlatformVersion": args.master_platform_version,
        "masterCoreVersion": args.master_core_version,
        "masterToolingVersion": args.master_tooling_version,
        "masterPlatformUpdateVersion": args.master_platform_update_version,
    }
    if args.kind == "platform-update":
        managed_state = load_managed_state(args.root, args)
        requires["managedState"] = managed_state
        requires["compatibility"] = managed_state.get("compatibility")
    else:
        requires["requestedPatchScope"] = args.requested_scope
    return {
        "schemaVersion": target_schema,
        "artifactId": canonical.manifest.artifact_id,
        "id": args.patch_id,
        "patchId": args.patch_id,
        "name": args.name,
        "scope": args.scope,
        "description": args.description,
        "type": args.kind,
        "baseline": {"expectedBeforeSha256": expected},
        "requires": requires,
        adapter["canonicalProjectionField"]: {
            "adapterId": adapter["adapterId"],
            "selectionPolicy": adapter["selectionPolicy"],
            "manifest": canonical.manifest.to_dict(),
        },
        "changes": [
            "Derived from the activation-bound Cocondo Patch Toolkit artifact model",
            "Adapted to the target-declared legacy V2 capability",
            "Binds operation hashes and executable modes to the live target baseline",
        ],
    }


def legacy_member(operation: Any, scope: str) -> str:
    log_prefix = f"patches/logs/{scope_log_dir(scope)}/"
    if operation.path.startswith(log_prefix) and CHANGELOG_RE.fullmatch(Path(operation.path).name):
        return f"logs/{Path(operation.path).name}"
    if operation.type == "delete":
        return f"delete/{operation.path}"
    return f"files/{operation.path}"


def write_legacy_archive(output: Path, manifest: dict[str, Any], canonical: Any, scope: str) -> None:
    entries: dict[str, tuple[bytes, int]] = {
        "manifest.json": ((json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8"), 0o644)
    }
    for operation in canonical.manifest.operations:
        member = legacy_member(operation, scope)
        if member in entries:
            fail(f"duplicate legacy archive member: {member}")
        if operation.type == "delete":
            entries[member] = (b"", 0o644)
        else:
            entries[member] = (canonical.payloads[operation.payload], int(operation.after_mode, 8))
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name(f".{output.name}.tmp")
    temporary.unlink(missing_ok=True)
    try:
        with zipfile.ZipFile(temporary, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
            for name in sorted(entries):
                data, mode = entries[name]
                info = zipfile.ZipInfo(name, FIXED_ZIP_TIME)
                info.compress_type = zipfile.ZIP_DEFLATED
                info.create_system = 3
                info.external_attr = (stat.S_IFREG | mode) << 16
                archive.writestr(info, data)
        os.replace(temporary, output)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def inspect_legacy_artifact(zip_path: Path, root: Path | None = None) -> dict[str, Any]:
    root = root or project_root()
    model = load_artifact_model(root)
    adapter = model["platformUpdateLegacyV2Adapter"]
    try:
        with zipfile.ZipFile(zip_path) as archive:
            names = archive.namelist()
            if len(names) != len(set(names)) or "manifest.json" not in names:
                fail("legacy V2 artifact has missing or duplicate manifest entries")
            manifest = json.loads(archive.read("manifest.json"))
            schema = manifest.get("schemaVersion")
            if not isinstance(schema, str) or not schema.endswith(adapter["schemaSuffix"]):
                fail(f"unsupported target compatibility schema: {schema!r}")
            projection = manifest.get(adapter["canonicalProjectionField"])
            if projection is None:
                return {"manifest": manifest, "canonical": None, "adapter": adapter}
            if not isinstance(projection, dict) or projection.get("adapterId") != adapter["adapterId"]:
                fail("legacy V2 artifact adapter identity is invalid")
            if projection.get("selectionPolicy") != adapter["selectionPolicy"]:
                fail("legacy V2 artifact selection policy is invalid")
            canonical_manifest_data = projection.get("manifest")
            canonical_manifest_value = model["PatchManifest"].from_dict(canonical_manifest_data)
            if canonical_manifest_value.artifact_id != manifest.get("artifactId") or canonical_manifest_value.patch_id != manifest.get("patchId"):
                fail("legacy V2 identity differs from canonical artifact model")
            if canonical_manifest_value.target_project_id != (manifest.get("requires") or {}).get("target"):
                fail("legacy V2 target binding differs from canonical artifact model")
            if list(canonical_manifest_value.allowed_scopes) != [manifest.get("scope")]:
                fail("legacy V2 scope differs from canonical artifact model")
            baseline = (manifest.get("baseline") or {}).get("expectedBeforeSha256")
            expected = {op.path: op.before_sha256 for op in canonical_manifest_value.operations}
            if baseline != expected:
                fail("legacy V2 baseline differs from canonical artifact model")
            for operation in canonical_manifest_value.operations:
                member = legacy_member(operation, manifest["scope"])
                if member not in names:
                    fail(f"legacy V2 archive is missing canonical operation member: {member}")
                if operation.type != "delete":
                    data = archive.read(member)
                    mode = "0755" if (archive.getinfo(member).external_attr >> 16) & 0o111 else "0644"
                    if sha256_bytes(data) != operation.after_sha256 or mode != operation.after_mode:
                        fail(f"legacy V2 payload differs from canonical operation: {operation.path}")
            expected_names = {"manifest.json"} | {
                legacy_member(operation, manifest["scope"]) for operation in canonical_manifest_value.operations
            }
            if set(name for name in names if not name.endswith("/")) != expected_names:
                fail("legacy V2 archive members differ from canonical artifact model")
            return {"manifest": manifest, "canonical": canonical_manifest_value, "adapter": adapter}
    except (OSError, zipfile.BadZipFile, json.JSONDecodeError) as exc:
        fail(f"cannot inspect legacy V2 artifact: {exc}")


def nested_field(value: Any, field: str) -> Any:
    for part in field.split("."):
        if not isinstance(value, dict):
            return ""
        value = value.get(part, "")
    return value


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Finalize or inspect a target-bound Platform Update artifact.")
    parser.add_argument("--inspect", type=Path)
    parser.add_argument("--field")
    parser.add_argument("--root", type=Path)
    parser.add_argument("--target-root", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--patch-id")
    parser.add_argument("--artifact-id")
    parser.add_argument("--name")
    parser.add_argument("--scope")
    parser.add_argument("--target-name")
    parser.add_argument("--profile", default="")
    parser.add_argument("--kind", choices=("platform-update", "platform-update-compatibility"), default="platform-update")
    parser.add_argument("--requested-scope", default="")
    parser.add_argument("--description", default="")
    parser.add_argument("--created-at")
    parser.add_argument("--master-platform-version", default="")
    parser.add_argument("--master-core-version", default="")
    parser.add_argument("--master-tooling-version", default="")
    parser.add_argument("--master-platform-update-version", default="")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = project_root()
    if args.inspect:
        inspected = inspect_legacy_artifact(args.inspect.resolve(), root)
        value = nested_field(inspected["manifest"], args.field) if args.field else inspected["manifest"]
        print(json.dumps(value, ensure_ascii=False, sort_keys=True) if isinstance(value, (dict, list)) else value)
        return 0
    required = ("root", "target_root", "output", "patch_id", "name", "scope", "target_name")
    missing = [name for name in required if getattr(args, name) is None]
    if missing:
        fail(f"missing required arguments: {', '.join(missing)}")
    args.root = args.root.resolve()
    args.target_root = args.target_root.resolve()
    args.output = args.output.resolve()
    args.artifact_id = validate_artifact_id(args.artifact_id or f"urn:uuid:{uuid.uuid4()}")
    args.created_at = args.created_at or datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    if not args.root.is_dir() or not args.target_root.is_dir():
        fail("patch staging root and target root must exist")
    if not PATCH_ID_RE.fullmatch(args.patch_id):
        fail(f"invalid target patch id: {args.patch_id}")
    if args.kind == "platform-update" and not NUMBERED_PATCH_ID_RE.fullmatch(args.patch_id):
        fail(f"normal target patch id must be six-digit and target-local: {args.patch_id}")
    if args.patch_id != f"{args.patch_id.split('_', 1)[0]}_{args.name}":
        fail("patch id/name mismatch")
    model = load_artifact_model(root)
    args.toolkit_version = json.loads((root / ACTIVATION_CONTRACT).read_text(encoding="utf-8"))["toolkitVersion"]
    operations, payloads = collect_canonical_operations(args.root, args.target_root, args.scope)
    manifest = canonical_manifest(args, model, operations)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="platform-update-canonical-", dir=args.output.parent) as temp_dir:
        canonical_path = Path(temp_dir) / "canonical.zip"
        model["write_patch"](canonical_path, manifest, payloads, args.description or None)
        canonical = model["inspect_patch"](canonical_path)
        target_schema = target_manifest_schema(args.target_root, model)
        legacy = legacy_manifest(args, model, canonical, target_schema)
        write_legacy_archive(args.output, legacy, canonical, args.scope)
    inspected = inspect_legacy_artifact(args.output, root)
    canonical_value = inspected["canonical"]
    assert canonical_value is not None
    summary = {
        "adapterId": model["platformUpdateLegacyV2Adapter"]["adapterId"],
        "artifactId": args.artifact_id,
        "canonicalSchemaVersion": canonical_value.schema_version,
        "targetSchemaVersion": inspected["manifest"]["schemaVersion"],
        "patchId": args.patch_id,
        "scope": args.scope,
        "operationCount": len(canonical_value.operations),
        "new": sum(op.type == "add" for op in canonical_value.operations),
        "modified": sum(op.type == "modify" for op in canonical_value.operations),
        "deleted": sum(op.type == "delete" for op in canonical_value.operations),
        "modeOnly": sum(
            op.type == "modify" and op.before_sha256 == op.after_sha256 and op.before_mode != op.after_mode
            for op in canonical_value.operations
        ),
        "expectedBeforeSha256Count": len(canonical_value.operations),
        "operations": [op.path for op in canonical_value.operations],
    }
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except FinalizeError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        raise SystemExit(1)
