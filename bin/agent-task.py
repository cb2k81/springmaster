#!/usr/bin/env python3
"""Fail-closed preparation and evidence harness for the Springmaster Codex pilot.

The harness intentionally has no Codex invocation and no Git integration command.
It prepares detached worktrees, validates immutable task contracts, performs
post-state scope checks, runs only predeclared qualification argv arrays and
removes disposable worktrees after explicit cleanup.
"""
from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any

TASK_SCHEMA_VERSION = "springmaster.agent-task.v1"
PILOT_ID = "springmaster-codex-pilot-v1"
REPOSITORY_ID = "springmaster"
TASK_ID_PATTERN = re.compile(r"^[A-Z][A-Z0-9-]{2,63}$")
ACTIVE_STATES = {"PREPARED", "QUALIFYING", "QUALIFIED", "FAILED", "POSTCHECK_PASSED", "POSTCHECK_FAILED"}
FORBIDDEN_COMMAND_PREFIXES: tuple[tuple[str, ...], ...] = (
    ("git", "push"),
    ("git", "reset", "--hard"),
    ("git", "clean"),
    ("git", "checkout"),
    ("git", "switch"),
    ("git", "branch"),
    ("git", "worktree"),
    ("ssh",),
    ("scp",),
    ("curl",),
    ("wget",),
)
REQUIRED_EVIDENCE = {
    "task-contract",
    "task-contract-sha256",
    "prepare-record",
    "integration-pre-state",
    "worktree-pre-state",
    "changed-path-report",
    "qualification-records",
    "final-result",
    "cleanup-disposition",
}


class AgentTaskError(RuntimeError):
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
    integration_branch: str
    project_id: str
    worktree_root: Path
    run_root: Path
    artifact_root: Path


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def run(
    argv: list[str],
    *,
    cwd: Path,
    env: dict[str, str] | None = None,
    timeout: int | None = None,
    check: bool = False,
) -> subprocess.CompletedProcess[str]:
    try:
        completed = subprocess.run(
            argv,
            cwd=cwd,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            check=False,
        )
    except FileNotFoundError as exc:
        raise AgentTaskError("COMMAND_NOT_FOUND", f"Command not found: {argv[0]}", argv=argv) from exc
    except subprocess.TimeoutExpired as exc:
        raise AgentTaskError("COMMAND_TIMEOUT", "Command timed out", argv=argv, timeoutSeconds=timeout) from exc
    if check and completed.returncode != 0:
        raise AgentTaskError(
            "COMMAND_FAILED",
            f"Command failed with exit code {completed.returncode}",
            argv=argv,
            stdout=completed.stdout[-4000:],
            stderr=completed.stderr[-4000:],
        )
    return completed


def git(root: Path, *args: str, check: bool = True) -> str:
    return run(["git", *args], cwd=root, check=check).stdout.strip()


def discover_root(explicit: str | None) -> Path:
    start = Path(explicit).expanduser() if explicit else Path.cwd()
    result = run(["git", "rev-parse", "--show-toplevel"], cwd=start, check=False)
    if result.returncode != 0 or not result.stdout.strip():
        raise AgentTaskError("PROJECT_ROOT_NOT_FOUND", "No Git project root could be resolved", start=str(start))
    return Path(result.stdout.strip()).resolve()


def parse_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.is_file():
        raise AgentTaskError("PROJECT_ENV_MISSING", "Project environment file is missing", path=str(path))
    for number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            raise AgentTaskError("PROJECT_ENV_INVALID", "Invalid environment line", path=str(path), line=number)
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
    expected = f"refs/heads/{branch}"
    matches = [Path(item["worktree"]).resolve() for item in parse_worktrees(root) if item.get("branch") == expected]
    if len(matches) != 1:
        raise AgentTaskError(
            "INTEGRATION_WORKTREE_UNRESOLVED",
            "Exactly one integration worktree is required",
            branch=branch,
            matches=[str(item) for item in matches],
        )
    return matches[0]


def path_contains(parent: Path, child: Path) -> bool:
    try:
        child.relative_to(parent)
        return True
    except ValueError:
        return False


