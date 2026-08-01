#!/usr/bin/env python3
"""Apply an immutable change bundle inside a prepared Codex task worktree.

This command deliberately has no Git integration, commit, patch creation, dry-run
or accept capability. It only materializes declared target bytes in the current
prepared detached task worktree after verifying bundle, task contract, paths,
hashes and modes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any

SCHEMA = "springmaster.codex-change-bundle.v1"
TASK_SCHEMA = "springmaster.agent-task.v2"
HEX64 = re.compile(r"^[0-9a-f]{64}$")
BUNDLE_ID = re.compile(r"^[a-z0-9][a-z0-9._-]{2,127}$")
TASK_ID = re.compile(r"^[A-Z][A-Z0-9-]{2,63}$")
ALLOWED_MODES = {"100644": 0o644, "100755": 0o755}
FORBIDDEN_PREFIXES = (
    ".git/", ".cocondo/", "patches/", "exports/", "target/", "build/", "tmp/"
)


class BundleError(RuntimeError):
    def __init__(self, code: str, message: str, **details: object) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details


def fail(condition: bool, code: str, message: str, **details: object) -> None:
    if not condition:
        raise BundleError(code, message, **details)


def run(argv: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(argv, cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    except FileNotFoundError as exc:
        raise BundleError("COMMAND_MISSING", "Required command is missing", command=argv[0]) from exc


def git(root: Path, *args: str) -> str:
    result = run(["git", *args], root)
    fail(result.returncode == 0, "GIT_COMMAND_FAILED", "Git command failed", argv=["git", *args], stderr=result.stderr[-2000:])
    return result.stdout.strip()


def sha_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_json_bytes(value: bytes, *, label: str) -> dict[str, Any]:
    try:
        parsed = json.loads(value.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise BundleError("JSON_INVALID", f"{label} is not valid UTF-8 JSON") from exc
    fail(isinstance(parsed, dict), "JSON_ROOT_INVALID", f"{label} root must be an object")
    return parsed


def canonical_relative(value: object) -> str:
    fail(isinstance(value, str) and value != "", "BUNDLE_PATH_INVALID", "Bundle path must be a non-empty string", path=value)
    pure = PurePosixPath(value)
    fail(not pure.is_absolute(), "BUNDLE_PATH_ABSOLUTE", "Bundle path must be relative", path=value)
    fail(all(part not in {"", ".", ".."} for part in pure.parts), "BUNDLE_PATH_TRAVERSAL", "Bundle path is not canonical", path=value)
    normalized = pure.as_posix()
    fail(not normalized.startswith(FORBIDDEN_PREFIXES) and normalized not in {".git", ".cocondo", "patches", "exports", "target", "build", "tmp"}, "BUNDLE_PATH_FORBIDDEN", "Bundle path is forbidden", path=normalized)
    return normalized


def configured_artifact_root(root: Path) -> Path:
    raw = os.environ.get("COCONDO_ARTIFACT_ROOT", "").strip()
    if not raw:
        result = run(["git", "config", "--path", "--get", "cocondo.artifactRoot"], root)
        if result.returncode == 0:
            raw = result.stdout.strip()
    fail(bool(raw), "ARTIFACT_ROOT_UNRESOLVED", "Artifact root is not configured")
    path = Path(raw).expanduser()
    fail(path.is_absolute() and path.is_dir() and not path.is_symlink(), "ARTIFACT_ROOT_INVALID", "Artifact root must be an existing absolute non-symlink directory", path=str(path))
    return path.resolve()


def path_below(parent: Path, child: Path) -> bool:
    try:
        child.relative_to(parent)
        return True
    except ValueError:
        return False


def assert_safe_target(root: Path, relative: str) -> Path:
    target = root / relative
    current = root
    for part in PurePosixPath(relative).parts[:-1]:
        current = current / part
        fail(not current.is_symlink(), "TARGET_PARENT_SYMLINK", "Target parent must not be a symlink", path=str(current))
        if current.exists():
            fail(current.is_dir(), "TARGET_PARENT_NOT_DIRECTORY", "Target parent is not a directory", path=str(current))
    fail(not target.is_symlink(), "TARGET_SYMLINK", "Target must not be a symlink", path=str(target))
    return target


def git_mode(path: Path) -> str | None:
    if not path.exists():
        return None
    fail(path.is_file(), "TARGET_NOT_REGULAR_FILE", "Target must be a regular file", path=str(path))
    executable = bool(path.stat().st_mode & stat.S_IXUSR)
    return "100755" if executable else "100644"


def validate_contract(value: dict[str, Any], task_id: str, base: str) -> list[str]:
    fail(value.get("schemaVersion") == TASK_SCHEMA, "TASK_CONTRACT_SCHEMA_INVALID", "Unsupported task contract schema")
    fail(value.get("taskId") == task_id, "TASK_ID_MISMATCH", "Task contract does not match invocation task", expected=task_id, actual=value.get("taskId"))
    fail(value.get("repositoryId") == "springmaster", "TASK_REPOSITORY_INVALID", "Task repository must be Springmaster")
    fail(value.get("mode") == "implementation", "TASK_MODE_INVALID", "Change bundles require an implementation task", mode=value.get("mode"))
    fail(value.get("baseCommit") == base, "TASK_BASE_MISMATCH", "Task contract base commit does not match worktree", expected=base, actual=value.get("baseCommit"))
    allowed = value.get("allowedPaths")
    fail(isinstance(allowed, list) and all(isinstance(item, str) and item for item in allowed), "TASK_ALLOWED_PATHS_INVALID", "Task allowed paths are invalid")
    return list(allowed)


def matches_allowed(path: str, patterns: list[str]) -> bool:
    import fnmatch
    return any(fnmatch.fnmatchcase(path, pattern) for pattern in patterns)


def validate_manifest(value: dict[str, Any], task_id: str, base: str, allowed: list[str]) -> list[dict[str, Any]]:
    fail(set(value) == {"schemaVersion", "bundleId", "taskId", "repositoryId", "baseCommit", "operations"}, "BUNDLE_FIELDS_INVALID", "Bundle manifest fields are invalid", fields=sorted(value))
    fail(value.get("schemaVersion") == SCHEMA, "BUNDLE_SCHEMA_INVALID", "Unsupported bundle schema")
    fail(isinstance(value.get("bundleId"), str) and BUNDLE_ID.fullmatch(value["bundleId"]) is not None, "BUNDLE_ID_INVALID", "Bundle ID is invalid")
    fail(value.get("taskId") == task_id and TASK_ID.fullmatch(task_id) is not None, "BUNDLE_TASK_MISMATCH", "Bundle task ID does not match prepared task", expected=task_id, actual=value.get("taskId"))
    fail(value.get("repositoryId") == "springmaster", "BUNDLE_REPOSITORY_INVALID", "Bundle repository must be Springmaster")
    fail(value.get("baseCommit") == base, "BUNDLE_BASE_MISMATCH", "Bundle base commit does not match prepared worktree", expected=base, actual=value.get("baseCommit"))
    operations = value.get("operations")
    fail(isinstance(operations, list) and 0 < len(operations) <= 200, "BUNDLE_OPERATIONS_INVALID", "Bundle operations must contain between 1 and 200 entries")
    normalized: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, item in enumerate(operations):
        fail(isinstance(item, dict), "BUNDLE_OPERATION_INVALID", "Bundle operation must be an object", index=index)
        fail(set(item) == {"path", "operation", "sourceSha256", "targetSha256", "mode"}, "BUNDLE_OPERATION_FIELDS_INVALID", "Bundle operation fields are invalid", index=index)
        path = canonical_relative(item.get("path"))
        fail(path not in seen, "BUNDLE_PATH_DUPLICATE", "Bundle path is duplicated", path=path)
        seen.add(path)
        fail(matches_allowed(path, allowed), "BUNDLE_PATH_OUTSIDE_TASK_SCOPE", "Bundle path is outside task allowed paths", path=path, allowedPaths=allowed)
        operation = item.get("operation")
        fail(operation in {"create", "replace", "delete"}, "BUNDLE_OPERATION_TYPE_INVALID", "Bundle operation type is invalid", path=path)
        source = item.get("sourceSha256")
        target = item.get("targetSha256")
        mode = item.get("mode")
        fail(source is None or (isinstance(source, str) and HEX64.fullmatch(source)), "BUNDLE_SOURCE_HASH_INVALID", "Source hash is invalid", path=path)
        fail(target is None or (isinstance(target, str) and HEX64.fullmatch(target)), "BUNDLE_TARGET_HASH_INVALID", "Target hash is invalid", path=path)
        fail(mode is None or mode in ALLOWED_MODES, "BUNDLE_MODE_INVALID", "Bundle mode is invalid", path=path)
        if operation == "create":
            fail(source is None and target is not None and mode is not None, "BUNDLE_CREATE_INVALID", "Create requires null source and target hash/mode", path=path)
        elif operation == "replace":
            fail(source is not None and target is not None and mode is not None, "BUNDLE_REPLACE_INVALID", "Replace requires source and target hash/mode", path=path)
        else:
            fail(source is not None and target is None and mode is None, "BUNDLE_DELETE_INVALID", "Delete requires source hash and null target/mode", path=path)
        normalized.append({"path": path, "operation": operation, "sourceSha256": source, "targetSha256": target, "mode": mode})
    return normalized


def read_bundle(bundle: Path) -> tuple[dict[str, Any], dict[str, bytes]]:
    fail(bundle.is_file() and not bundle.is_symlink(), "BUNDLE_FILE_INVALID", "Bundle must be a regular non-symlink ZIP", path=str(bundle))
    try:
        with zipfile.ZipFile(bundle) as archive:
            names = archive.namelist()
            fail(len(names) == len(set(names)), "BUNDLE_ZIP_DUPLICATE_ENTRY", "Bundle ZIP contains duplicate entries")
            fail("manifest.json" in names, "BUNDLE_MANIFEST_MISSING", "Bundle manifest.json is missing")
            payload: dict[str, bytes] = {}
            for info in archive.infolist():
                fail(not info.is_dir(), "BUNDLE_ZIP_DIRECTORY_ENTRY", "Bundle ZIP must not contain directory entries", entry=info.filename)
                path = PurePosixPath(info.filename)
                fail(not path.is_absolute() and all(part not in {"", ".", ".."} for part in path.parts), "BUNDLE_ZIP_PATH_INVALID", "Bundle ZIP entry is unsafe", entry=info.filename)
                mode = (info.external_attr >> 16) & 0o170000
                fail(mode != stat.S_IFLNK, "BUNDLE_ZIP_SYMLINK", "Bundle ZIP must not contain symlinks", entry=info.filename)
                if info.filename.startswith("payload/"):
                    relative = info.filename[len("payload/"):]
                    canonical_relative(relative)
                    payload[relative] = archive.read(info)
                elif info.filename != "manifest.json":
                    raise BundleError("BUNDLE_ZIP_ENTRY_UNEXPECTED", "Bundle ZIP contains an unexpected entry", entry=info.filename)
            return load_json_bytes(archive.read("manifest.json"), label="manifest.json"), payload
    except zipfile.BadZipFile as exc:
        raise BundleError("BUNDLE_ZIP_INVALID", "Bundle is not a valid ZIP") from exc


def apply_bundle(root: Path, bundle: Path, contract_path: Path, task_id: str) -> dict[str, Any]:
    fail(git(root, "rev-parse", "--show-toplevel") == str(root), "WORKTREE_ROOT_INVALID", "Current directory must be the task worktree root")
    branch = run(["git", "symbolic-ref", "-q", "HEAD"], root)
    fail(branch.returncode != 0, "WORKTREE_NOT_DETACHED", "Change bundles may only be applied in a detached task worktree")
    base = git(root, "rev-parse", "HEAD")
    status_raw = run(["git", "status", "--porcelain=v1", "-z", "--untracked-files=all"], root)
    fail(status_raw.returncode == 0, "GIT_STATUS_FAILED", "Cannot inspect task worktree status", stderr=status_raw.stderr[-2000:])
    artifact_root = configured_artifact_root(root)
    resolved_bundle = bundle.resolve()
    fail(path_below(artifact_root, resolved_bundle), "BUNDLE_OUTSIDE_ARTIFACT_ROOT", "Bundle must be below the configured external artifact root", bundle=str(resolved_bundle), artifactRoot=str(artifact_root))
    contract = load_json_bytes(contract_path.read_bytes(), label="task contract")
    allowed = validate_contract(contract, task_id, base)
    manifest, payload = read_bundle(resolved_bundle)
    operations = validate_manifest(manifest, task_id, base, allowed)
    expected_payload = {item["path"] for item in operations if item["operation"] != "delete"}
    fail(set(payload) == expected_payload, "BUNDLE_PAYLOAD_SET_MISMATCH", "Bundle payload set does not match operations", expected=sorted(expected_payload), actual=sorted(payload))
    targets: list[tuple[dict[str, Any], Path, bytes | None, str | None, str | None]] = []
    all_target = True
    all_source = True
    for item in operations:
        target = assert_safe_target(root, item["path"])
        exists = target.exists()
        current_hash = sha_file(target) if exists else None
        current_mode = git_mode(target) if exists else None
        target_hash = item["targetSha256"]
        source_hash = item["sourceSha256"]
        target_state = (not exists if item["operation"] == "delete" else exists and current_hash == target_hash and current_mode == item["mode"])
        source_state = (not exists if item["operation"] == "create" else exists and current_hash == source_hash)
        all_target = all_target and target_state
        all_source = all_source and source_state
        data = payload.get(item["path"])
        if data is not None:
            fail(sha_bytes(data) == target_hash, "BUNDLE_PAYLOAD_HASH_MISMATCH", "Payload hash does not match manifest", path=item["path"])
        targets.append((item, target, data, current_hash, current_mode))
    bundle_paths = {item["path"] for item in operations}
    status_paths: set[str] = set()
    entries = status_raw.stdout.split("\0")
    index = 0
    while index < len(entries):
        entry = entries[index]
        if not entry:
            break
        code = entry[:2]
        path = entry[3:].replace("\\", "/")
        if "R" in code or "C" in code:
            index += 1
            fail(index < len(entries) and entries[index], "GIT_STATUS_INVALID", "Rename/copy status is incomplete")
            path = entries[index].replace("\\", "/")
        status_paths.add(path)
        index += 1
    if all_target:
        fail(status_paths.issubset(bundle_paths), "WORKTREE_UNRELATED_CHANGES", "Task worktree contains changes outside the bundle", changedPaths=sorted(status_paths), bundlePaths=sorted(bundle_paths))
        return {"schemaVersion": "springmaster.codex-change-bundle-result.v1", "status": "ALREADY_APPLIED", "bundleId": manifest["bundleId"], "taskId": task_id, "baseCommit": base, "changedPaths": sorted(bundle_paths)}
    fail(all_source, "BUNDLE_SOURCE_STATE_MISMATCH", "Worktree is neither complete source state nor complete target state", states=[{"path": item["path"], "actualSha256": current_hash, "actualMode": current_mode} for item, _, _, current_hash, current_mode in targets])
    fail(not status_paths, "WORKTREE_NOT_CLEAN", "Task worktree must be clean before first bundle apply", changedPaths=sorted(status_paths))
    backups: list[tuple[Path, bytes | None, int | None]] = []
    created_dirs: list[Path] = []
    try:
        for item, target, data, _, _ in targets:
            backups.append((target, target.read_bytes() if target.exists() else None, stat.S_IMODE(target.stat().st_mode) if target.exists() else None))
            if item["operation"] == "delete":
                target.unlink()
                continue
            parent = target.parent
            missing: list[Path] = []
            probe = parent
            while probe != root and not probe.exists():
                missing.append(probe)
                probe = probe.parent
            for directory in reversed(missing):
                directory.mkdir(mode=0o755)
                created_dirs.append(directory)
            fd, temporary_name = tempfile.mkstemp(prefix=f".{target.name}.", dir=parent)
            try:
                with os.fdopen(fd, "wb") as handle:
                    handle.write(data or b"")
                    handle.flush()
                    os.fsync(handle.fileno())
                os.chmod(temporary_name, ALLOWED_MODES[item["mode"]])
                os.replace(temporary_name, target)
            finally:
                if os.path.exists(temporary_name):
                    os.unlink(temporary_name)
        for item, target, _, _, _ in targets:
            if item["operation"] == "delete":
                fail(not target.exists(), "BUNDLE_TARGET_VERIFY_FAILED", "Deleted target still exists", path=item["path"])
            else:
                fail(target.is_file() and sha_file(target) == item["targetSha256"] and git_mode(target) == item["mode"], "BUNDLE_TARGET_VERIFY_FAILED", "Target verification failed", path=item["path"])
    except Exception:
        for target, data, mode in reversed(backups):
            try:
                if data is None:
                    if target.exists() and target.is_file():
                        target.unlink()
                else:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(data)
                    if mode is not None:
                        target.chmod(mode)
            except Exception:
                pass
        for directory in reversed(created_dirs):
            try:
                directory.rmdir()
            except OSError:
                pass
        raise
    return {"schemaVersion": "springmaster.codex-change-bundle-result.v1", "status": "APPLIED", "bundleId": manifest["bundleId"], "taskId": task_id, "baseCommit": base, "changedPaths": sorted(item["path"] for item in operations)}


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser()
    result.add_argument("--project-root", default=".")
    result.add_argument("--format", choices=("human", "json"), default="human")
    sub = result.add_subparsers(dest="command", required=True)
    apply = sub.add_parser("apply")
    apply.add_argument("--bundle")
    apply.add_argument("--task-contract")
    apply.add_argument("--task-id")
    return result


def emit(value: dict[str, Any], fmt: str) -> None:
    if fmt == "json":
        print(json.dumps(value, sort_keys=True, ensure_ascii=False))
    else:
        for key in ("status", "bundleId", "taskId", "baseCommit"):
            if key in value:
                print(f"{key.upper()}={value[key]}")
        for path in value.get("changedPaths", []):
            print(f"CHANGED_PATH={path}")


def main() -> int:
    args = parser().parse_args()
    try:
        root = Path(args.project_root).resolve()
        bundle_raw = args.bundle or os.environ.get("SPRINGMASTER_CODEX_CHANGE_BUNDLE")
        contract_raw = args.task_contract or os.environ.get("SPRINGMASTER_AGENT_TASK_CONTRACT")
        task_id = args.task_id or os.environ.get("SPRINGMASTER_AGENT_TASK_ID")
        fail(bool(bundle_raw), "BUNDLE_PATH_MISSING", "Bundle path is required")
        fail(bool(contract_raw), "TASK_CONTRACT_PATH_MISSING", "Task contract path is required")
        fail(isinstance(task_id, str) and TASK_ID.fullmatch(task_id) is not None, "TASK_ID_INVALID", "Task ID is missing or invalid")
        value = apply_bundle(root, Path(str(bundle_raw)).expanduser(), Path(str(contract_raw)).expanduser(), task_id)
        emit(value, args.format)
        return 0
    except BundleError as exc:
        payload = {"status": "TOOL_ERROR", "errorCode": exc.code, "message": exc.message, **exc.details}
        if getattr(args, "format", "human") == "json":
            print(json.dumps(payload, sort_keys=True, ensure_ascii=False))
        else:
            print(f"STATUS=TOOL_ERROR\nERROR_CODE={exc.code}\nMESSAGE={exc.message}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
