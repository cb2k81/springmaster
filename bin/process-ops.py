#!/usr/bin/env python3
"""Project-neutral operational facade for detached Cocondo Toolkit runs."""

from __future__ import annotations

import argparse
import fcntl
import fnmatch
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import time
import zipfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

ACTIVE_STATES = {"STARTING", "WAITING_FOR_LOCK", "RUNNING"}
TERMINAL_STATES = {
    "DRY_RUN_SUCCEEDED",
    "SUCCEEDED",
    "SUCCEEDED_WITH_WARNINGS",
    "FAILED",
    "ABORTED",
    "ORPHANED",
    "INCONSISTENT",
}
FAILURE_STATES = {"FAILED", "ABORTED", "ORPHANED", "INCONSISTENT", "SUCCEEDED_WITH_WARNINGS"}
SINGLETON_KEY_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
PATCH_ID_PATTERN = re.compile(r"^(?P<number>[0-9]{6})_(?P<name>[A-Za-z0-9][A-Za-z0-9._-]*)$")
DELIVERY_ID_PATTERN = re.compile(r"^(?P<number>[0-9]{6})-(?P<name>[A-Za-z0-9][A-Za-z0-9._-]*)$")
DELIVERY_NAME_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,120}$")
DELIVERY_REVISION_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,120}$")
WORKSPACE_WRITERS = {"workspace-start", "patch-dry-run", "patch-accept", "diagnose", "incident", "diagnostic-handoff", "delivery-prepare"}
ARTIFACT_AUTHORIZATION_SCHEMA = "cocondo.artifact-root-authorization.v1"
DELIVERY_INVENTORY_SCHEMA = "cocondo.delivery-inventory.v1"
DELIVERY_RECORD_SCHEMA = "cocondo.delivery-record.v1"
WORKSPACE_SCHEMA = "cocondo.operator-workspace.v2"


class ProcessOpsError(RuntimeError):
    def __init__(self, code: str, message: str, **details: object) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details