def assert_no_symlink_components(path: Path) -> None:
    current = Path(path.anchor)
    for part in path.parts[1:]:
        current = current / part
        if current.exists() and stat.S_ISLNK(current.lstat().st_mode):
            raise AgentTaskError("EXTERNAL_ROOT_SYMLINK", "External root contains a symlink component", path=str(path), component=str(current))


def external_root(name: str) -> Path:
    raw = os.environ.get(name)
    if not raw:
        raise AgentTaskError("EXTERNAL_ROOT_UNSET", f"Required environment variable is not set: {name}", variable=name)
    expanded = Path(raw).expanduser()
    if not expanded.is_absolute():
        raise AgentTaskError("EXTERNAL_ROOT_NOT_ABSOLUTE", "External root must be absolute", variable=name, value=raw)
    expanded.mkdir(parents=True, exist_ok=True)
    assert_no_symlink_components(expanded)
    return expanded.resolve()


def resolve_context(explicit_root: str | None) -> Context:
    current = discover_root(explicit_root)
    env = parse_env_file(current / ".cocondo/tooling/project.env")
    branch = env.get("CPATCH_INTEGRATION_BRANCH", "main")
    project_id = env.get("CPATCH_PROJECT_ID", current.name)
    integration = resolve_integration_root(current, branch)
    common = Path(git(current, "rev-parse", "--path-format=absolute", "--git-common-dir")).resolve()
    roots = {
        "COCONDO_WORKTREE_ROOT": external_root("COCONDO_WORKTREE_ROOT"),
        "COCONDO_AGENT_RUN_ROOT": external_root("COCONDO_AGENT_RUN_ROOT"),
        "COCONDO_ARTIFACT_ROOT": external_root("COCONDO_ARTIFACT_ROOT"),
    }
    values = list(roots.values())
    if len(set(values)) != len(values):
        raise AgentTaskError("EXTERNAL_ROOTS_NOT_DISTINCT", "External roots must be pairwise distinct", roots={k: str(v) for k, v in roots.items()})
    for variable, value in roots.items():
        if path_contains(integration, value) or path_contains(value, integration):
            raise AgentTaskError("EXTERNAL_ROOT_PROJECT_OVERLAP", "External root must not overlap the project", variable=variable, path=str(value))
        if path_contains(common, value) or path_contains(value, common):
            raise AgentTaskError("EXTERNAL_ROOT_GIT_OVERLAP", "External root must not overlap the Git common directory", variable=variable, path=str(value))
    return Context(
        current_root=current,
        integration_root=integration,
        git_common_dir=common,
        integration_branch=branch,
        project_id=project_id,
        worktree_root=roots["COCONDO_WORKTREE_ROOT"],
        run_root=roots["COCONDO_AGENT_RUN_ROOT"],
        artifact_root=roots["COCONDO_ARTIFACT_ROOT"],
    )


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise AgentTaskError("JSON_MISSING", "JSON file is missing", path=str(path)) from exc
    except json.JSONDecodeError as exc:
        raise AgentTaskError("JSON_INVALID", "JSON file is invalid", path=str(path), line=exc.lineno, column=exc.colno) from exc
    if not isinstance(value, dict):
        raise AgentTaskError("JSON_ROOT_INVALID", "JSON root must be an object", path=str(path))
    return value


def atomic_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def atomic_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(value, encoding="utf-8")
    os.replace(temporary, path)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def require(condition: bool, code: str, message: str, **details: object) -> None:
    if not condition:
        raise AgentTaskError(code, message, **details)


def validate_task(task: dict[str, Any]) -> None:
    required = {
        "schemaVersion", "taskId", "pilotId", "repositoryId", "mode", "baseCommit", "integrationBranch",
        "riskClass", "changeClasses", "allowedPaths", "forbiddenPaths", "limits", "capabilities",
        "qualificationCommands", "requiredEvidence", "completionCriteria",
    }
    unknown = set(task) - (required | {"notes"})
    missing = required - set(task)
    require(not missing, "TASK_FIELDS_MISSING", "Task contract has missing fields", fields=sorted(missing))
    require(not unknown, "TASK_FIELDS_UNKNOWN", "Task contract has unknown fields", fields=sorted(unknown))
    require(task["schemaVersion"] == TASK_SCHEMA_VERSION, "TASK_SCHEMA_INVALID", "Unsupported task schema version")
    require(isinstance(task["taskId"], str) and TASK_ID_PATTERN.fullmatch(task["taskId"]) is not None, "TASK_ID_INVALID", "Invalid task ID")
    require(task["pilotId"] == PILOT_ID, "TASK_PILOT_INVALID", "Task is not part of the Springmaster Codex pilot")
    require(task["repositoryId"] == REPOSITORY_ID, "TASK_REPOSITORY_INVALID", "Task repository must be Springmaster")
    require(task["mode"] in {"analysis", "implementation", "qualification"}, "TASK_MODE_INVALID", "Invalid task mode")
    require(isinstance(task["baseCommit"], str) and re.fullmatch(r"[0-9a-f]{40}", task["baseCommit"]) is not None, "TASK_BASE_COMMIT_INVALID", "Invalid base commit")
    require(task["integrationBranch"] == "main", "TASK_BRANCH_INVALID", "Integration branch must be main")
    require(task["riskClass"] in {"low", "medium", "high", "critical"}, "TASK_RISK_INVALID", "Invalid risk class")
    for key in ("changeClasses", "allowedPaths", "forbiddenPaths", "requiredEvidence", "completionCriteria"):
        require(isinstance(task[key], list) and len(task[key]) > 0, "TASK_LIST_INVALID", f"{key} must be a non-empty list", field=key)
        require(len(set(map(str, task[key]))) == len(task[key]), "TASK_LIST_DUPLICATE", f"{key} must not contain duplicates", field=key)
    require(all(isinstance(item, str) and item for item in task["allowedPaths"]), "TASK_ALLOWED_PATH_INVALID", "Allowed paths must be strings")
    require(all(isinstance(item, str) and item for item in task["forbiddenPaths"]), "TASK_FORBIDDEN_PATH_INVALID", "Forbidden paths must be strings")
    for pattern in list(task["allowedPaths"]) + list(task["forbiddenPaths"]):
        require(not pattern.startswith("/") and ".." not in PurePosixPath(pattern).parts, "TASK_PATH_PATTERN_INVALID", "Path patterns must be repository-relative", pattern=pattern)
    limits = task["limits"]
    require(isinstance(limits, dict) and set(limits) == {"maxChangedFiles", "maxAddedBytes"}, "TASK_LIMITS_INVALID", "Limits object is invalid")
    require(isinstance(limits["maxChangedFiles"], int) and 1 <= limits["maxChangedFiles"] <= 200, "TASK_MAX_FILES_INVALID", "maxChangedFiles is invalid")
    require(isinstance(limits["maxAddedBytes"], int) and 0 <= limits["maxAddedBytes"] <= 10 * 1024 * 1024, "TASK_MAX_BYTES_INVALID", "maxAddedBytes is invalid")
    caps = task["capabilities"]
    expected_caps = {"mayModifyTests", "mayModifyGovernance", "mayModifyContracts", "mayCommit", "mayPush", "network"}
    require(isinstance(caps, dict) and set(caps) == expected_caps, "TASK_CAPABILITIES_INVALID", "Capabilities object is invalid")
    require(caps["mayCommit"] is False and caps["mayPush"] is False and caps["network"] == "disabled", "TASK_CAPABILITY_FORBIDDEN", "Commit, push and network must be disabled")
    require(all(isinstance(caps[key], bool) for key in ("mayModifyTests", "mayModifyGovernance", "mayModifyContracts")), "TASK_CAPABILITY_TYPE_INVALID", "Capability flags must be boolean")
    evidence = set(task["requiredEvidence"])
    require(REQUIRED_EVIDENCE <= evidence, "TASK_EVIDENCE_INCOMPLETE", "Required evidence list is incomplete", missing=sorted(REQUIRED_EVIDENCE - evidence))
    commands = task["qualificationCommands"]
    require(isinstance(commands, list) and commands, "TASK_COMMANDS_INVALID", "Qualification commands must be a non-empty list")
    command_ids: set[str] = set()
    for command in commands:
        require(isinstance(command, dict) and set(command) == {"id", "argv", "timeoutSeconds"}, "TASK_COMMAND_INVALID", "Qualification command is invalid")
        command_id = command["id"]
        require(isinstance(command_id, str) and re.fullmatch(r"[a-z][a-z0-9-]*", command_id) is not None, "TASK_COMMAND_ID_INVALID", "Qualification command ID is invalid")
        require(command_id not in command_ids, "TASK_COMMAND_ID_DUPLICATE", "Qualification command IDs must be unique", commandId=command_id)
        command_ids.add(command_id)
        argv = command["argv"]
        require(isinstance(argv, list) and argv and all(isinstance(item, str) and item for item in argv), "TASK_COMMAND_ARGV_INVALID", "Qualification argv must be a non-empty string array")
        for prefix in FORBIDDEN_COMMAND_PREFIXES:
            require(tuple(argv[:len(prefix)]) != prefix, "TASK_COMMAND_FORBIDDEN", "Qualification command family is forbidden", argv=argv)
        require(isinstance(command["timeoutSeconds"], int) and 1 <= command["timeoutSeconds"] <= 7200, "TASK_COMMAND_TIMEOUT_INVALID", "Qualification timeout is invalid")