@dataclass(frozen=True)
class Context:
    current_root: Path
    integration_root: Path
    git_common_dir: Path
    project_id: str
    integration_branch: str
    toolkit_run_root: Path
    toolkit_lock_root: Path
    toolkit_accepted_root: Path
    process_state_root: Path
    process_incident_root: Path
    process_delivery_root: Path
    artifact_authorization_record: Path
    operator_log_root: Path
    operator_work_root: Path
    artifact_root: Path | None
    artifact_root_source: str | None
    worktree_root: Path | None


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def run_command(
    command: list[str],
    *,
    cwd: Path,
    check: bool = False,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        command,
        cwd=cwd,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if check and completed.returncode != 0:
        raise ProcessOpsError(
            "COMMAND_FAILED",
            f"Command failed with exit code {completed.returncode}",
            command=command,
            stdout=completed.stdout[-4000:],
            stderr=completed.stderr[-4000:],
        )
    return completed


def git(root: Path, *args: str, check: bool = True) -> str:
    result = run_command(["git", *args], cwd=root, check=check)
    return result.stdout.strip()


def discover_root(explicit: str | None) -> Path:
    start = Path(explicit).expanduser() if explicit else Path.cwd()
    result = run_command(["git", "rev-parse", "--show-toplevel"], cwd=start, check=False)
    if result.returncode != 0 or not result.stdout.strip():
        raise ProcessOpsError("PROJECT_ROOT_NOT_FOUND", "No Git project root could be resolved", start=str(start))
    return Path(result.stdout.strip()).resolve()


def parse_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.is_file():
        return values
    for number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            raise ProcessOpsError("PROJECT_ENV_INVALID", "Invalid project env line", path=str(path), line=number)
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    return values


def parse_worktrees(root: Path) -> list[dict[str, str]]:
    output = git(root, "worktree", "list", "--porcelain")
    entries: list[dict[str, str]] = []
    current: dict[str, str] = {}
    for raw in output.splitlines() + [""]:
        if not raw:
            if current:
                entries.append(current)
                current = {}
            continue
        key, _, value = raw.partition(" ")
        current[key] = value
    return entries


def resolve_integration_root(root: Path, branch: str) -> Path:
    expected_ref = f"refs/heads/{branch}"
    matches = [Path(item["worktree"]).resolve() for item in parse_worktrees(root) if item.get("branch") == expected_ref]
    if len(matches) != 1:
        raise ProcessOpsError(
            "INTEGRATION_WORKTREE_UNRESOLVED",
            "Exactly one integration worktree is required",
            branch=branch,
            matches=[str(path) for path in matches],
        )
    return matches[0]


def resolve_config_path(value: str, *, project_root: Path, git_common_dir: Path) -> Path:
    path = Path(value).expanduser()
    if path.is_absolute():
        return Path(os.path.abspath(str(path)))
    parts = path.parts
    if parts and parts[0] == ".git":
        return Path(os.path.abspath(str(git_common_dir.joinpath(*parts[1:]))))
    return Path(os.path.abspath(str(project_root / path)))


def resolve_project_relative_runtime_path(value: str, *, project_root: Path, key: str) -> Path:
    if not value or value.startswith("~"):
        raise ProcessOpsError("PROCESS_PROJECT_PATH_INVALID", "Project runtime path must be a non-empty project-relative path", key=key, value=value)
    path = Path(value)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        raise ProcessOpsError("PROCESS_PROJECT_PATH_INVALID", "Project runtime path must not be absolute or escape the project", key=key, value=value)
    resolved = project_root.joinpath(*path.parts)
    try:
        resolved.relative_to(project_root)
    except ValueError as exc:
        raise ProcessOpsError("PROCESS_PROJECT_PATH_ESCAPE", "Project runtime path escapes the integration root", key=key, value=value) from exc
    if resolved == project_root or resolved == project_root / ".git":
        raise ProcessOpsError("PROCESS_PROJECT_PATH_INVALID", "Project runtime path must be a dedicated subdirectory", key=key, value=value)
    return resolved


def optional_path(value: str | None) -> Path | None:
    if not value:
        return None
    return Path(value).expanduser().resolve(strict=False)


def lexical_absolute_path(value: str, *, key: str) -> Path:
    path = Path(value).expanduser()
    if not path.is_absolute():
        raise ProcessOpsError(
            "EXTERNAL_ROOT_NOT_ABSOLUTE",
            "External root configuration must be absolute",
            key=key,
            value=value,
        )
    return Path(os.path.abspath(str(path)))


def resolve_configured_artifact_root(current_root: Path) -> tuple[Path | None, str | None]:
    env_value = os.environ.get("COCONDO_ARTIFACT_ROOT")
    git_value = git(current_root, "config", "--get", "cocondo.artifactRoot", check=False) or None
    configured: list[tuple[str, Path]] = []
    if env_value:
        configured.append(("environment:COCONDO_ARTIFACT_ROOT", lexical_absolute_path(env_value, key="COCONDO_ARTIFACT_ROOT")))
    if git_value:
        configured.append(("git-config:cocondo.artifactRoot", lexical_absolute_path(git_value, key="cocondo.artifactRoot")))
    if not configured:
        return None, None
    unique = {str(path) for _source, path in configured}
    if len(unique) != 1:
        raise ProcessOpsError(
            "ARTIFACT_ROOT_CONFIGURATION_AMBIGUOUS",
            "Environment and Git configuration select different artifact roots",
            configured=[{"source": source, "path": str(path)} for source, path in configured],
        )
    source = "+".join(item[0] for item in configured)
    return configured[0][1], source


def resolve_context(explicit_root: str | None) -> Context:
    current_root = discover_root(explicit_root)
    git_common_dir = Path(git(current_root, "rev-parse", "--path-format=absolute", "--git-common-dir")).resolve()
    project_env = parse_env_file(current_root / ".cocondo/tooling/project.env")
    process_env = parse_env_file(current_root / ".cocondo/process.env")
    project_id = project_env.get("CPATCH_PROJECT_ID") or current_root.name
    integration_branch = project_env.get("CPATCH_INTEGRATION_BRANCH", "main")
    integration_root = resolve_integration_root(current_root, integration_branch)

    toolkit_run_root = resolve_config_path(
        project_env.get("CPATCH_RUN_DIRECTORY", ".git/cocondo-toolkit/runs"),
        project_root=integration_root,
        git_common_dir=git_common_dir,
    )
    toolkit_lock_root = resolve_config_path(
        project_env.get("CPATCH_LOCK_DIRECTORY", ".git/cocondo-toolkit/locks"),
        project_root=integration_root,
        git_common_dir=git_common_dir,
    )
    toolkit_accepted_root = resolve_config_path(
        project_env.get("CPATCH_ACCEPTED_DIRECTORY", ".git/cocondo-toolkit/accepted"),
        project_root=integration_root,
        git_common_dir=git_common_dir,
    )
    process_state_root = resolve_config_path(
        process_env.get("CPROCESS_STATE_DIRECTORY", ".git/cocondo-process"),
        project_root=integration_root,
        git_common_dir=git_common_dir,
    )
    process_incident_root = resolve_config_path(
        process_env.get("CPROCESS_INCIDENT_DIRECTORY", ".git/cocondo-process/incidents"),
        project_root=integration_root,
        git_common_dir=git_common_dir,
    )
    process_delivery_root = resolve_config_path(
        process_env.get("CPROCESS_DELIVERY_DIRECTORY", ".git/cocondo-process/deliveries"),
        project_root=integration_root,
        git_common_dir=git_common_dir,
    )
    artifact_authorization_record = resolve_config_path(
        process_env.get(
            "CPROCESS_ARTIFACT_AUTHORIZATION_RECORD",
            ".git/cocondo-process/authorizations/artifact-root.json",
        ),
        project_root=integration_root,
        git_common_dir=git_common_dir,
    )
    operator_log_root = resolve_project_relative_runtime_path(
        process_env.get("CPROCESS_OPERATOR_LOG_DIRECTORY", "patches/logs/validation"),
        project_root=integration_root,
        key="CPROCESS_OPERATOR_LOG_DIRECTORY",
    )
    operator_work_root = resolve_project_relative_runtime_path(
        process_env.get("CPROCESS_WORK_DIRECTORY", "patches/work"),
        project_root=integration_root,
        key="CPROCESS_WORK_DIRECTORY",
    )

    artifact_root, artifact_root_source = resolve_configured_artifact_root(current_root)
    worktree_root = optional_path(
        os.environ.get("COCONDO_WORKTREE_ROOT")
        or git(current_root, "config", "--get", "cocondo.worktreeRoot", check=False)
        or None
    )

    git_common_paths = {
        "toolkitRunRoot": toolkit_run_root,
        "toolkitLockRoot": toolkit_lock_root,
        "toolkitAcceptedRoot": toolkit_accepted_root,
        "processStateRoot": process_state_root,
        "processIncidentRoot": process_incident_root,
        "processDeliveryRoot": process_delivery_root,
        "artifactAuthorizationRecord": artifact_authorization_record,
    }
    for role, path in git_common_paths.items():
        try:
            relative = path.relative_to(git_common_dir)
        except ValueError as exc:
            raise ProcessOpsError(
                "PROCESS_GIT_COMMON_PATH_INVALID",
                "Canonical runtime and authorization paths must remain below the Git common directory",
                role=role,
                path=str(path),
                gitCommonDirectory=str(git_common_dir),
            ) from exc
        current = git_common_dir
        for part in relative.parts:
            current = current / part
            if current.is_symlink():
                raise ProcessOpsError(
                    "PROCESS_GIT_COMMON_PATH_SYMLINK",
                    "Git-common runtime and authorization path components must not be symlinks",
                    role=role,
                    path=str(current),
                )

    return Context(
        current_root=current_root,
        integration_root=integration_root,
        git_common_dir=git_common_dir,
        project_id=project_id,
        integration_branch=integration_branch,
        toolkit_run_root=toolkit_run_root,
        toolkit_lock_root=toolkit_lock_root,
        toolkit_accepted_root=toolkit_accepted_root,
        process_state_root=process_state_root,
        process_incident_root=process_incident_root,
        process_delivery_root=process_delivery_root,
        artifact_authorization_record=artifact_authorization_record,
        operator_log_root=operator_log_root,
        operator_work_root=operator_work_root,
        artifact_root=artifact_root,
        artifact_root_source=artifact_root_source,
        worktree_root=worktree_root,
    )



def iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def safe_component(value: object, fallback: str) -> str:
    text = str(value or fallback)
    normalized = re.sub(r"[^A-Za-z0-9._-]+", "-", text).strip(".-")
    return normalized[:160] or fallback


def project_relative(context: Context, path: Path) -> str:
    try:
        return path.resolve(strict=False).relative_to(context.integration_root).as_posix()
    except ValueError as exc:
        raise ProcessOpsError("PROCESS_PROJECT_PATH_ESCAPE", "Path is outside the integration root", path=str(path)) from exc


def path_is_within(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def read_required_json(path: Path, *, error_code: str, message: str) -> dict[str, Any]:
    if path.is_symlink() or not path.is_file():
        raise ProcessOpsError(error_code, message, path=str(path))
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ProcessOpsError(error_code, message, path=str(path), detail=str(exc)) from exc
    if not isinstance(value, dict):
        raise ProcessOpsError(error_code, message, path=str(path), detail="JSON object required")
    return value


def validate_external_artifact_root(context: Context) -> tuple[Path, os.stat_result]:
    configured = context.artifact_root
    if configured is None:
        raise ProcessOpsError("ARTIFACT_ROOT_UNCONFIGURED", "No artifact root is configured")
    if configured.is_symlink():
        raise ProcessOpsError("ARTIFACT_ROOT_SYMLINK_FORBIDDEN", "Artifact root must not be a symlink", path=str(configured))
    if not configured.exists():
        raise ProcessOpsError("ARTIFACT_ROOT_MISSING", "Artifact root must already exist", path=str(configured))
    if not configured.is_dir():
        raise ProcessOpsError("ARTIFACT_ROOT_NOT_DIRECTORY", "Artifact root must be a directory", path=str(configured))
    try:
        canonical = configured.resolve(strict=True)
    except OSError as exc:
        raise ProcessOpsError("ARTIFACT_ROOT_CANONICALIZATION_FAILED", "Artifact root cannot be canonicalized", path=str(configured), detail=str(exc)) from exc
    if canonical != configured:
        raise ProcessOpsError(
            "ARTIFACT_ROOT_CANONICAL_MISMATCH",
            "Configured artifact root is not its canonical path",
            configuredPath=str(configured),
            canonicalPath=str(canonical),
        )
    forbidden_roots = [
        context.integration_root,
        context.git_common_dir,
        Path("/home"),
        Path("/root"),
        Path("/tmp"),
        Path("/var/tmp"),
        Path("/dev/shm"),
    ]
    try:
        operator_home = Path.home().resolve(strict=False)
    except Exception:
        operator_home = Path.home()
    forbidden_roots.append(operator_home)
    for forbidden in forbidden_roots:
        if canonical == forbidden or path_is_within(canonical, forbidden):
            raise ProcessOpsError(
                "ARTIFACT_ROOT_FORBIDDEN",
                "Artifact root is inside a forbidden location",
                path=str(canonical),
                forbiddenRoot=str(forbidden),
            )
    if os.path.ismount(canonical):
        # A dedicated external filesystem is allowed; the check is recorded, not rejected.
        pass
    metadata = canonical.stat()
    if metadata.st_mode & 0o222 == 0 or metadata.st_mode & 0o111 == 0:
        raise ProcessOpsError(
            "ARTIFACT_ROOT_NOT_WRITABLE",
            "Artifact root must have explicit write and search permission bits",
            path=str(canonical),
            mode=oct(stat.S_IMODE(metadata.st_mode)),
        )
    if not os.access(canonical, os.R_OK | os.W_OK | os.X_OK):
        raise ProcessOpsError("ARTIFACT_ROOT_NOT_WRITABLE", "Artifact root must be readable, writable and searchable", path=str(canonical))
    return canonical, metadata


def artifact_authorization_payload(context: Context) -> dict[str, Any]:
    canonical, metadata = validate_external_artifact_root(context)
    return {
        "schemaVersion": ARTIFACT_AUTHORIZATION_SCHEMA,
        "projectId": context.project_id,
        "configuredPath": str(context.artifact_root),
        "canonicalPath": str(canonical),
        "configurationSource": context.artifact_root_source,
        "device": metadata.st_dev,
        "inode": metadata.st_ino,
        "authorizedAt": iso_now(),
        "authorizationScope": "external-artifact-root",
        "rootCreatedByAuthorization": False,
    }


def verify_artifact_root_authorization(context: Context) -> Path:
    canonical, metadata = validate_external_artifact_root(context)
    record = read_required_json(
        context.artifact_authorization_record,
        error_code="ARTIFACT_ROOT_UNAUTHORIZED",
        message="Artifact root authorization record is missing or invalid",
    )
    expected = {
        "schemaVersion": ARTIFACT_AUTHORIZATION_SCHEMA,
        "projectId": context.project_id,
        "configuredPath": str(context.artifact_root),
        "canonicalPath": str(canonical),
        "device": metadata.st_dev,
        "inode": metadata.st_ino,
        "authorizationScope": "external-artifact-root",
        "rootCreatedByAuthorization": False,
    }
    mismatches = {
        key: {"expected": value, "actual": record.get(key)}
        for key, value in expected.items()
        if record.get(key) != value
    }
    if mismatches:
        raise ProcessOpsError(
            "ARTIFACT_ROOT_AUTHORIZATION_MISMATCH",
            "Artifact root authorization does not match the configured canonical root",
            path=str(context.artifact_authorization_record),
            mismatches=mismatches,
        )
    return canonical


def load_process_contract(context: Context) -> dict[str, Any]:
    # Runtime semantics are owned by the invoking worktree. Reading the
    # integration checkout here would make a qualified candidate depend on an
    # older contract until acceptance and would hide candidate-only policy.
    path = context.current_root / "contracts/governance/tooling/process-operations-contract.json"
    return read_required_json(
        path,
        error_code="PROCESS_CONTRACT_RUNTIME_INVALID",
        message="Process operations contract is missing or invalid",
    )


def delivery_inventory_policy(context: Context) -> dict[str, Any]:
    contract = load_process_contract(context)
    policy = contract.get("deliveryInventoryPolicy")
    if not isinstance(policy, dict):
        raise ProcessOpsError("DELIVERY_INVENTORY_POLICY_MISSING", "Delivery inventory policy is missing")
    return policy


def assert_no_symlink_components(
    project_root: Path,
    target: Path,
    *,
    error_code: str,
    path_role: str,
) -> None:
    current = project_root
    try:
        relative = target.relative_to(project_root)
    except ValueError as exc:
        raise ProcessOpsError(
            "PROCESS_PROJECT_PATH_ESCAPE",
            "Operator runtime path escapes the integration root",
            path=str(target),
            pathRole=path_role,
        ) from exc
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            raise ProcessOpsError(
                error_code,
                "Symlink component is forbidden",
                path=str(current),
                pathRole=path_role,
            )


def git_tracked_below(context: Context, path: Path) -> list[str]:
    relative = project_relative(context, path)
    output = git(context.integration_root, "ls-files", "--", relative, check=False)
    return [line for line in output.splitlines() if line.strip()]


def assert_runtime_path_ignored(context: Context, path: Path) -> None:
    relative = project_relative(context, path)
    probe = f"{relative}/.cocondo-ignore-probe"
    result = run_command(["git", "check-ignore", "-q", "--", probe], cwd=context.integration_root, check=False)
    if result.returncode != 0:
        raise ProcessOpsError("OPERATOR_RUNTIME_PATH_NOT_IGNORED", "Operator runtime path must be ignored by Git", path=relative)


def validate_workspace_tree(root: Path) -> None:
    if root.is_symlink():
        raise ProcessOpsError("OPERATOR_WORKSPACE_SYMLINK_FORBIDDEN", "Operator workspace root must not be a symlink", path=str(root))
    if not root.exists():
        raise ProcessOpsError("OPERATOR_WORKSPACE_MISSING", "Operator workspace root must already exist", path=str(root))
    if not root.is_dir():
        raise ProcessOpsError("OPERATOR_WORKSPACE_NOT_DIRECTORY", "Operator workspace root must be a directory", path=str(root))
    if os.path.ismount(root):
        raise ProcessOpsError("OPERATOR_WORKSPACE_MOUNT_FORBIDDEN", "Operator workspace root must not be a mount point", path=str(root))

    def inspect_directory(directory: Path) -> None:
        try:
            entries = sorted(os.scandir(directory), key=lambda item: item.name)
        except OSError as exc:
            raise ProcessOpsError("OPERATOR_WORKSPACE_READ_FAILED", "Operator workspace cannot be inventoried", path=str(directory), detail=str(exc)) from exc
        for entry in entries:
            path = Path(entry.path)
            if entry.name == ".git":
                raise ProcessOpsError("OPERATOR_WORKSPACE_NESTED_REPOSITORY", "Nested Git repository metadata is forbidden", path=str(path))
            mode = entry.stat(follow_symlinks=False).st_mode
            if stat.S_ISLNK(mode):
                raise ProcessOpsError("OPERATOR_WORKSPACE_SYMLINK_FORBIDDEN", "Symlink content is forbidden", path=str(path))
            if os.path.ismount(path):
                raise ProcessOpsError("OPERATOR_WORKSPACE_MOUNT_FORBIDDEN", "Mount point content is forbidden", path=str(path))
            if stat.S_ISDIR(mode):
                inspect_directory(path)
            elif not stat.S_ISREG(mode):
                raise ProcessOpsError("OPERATOR_WORKSPACE_SPECIAL_FILE_FORBIDDEN", "Only regular files and directories are allowed", path=str(path))

    inspect_directory(root)


def workspace_record_path(context: Context) -> Path:
    return context.operator_work_root / "WORKSPACE.json"


def read_workspace_record(context: Context) -> dict[str, Any] | None:
    path = workspace_record_path(context)
    if not path.exists() and not path.is_symlink():
        return None
    if path.is_symlink():
        raise ProcessOpsError("OPERATOR_WORKSPACE_RECORD_INVALID", "Workspace record must not be a symlink", path=str(path))
    record = read_json_file(path)
    if record is None:
        raise ProcessOpsError("OPERATOR_WORKSPACE_RECORD_INVALID", "Workspace record is not valid JSON", path=str(path))
    if record.get("schemaVersion") not in {"cocondo.operator-workspace.v1", WORKSPACE_SCHEMA}:
        raise ProcessOpsError("OPERATOR_WORKSPACE_RECORD_INVALID", "Workspace record schema is unsupported", path=str(path))
    return record


def workspace_run_status(context: Context, record: dict[str, Any]) -> str | None:
    run_id = record.get("runId")
    if not isinstance(run_id, str) or not run_id:
        record_status = str(record.get("status") or "")
        allowed_local_states = {"PREPARED", "COMPLETED", *TERMINAL_STATES}
        if record_status not in allowed_local_states:
            raise ProcessOpsError(
                "OPERATOR_WORKSPACE_STATUS_UNRESOLVED",
                "Prior workspace record has no resolvable run and no recognized local state",
                status=record_status or None,
                operation=record.get("operation"),
            )
        return record_status
    try:
        payload = status_payload(context, run_id)
    except ProcessOpsError as exc:
        raise ProcessOpsError("OPERATOR_WORKSPACE_STATUS_UNRESOLVED", "Prior workspace run status cannot be resolved", runId=run_id) from exc
    status = str(payload.get("status") or "UNKNOWN")
    if status not in ACTIVE_STATES and status not in TERMINAL_STATES:
        raise ProcessOpsError("OPERATOR_WORKSPACE_STATUS_UNRESOLVED", "Prior workspace run returned an unknown status", runId=run_id, status=status)
    return status


def clear_workspace_contents(root: Path) -> tuple[int, list[str], str]:
    entries: list[str] = []
    children = sorted(root.iterdir(), key=lambda item: item.name)
    for child in children:
        mode = child.lstat().st_mode
        kind = "directory" if stat.S_ISDIR(mode) else "file"
        entries.append(f"{kind}:{child.name}")
    for child in children:
        mode = child.lstat().st_mode
        if stat.S_ISDIR(mode):
            shutil.rmtree(child)
        elif stat.S_ISREG(mode):
            child.unlink()
        else:
            raise ProcessOpsError("OPERATOR_WORKSPACE_SPECIAL_FILE_FORBIDDEN", "Workspace changed after validation", path=str(child))
    digest = hashlib.sha256(("\n".join(entries) + ("\n" if entries else "")).encode("utf-8")).hexdigest()
    return len(entries), entries, digest


def prepare_operator_workspace(
    context: Context,
    operation: str,
    subject: str,
    *,
    run_reference: str | None = None,
) -> dict[str, Any]:
    lock_path = context.process_state_root / "locks" / "operator-workspace-start.lock"
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with lock_path.open("a+b") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        assert_no_symlink_components(
            context.integration_root,
            context.operator_work_root,
            error_code="OPERATOR_WORKSPACE_SYMLINK_FORBIDDEN",
            path_role="operator-workspace",
        )
        validate_workspace_tree(context.operator_work_root)
        tracked = git_tracked_below(context, context.operator_work_root)
        if tracked:
            raise ProcessOpsError("OPERATOR_WORKSPACE_TRACKED_CONTENT", "Tracked content below the operator workspace is forbidden", paths=tracked[:40])
        assert_runtime_path_ignored(context, context.operator_work_root)
        previous = read_workspace_record(context)
        if previous is not None:
            status = workspace_run_status(context, previous)
            if status in ACTIVE_STATES:
                raise ProcessOpsError(
                    "OPERATOR_WORKSPACE_ACTIVE",
                    "Active prior workflow blocks workspace cleanup",
                    runId=previous.get("runId"),
                    status=status,
                    operation=previous.get("operation"),
                )
        removed, removed_entries, removed_digest = clear_workspace_contents(context.operator_work_root)
        operation_id = f"{safe_component(operation, 'writer')}-{utc_stamp()}-{os.getpid()}-{time.time_ns() % 1000000:06d}"
        record: dict[str, Any] = {
            "schemaVersion": WORKSPACE_SCHEMA,
            "operationId": operation_id,
            "workflowId": operation_id,
            "projectId": context.project_id,
            "operation": operation,
            "subject": subject,
            "preparedAt": iso_now(),
            "status": "PREPARED",
            "removedEntryCount": removed,
            "removedEntryNames": removed_entries,
            "removedEntryListSha256": removed_digest,
            "workspaceRootPreserved": True,
            "canonicalRunState": "git-common-directory",
            "agentWritePolicy": "forbidden",
        }
        if run_reference:
            record["runId"] = run_reference
            record["boundRunReference"] = run_reference
        atomic_json(workspace_record_path(context), record)
        return record



def update_workspace_record(context: Context, payload: dict[str, Any], **extra: object) -> None:
    path = workspace_record_path(context)
    if not path.is_file():
        return
    record = read_workspace_record(context) or {}
    payload_run = payload.get("runId")
    record_run = record.get("runId")
    if record_run and payload_run and record_run != payload_run:
        return
    for key in ("runId", "artifactId", "patchId", "status", "phase", "message", "exitCode", "logFile"):
        if payload.get(key) is not None:
            record[key] = payload.get(key)
    record.update(extra)
    record["updatedAt"] = iso_now()
    atomic_json(path, record)


def prepare_operator_log_directory(context: Context, payload: dict[str, Any]) -> Path:
    assert_no_symlink_components(
        context.integration_root,
        context.operator_log_root,
        error_code="OPERATOR_LOG_SYMLINK_FORBIDDEN",
        path_role="operator-log-root",
    )
    context.operator_log_root.mkdir(parents=True, exist_ok=True)
    if context.operator_log_root.is_symlink() or not context.operator_log_root.is_dir():
        raise ProcessOpsError("OPERATOR_LOG_PATH_INVALID", "Operator log root must be a real directory", path=str(context.operator_log_root))

    patch_id = safe_component(payload.get("patchId"), "unscoped")
    run_id = safe_component(payload.get("runId"), "no-run-id")
    directory = context.operator_log_root / patch_id / run_id
    assert_no_symlink_components(
        context.integration_root,
        directory,
        error_code="OPERATOR_LOG_SYMLINK_FORBIDDEN",
        path_role="operator-run-log",
    )

    tracked = git_tracked_below(context, directory)
    if tracked:
        raise ProcessOpsError(
            "OPERATOR_LOG_TRACKED_CONTENT",
            "Tracked content below the current operator run log directory is forbidden",
            path=project_relative(context, directory),
            paths=tracked[:40],
        )

    assert_runtime_path_ignored(context, directory)
    directory.mkdir(parents=True, exist_ok=True)
    if directory.is_symlink() or not directory.is_dir():
        raise ProcessOpsError("OPERATOR_LOG_PATH_INVALID", "Operator run log path must be a real directory", path=str(directory))
    return directory


def operator_log_directory(context: Context, payload: dict[str, Any]) -> Path:
    patch_id = safe_component(payload.get("patchId"), "unscoped")
    run_id = safe_component(payload.get("runId"), "no-run-id")
    return context.operator_log_root / patch_id / run_id


def persist_operator_log(context: Context, operation: str, payload: dict[str, Any]) -> Path:
    directory = prepare_operator_log_directory(context, payload)
    target = directory / f"{utc_stamp()}-{safe_component(operation, 'operation')}.json"
    atomic_json(target, payload)
    return target


def append_operator_event(context: Context, payload: dict[str, Any]) -> Path:
    directory = prepare_operator_log_directory(context, payload)
    target = directory / "watch.jsonl"
    with target.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(compact(payload), sort_keys=True, separators=(",", ":")) + "\n")
    return target


def deterministic_zip(source_root: Path, target: Path) -> None:
    with zipfile.ZipFile(target, mode="x", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(item for item in source_root.rglob("*") if item.is_file()):
            info = zipfile.ZipInfo(path.relative_to(source_root).as_posix(), date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            info.create_system = 3
            archive.writestr(info, path.read_bytes())


def atomic_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def atomic_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(value, encoding="utf-8")
    os.replace(temporary, path)


def validate_singleton_key(value: str) -> str:
    if not SINGLETON_KEY_PATTERN.fullmatch(value):
        raise ProcessOpsError(
            "SINGLETON_KEY_INVALID",
            "Singleton key must use only letters, digits, dot, underscore and hyphen",
            singletonKey=value,
        )
    return value


def read_json_file(path: Path) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None



def require_inventory_directory(path: Path, *, code_prefix: str) -> None:
    if path.is_symlink():
        raise ProcessOpsError(f"{code_prefix}_SYMLINK", "Inventory root must not be a symlink", path=str(path))
    if not path.exists():
        raise ProcessOpsError(f"{code_prefix}_MISSING", "Inventory root must already exist", path=str(path))
    if not path.is_dir():
        raise ProcessOpsError(f"{code_prefix}_NOT_DIRECTORY", "Inventory root must be a directory", path=str(path))
    if os.path.ismount(path):
        raise ProcessOpsError(f"{code_prefix}_MOUNT_FORBIDDEN", "Inventory root must not be a mount point", path=str(path))


def canonical_patch_identity(value: object, *, source: str) -> tuple[int, str]:
    if not isinstance(value, str):
        raise ProcessOpsError("DELIVERY_PATCH_ID_INVALID", "Patch ID must be a canonical string", source=source, patchId=value)
    match = PATCH_ID_PATTERN.fullmatch(value)
    if match is None:
        raise ProcessOpsError("DELIVERY_PATCH_ID_INVALID", "Patch ID is not canonical", source=source, patchId=value)
    return int(match.group("number")), value


def canonical_delivery_identity(value: str, *, source: str) -> tuple[int, str]:
    match = DELIVERY_ID_PATTERN.fullmatch(value)
    if match is None:
        raise ProcessOpsError("DELIVERY_ID_INVALID", "Delivery directory name is not canonical", source=source, deliveryId=value)
    return int(match.group("number")), value


def legacy_numeric_patch_identity(
    record: dict[str, Any],
    *,
    source: str,
    policy: dict[str, Any],
) -> tuple[int, str] | None:
    value = record.get("patchId")
    numeric_pattern = policy.get("numericPatchIdPattern")
    if not isinstance(value, str) or not isinstance(numeric_pattern, str):
        return None
    if re.fullmatch(numeric_pattern, value) is None:
        return None

    expected_schema = policy.get("recordSchema")
    commands = policy.get("commands")
    artifact_pattern = policy.get("artifactFilePattern")
    artifact_id_pattern = policy.get("artifactIdPattern")
    if (
        not isinstance(expected_schema, str)
        or not isinstance(commands, list)
        or not all(isinstance(item, str) and item for item in commands)
        or not isinstance(artifact_pattern, str)
        or not isinstance(artifact_id_pattern, str)
    ):
        raise ProcessOpsError(
            "DELIVERY_INVENTORY_POLICY_INVALID",
            "Legacy numeric patch-run compatibility policy is incomplete",
        )

    if record.get("schemaVersion") != expected_schema or record.get("command") not in commands:
        raise ProcessOpsError(
            "DELIVERY_LEGACY_PATCH_RUN_UNVERIFIED",
            "Numeric legacy patch ID is not backed by an allowed run schema and command",
            source=source,
            patchId=value,
            schemaVersion=record.get("schemaVersion"),
            command=record.get("command"),
        )

    artifact_id = record.get("artifactId")
    metadata = record.get("metadata")
    artifact_file = metadata.get("artifactFile") if isinstance(metadata, dict) else None
    if not isinstance(artifact_id, str) or not isinstance(artifact_file, str) or Path(artifact_file).name != artifact_file:
        raise ProcessOpsError(
            "DELIVERY_LEGACY_PATCH_RUN_UNVERIFIED",
            "Numeric legacy patch ID lacks canonical artifact evidence",
            source=source,
            patchId=value,
            artifactId=artifact_id,
            artifactFile=artifact_file,
        )

    artifact_match = re.fullmatch(artifact_pattern, artifact_file)
    artifact_id_match = re.fullmatch(artifact_id_pattern, artifact_id)
    if artifact_match is None or artifact_id_match is None:
        raise ProcessOpsError(
            "DELIVERY_LEGACY_PATCH_RUN_UNVERIFIED",
            "Numeric legacy patch ID artifact evidence is not canonical",
            source=source,
            patchId=value,
            artifactId=artifact_id,
            artifactFile=artifact_file,
        )

    canonical_patch_id = artifact_match.group("patchId")
    artifact_token = artifact_match.group("artifactToken").lower()
    identity_token = artifact_id_match.group("artifactToken").lower()
    patch_number, canonical_patch_id = canonical_patch_identity(canonical_patch_id, source=source)
    if f"{patch_number:06d}" != value or artifact_token != identity_token:
        raise ProcessOpsError(
            "DELIVERY_LEGACY_PATCH_RUN_IDENTITY_CONFLICT",
            "Numeric legacy patch ID conflicts with canonical artifact evidence",
            source=source,
            patchId=value,
            canonicalPatchId=canonical_patch_id,
            artifactId=artifact_id,
            artifactFile=artifact_file,
        )
    return patch_number, canonical_patch_id


def read_delivery_record(directory: Path, delivery_id: str, delivery_number: int) -> tuple[str | None, dict[str, Any] | None]:
    path = directory / "delivery.json"
    if not path.exists() and not path.is_symlink():
        return None, None
    record = read_required_json(
        path,
        error_code="DELIVERY_RECORD_INVALID",
        message="Delivery record is unreadable or invalid",
    )
    if record.get("schemaVersion") != DELIVERY_RECORD_SCHEMA:
        raise ProcessOpsError("DELIVERY_RECORD_INVALID", "Delivery record schema is unsupported", path=str(path), actual=record.get("schemaVersion"))
    if record.get("deliveryId") != delivery_id:
        raise ProcessOpsError("DELIVERY_IDENTITY_CONFLICT", "Delivery record does not match its directory", path=str(path), deliveryId=delivery_id, recordDeliveryId=record.get("deliveryId"))
    patch_number, patch_id = canonical_patch_identity(record.get("patchId"), source=str(path))
    if patch_number != delivery_number:
        raise ProcessOpsError("DELIVERY_IDENTITY_CONFLICT", "Delivery and patch identities use different numbers", path=str(path), deliveryId=delivery_id, patchId=patch_id)
    delivery_name = delivery_id.split("-", 1)[1]
    patch_name = patch_id.split("_", 1)[1]
    record_name = record.get("name")
    if record_name != delivery_name or record_name != patch_name:
        raise ProcessOpsError(
            "DELIVERY_IDENTITY_CONFLICT",
            "Delivery directory, patch ID and record name do not describe one identity",
            path=str(path),
            deliveryName=delivery_name,
            patchName=patch_name,
            recordName=record_name,
        )
    revision = record.get("revision")
    if not isinstance(revision, str) or not DELIVERY_REVISION_PATTERN.fullmatch(revision):
        raise ProcessOpsError("DELIVERY_RECORD_INVALID", "Delivery record revision is not canonical", path=str(path), revision=revision)
    return patch_id, record


def accepted_patch_identity(
    record_path: Path,
    record: dict[str, Any],
    *,
    run_claims_by_artifact: dict[str, list[dict[str, Any]]],
    policy: dict[str, Any],
    project_id: str,
) -> tuple[int, str, str]:
    if record.get("schemaVersion") != policy.get("recordSchema"):
        raise ProcessOpsError(
            "DELIVERY_ACCEPTED_RECORD_INVALID",
            "Accepted patch record schema is unsupported",
            path=str(record_path),
            actual=record.get("schemaVersion"),
        )
    if record.get("projectId") != project_id:
        raise ProcessOpsError(
            "DELIVERY_ACCEPTED_RECORD_INVALID",
            "Accepted patch record belongs to another project",
            path=str(record_path),
            projectId=record.get("projectId"),
            expectedProjectId=project_id,
        )
    artifact_id = record.get("artifactId")
    artifact_pattern = policy.get("artifactIdPattern")
    if not isinstance(artifact_id, str) or not isinstance(artifact_pattern, str):
        raise ProcessOpsError(
            "DELIVERY_ACCEPTED_RECORD_INVALID",
            "Accepted patch record has no canonical artifact identity",
            path=str(record_path),
        )
    artifact_match = re.fullmatch(artifact_pattern, artifact_id)
    if artifact_match is None:
        raise ProcessOpsError(
            "DELIVERY_ACCEPTED_RECORD_INVALID",
            "Accepted patch artifact identity is invalid",
            path=str(record_path),
            artifactId=artifact_id,
        )
    artifact_uuid = artifact_match.group("artifactUuid").lower()
    if record_path.name.lower() != f"{artifact_uuid}.json":
        raise ProcessOpsError(
            "DELIVERY_ACCEPTED_RECORD_INVALID",
            "Accepted patch record filename does not match artifact identity",
            path=str(record_path),
            artifactId=artifact_id,
        )

    patch_id_value = record.get("patchId")
    if isinstance(patch_id_value, str) and PATCH_ID_PATTERN.fullmatch(patch_id_value):
        patch_number, patch_id = canonical_patch_identity(patch_id_value, source=str(record_path))
        return patch_number, patch_id, artifact_id

    numeric_pattern = policy.get("numericPatchIdPattern")
    if not isinstance(patch_id_value, str) or not isinstance(numeric_pattern, str) or re.fullmatch(numeric_pattern, patch_id_value) is None:
        raise ProcessOpsError(
            "DELIVERY_ACCEPTED_PATCH_ID_INVALID",
            "Accepted patch ID is neither canonical nor a supported legacy numeric ID",
            path=str(record_path),
            patchId=patch_id_value,
        )

    number = int(patch_id_value)
    candidates = {
        str(claim["patchId"])
        for claim in run_claims_by_artifact.get(artifact_id, [])
        if claim.get("command") == policy.get("numericResolutionCommand")
        and claim.get("status") == policy.get("numericResolutionStatus")
        and claim.get("number") == number
    }
    if len(candidates) != 1:
        raise ProcessOpsError(
            "DELIVERY_ACCEPTED_PATCH_ID_UNRESOLVED",
            "Legacy numeric accepted patch ID cannot be resolved to one canonical identity",
            path=str(record_path),
            patchId=patch_id_value,
            artifactId=artifact_id,
            candidates=sorted(candidates),
        )
    return number, next(iter(candidates)), artifact_id


def build_delivery_inventory(
    context: Context,
    *,
    current_delivery: str | None = None,
    patch_name: str | None = None,
) -> dict[str, Any]:
    policy = delivery_inventory_policy(context)
    known_patterns = policy.get("knownMetadataPatterns")
    if not isinstance(known_patterns, list) or not known_patterns or not all(isinstance(item, str) and item for item in known_patterns):
        raise ProcessOpsError("DELIVERY_INVENTORY_POLICY_INVALID", "Known metadata patterns are missing or invalid")
    scope_fields = policy.get("patchScopeFields")
    if not isinstance(scope_fields, list) or not scope_fields or not all(isinstance(item, str) and item for item in scope_fields):
        raise ProcessOpsError("DELIVERY_INVENTORY_POLICY_INVALID", "Patch scope fields are missing or invalid")
    expected_entry_policies = {
        "deliveryDirectory": "RESERVE",
        "knownHistoricalMetadata": "IGNORE_AND_COUNT",
        "genericRunRecord": "IGNORE_AND_COUNT",
        "patchRunRecord": "RESERVE",
        "legacyNumericPatchRunRecord": "RESERVE",
        "acceptedPatchRecord": "RESERVE",
        "historicalFailedRunUnderAcceptedOwner": "IGNORE_AND_COUNT",
        "currentDelivery": "CURRENT_DELIVERY_EXCEPTION",
        "unknownRegularFile": "BLOCKING_TOOL_ERROR",
        "symlink": "BLOCKING_TOOL_ERROR",
        "specialFile": "BLOCKING_TOOL_ERROR",
        "unreadableOrInconsistentJson": "BLOCKING_TOOL_ERROR",
        "identityConflict": "BLOCKING_TOOL_ERROR",
    }
    if policy.get("entryPolicies") != expected_entry_policies:
        raise ProcessOpsError("DELIVERY_INVENTORY_POLICY_INVALID", "Entry policies are incomplete or inconsistent")
    if policy.get("freeTextNumbersReserveIdentity") is not False or policy.get("currentDeliveryMatchCount") != 1:
        raise ProcessOpsError("DELIVERY_INVENTORY_POLICY_INVALID", "Identity policy is incomplete or inconsistent")
    legacy_policy = policy.get("legacyNumericPatchRunCompatibility")
    if not isinstance(legacy_policy, dict) or legacy_policy.get("policy") != "RESERVE":
        raise ProcessOpsError("DELIVERY_INVENTORY_POLICY_INVALID", "Legacy numeric patch-run compatibility policy is missing")
    accepted_policy = policy.get("acceptedPatchAuthority")
    expected_accepted_policy = {
        "policy": "RESERVE",
        "recordSchema": "cocondo.patch-acceptance.v2",
        "artifactIdPattern": "^urn:uuid:(?P<artifactUuid>[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})$",
        "numericPatchIdPattern": "^[0-9]{6}$",
        "numericResolutionCommand": "patch-accept",
        "numericResolutionStatus": "SUCCEEDED",
        "historicalFailedStatuses": ["ABORTED", "FAILED", "INCONSISTENT", "ORPHANED"],
        "differentDeliveryOrNonFailedRun": "BLOCKING_TOOL_ERROR",
        "multipleAcceptedOwners": "BLOCKING_TOOL_ERROR",
    }
    if accepted_policy != expected_accepted_policy:
        raise ProcessOpsError("DELIVERY_INVENTORY_POLICY_INVALID", "Accepted patch authority policy is missing or inconsistent")
    historical_failed_statuses = set(accepted_policy["historicalFailedStatuses"])

    require_inventory_directory(context.process_delivery_root, code_prefix="DELIVERY_ROOT")
    entries: list[dict[str, Any]] = []
    reserved_numbers: set[int] = set()
    identity_claims: dict[int, list[dict[str, Any]]] = {}
    run_claims_by_artifact: dict[str, list[dict[str, Any]]] = {}
    current_exception_count = 0
    known_metadata_count = 0
    delivery_directory_count = 0
    generic_run_count = 0
    patch_run_count = 0
    legacy_numeric_patch_run_count = 0
    accepted_patch_record_count = 0
    accepted_owner_count = 0
    historical_failed_attempt_count = 0

    for entry in sorted(context.process_delivery_root.iterdir(), key=lambda item: item.name):
        mode = entry.lstat().st_mode
        if stat.S_ISLNK(mode):
            raise ProcessOpsError("DELIVERY_INVENTORY_SYMLINK", "Delivery inventory contains a symlink", path=str(entry))
        if stat.S_ISDIR(mode):
            delivery_number, delivery_id = canonical_delivery_identity(entry.name, source=str(entry))
            delivery_directory_count += 1
            patch_id, delivery_record = read_delivery_record(entry, delivery_id, delivery_number)
            if current_delivery is not None and delivery_id == current_delivery:
                current_exception_count += 1
                policy_name = "CURRENT_DELIVERY_EXCEPTION"
            else:
                reserved_numbers.add(delivery_number)
                policy_name = "RESERVE"
            entry_record = {
                "source": "delivery",
                "path": entry.name,
                "entryType": "directory",
                "deliveryId": delivery_id,
                "patchId": patch_id,
                "number": delivery_number,
                "name": delivery_record.get("name") if delivery_record else None,
                "revision": delivery_record.get("revision") if delivery_record else None,
                "status": delivery_record.get("status") if delivery_record else None,
                "policy": policy_name,
            }
            entries.append(entry_record)
            if patch_id is not None:
                identity_claims.setdefault(delivery_number, []).append({
                    "sourceType": "delivery",
                    "patchId": patch_id,
                    "entry": entry_record,
                })
            continue
        if stat.S_ISREG(mode):
            if any(fnmatch.fnmatchcase(entry.name, pattern) for pattern in known_patterns):
                known_metadata_count += 1
                entries.append({
                    "source": "delivery",
                    "path": entry.name,
                    "entryType": "known-metadata",
                    "policy": "IGNORE_AND_COUNT",
                })
                continue
            raise ProcessOpsError("DELIVERY_INVENTORY_UNKNOWN_ENTRY", "Unknown regular file in delivery inventory", path=str(entry))
        raise ProcessOpsError("DELIVERY_INVENTORY_SPECIAL_FILE", "Delivery inventory contains a special file", path=str(entry), mode=oct(mode))

    if current_delivery is not None and current_exception_count != 1:
        raise ProcessOpsError(
            "CURRENT_DELIVERY_EXCEPTION_INVALID",
            "Current delivery must match exactly one delivery directory",
            currentDelivery=current_delivery,
            matchCount=current_exception_count,
        )

    require_inventory_directory(context.toolkit_run_root, code_prefix="TOOLKIT_RUN_ROOT")
    for run_dir in sorted(context.toolkit_run_root.iterdir(), key=lambda item: item.name):
        mode = run_dir.lstat().st_mode
        if stat.S_ISLNK(mode):
            raise ProcessOpsError("DELIVERY_RUN_INVENTORY_SYMLINK", "Run inventory contains a symlink", path=str(run_dir))
        if not stat.S_ISDIR(mode):
            raise ProcessOpsError("DELIVERY_RUN_INVENTORY_SPECIAL_ENTRY", "Run inventory contains a non-directory entry", path=str(run_dir), mode=oct(mode))
        record_path = run_dir / "run.json"
        record = read_required_json(
            record_path,
            error_code="DELIVERY_RUN_RECORD_INVALID",
            message="Run record is missing or invalid",
        )
        patch_id_value = record.get("patchId")
        scoped = {
            field: record.get(field)
            for field in scope_fields
            if record.get(field) not in (None, "", [], {})
        }
        if patch_id_value is None:
            if scoped:
                raise ProcessOpsError(
                    "DELIVERY_RUN_PATCH_ID_MISSING",
                    "Patch-scoped run record has no patchId",
                    path=str(record_path),
                    scopedFields=scoped,
                )
            generic_run_count += 1
            entries.append({
                "source": "run",
                "path": run_dir.name,
                "entryType": "generic-run",
                "runId": record.get("runId"),
                "policy": "IGNORE_AND_COUNT",
            })
            continue
        legacy_identity = legacy_numeric_patch_identity(
            record,
            source=str(record_path),
            policy=legacy_policy,
        )
        if legacy_identity is None:
            patch_number, patch_id = canonical_patch_identity(patch_id_value, source=str(record_path))
            entry_type = "patch-run"
        else:
            patch_number, patch_id = legacy_identity
            entry_type = "legacy-numeric-patch-run"
            legacy_numeric_patch_run_count += 1
        reserved_numbers.add(patch_number)
        patch_run_count += 1
        entry_record = {
            "source": "run",
            "path": run_dir.name,
            "entryType": entry_type,
            "runId": record.get("runId"),
            "patchId": patch_id,
            "legacyPatchId": patch_id_value if legacy_identity is not None else None,
            "artifactId": record.get("artifactId"),
            "command": record.get("command"),
            "status": record.get("status"),
            "number": patch_number,
            "policy": "RESERVE",
        }
        entries.append(entry_record)
        claim = {
            "sourceType": "run",
            "patchId": patch_id,
            "number": patch_number,
            "artifactId": record.get("artifactId"),
            "command": record.get("command"),
            "status": record.get("status"),
            "entry": entry_record,
        }
        identity_claims.setdefault(patch_number, []).append(claim)
        artifact_id = record.get("artifactId")
        if isinstance(artifact_id, str) and artifact_id:
            run_claims_by_artifact.setdefault(artifact_id, []).append(claim)

    require_inventory_directory(context.toolkit_accepted_root, code_prefix="TOOLKIT_ACCEPTED_ROOT")
    for accepted_path in sorted(context.toolkit_accepted_root.iterdir(), key=lambda item: item.name):
        mode = accepted_path.lstat().st_mode
        if stat.S_ISLNK(mode):
            raise ProcessOpsError("DELIVERY_ACCEPTED_INVENTORY_SYMLINK", "Accepted patch inventory contains a symlink", path=str(accepted_path))
        if not stat.S_ISREG(mode):
            raise ProcessOpsError("DELIVERY_ACCEPTED_INVENTORY_SPECIAL_ENTRY", "Accepted patch inventory contains a non-file entry", path=str(accepted_path), mode=oct(mode))
        record = read_required_json(
            accepted_path,
            error_code="DELIVERY_ACCEPTED_RECORD_INVALID",
            message="Accepted patch record is unreadable or invalid",
        )
        patch_number, patch_id, artifact_id = accepted_patch_identity(
            accepted_path,
            record,
            run_claims_by_artifact=run_claims_by_artifact,
            policy=accepted_policy,
            project_id=context.project_id,
        )
        reserved_numbers.add(patch_number)
        accepted_patch_record_count += 1
        entry_record = {
            "source": "accepted",
            "path": accepted_path.name,
            "entryType": "accepted-patch-record",
            "artifactId": artifact_id,
            "patchId": patch_id,
            "legacyPatchId": record.get("patchId") if record.get("patchId") != patch_id else None,
            "number": patch_number,
            "status": "ACCEPTED",
            "policy": "RESERVE",
        }
        entries.append(entry_record)
        identity_claims.setdefault(patch_number, []).append({
            "sourceType": "accepted",
            "patchId": patch_id,
            "artifactId": artifact_id,
            "entry": entry_record,
        })

    conflicts: dict[str, list[str]] = {}
    for number, claims in sorted(identity_claims.items()):
        accepted_identities = {
            str(claim["patchId"])
            for claim in claims
            if claim.get("sourceType") == "accepted"
        }
        if len(accepted_identities) > 1:
            conflicts[f"{number:06d}"] = sorted({str(claim["patchId"]) for claim in claims})
            continue
        if len(accepted_identities) == 1:
            accepted_owner_count += 1
            owner = next(iter(accepted_identities))
            unresolved = {owner}
            for claim in claims:
                identity = str(claim["patchId"])
                if identity == owner:
                    continue
                if claim.get("sourceType") == "run" and claim.get("status") in historical_failed_statuses:
                    entry_record = claim["entry"]
                    entry_record["entryType"] = "historical-failed-patch-run"
                    entry_record["policy"] = "IGNORE_AND_COUNT"
                    entry_record["acceptedPatchId"] = owner
                    historical_failed_attempt_count += 1
                    continue
                unresolved.add(identity)
            if len(unresolved) > 1:
                conflicts[f"{number:06d}"] = sorted(unresolved)
            continue
        identities = {str(claim["patchId"]) for claim in claims}
        if len(identities) > 1:
            conflicts[f"{number:06d}"] = sorted(identities)

    if conflicts:
        raise ProcessOpsError(
            "DELIVERY_PATCH_IDENTITY_CONFLICT",
            "One local patch number maps to multiple patch identities",
            conflicts=conflicts,
        )

    next_number = max(reserved_numbers, default=0) + 1
    if next_number > 999999:
        raise ProcessOpsError("DELIVERY_ID_EXHAUSTED", "No six-digit delivery identity remains")
    result: dict[str, Any] = {
        "schemaVersion": DELIVERY_INVENTORY_SCHEMA,
        "projectId": context.project_id,
        "deliveryRoot": str(context.process_delivery_root),
        "toolkitRunRoot": str(context.toolkit_run_root),
        "toolkitAcceptedRoot": str(context.toolkit_accepted_root),
        "currentDelivery": current_delivery,
        "currentDeliveryExceptionCount": current_exception_count,
        "entries": entries,
        "summary": {
            "deliveryDirectoryCount": delivery_directory_count,
            "knownMetadataEntryCount": known_metadata_count,
            "genericRunCount": generic_run_count,
            "patchRunCount": patch_run_count,
            "legacyNumericPatchRunCount": legacy_numeric_patch_run_count,
            "acceptedPatchRecordCount": accepted_patch_record_count,
            "acceptedOwnerCount": accepted_owner_count,
            "historicalFailedAttemptCount": historical_failed_attempt_count,
            "unknownEntryCount": 0,
            "reservedNumberCount": len(reserved_numbers),
        },
        "reservedNumbers": [f"{number:06d}" for number in sorted(reserved_numbers)],
        "nextNumber": f"{next_number:06d}",
        "policies": {
            "deliveryDirectory": "RESERVE",
            "knownMetadata": "IGNORE_AND_COUNT",
            "genericRun": "IGNORE_AND_COUNT",
            "patchRun": "RESERVE",
            "legacyNumericPatchRun": "RESERVE_WITH_CANONICAL_ARTIFACT_EVIDENCE",
            "acceptedPatch": "RESERVE_AS_CANONICAL_NUMBER_OWNER",
            "historicalFailedRunUnderAcceptedOwner": "IGNORE_AND_COUNT",
            "currentDelivery": "CURRENT_DELIVERY_EXCEPTION",
            "unknownOrUnsafe": "BLOCKING_TOOL_ERROR",
        },
    }
    if patch_name is not None:
        if not DELIVERY_NAME_PATTERN.fullmatch(patch_name):
            raise ProcessOpsError("DELIVERY_NAME_INVALID", "Delivery name is not canonical", name=patch_name)
        result["patchId"] = f"{next_number:06d}_{patch_name}"
        result["deliveryId"] = f"{next_number:06d}-{patch_name}"
    return result


def named_generic_runs(context: Context, effective_name: str) -> list[dict[str, Any]]:
    matches: list[dict[str, Any]] = []
    for record_path in sorted(context.toolkit_run_root.glob("run-*/run.json")):
        record = read_json_file(record_path)
        if not record or record.get("command") != "generic-run":
            continue
        metadata = record.get("metadata")
        if not isinstance(metadata, dict) or metadata.get("name") != effective_name:
            continue
        run_id = record.get("runId")
        if not isinstance(run_id, str) or not run_id:
            continue
        try:
            matches.append(crun_json(context, ["status", run_id]))
        except ProcessOpsError:
            continue
    return sorted(matches, key=lambda item: str(item.get("runId") or ""))


def select_singleton_run(records: list[dict[str, Any]]) -> dict[str, Any] | None:
    active = [item for item in records if str(item.get("status")) in ACTIVE_STATES]
    if len(active) > 1:
        raise ProcessOpsError(
            "MULTIPLE_ACTIVE_SINGLETON_RUNS",
            "More than one active run exists for the singleton key",
            runIds=[item.get("runId") for item in active],
        )
    if active:
        return active[0]
    return records[-1] if records else None


def parse_json_output(result: subprocess.CompletedProcess[str], *, command: list[str]) -> dict[str, Any]:
    try:
        value = json.loads(result.stdout)
    except Exception as exc:
        raise ProcessOpsError(
            "COMMAND_JSON_INVALID",
            "Command did not return a JSON object",
            command=command,
            exitCode=result.returncode,
            stdout=result.stdout[-4000:],
            stderr=result.stderr[-4000:],
            reason=str(exc),
        ) from exc
    if not isinstance(value, dict):
        raise ProcessOpsError("COMMAND_JSON_INVALID", "Command JSON root must be an object", command=command)
    value.setdefault("commandExitCode", result.returncode)
    if result.stderr.strip():
        value.setdefault("commandStderr", result.stderr[-4000:])
    return value


def cpatch_json(context: Context, arguments: Iterable[str]) -> dict[str, Any]:
    command = [str(context.integration_root / "bin/cpatch"), *arguments, "--format", "json"]
    result = run_command(command, cwd=context.integration_root, check=False)
    return parse_json_output(result, command=command)


def crun_json(context: Context, arguments: Iterable[str]) -> dict[str, Any]:
    values = list(arguments)
    if "--" in values:
        index = values.index("--")
        values = [*values[:index], "--format", "json", *values[index:]]
    else:
        values.extend(["--format", "json"])
    command = [str(context.integration_root / "bin/crun"), *values]
    result = run_command(command, cwd=context.integration_root, check=False)
    return parse_json_output(result, command=command)


def assert_integration_clean(context: Context) -> None:
    branch = git(context.integration_root, "branch", "--show-current")
    if branch != context.integration_branch:
        raise ProcessOpsError(
            "INTEGRATION_BRANCH_MISMATCH",
            "Resolved integration worktree is on the wrong branch",
            expected=context.integration_branch,
            actual=branch,
            root=str(context.integration_root),
        )
    status = git(context.integration_root, "status", "--porcelain=v1", "--untracked-files=all")
    if status:
        raise ProcessOpsError(
            "INTEGRATION_WORKTREE_DIRTY",
            "Integration worktree must be clean before a mutating patch run",
            root=str(context.integration_root),
            status=status.splitlines()[:40],
        )


def compact(value: dict[str, Any]) -> dict[str, Any]:
    keys = (
        "ok",
        "runId",
        "artifactId",
        "patchId",
        "status",
        "phase",
        "message",
        "exitCode",
        "pid",
        "logFile",
        "commandExitCode",
    )
    result = {key: value.get(key) for key in keys if value.get(key) is not None}
    nested_run = value.get("run")
    if isinstance(nested_run, dict):
        for key in keys:
            if key not in result and nested_run.get(key) is not None:
                result[key] = nested_run.get(key)
    return result


def emit(value: dict[str, Any], output_format: str) -> None:
    if output_format == "json":
        print(json.dumps(value, indent=2, sort_keys=True))
        return
    if output_format == "env":
        for key, item in value.items():
            if isinstance(item, bool):
                text = str(item).lower()
            elif item is None:
                text = ""
            elif isinstance(item, (dict, list)):
                text = json.dumps(item, separators=(",", ":"), sort_keys=True)
            else:
                text = str(item)
            print(f"{key.upper()}={text}")
        return
    for key, item in value.items():
        print(f"{key}={item}")


def persist_operation(context: Context, name: str, payload: dict[str, Any]) -> Path:
    run_id = str(payload.get("runId") or "no-run-id")
    target = context.process_state_root / "operations" / f"{utc_stamp()}-{name}-{run_id}.json"
    atomic_json(target, payload)
    return target


def resolve_artifact(value: str, context: Context) -> Path:
    candidate = Path(value).expanduser()
    used_configured_root = False
    if candidate.is_absolute():
        lexical = Path(os.path.abspath(str(candidate)))
        path = lexical.resolve(strict=False)
        if context.artifact_root is not None and (
            lexical == context.artifact_root or path_is_within(lexical, context.artifact_root)
        ):
            used_configured_root = True
    elif candidate.exists() or candidate.is_symlink():
        path = candidate.resolve(strict=False)
    elif context.artifact_root is not None:
        root = verify_artifact_root_authorization(context)
        path = (root / candidate).resolve(strict=False)
        used_configured_root = True
    else:
        path = candidate.resolve(strict=False)
    if used_configured_root:
        root = verify_artifact_root_authorization(context)
        if not path_is_within(path, root):
            raise ProcessOpsError("ARTIFACT_PATH_ESCAPE", "Artifact path escapes the authorized artifact root", artifact=str(path), artifactRoot=str(root))
    if path.is_symlink():
        raise ProcessOpsError("ARTIFACT_SYMLINK_FORBIDDEN", "Patch artifact must not be a symlink", artifact=str(path))
    if not path.is_file():
        raise ProcessOpsError("ARTIFACT_NOT_FOUND", "Patch artifact does not exist", artifact=str(path))
    return path



def command_workspace_start(args: argparse.Namespace, context: Context) -> int:
    if args.operation not in WORKSPACE_WRITERS:
        raise ProcessOpsError("OPERATOR_WORKSPACE_OPERATION_INVALID", "Workspace start operation is not a registered writer", operation=args.operation)
    record = prepare_operator_workspace(
        context,
        args.operation,
        args.subject or args.operation,
        run_reference=args.run_reference,
    )
    summary = {
        "status": "PREPARED",
        "operationId": record.get("operationId"),
        "operation": record.get("operation"),
        "subject": record.get("subject"),
        "operatorWorkspace": str(context.operator_work_root),
        "removedEntryCount": record.get("removedEntryCount"),
        "removedEntryListSha256": record.get("removedEntryListSha256"),
        "workspaceRootPreserved": record.get("workspaceRootPreserved"),
    }
    emit(record if args.verbose else summary, args.format)
    return 0


def command_artifact_root_authorize(args: argparse.Namespace, context: Context) -> int:
    payload = artifact_authorization_payload(context)
    path = context.artifact_authorization_record
    if path.exists() or path.is_symlink():
        if path.is_symlink():
            raise ProcessOpsError("ARTIFACT_ROOT_AUTHORIZATION_RECORD_SYMLINK", "Authorization record must not be a symlink", path=str(path))
        existing = read_required_json(
            path,
            error_code="ARTIFACT_ROOT_AUTHORIZATION_RECORD_INVALID",
            message="Existing artifact root authorization is invalid",
        )
        comparable_keys = (
            "schemaVersion",
            "projectId",
            "configuredPath",
            "canonicalPath",
            "device",
            "inode",
            "authorizationScope",
            "rootCreatedByAuthorization",
        )
        if all(existing.get(key) == payload.get(key) for key in comparable_keys):
            payload = existing
            payload["authorizationDisposition"] = "ALREADY_AUTHORIZED"
            emit(payload, args.format)
            return 0
        if not args.replace:
            raise ProcessOpsError(
                "ARTIFACT_ROOT_AUTHORIZATION_EXISTS",
                "A different artifact root authorization already exists; --replace is required",
                path=str(path),
                existingCanonicalPath=existing.get("canonicalPath"),
                requestedCanonicalPath=payload.get("canonicalPath"),
            )
    payload["authorizationDisposition"] = "REPLACED" if path.exists() else "AUTHORIZED"
    atomic_json(path, payload)
    emit(payload, args.format)
    return 0


def command_artifact_root_status(args: argparse.Namespace, context: Context) -> int:
    canonical = verify_artifact_root_authorization(context)
    record = read_required_json(
        context.artifact_authorization_record,
        error_code="ARTIFACT_ROOT_UNAUTHORIZED",
        message="Artifact root authorization record is missing or invalid",
    )
    value = dict(record)
    value["status"] = "AUTHORIZED"
    value["verifiedCanonicalPath"] = str(canonical)
    emit(value, args.format)
    return 0


def command_delivery_inventory(args: argparse.Namespace, context: Context) -> int:
    inventory = build_delivery_inventory(
        context,
        current_delivery=args.current_delivery,
        patch_name=getattr(args, "name", None),
    )
    if getattr(args, "verbose", False) or args.format == "json":
        emit(inventory, args.format)
    else:
        summary = dict(inventory["summary"])
        summary.update({
            "status": "PASS",
            "nextNumber": inventory["nextNumber"],
            "currentDeliveryExceptionCount": inventory["currentDeliveryExceptionCount"],
        })
        if inventory.get("patchId"):
            summary["patchId"] = inventory["patchId"]
            summary["deliveryId"] = inventory["deliveryId"]
        emit(summary, args.format)
    return 0


def command_delivery_prepare(args: argparse.Namespace, context: Context) -> int:
    if not DELIVERY_REVISION_PATTERN.fullmatch(args.revision):
        raise ProcessOpsError("DELIVERY_REVISION_INVALID", "Delivery revision is not canonical", revision=args.revision)
    assert_integration_clean(context)
    lock_path = context.process_state_root / "locks" / "delivery-prepare.lock"
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with lock_path.open("a+b") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        inventory = build_delivery_inventory(
            context,
            current_delivery=args.current_delivery,
            patch_name=args.name,
        )
        duplicate_revisions = [
            item.get("deliveryId")
            for item in inventory.get("entries", [])
            if item.get("source") == "delivery"
            and item.get("name") == args.name
            and item.get("revision") == args.revision
        ]
        if duplicate_revisions:
            raise ProcessOpsError(
                "DELIVERY_REVISION_ALREADY_PREPARED",
                "The immutable delivery revision is already prepared",
                name=args.name,
                revision=args.revision,
                deliveryIds=sorted(str(value) for value in duplicate_revisions),
            )
        workspace = prepare_operator_workspace(
            context,
            "delivery-prepare",
            str(inventory["deliveryId"]),
        )
        delivery_id = str(inventory["deliveryId"])
        patch_id = str(inventory["patchId"])
        directory = context.process_delivery_root / delivery_id
        if directory.exists() or directory.is_symlink():
            raise ProcessOpsError("DELIVERY_ALREADY_EXISTS", "Delivery directory already exists", deliveryId=delivery_id, path=str(directory))
        directory.mkdir(mode=0o700)
        record = {
            "schemaVersion": DELIVERY_RECORD_SCHEMA,
            "projectId": context.project_id,
            "deliveryId": delivery_id,
            "patchId": patch_id,
            "name": args.name,
            "revision": args.revision,
            "status": "PREPARED",
            "createdAt": iso_now(),
            "sourceHead": git(context.integration_root, "rev-parse", "HEAD"),
            "sourceBranch": git(context.integration_root, "branch", "--show-current"),
            "workspaceOperationId": workspace.get("operationId"),
            "artifactPublication": "NOT_STARTED",
            "artifactRootUsed": False,
            "immutableRevision": True,
        }
        atomic_json(directory / "delivery.json", record)
        update_workspace_record(
            context,
            record,
            deliveryId=delivery_id,
            patchId=patch_id,
            deliveryDirectory=str(directory),
        )
    result = dict(record)
    result["deliveryDirectory"] = str(directory)
    result["workspaceCleanupRemovedEntries"] = workspace.get("removedEntryCount")
    result["workspaceCleanupListSha256"] = workspace.get("removedEntryListSha256")
    report = persist_operation(context, "delivery-prepare", result)
    result["operationReport"] = str(report)
    emit(result, args.format)
    return 0



def command_resolve(args: argparse.Namespace, context: Context) -> int:
    value = {
        "projectId": context.project_id,
        "currentRoot": str(context.current_root),
        "integrationBranch": context.integration_branch,
        "integrationRoot": str(context.integration_root),
        "gitCommonDir": str(context.git_common_dir),
        "toolkitRunRoot": str(context.toolkit_run_root),
        "toolkitLockRoot": str(context.toolkit_lock_root),
        "toolkitAcceptedRoot": str(context.toolkit_accepted_root),
        "processStateRoot": str(context.process_state_root),
        "processIncidentRoot": str(context.process_incident_root),
        "processDeliveryRoot": str(context.process_delivery_root),
        "artifactAuthorizationRecord": str(context.artifact_authorization_record),
        "operatorLogRoot": str(context.operator_log_root),
        "operatorWorkRoot": str(context.operator_work_root),
        "artifactRoot": str(context.artifact_root) if context.artifact_root else None,
        "artifactRootSource": context.artifact_root_source,
        "worktreeRoot": str(context.worktree_root) if context.worktree_root else None,
    }
    emit(value, args.format)
    return 0


def command_patch_start(args: argparse.Namespace, context: Context, *, accept: bool) -> int:
    assert_integration_clean(context)
    artifact = resolve_artifact(args.artifact, context)
    name = "patch-accept" if accept else "patch-dry-run"
    workspace = prepare_operator_workspace(context, name, artifact.name)
    if accept:
        command = ["accept", str(artifact), "--profile", args.profile]
        if args.no_commit:
            command.append("--no-commit")
    else:
        command = ["apply", str(artifact), "--dry-run", "--profile", args.profile]
    payload = cpatch_json(context, command)
    payload["operation"] = name
    payload["artifactFileName"] = artifact.name
    payload["integrationRoot"] = str(context.integration_root)
    payload["operatorWorkspace"] = str(context.operator_work_root)
    payload["workspaceOperationId"] = workspace.get("operationId")
    payload["workspaceCleanupRemovedEntries"] = workspace.get("removedEntryCount", 0)
    payload["workspaceCleanupListSha256"] = workspace.get("removedEntryListSha256")
    update_workspace_record(context, payload)
    report = persist_operation(context, name, payload)
    operator_log = persist_operator_log(context, name, payload)
    summary = compact(payload)
    summary["operationReport"] = str(report)
    summary["operatorLog"] = str(operator_log)
    summary["operatorWorkspace"] = str(context.operator_work_root)
    summary["workspaceOperationId"] = workspace.get("operationId")
    summary["workspaceCleanupRemovedEntries"] = workspace.get("removedEntryCount", 0)
    summary["workspaceCleanupListSha256"] = workspace.get("removedEntryListSha256")
    emit(summary, args.format)
    return 0 if payload.get("runId") else 9


def command_run_start(args: argparse.Namespace, context: Context) -> int:
    command = args.command[1:] if args.command and args.command[0] == "--" else args.command
    if not command:
        raise ProcessOpsError("RUN_COMMAND_EMPTY", "A command is required after --")
    cwd = Path(args.cwd).expanduser()
    if not cwd.is_absolute():
        cwd = (context.current_root / cwd).resolve()

    if not args.singleton_key:
        payload = crun_json(context, ["start", "--name", args.name, "--cwd", str(cwd), "--", *command])
        payload["operation"] = "run-start"
        payload["resolvedCwd"] = str(cwd)
        payload["startDisposition"] = "STARTED"
    else:
        singleton_key = validate_singleton_key(args.singleton_key)
        effective_name = f"cocondo-singleton:{context.project_id}:{singleton_key}"
        lock_path = context.process_state_root / "locks" / f"run-start-{singleton_key}.lock"
        pointer_path = context.process_state_root / "pointers" / f"{singleton_key}.run-id"
        lock_path.parent.mkdir(parents=True, exist_ok=True)
        with lock_path.open("a+b") as handle:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
            existing = select_singleton_run(named_generic_runs(context, effective_name))
            if existing is not None and str(existing.get("status")) in ACTIVE_STATES:
                payload = dict(existing)
                payload["startDisposition"] = "REUSED_ACTIVE"
                atomic_text(pointer_path, f"{payload.get('runId')}\n")
            elif existing is not None and not args.restart_terminal:
                payload = dict(existing)
                payload["startDisposition"] = "REUSED_TERMINAL"
                atomic_text(pointer_path, f"{payload.get('runId')}\n")
            else:
                payload = crun_json(
                    context,
                    ["start", "--name", effective_name, "--cwd", str(cwd), "--", *command],
                )
                if not payload.get("runId"):
                    raise ProcessOpsError(
                        "RUN_START_WITHOUT_ID",
                        "Detached run did not return a runId",
                        payload=payload,
                    )
                payload["startDisposition"] = "RESTARTED" if existing is not None else "STARTED"
                atomic_text(pointer_path, f"{payload['runId']}\n")
            payload["singletonKey"] = singleton_key
            payload["singletonPointer"] = str(pointer_path)
            payload["effectiveName"] = effective_name
        payload["operation"] = "run-start"
        payload["resolvedCwd"] = str(cwd)

    report = persist_operation(context, "run-start", payload)
    summary = compact(payload)
    for key in ("startDisposition", "singletonKey", "singletonPointer", "effectiveName"):
        if payload.get(key) is not None:
            summary[key] = payload.get(key)
    summary["operationReport"] = str(report)
    emit(summary, args.format)
    return 0 if payload.get("runId") else 9


def status_payload(context: Context, reference: str) -> dict[str, Any]:
    return cpatch_json(context, ["status", reference])


def command_status(args: argparse.Namespace, context: Context) -> int:
    payload = status_payload(context, args.reference)
    update_workspace_record(context, payload)
    report = persist_operation(context, "status", payload)
    operator_log = persist_operator_log(context, "status", payload)
    summary = compact(payload)
    summary["operationReport"] = str(report)
    summary["operatorLog"] = str(operator_log)
    emit(summary, args.format)
    return 0


def recommendation(status: str) -> str:
    if status in ACTIVE_STATES:
        return "watch-or-wait-existing-run"
    if status == "DRY_RUN_SUCCEEDED":
        return "review-result-then-start-accept-explicitly"
    if status == "SUCCEEDED":
        return "verify-evidence-and-postconditions"
    if status in FAILURE_STATES:
        return "diagnose-existing-run-do-not-restart-blindly"
    return "inspect-status-and-run-record"


def command_resume(args: argparse.Namespace, context: Context) -> int:
    payload = status_payload(context, args.reference)
    update_workspace_record(context, payload)
    summary = compact(payload)
    summary["recommendedAction"] = recommendation(str(summary.get("status") or "UNKNOWN"))
    report = persist_operation(context, "resume", payload)
    operator_log = persist_operator_log(context, "resume", payload)
    summary["operationReport"] = str(report)
    summary["operatorLog"] = str(operator_log)
    emit(summary, args.format)
    return 0


def command_observe(args: argparse.Namespace, context: Context, *, verbose: bool) -> int:
    started = time.monotonic()
    last_signature: tuple[object, ...] | None = None
    try:
        while True:
            payload = status_payload(context, args.reference)
            summary = compact(payload)
            signature = (summary.get("status"), summary.get("phase"), summary.get("message"), summary.get("exitCode"))
            if signature != last_signature:
                update_workspace_record(context, payload)
                append_operator_event(context, payload)
                if verbose:
                    emit(summary, args.format)
            last_signature = signature
            status = str(summary.get("status") or "UNKNOWN")
            if status in TERMINAL_STATES:
                if not verbose:
                    emit(summary, args.format)
                if args.strict_exit and status in FAILURE_STATES:
                    return int(summary.get("exitCode") or 1)
                return 0
            if args.timeout is not None and time.monotonic() - started >= args.timeout:
                emit({"status": status, "observer": "TIMEOUT", "workerUnchanged": True}, args.format)
                return 0
            time.sleep(args.interval)
    except KeyboardInterrupt:
        emit({"observer": "INTERRUPTED", "workerUnchanged": True, "reference": args.reference}, args.format)
        return 0


def command_result(args: argparse.Namespace, context: Context) -> int:
    payload = cpatch_json(context, ["result", args.reference])
    update_workspace_record(context, payload)
    report = persist_operation(context, "result", payload)
    operator_log = persist_operator_log(context, "result", payload)
    summary = compact(payload)
    summary["operationReport"] = str(report)
    summary["operatorLog"] = str(operator_log)
    emit(payload if args.verbose else summary, args.format)
    if args.strict_exit and str(summary.get("status")) in FAILURE_STATES:
        return int(summary.get("exitCode") or 1)
    return 0


def command_diagnose(args: argparse.Namespace, context: Context) -> int:
    status = status_payload(context, args.reference)
    run_status = str(status.get("status") or "UNKNOWN")
    if run_status in ACTIVE_STATES:
        raise ProcessOpsError("WRITER_ACTIVE_RUN_BLOCKED", "Diagnosis writer requires a terminal run", runId=status.get("runId"), status=run_status)
    run_id = str(status.get("runId") or args.reference)
    workspace = prepare_operator_workspace(
        context,
        "diagnose",
        run_id,
        run_reference=run_id,
    )
    if args.output:
        output = Path(args.output).expanduser().resolve(strict=False)
        allowed = path_is_within(output, context.process_state_root) or path_is_within(output, context.operator_work_root)
        if not allowed:
            raise ProcessOpsError("DIAGNOSE_OUTPUT_UNAUTHORIZED", "Diagnosis output must remain in process state or operator workspace", output=str(output))
    else:
        output = context.operator_work_root / f"diagnose-{safe_component(run_id, 'run')}.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = cpatch_json(context, ["diagnose", args.reference, "--output", str(output)])
    update_workspace_record(
        context,
        payload,
        diagnosticFile=str(output),
        workspaceOperationId=workspace.get("operationId"),
    )
    operator_log = persist_operator_log(context, "diagnose", payload)
    summary = compact(payload)
    summary["diagnosticFile"] = str(output)
    summary["operatorLog"] = str(operator_log)
    summary["operatorWorkspace"] = str(context.operator_work_root)
    summary["workspaceOperationId"] = workspace.get("operationId")
    summary["workspaceCleanupRemovedEntries"] = workspace.get("removedEntryCount")
    emit(summary, args.format)
    return 0



def copy_if_file(source: Path, destination: Path) -> None:
    if source.is_file():
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)


def command_incident(args: argparse.Namespace, context: Context) -> int:
    payload = status_payload(context, args.reference)
    status = str(payload.get("status") or "UNKNOWN")
    if status in ACTIVE_STATES:
        raise ProcessOpsError("WRITER_ACTIVE_RUN_BLOCKED", "Incident collector requires a terminal run", runId=payload.get("runId"), status=status)
    run_id = str(payload.get("runId") or args.reference)
    workspace = prepare_operator_workspace(
        context,
        "incident",
        run_id,
        run_reference=run_id,
    )
    incident_dir = context.process_incident_root / f"{utc_stamp()}-{run_id}"
    incident_dir.mkdir(parents=True, exist_ok=False)
    atomic_json(incident_dir / "status.json", payload)

    source_run_dir = context.toolkit_run_root / run_id
    for relative in ("run.json", "run.log", "invocation.json", "validation/stages.json", "command.json"):
        copy_if_file(source_run_dir / relative, incident_dir / relative)

    diagnose = cpatch_json(context, ["diagnose", args.reference, "--output", str(incident_dir / "diagnose.json")])
    atomic_json(incident_dir / "diagnose-command.json", diagnose)
    summary = compact(payload)
    summary["incidentDirectory"] = str(incident_dir)
    summary["recommendedAction"] = recommendation(status)
    summary["workspaceOperationId"] = workspace.get("operationId")
    summary["workspaceCleanupRemovedEntries"] = workspace.get("removedEntryCount")
    atomic_json(incident_dir / "summary.json", summary)
    update_workspace_record(
        context,
        payload,
        incidentDirectory=str(incident_dir),
        workspaceOperationId=workspace.get("operationId"),
    )
    emit(summary, args.format)
    return 0



def command_diagnostic_handoff(args: argparse.Namespace, context: Context) -> int:
    payload = status_payload(context, args.reference)
    status = str(payload.get("status") or "UNKNOWN")
    if status in ACTIVE_STATES:
        raise ProcessOpsError("DIAGNOSTIC_HANDOFF_ACTIVE_RUN", "Diagnostic handoff requires a terminal run", runId=payload.get("runId"), status=status)
    run_id = str(payload.get("runId") or args.reference)
    workspace = prepare_operator_workspace(
        context,
        "diagnostic-handoff",
        run_id,
        run_reference=run_id,
    )
    patch_id = safe_component(payload.get("patchId"), "unscoped")
    archive = context.operator_work_root / f"{patch_id}-diagnostics-{safe_component(run_id, 'run')}.zip"
    if archive.exists():
        raise ProcessOpsError("DIAGNOSTIC_HANDOFF_EXISTS", "Diagnostic handoff archive already exists", archive=str(archive))
    with tempfile.TemporaryDirectory(prefix="diagnostic-handoff-", dir=context.process_state_root) as temporary_text:
        temporary = Path(temporary_text)
        atomic_json(temporary / "status.json", payload)
        diagnosis_path = temporary / "diagnose.json"
        diagnosis = cpatch_json(context, ["diagnose", args.reference, "--output", str(diagnosis_path)])
        atomic_json(temporary / "diagnose-command.json", diagnosis)
        run_dir = context.toolkit_run_root / run_id
        for relative in ("run.json", "run.log", "invocation.json", "command.json", "validation/stages.json"):
            copy_if_file(run_dir / relative, temporary / "canonical-run" / relative)
        validation_dir = run_dir / "validation"
        if validation_dir.is_dir():
            for source in sorted(validation_dir.glob("*.log")):
                copy_if_file(source, temporary / "canonical-run" / "validation" / source.name)
        log_dir = operator_log_directory(context, payload)
        if log_dir.is_dir():
            shutil.copytree(log_dir, temporary / "operator-logs", dirs_exist_ok=True)
        copy_if_file(workspace_record_path(context), temporary / "WORKSPACE.json")
        summary = {
            "schemaVersion": "cocondo.diagnostic-handoff.v1",
            "projectId": context.project_id,
            "runId": run_id,
            "patchId": payload.get("patchId"),
            "artifactId": payload.get("artifactId"),
            "status": status,
            "createdAt": iso_now(),
            "canonicalRunRoot": str(run_dir),
            "operatorLogRoot": str(log_dir),
            "workspaceOperationId": workspace.get("operationId"),
            "workspaceCleanupRemovedEntries": workspace.get("removedEntryCount"),
            "sourceMutation": False,
        }
        atomic_json(temporary / "summary.json", summary)
        manifest_lines: list[str] = []
        for source in sorted(item for item in temporary.rglob("*") if item.is_file()):
            digest = hashlib.sha256(source.read_bytes()).hexdigest()
            manifest_lines.append(f"{digest}  {source.relative_to(temporary).as_posix()}")
        atomic_text(temporary / "MANIFEST.sha256", "\n".join(manifest_lines) + "\n")
        deterministic_zip(temporary, archive)
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    update_workspace_record(
        context,
        payload,
        diagnosticArchive=str(archive),
        diagnosticArchiveSha256=digest,
        workspaceOperationId=workspace.get("operationId"),
    )
    handoff_payload = dict(payload)
    handoff_payload["diagnosticArchive"] = str(archive)
    handoff_payload["diagnosticArchiveSha256"] = digest
    operator_log = persist_operator_log(context, "diagnostic-handoff", handoff_payload)
    summary = compact(payload)
    summary["diagnosticArchive"] = str(archive)
    summary["diagnosticArchiveSha256"] = digest
    summary["operatorLog"] = str(operator_log)
    summary["workspaceOperationId"] = workspace.get("operationId")
    summary["workspaceCleanupRemovedEntries"] = workspace.get("removedEntryCount")
    emit(summary, args.format)
    return 0



def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Terminal-safe process operations for Cocondo Toolkit runs")
    parser.add_argument("--project-root")
    parser.add_argument("--format", choices=("human", "env", "json"), default="human")
    sub = parser.add_subparsers(dest="command_name", required=True)

    sub.add_parser("resolve")

    dry = sub.add_parser("patch-dry-run")
    dry.add_argument("artifact")
    dry.add_argument("--profile", default="auto")

    accept = sub.add_parser("patch-accept")
    accept.add_argument("artifact")
    accept.add_argument("--profile", default="auto")
    accept.add_argument("--no-commit", action="store_true")

    run_start = sub.add_parser("run-start")
    run_start.add_argument("--name", default="command")
    run_start.add_argument("--cwd", default=".")
    run_start.add_argument("--singleton-key")
    run_start.add_argument("--restart-terminal", action="store_true")
    run_start.add_argument("command", nargs=argparse.REMAINDER)

    for name in ("status", "resume"):
        command = sub.add_parser(name)
        command.add_argument("reference")

    for name in ("watch", "wait"):
        command = sub.add_parser(name)
        command.add_argument("reference")
        command.add_argument("--interval", type=float, default=2.0)
        command.add_argument("--timeout", type=float)
        command.add_argument("--strict-exit", action="store_true")

    result = sub.add_parser("result")
    result.add_argument("reference")
    result.add_argument("--verbose", action="store_true")
    result.add_argument("--strict-exit", action="store_true")

    diagnose = sub.add_parser("diagnose")
    diagnose.add_argument("reference")
    diagnose.add_argument("--output")

    incident = sub.add_parser("incident")
    incident.add_argument("reference")

    handoff = sub.add_parser("diagnostic-handoff")
    handoff.add_argument("reference")

    workspace = sub.add_parser("workspace-start")
    workspace.add_argument("--operation", required=True)
    workspace.add_argument("--subject")
    workspace.add_argument("--run-reference")
    workspace.add_argument("--verbose", action="store_true")

    artifact_authorize = sub.add_parser("artifact-root-authorize")
    artifact_authorize.add_argument("--replace", action="store_true")

    sub.add_parser("artifact-root-status")

    delivery_inventory = sub.add_parser("delivery-inventory")
    delivery_inventory.add_argument("--current-delivery")
    delivery_inventory.add_argument("--verbose", action="store_true")

    delivery_next = sub.add_parser("delivery-next-id")
    delivery_next.add_argument("--name", required=True)
    delivery_next.add_argument("--current-delivery")
    delivery_next.add_argument("--verbose", action="store_true")

    delivery_prepare = sub.add_parser("delivery-prepare")
    delivery_prepare.add_argument("--name", required=True)
    delivery_prepare.add_argument("--revision", required=True)
    delivery_prepare.add_argument("--current-delivery")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        context = resolve_context(args.project_root)
        if args.command_name == "resolve":
            return command_resolve(args, context)
        if args.command_name == "patch-dry-run":
            return command_patch_start(args, context, accept=False)
        if args.command_name == "patch-accept":
            return command_patch_start(args, context, accept=True)
        if args.command_name == "run-start":
            return command_run_start(args, context)
        if args.command_name == "status":
            return command_status(args, context)
        if args.command_name == "resume":
            return command_resume(args, context)
        if args.command_name == "watch":
            return command_observe(args, context, verbose=True)
        if args.command_name == "wait":
            return command_observe(args, context, verbose=False)
        if args.command_name == "result":
            return command_result(args, context)
        if args.command_name == "diagnose":
            return command_diagnose(args, context)
        if args.command_name == "incident":
            return command_incident(args, context)
        if args.command_name == "diagnostic-handoff":
            return command_diagnostic_handoff(args, context)
        if args.command_name == "workspace-start":
            return command_workspace_start(args, context)
        if args.command_name == "artifact-root-authorize":
            return command_artifact_root_authorize(args, context)
        if args.command_name == "artifact-root-status":
            return command_artifact_root_status(args, context)
        if args.command_name in {"delivery-inventory", "delivery-next-id"}:
            return command_delivery_inventory(args, context)
        if args.command_name == "delivery-prepare":
            return command_delivery_prepare(args, context)
        raise ProcessOpsError("COMMAND_UNSUPPORTED", "Unsupported command", command=args.command_name)
    except ProcessOpsError as exc:
        error = {"ok": False, "errorCode": exc.code, "message": exc.message, **exc.details}
        emit(error, getattr(args, "format", "human"))
        return 9


if __name__ == "__main__":
    raise SystemExit(main())