def integration_state(root: Path) -> dict[str, Any]:
    return {
        "root": str(root),
        "head": git(root, "rev-parse", "HEAD"),
        "branch": git(root, "branch", "--show-current"),
        "statusPorcelainV1": git(root, "status", "--porcelain=v1", "--untracked-files=all"),
    }


def worktree_state(root: Path) -> dict[str, Any]:
    branch = git(root, "branch", "--show-current")
    return {
        "root": str(root),
        "head": git(root, "rev-parse", "HEAD"),
        "branch": branch,
        "detached": branch == "",
        "statusPorcelainV1": git(root, "status", "--porcelain=v1", "--untracked-files=all"),
    }


def task_slug(task_id: str) -> str:
    return task_id.lower()


def run_dir(context: Context, task_id: str) -> Path:
    return context.run_root / task_slug(task_id)


def task_worktree(context: Context, task_id: str) -> Path:
    return context.worktree_root / task_slug(task_id)


def load_run_record(context: Context, task_id: str) -> tuple[Path, dict[str, Any]]:
    directory = run_dir(context, task_id)
    record_path = directory / "run.json"
    record = load_json(record_path)
    return directory, record


def active_task_records(context: Context) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    if not context.run_root.exists():
        return records
    for path in sorted(context.run_root.glob("*/run.json")):
        try:
            value = load_json(path)
        except AgentTaskError:
            continue
        if value.get("status") in ACTIVE_STATES:
            records.append(value)
    return records


def cmd_validate(args: argparse.Namespace) -> dict[str, Any]:
    task_path = Path(args.task).expanduser().resolve()
    task = load_json(task_path)
    validate_task(task)
    return {"status": "PASS", "taskId": task["taskId"], "taskPath": str(task_path), "schemaVersion": task["schemaVersion"]}


def cmd_prepare(args: argparse.Namespace) -> dict[str, Any]:
    context = resolve_context(args.project_root)
    require(context.project_id == REPOSITORY_ID, "PROJECT_ID_INVALID", "Current project is not Springmaster", projectId=context.project_id)
    task_path = Path(args.task).expanduser().resolve()
    task = load_json(task_path)
    validate_task(task)
    task_id = task["taskId"]
    directory = run_dir(context, task_id)
    worktree = task_worktree(context, task_id)
    require(not directory.exists(), "TASK_ALREADY_EXISTS", "Task run directory already exists", path=str(directory))
    require(not worktree.exists(), "TASK_WORKTREE_EXISTS", "Task worktree path already exists", path=str(worktree))
    active = active_task_records(context)
    require(not active, "ACTIVE_TASK_EXISTS", "Only one active pilot task is allowed", activeTaskIds=[item.get("taskId") for item in active])
    before = integration_state(context.integration_root)
    require(before["branch"] == context.integration_branch, "INTEGRATION_BRANCH_INVALID", "Integration worktree is not on the configured branch", state=before)
    require(before["statusPorcelainV1"] == "", "INTEGRATION_TREE_DIRTY", "Integration worktree must be clean", state=before)
    require(before["head"] == task["baseCommit"], "BASE_COMMIT_MISMATCH", "Task base commit must equal integration HEAD", taskBase=task["baseCommit"], integrationHead=before["head"])
    git(context.integration_root, "cat-file", "-e", f"{task['baseCommit']}^{{commit}}")
    directory.mkdir(parents=True)
    stored_contract = directory / "task-contract.json"
    shutil.copyfile(task_path, stored_contract)
    contract_hash = sha256_file(stored_contract)
    atomic_text(directory / "task-contract.sha256", f"{contract_hash}  task-contract.json\n")
    atomic_json(directory / "integration-pre-state.json", before)
    context.worktree_root.mkdir(parents=True, exist_ok=True)
    try:
        git(context.integration_root, "worktree", "add", "--detach", str(worktree), task["baseCommit"])
    except Exception:
        shutil.rmtree(directory, ignore_errors=True)
        raise
    after_worktree = worktree_state(worktree)
    require(after_worktree["head"] == task["baseCommit"] and after_worktree["detached"], "WORKTREE_PREPARE_INVALID", "Prepared worktree is not detached at the task base", state=after_worktree)
    atomic_json(directory / "worktree-pre-state.json", after_worktree)
    prepare = {
        "schemaVersion": "springmaster.agent-task-prepare-record.v1",
        "taskId": task_id,
        "preparedAt": utc_now(),
        "projectId": context.project_id,
        "integrationRoot": str(context.integration_root),
        "gitCommonDir": str(context.git_common_dir),
        "worktreeRoot": str(context.worktree_root),
        "worktreePath": str(worktree),
        "runDirectory": str(directory),
        "artifactRoot": str(context.artifact_root),
        "baseCommit": task["baseCommit"],
        "taskContractSha256": contract_hash,
        "codexInvocation": "NOT_PERFORMED",
    }
    atomic_json(directory / "prepare-record.json", prepare)
    run_record = {
        "schemaVersion": "springmaster.agent-task-run.v1",
        "taskId": task_id,
        "status": "PREPARED",
        "preparedAt": prepare["preparedAt"],
        "baseCommit": task["baseCommit"],
        "worktreePath": str(worktree),
        "runDirectory": str(directory),
        "codexInvocation": "NOT_PERFORMED",
    }
    atomic_json(directory / "run.json", run_record)
    return {"status": "PREPARED", "taskId": task_id, "worktreePath": str(worktree), "runDirectory": str(directory), "nextAction": "EXPLICIT_CODEX_CALIBRATION_ONLY"}


def parse_changed_paths(root: Path) -> list[str]:
    result = run(["git", "status", "--porcelain=v1", "-z", "--untracked-files=all"], cwd=root, check=True)
    raw = result.stdout
    entries = raw.split("\0")
    paths: list[str] = []
    index = 0
    while index < len(entries):
        entry = entries[index]
        if not entry:
            break
        status_code = entry[:2]
        path = entry[3:]
        if "R" in status_code or "C" in status_code:
            index += 1
            if index >= len(entries) or not entries[index]:
                raise AgentTaskError("GIT_STATUS_INVALID", "Rename/copy status is incomplete")
            path = entries[index]
        paths.append(path.replace("\\", "/"))
        index += 1
    return sorted(set(paths))


def pattern_matches(path: str, pattern: str) -> bool:
    normalized = pattern.rstrip("/")
    if normalized.endswith("/**"):
        prefix = normalized[:-3].rstrip("/")
        return path == prefix or path.startswith(prefix + "/")
    return fnmatch.fnmatchcase(path, normalized)


def root_level(path: str) -> bool:
    return "/" not in path


def added_bytes(root: Path, paths: list[str]) -> int:
    total = 0
    for relative in paths:
        candidate = root / relative
        if candidate.is_file() and not candidate.is_symlink():
            total += candidate.stat().st_size
    return total


def changed_symlinks(root: Path, paths: list[str]) -> list[str]:
    return [relative for relative in paths if (root / relative).is_symlink()]


def validate_post_state(context: Context, directory: Path, record: dict[str, Any]) -> dict[str, Any]:
    task = load_json(directory / "task-contract.json")
    validate_task(task)
    expected_hash = (directory / "task-contract.sha256").read_text(encoding="utf-8").split()[0]
    current_hash = sha256_file(directory / "task-contract.json")
    findings: list[dict[str, Any]] = []
    if current_hash != expected_hash:
        findings.append({"code": "TASK_CONTRACT_MUTATED", "expected": expected_hash, "actual": current_hash})
    integration_before = load_json(directory / "integration-pre-state.json")
    integration_after = integration_state(context.integration_root)
    if integration_after["head"] != integration_before["head"]:
        findings.append({"code": "INTEGRATION_HEAD_CHANGED", "before": integration_before["head"], "after": integration_after["head"]})
    if integration_after["statusPorcelainV1"] != integration_before["statusPorcelainV1"]:
        findings.append({"code": "INTEGRATION_TREE_CHANGED", "before": integration_before["statusPorcelainV1"], "after": integration_after["statusPorcelainV1"]})
    worktree = Path(record["worktreePath"])
    if not worktree.is_dir():
        findings.append({"code": "WORKTREE_MISSING", "path": str(worktree)})
        changed: list[str] = []
        state: dict[str, Any] = {"root": str(worktree), "missing": True}
    else:
        state = worktree_state(worktree)
        changed = parse_changed_paths(worktree)
        if state["head"] != task["baseCommit"]:
            findings.append({"code": "WORKTREE_HEAD_CHANGED", "expected": task["baseCommit"], "actual": state["head"]})
        if not state["detached"]:
            findings.append({"code": "WORKTREE_NOT_DETACHED", "branch": state["branch"]})
        symlinks = changed_symlinks(worktree, changed)
        for path in symlinks:
            findings.append({"code": "CHANGED_SYMLINK_FORBIDDEN", "path": path})
        for path in changed:
            allowed = any(pattern_matches(path, pattern) for pattern in task["allowedPaths"])
            forbidden = any(pattern_matches(path, pattern) for pattern in task["forbiddenPaths"])
            if path == ".git" or path.startswith(".git/"):
                forbidden = True
            if root_level(path) and path not in task["allowedPaths"]:
                allowed = False
                findings.append({"code": "ROOT_WRITE_NOT_EXACTLY_ALLOWED", "path": path})
            if forbidden:
                findings.append({"code": "FORBIDDEN_PATH_CHANGED", "path": path})
            elif not allowed:
                findings.append({"code": "UNDECLARED_PATH_CHANGED", "path": path})
        if len(changed) > task["limits"]["maxChangedFiles"]:
            findings.append({"code": "CHANGED_FILE_LIMIT_EXCEEDED", "actual": len(changed), "maximum": task["limits"]["maxChangedFiles"]})
        size = added_bytes(worktree, changed)
        if size > task["limits"]["maxAddedBytes"]:
            findings.append({"code": "ADDED_BYTE_LIMIT_EXCEEDED", "actual": size, "maximum": task["limits"]["maxAddedBytes"]})
        if not task["capabilities"]["mayModifyTests"]:
            for path in changed:
                if path.startswith("src/test/") or path.endswith("-it.sh") or "/test" in path.lower():
                    findings.append({"code": "TEST_CHANGE_FORBIDDEN", "path": path})
        if not task["capabilities"]["mayModifyGovernance"]:
            for path in changed:
                if path.startswith("PROJECT_DOCS/GOVERNANCE/") or path.startswith("PROJECT_DOCS/ADR/"):
                    findings.append({"code": "GOVERNANCE_CHANGE_FORBIDDEN", "path": path})
        if not task["capabilities"]["mayModifyContracts"]:
            for path in changed:
                if path.startswith("contracts/"):
                    findings.append({"code": "CONTRACT_CHANGE_FORBIDDEN", "path": path})
    report = {
        "schemaVersion": "springmaster.agent-task-changed-path-report.v1",
        "taskId": task["taskId"],
        "checkedAt": utc_now(),
        "status": "PASS" if not findings else "FINDINGS",
        "findingCount": len(findings),
        "findings": findings,
        "changedPaths": changed,
        "integrationState": integration_after,
        "worktreeState": state,
    }
    atomic_json(directory / "changed-path-report.json", report)
    record["lastPostcheckAt"] = report["checkedAt"]
    record["status"] = "POSTCHECK_PASSED" if not findings else "POSTCHECK_FAILED"
    atomic_json(directory / "run.json", record)
    return report


def cmd_postcheck(args: argparse.Namespace) -> dict[str, Any]:
    context = resolve_context(args.project_root)
    directory, record = load_run_record(context, args.task_id)
    return validate_post_state(context, directory, record)


def sanitized_environment(context: Context, directory: Path) -> dict[str, str]:
    allowed = {"PATH", "HOME", "USER", "LOGNAME", "LANG", "LC_ALL", "TZ", "JAVA_HOME", "MAVEN_OPTS", "NODE_OPTIONS", "NPM_CONFIG_CACHE", "PLAYWRIGHT_BROWSERS_PATH"}
    environment = {key: value for key, value in os.environ.items() if key in allowed}
    environment.update({
        "CI": "true",
        "GIT_TERMINAL_PROMPT": "0",
        "COCONDO_AGENT_TASK_RUN_DIR": str(directory),
        "COCONDO_ARTIFACT_ROOT": str(context.artifact_root),
    })
    return environment


def cmd_qualify(args: argparse.Namespace) -> dict[str, Any]:
    context = resolve_context(args.project_root)
    directory, record = load_run_record(context, args.task_id)
    pre = validate_post_state(context, directory, record)
    if pre["findingCount"]:
        raise AgentTaskError("POSTCHECK_FINDINGS", "Qualification is blocked by pre-qualification findings", findings=pre["findings"])
    task = load_json(directory / "task-contract.json")
    worktree = Path(record["worktreePath"])
    record["status"] = "QUALIFYING"
    atomic_json(directory / "run.json", record)
    qualification_dir = directory / "qualification"
    qualification_dir.mkdir(parents=True, exist_ok=True)
    results: list[dict[str, Any]] = []
    for item in task["qualificationCommands"]:
        started = utc_now()
        command_id = item["id"]
        log_path = qualification_dir / f"{command_id}.log"
        try:
            completed = run(item["argv"], cwd=worktree, env=sanitized_environment(context, directory), timeout=item["timeoutSeconds"], check=False)
            output = completed.stdout + ("\n--- STDERR ---\n" if completed.stderr else "") + completed.stderr
            atomic_text(log_path, output)
            result = {
                "id": command_id,
                "argv": item["argv"],
                "timeoutSeconds": item["timeoutSeconds"],
                "startedAt": started,
                "finishedAt": utc_now(),
                "exitCode": completed.returncode,
                "status": "PASS" if completed.returncode == 0 else "FAIL",
                "logPath": str(log_path),
            }
        except AgentTaskError as exc:
            atomic_text(log_path, json.dumps({"errorCode": exc.code, "message": exc.message, "details": exc.details}, sort_keys=True) + "\n")
            result = {
                "id": command_id,
                "argv": item["argv"],
                "timeoutSeconds": item["timeoutSeconds"],
                "startedAt": started,
                "finishedAt": utc_now(),
                "exitCode": None,
                "status": "TOOL_ERROR",
                "errorCode": exc.code,
                "logPath": str(log_path),
            }
        atomic_json(qualification_dir / f"{command_id}.json", result)
        results.append(result)
        if result["status"] != "PASS":
            break
    post = validate_post_state(context, directory, load_json(directory / "run.json"))
    passed = all(item["status"] == "PASS" for item in results) and post["findingCount"] == 0 and len(results) == len(task["qualificationCommands"])
    final = {
        "schemaVersion": "springmaster.agent-task-final-result.v1",
        "taskId": task["taskId"],
        "finishedAt": utc_now(),
        "status": "QUALIFIED" if passed else "FAILED",
        "qualificationResults": results,
        "postcheckStatus": post["status"],
        "postcheckFindingCount": post["findingCount"],
        "codexInvocation": "NOT_PERFORMED_BY_HARNESS",
        "integrationAuthorized": False,
    }
    atomic_json(directory / "final-result.json", final)
    record = load_json(directory / "run.json")
    record["status"] = final["status"]
    record["finishedAt"] = final["finishedAt"]
    atomic_json(directory / "run.json", record)
    return final


def cmd_status(args: argparse.Namespace) -> dict[str, Any]:
    context = resolve_context(args.project_root)
    directory, record = load_run_record(context, args.task_id)
    result = dict(record)
    result["runDirectory"] = str(directory)
    for name in ("changed-path-report.json", "final-result.json", "cleanup-disposition.json"):
        path = directory / name
        if path.is_file():
            result[name.removesuffix(".json")] = load_json(path)
    return result


def cmd_cleanup(args: argparse.Namespace) -> dict[str, Any]:
    context = resolve_context(args.project_root)
    directory, record = load_run_record(context, args.task_id)
    worktree = Path(record["worktreePath"])
    dirty = False
    if worktree.is_dir():
        dirty = bool(git(worktree, "status", "--porcelain=v1", "--untracked-files=all"))
        if dirty and not args.discard:
            raise AgentTaskError("DIRTY_WORKTREE_REQUIRES_DISCARD", "Worktree has changes; use --discard only after evidence review", path=str(worktree))
        argv = ["git", "worktree", "remove"]
        if args.discard:
            argv.append("--force")
        argv.append(str(worktree))
        run(argv, cwd=context.integration_root, check=True)
        git(context.integration_root, "worktree", "prune")
    disposition = {
        "schemaVersion": "springmaster.agent-task-cleanup-disposition.v1",
        "taskId": args.task_id,
        "cleanedAt": utc_now(),
        "worktreePath": str(worktree),
        "worktreeWasDirty": dirty,
        "discardAuthorized": bool(args.discard),
        "evidenceRetained": True,
    }
    atomic_json(directory / "cleanup-disposition.json", disposition)
    record["status"] = "CLEANED"
    record["cleanedAt"] = disposition["cleanedAt"]
    atomic_json(directory / "run.json", record)
    return disposition


def emit(value: dict[str, Any], output_format: str) -> None:
    if output_format == "json":
        print(json.dumps(value, sort_keys=True, ensure_ascii=False))
        return
    preferred = ("status", "taskId", "worktreePath", "runDirectory", "nextAction", "findingCount")
    printed: set[str] = set()
    for key in preferred:
        if key in value and not isinstance(value[key], (dict, list)):
            print(f"{key}={value[key]}")
            printed.add(key)
    for key in sorted(value):
        if key not in printed and not isinstance(value[key], (dict, list)):
            print(f"{key}={value[key]}")


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--project-root")
    result.add_argument("--format", choices=("text", "json"), default="text")
    sub = result.add_subparsers(dest="command", required=True)
    validate = sub.add_parser("validate")
    validate.add_argument("task")
    prepare = sub.add_parser("prepare")
    prepare.add_argument("task")
    for command in ("status", "postcheck", "qualify"):
        item = sub.add_parser(command)
        item.add_argument("task_id")
    cleanup = sub.add_parser("cleanup")
    cleanup.add_argument("task_id")
    cleanup.add_argument("--discard", action="store_true")
    return result


def main() -> int:
    args = parser().parse_args()
    try:
        if args.command == "validate":
            value = cmd_validate(args)
        elif args.command == "prepare":
            value = cmd_prepare(args)
        elif args.command == "status":
            value = cmd_status(args)
        elif args.command == "postcheck":
            value = cmd_postcheck(args)
        elif args.command == "qualify":
            value = cmd_qualify(args)
        elif args.command == "cleanup":
            value = cmd_cleanup(args)
        else:
            raise AgentTaskError("COMMAND_INVALID", "Unknown command")
        emit(value, args.format)
        if args.command == "postcheck" and value.get("findingCount", 0):
            return 1
        if args.command == "qualify" and value.get("status") != "QUALIFIED":
            return 1
        return 0
    except AgentTaskError as exc:
        payload = {"status": "TOOL_ERROR", "errorCode": exc.code, "message": exc.message, "details": exc.details}
        if args.format == "json":
            print(json.dumps(payload, sort_keys=True, ensure_ascii=False))
        else:
            print("status=TOOL_ERROR")
            print(f"errorCode={exc.code}")
            print(f"message={exc.message}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
