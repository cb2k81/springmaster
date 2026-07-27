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

TASK_SCHEMA_VERSION = "springmaster.agent-task.v2"
PILOT_CONTRACT_SCHEMA_VERSION = "springmaster.codex-pilot-contract.v1"
OPERATOR_EFFECT_SCHEMA_VERSION = "springmaster.operator-command-effect.v1"
INVOCATION_RECORD_SCHEMA_VERSION = "springmaster.codex-invocation-record.v1"
PILOT_ID = "springmaster-codex-pilot-v1"
REPOSITORY_ID = "springmaster"
TASK_ID_PATTERN = re.compile(r"^[A-Z][A-Z0-9-]{2,63}$")
ACTIVE_STATES = {"PREPARED", "QUALIFYING", "QUALIFIED", "FAILED", "POSTCHECK_PASSED", "POSTCHECK_FAILED"}
VALID_RUN_STATES = ACTIVE_STATES | {"CLEANED", "CLEANED_INCOMPLETE"}
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
    "operator-command-effect",
    "operator-command-effect-sha256",
    "invocation-record",
    "invocation-record-sha256",
    "changed-path-report",
    "qualification-records",
    "final-result",
    "cleanup-disposition",
}

EVIDENCE_FILES = {
    "task-contract": "task-contract.json",
    "task-contract-sha256": "task-contract.sha256",
    "prepare-record": "prepare-record.json",
    "integration-pre-state": "integration-pre-state.json",
    "worktree-pre-state": "worktree-pre-state.json",
    "operator-command-effect": "operator-command-effect.json",
    "operator-command-effect-sha256": "operator-command-effect.sha256",
    "invocation-record": "invocation-record.json",
    "invocation-record-sha256": "invocation-record.sha256",
    "changed-path-report": "changed-path-report.json",
    "final-result": "final-result.json",
    "cleanup-disposition": "cleanup-disposition.json",
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
    if not expanded.exists() or not expanded.is_dir():
        raise AgentTaskError("EXTERNAL_ROOT_MISSING", "External root must be provisioned explicitly and exist as a directory", variable=name, value=raw)
    assert_no_symlink_components(expanded)
    resolved = expanded.resolve()
    if not os.access(resolved, os.W_OK | os.X_OK):
        raise AgentTaskError("EXTERNAL_ROOT_NOT_WRITABLE", "External root must be writable and searchable", variable=name, value=str(resolved))
    return resolved


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


def load_pilot_contract(root: Path) -> dict[str, Any]:
    contract = load_json(root / "contracts/governance/agent/codex-pilot-contract.json")
    require(
        contract.get("schemaVersion") == PILOT_CONTRACT_SCHEMA_VERSION,
        "PILOT_CONTRACT_INVALID",
        "Unsupported Codex pilot contract schema",
        actual=contract.get("schemaVersion"),
    )
    return contract


def required_qualification_ids(task: dict[str, Any], policy: dict[str, Any]) -> set[str]:
    semantics = policy.get("taskSemantics")
    require(isinstance(semantics, dict), "PILOT_TASK_SEMANTICS_MISSING", "Pilot task semantics are missing")
    risk_policies = semantics.get("riskPolicies")
    class_policies = semantics.get("changeClassPolicies")
    require(isinstance(risk_policies, dict) and isinstance(class_policies, dict), "PILOT_TASK_SEMANTICS_INVALID", "Pilot task qualification policies are invalid")
    risk = risk_policies.get(task["riskClass"])
    require(isinstance(risk, dict), "TASK_RISK_POLICY_MISSING", "Task risk class has no policy", riskClass=task["riskClass"])
    allowed_modes = risk.get("allowedModes")
    require(isinstance(allowed_modes, list) and task["mode"] in allowed_modes, "TASK_RISK_MODE_FORBIDDEN", "Task mode is forbidden for the selected risk class", mode=task["mode"], riskClass=task["riskClass"])
    result = set(risk.get("requiredQualificationCommandIds", []))
    for change_class in task["changeClasses"]:
        class_policy = class_policies.get(change_class)
        require(isinstance(class_policy, dict), "TASK_CHANGE_CLASS_INVALID", "Task change class is not registered", changeClass=change_class)
        result.update(class_policy.get("requiredQualificationCommandIds", []))
    return result


def validate_task(task: dict[str, Any], policy: dict[str, Any]) -> None:
    required = {
        "schemaVersion", "taskId", "pilotId", "repositoryId", "mode", "baseCommit", "integrationBranch",
        "riskClass", "changeClasses", "allowedPaths", "forbiddenPaths", "limits", "capabilities",
        "qualificationCommands", "requiredEvidence", "completionCriteria",
    }
    unknown = set(task) - (required | {"notes"})
    missing = required - set(task)
    require(not missing, "TASK_FIELDS_MISSING", "Task contract has missing fields", fields=sorted(missing))
    require(not unknown, "TASK_FIELDS_UNKNOWN", "Task contract has unknown fields", fields=sorted(unknown))
    task_contract = policy.get("taskContract") if isinstance(policy.get("taskContract"), dict) else {}
    expected_schema = task_contract.get("schemaVersion")
    require(expected_schema == TASK_SCHEMA_VERSION, "PILOT_TASK_SCHEMA_INVALID", "Pilot contract does not activate the supported task schema", expected=TASK_SCHEMA_VERSION, actual=expected_schema)
    require(task["schemaVersion"] == TASK_SCHEMA_VERSION, "TASK_SCHEMA_INVALID", "Unsupported task schema version")
    require(isinstance(task["taskId"], str) and TASK_ID_PATTERN.fullmatch(task["taskId"]) is not None, "TASK_ID_INVALID", "Invalid task ID")
    pilot = policy.get("pilot") if isinstance(policy.get("pilot"), dict) else {}
    require(task["pilotId"] == pilot.get("pilotId") == PILOT_ID, "TASK_PILOT_INVALID", "Task is not part of the active Springmaster Codex pilot")
    require(task["repositoryId"] == pilot.get("repositoryId") == REPOSITORY_ID, "TASK_REPOSITORY_INVALID", "Task repository must be Springmaster")
    semantics = policy.get("taskSemantics") if isinstance(policy.get("taskSemantics"), dict) else {}
    supported_modes = semantics.get("supportedModes")
    require(isinstance(supported_modes, list) and task["mode"] in supported_modes, "TASK_MODE_INVALID", "Invalid task mode")
    require(isinstance(task["baseCommit"], str) and re.fullmatch(r"[0-9a-f]{40}", task["baseCommit"]) is not None, "TASK_BASE_COMMIT_INVALID", "Invalid base commit")
    require(task["integrationBranch"] == pilot.get("integrationBranch") == "main", "TASK_BRANCH_INVALID", "Integration branch must be main")
    risk_policies = semantics.get("riskPolicies")
    require(isinstance(risk_policies, dict) and task["riskClass"] in risk_policies, "TASK_RISK_INVALID", "Invalid risk class")
    for key in ("changeClasses", "allowedPaths", "forbiddenPaths", "requiredEvidence"):
        require(isinstance(task[key], list) and len(task[key]) > 0, "TASK_LIST_INVALID", f"{key} must be a non-empty list", field=key)
        require(len(set(map(str, task[key]))) == len(task[key]), "TASK_LIST_DUPLICATE", f"{key} must not contain duplicates", field=key)
    require(all(isinstance(item, str) and item for item in task["changeClasses"]), "TASK_CHANGE_CLASS_INVALID", "Change classes must be strings")
    class_policies = semantics.get("changeClassPolicies")
    require(isinstance(class_policies, dict), "PILOT_TASK_SEMANTICS_INVALID", "Change class policies are missing")
    unknown_classes = sorted(set(task["changeClasses"]) - set(class_policies))
    require(not unknown_classes, "TASK_CHANGE_CLASS_INVALID", "Task contains unregistered change classes", changeClasses=unknown_classes)
    require(all(isinstance(item, str) and item for item in task["allowedPaths"]), "TASK_ALLOWED_PATH_INVALID", "Allowed paths must be strings")
    require(all(isinstance(item, str) and item for item in task["forbiddenPaths"]), "TASK_FORBIDDEN_PATH_INVALID", "Forbidden paths must be strings")
    for pattern in list(task["allowedPaths"]) + list(task["forbiddenPaths"]):
        require(not pattern.startswith("/") and ".." not in PurePosixPath(pattern).parts, "TASK_PATH_PATTERN_INVALID", "Path patterns must be repository-relative", pattern=pattern)
    limits = task["limits"]
    require(isinstance(limits, dict) and set(limits) == {"maxChangedFiles", "maxNetAddedBytes"}, "TASK_LIMITS_INVALID", "Limits object is invalid")
    require(isinstance(limits["maxChangedFiles"], int) and 0 <= limits["maxChangedFiles"] <= 200, "TASK_MAX_FILES_INVALID", "maxChangedFiles is invalid")
    require(isinstance(limits["maxNetAddedBytes"], int) and 0 <= limits["maxNetAddedBytes"] <= 10 * 1024 * 1024, "TASK_MAX_BYTES_INVALID", "maxNetAddedBytes is invalid")
    caps = task["capabilities"]
    expected_caps = {"mayModifyTests", "mayModifyGovernance", "mayModifyContracts", "mayCommit", "mayPush", "network"}
    require(isinstance(caps, dict) and set(caps) == expected_caps, "TASK_CAPABILITIES_INVALID", "Capabilities object is invalid")
    require(caps["mayCommit"] is False and caps["mayPush"] is False and caps["network"] == "disabled", "TASK_CAPABILITY_FORBIDDEN", "Commit, push and agent shell network must be disabled")
    require(all(isinstance(caps[key], bool) for key in ("mayModifyTests", "mayModifyGovernance", "mayModifyContracts")), "TASK_CAPABILITY_TYPE_INVALID", "Capability flags must be boolean")
    mode_policies = semantics.get("modePolicies")
    mode_policy = mode_policies.get(task["mode"]) if isinstance(mode_policies, dict) else None
    require(isinstance(mode_policy, dict), "TASK_MODE_POLICY_MISSING", "Task mode has no semantic policy", mode=task["mode"])
    if mode_policy.get("changedPathPolicy") == "forbid":
        require(limits["maxChangedFiles"] == 0 and limits["maxNetAddedBytes"] == 0, "TASK_MODE_LIMITS_INVALID", "Non-mutating task modes require zero change limits", mode=task["mode"])
        require(not any(caps[key] for key in ("mayModifyTests", "mayModifyGovernance", "mayModifyContracts")), "TASK_MODE_CAPABILITIES_INVALID", "Non-mutating task modes cannot grant modification capabilities", mode=task["mode"])
    capability_classes = semantics.get("capabilityChangeClasses")
    require(isinstance(capability_classes, dict), "PILOT_TASK_SEMANTICS_INVALID", "Capability change-class mapping is missing")
    for capability, change_class in capability_classes.items():
        if caps.get(capability):
            require(change_class in task["changeClasses"], "TASK_CAPABILITY_CLASS_MISSING", "Enabled capability requires its registered change class", capability=capability, changeClass=change_class)
    evidence = set(task["requiredEvidence"])
    require(evidence == REQUIRED_EVIDENCE, "TASK_EVIDENCE_INVALID", "Required evidence must match the active pilot evidence set", missing=sorted(REQUIRED_EVIDENCE - evidence), unknown=sorted(evidence - REQUIRED_EVIDENCE))
    criteria = task["completionCriteria"]
    expected_criteria = {
        "postcheckPass": True,
        "allQualificationCommandsPass": True,
        "requiredEvidenceComplete": True,
        "invocationRecordRequired": True,
        "explicitCleanupDisposition": True,
    }
    require(criteria == expected_criteria, "TASK_COMPLETION_CRITERIA_INVALID", "Completion criteria must match the active fail-closed pilot criteria")
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
    required_ids = required_qualification_ids(task, policy)
    require(required_ids <= command_ids, "TASK_QUALIFICATION_INCOMPLETE", "Qualification commands do not satisfy risk and change-class policy", missing=sorted(required_ids - command_ids))


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
    children = sorted(context.run_root.iterdir())
    unexpected = [str(path) for path in children if not path.is_dir()]
    if unexpected:
        raise AgentTaskError("ACTIVE_TASK_RECORD_INVALID", "External run root contains unexpected non-directory entries", paths=unexpected)
    for directory in children:
        path = directory / "run.json"
        try:
            value = load_json(path)
        except AgentTaskError as exc:
            raise AgentTaskError(
                "ACTIVE_TASK_RECORD_INVALID",
                "An agent run directory has missing or invalid run evidence",
                path=str(path),
                cause=exc.code,
            ) from exc
        task_id = value.get("taskId")
        status = value.get("status")
        if not isinstance(task_id, str) or TASK_ID_PATTERN.fullmatch(task_id) is None or status not in VALID_RUN_STATES:
            raise AgentTaskError("ACTIVE_TASK_RECORD_INVALID", "An agent run record has invalid identity or status", path=str(path), status=status)
        if task_slug(task_id) != directory.name:
            raise AgentTaskError("ACTIVE_TASK_RECORD_INVALID", "Agent run directory and task identity do not match", path=str(path), taskId=task_id)
        if value.get("status") in ACTIVE_STATES:
            records.append(value)
    return records


def validate_string_list(value: object, *, code: str, field: str, allow_empty: bool = False) -> list[str]:
    require(isinstance(value, list), code, f"{field} must be a list", field=field)
    result = value
    require(allow_empty or len(result) > 0, code, f"{field} must not be empty", field=field)
    require(all(isinstance(item, str) and item for item in result), code, f"{field} must contain non-empty strings", field=field)
    require(len(set(result)) == len(result), code, f"{field} must not contain duplicates", field=field)
    return result


def parse_utc_timestamp(value: object, *, code: str, field: str) -> datetime:
    require(isinstance(value, str) and value.endswith("Z"), code, "Timestamp must be an ISO-8601 UTC value", field=field)
    try:
        parsed = datetime.fromisoformat(value.removesuffix("Z") + "+00:00")
    except ValueError as exc:
        raise AgentTaskError(code, "Timestamp must be an ISO-8601 UTC value", field=field, value=value) from exc
    require(parsed.tzinfo is not None and parsed.utcoffset() == timezone.utc.utcoffset(parsed), code, "Timestamp must be UTC", field=field)
    return parsed


def argv_flag_value(argv: list[str], flag: str, *, code: str) -> str:
    positions = [index for index, item in enumerate(argv) if item == flag]
    require(len(positions) == 1, code, "Required Codex flag must occur exactly once", flag=flag, count=len(positions))
    index = positions[0]
    require(index + 1 < len(argv) and not argv[index + 1].startswith("-"), code, "Required Codex flag value is missing", flag=flag)
    return argv[index + 1]


def validate_codex_argv(argv: list[str], task: dict[str, Any], agent: dict[str, Any], invocation_policy: dict[str, Any]) -> None:
    prefix = invocation_policy.get("requiredArgvPrefix", [])
    require(argv[:len(prefix)] == prefix, "INVOCATION_ARGV_PREFIX_INVALID", "Codex invocation must use the required non-interactive exec prefix", expected=prefix, actual=argv[:len(prefix)])
    forbidden_flags = invocation_policy.get("forbiddenFlags", [])
    for item in argv:
        for forbidden in forbidden_flags:
            require(item != forbidden and not item.startswith(forbidden + "="), "INVOCATION_FLAG_FORBIDDEN", "Codex invocation contains a forbidden flag", flag=item)
    for flag in invocation_policy.get("requiredBooleanFlags", []):
        require(argv.count(flag) == 1, "INVOCATION_FLAG_REQUIRED", "Required Codex flag must occur exactly once", flag=flag, count=argv.count(flag))
    model = argv_flag_value(argv, "--model", code="INVOCATION_MODEL_FLAG_INVALID")
    require(model == agent["model"], "INVOCATION_MODEL_MISMATCH", "Codex model flag differs from the recorded model", expected=agent["model"], actual=model)
    approval = argv_flag_value(argv, "--ask-for-approval", code="INVOCATION_APPROVAL_FLAG_INVALID")
    require(approval == invocation_policy.get("requiredApprovalPolicy") == "never", "INVOCATION_APPROVAL_INVALID", "Codex approval policy must be never", actual=approval)
    mode_policies = invocation_policy.get("modeSandboxPolicies", {})
    mode_policy = mode_policies.get(task["mode"], {}) if isinstance(mode_policies, dict) else {}
    sandbox = argv_flag_value(argv, "--sandbox", code="INVOCATION_SANDBOX_FLAG_INVALID")
    require(sandbox == mode_policy.get("cliValue"), "INVOCATION_SANDBOX_INVALID", "Codex sandbox does not match the task mode", mode=task["mode"], expected=mode_policy.get("cliValue"), actual=sandbox)


def validate_platform_sandbox(value: object, task: dict[str, Any], worktree: Path, invocation_policy: dict[str, Any]) -> None:
    expected_fields = {
        "implementation", "workspaceRoot", "additionalWritableRoots", "operatorHomeWritable",
        "operatorDownloadsWritable", "integrationWorktreeWritable", "gitCommonDirectoryWritable",
        "externalRunRootWritable", "externalArtifactRootWritable", "temporaryDirectoriesWritable",
    }
    require(isinstance(value, dict) and set(value) == expected_fields, "INVOCATION_PLATFORM_SANDBOX_INVALID", "Platform sandbox fields are invalid")
    require(value["implementation"] == invocation_policy.get("platformSandboxImplementation") == "linux-bwrap", "INVOCATION_PLATFORM_SANDBOX_INVALID", "Linux bwrap sandbox implementation is required")
    require(isinstance(value["workspaceRoot"], str) and Path(value["workspaceRoot"]).is_absolute(), "INVOCATION_PLATFORM_SANDBOX_INVALID", "Platform workspace root must be absolute")
    require(Path(value["workspaceRoot"]).resolve() == worktree.resolve(), "INVOCATION_PLATFORM_SANDBOX_INVALID", "Platform workspace root must equal the prepared task worktree", expected=str(worktree), actual=value["workspaceRoot"])
    require(value["additionalWritableRoots"] == invocation_policy.get("additionalWritableRoots") == [], "INVOCATION_ADDITIONAL_WRITE_ROOT_FORBIDDEN", "Codex may not receive additional writable roots", actual=value["additionalWritableRoots"])
    for field in expected_fields - {"implementation", "workspaceRoot", "additionalWritableRoots"}:
        require(value[field] is False, "INVOCATION_HOST_WRITE_SCOPE_FORBIDDEN", "Codex host write scope must remain disabled", field=field, actual=value[field])


def validate_operator_effect(effect: dict[str, Any], task: dict[str, Any], record: dict[str, Any], worktree: Path, policy: dict[str, Any]) -> None:
    expected_fields = {
        "schemaVersion", "commandId", "taskId", "purpose", "argv", "workingDirectory",
        "reads", "writes", "network", "repositoryMutation", "destructiveActions",
        "directoryCreationPolicy", "overwritePolicy", "environmentInputs",
    }
    require(set(effect) == expected_fields, "OPERATOR_EFFECT_FIELDS_INVALID", "Operator command effect fields are invalid", missing=sorted(expected_fields - set(effect)), unknown=sorted(set(effect) - expected_fields))
    invocation_policy = policy.get("invocation") if isinstance(policy.get("invocation"), dict) else {}
    require(effect["schemaVersion"] == invocation_policy.get("effectSchemaVersion") == OPERATOR_EFFECT_SCHEMA_VERSION, "OPERATOR_EFFECT_SCHEMA_INVALID", "Operator command effect schema is invalid")
    require(effect["taskId"] == task["taskId"], "OPERATOR_EFFECT_TASK_INVALID", "Operator command effect is bound to another task")
    require(isinstance(effect["commandId"], str) and re.fullmatch(r"[a-z][a-z0-9-]*", effect["commandId"]) is not None, "OPERATOR_EFFECT_COMMAND_ID_INVALID", "Operator command effect command ID is invalid")
    require(isinstance(effect["purpose"], str) and effect["purpose"].strip(), "OPERATOR_EFFECT_PURPOSE_INVALID", "Operator command effect purpose is required")
    argv = validate_string_list(effect["argv"], code="OPERATOR_EFFECT_ARGV_INVALID", field="argv")
    require(argv == record.get("execution", {}).get("argv"), "INVOCATION_ARGV_MISMATCH", "Operator effect and invocation record argv differ")
    require(isinstance(effect["workingDirectory"], str) and Path(effect["workingDirectory"]).is_absolute(), "OPERATOR_EFFECT_CWD_INVALID", "Operator effect working directory must be absolute")
    require(Path(effect["workingDirectory"]).resolve() == worktree.resolve(), "OPERATOR_EFFECT_CWD_INVALID", "Codex calibration must run in the prepared task worktree", expected=str(worktree), actual=effect["workingDirectory"])
    require(effect["workingDirectory"] == record.get("execution", {}).get("workingDirectory"), "INVOCATION_CWD_MISMATCH", "Operator effect and invocation record working directory differ")
    reads = validate_string_list(effect["reads"], code="OPERATOR_EFFECT_READS_INVALID", field="reads")
    writes = validate_string_list(effect["writes"], code="OPERATOR_EFFECT_WRITES_INVALID", field="writes", allow_empty=True)
    allowed_reads = set(invocation_policy.get("allowedReadScopes", []))
    required_reads = set(invocation_policy.get("requiredReadScopes", []))
    mode_writes = invocation_policy.get("modeWriteScopes", {})
    required_writes = mode_writes.get(task["mode"], []) if isinstance(mode_writes, dict) else []
    require(set(reads) <= allowed_reads, "OPERATOR_EFFECT_READ_SCOPE_INVALID", "Operator effect declares an unauthorized read scope", unauthorized=sorted(set(reads) - allowed_reads))
    require(required_reads <= set(reads), "OPERATOR_EFFECT_READ_SCOPE_INVALID", "Operator effect omits a required read scope", missing=sorted(required_reads - set(reads)))
    require(writes == required_writes, "OPERATOR_EFFECT_WRITE_SCOPE_INVALID", "Operator effect write scope does not match the task mode", mode=task["mode"], expected=required_writes, actual=writes)
    require(effect["network"] == invocation_policy.get("networkPolicy"), "OPERATOR_EFFECT_NETWORK_INVALID", "Operator effect network policy is invalid")
    mode_mutations = invocation_policy.get("modeRepositoryMutationPolicies", {})
    expected_mutation = mode_mutations.get(task["mode"]) if isinstance(mode_mutations, dict) else None
    require(effect["repositoryMutation"] == expected_mutation, "OPERATOR_EFFECT_REPOSITORY_MUTATION_INVALID", "Operator effect repository mutation policy does not match the task mode", mode=task["mode"], expected=expected_mutation, actual=effect["repositoryMutation"])
    destructive = validate_string_list(effect["destructiveActions"], code="OPERATOR_EFFECT_DESTRUCTIVE_INVALID", field="destructiveActions", allow_empty=True)
    require(not destructive, "OPERATOR_EFFECT_DESTRUCTIVE_INVALID", "Codex calibration may not declare destructive actions", actions=destructive)
    require(effect["directoryCreationPolicy"] == invocation_policy.get("directoryCreationPolicy"), "OPERATOR_EFFECT_DIRECTORY_POLICY_INVALID", "Operator effect directory creation policy is invalid")
    require(effect["overwritePolicy"] == invocation_policy.get("overwritePolicy"), "OPERATOR_EFFECT_OVERWRITE_POLICY_INVALID", "Operator effect overwrite policy is invalid")
    environment_inputs = validate_string_list(effect["environmentInputs"], code="OPERATOR_EFFECT_ENV_INVALID", field="environmentInputs", allow_empty=True)
    allowlist = set(invocation_policy.get("environmentAllowlist", []))
    require(set(environment_inputs) <= allowlist, "OPERATOR_EFFECT_ENV_INVALID", "Operator effect declares unauthorized environment inputs", unauthorized=sorted(set(environment_inputs) - allowlist))


def validate_invocation_record(record: dict[str, Any], task: dict[str, Any], worktree: Path, policy: dict[str, Any]) -> None:
    expected_fields = {"schemaVersion", "taskId", "commandId", "recordedAt", "agent", "execution"}
    require(set(record) == expected_fields, "INVOCATION_RECORD_FIELDS_INVALID", "Codex invocation record fields are invalid", missing=sorted(expected_fields - set(record)), unknown=sorted(set(record) - expected_fields))
    invocation_policy = policy.get("invocation") if isinstance(policy.get("invocation"), dict) else {}
    require(record["schemaVersion"] == invocation_policy.get("recordSchemaVersion") == INVOCATION_RECORD_SCHEMA_VERSION, "INVOCATION_RECORD_SCHEMA_INVALID", "Codex invocation record schema is invalid")
    require(record["taskId"] == task["taskId"], "INVOCATION_RECORD_TASK_INVALID", "Codex invocation record is bound to another task")
    require(isinstance(record["commandId"], str) and re.fullmatch(r"[a-z][a-z0-9-]*", record["commandId"]) is not None, "INVOCATION_RECORD_COMMAND_ID_INVALID", "Codex invocation command ID is invalid")
    recorded_at = parse_utc_timestamp(record["recordedAt"], code="INVOCATION_RECORDED_AT_INVALID", field="recordedAt")
    agent = record["agent"]
    require(isinstance(agent, dict) and set(agent) == {"name", "cliVersion", "model"}, "INVOCATION_AGENT_INVALID", "Invocation agent identity is invalid")
    require(agent["name"] == invocation_policy.get("agentName") == "codex", "INVOCATION_AGENT_INVALID", "Only Codex calibration records are accepted")
    require(all(isinstance(agent[key], str) and agent[key].strip() for key in ("cliVersion", "model")), "INVOCATION_AGENT_INVALID", "Codex CLI version and model are required")
    execution = record["execution"]
    expected_execution_fields = {"argv", "workingDirectory", "sandboxProfile", "approvalPolicy", "platformSandbox", "environmentKeys", "startedAt", "finishedAt", "exitCode", "status"}
    require(isinstance(execution, dict) and set(execution) == expected_execution_fields, "INVOCATION_EXECUTION_INVALID", "Invocation execution fields are invalid")
    argv = validate_string_list(execution["argv"], code="INVOCATION_ARGV_INVALID", field="execution.argv")
    require(Path(argv[0]).name == invocation_policy.get("executableName") == "codex", "INVOCATION_EXECUTABLE_INVALID", "Invocation executable must be Codex", actual=argv[0])
    validate_codex_argv(argv, task, agent, invocation_policy)
    require(isinstance(execution["workingDirectory"], str) and Path(execution["workingDirectory"]).is_absolute(), "INVOCATION_CWD_INVALID", "Invocation working directory must be absolute")
    require(Path(execution["workingDirectory"]).resolve() == worktree.resolve(), "INVOCATION_CWD_INVALID", "Invocation working directory must equal the prepared task worktree", expected=str(worktree), actual=execution["workingDirectory"])
    mode_sandbox = invocation_policy.get("modeSandboxPolicies", {}).get(task["mode"], {})
    require(execution["sandboxProfile"] == mode_sandbox.get("recordValue"), "INVOCATION_SANDBOX_INVALID", "Recorded sandbox profile does not match the task mode", mode=task["mode"], expected=mode_sandbox.get("recordValue"), actual=execution["sandboxProfile"])
    require(execution["approvalPolicy"] == invocation_policy.get("requiredApprovalPolicy") == "never", "INVOCATION_APPROVAL_INVALID", "Approval policy must be never")
    validate_platform_sandbox(execution["platformSandbox"], task, worktree, invocation_policy)
    environment_keys = validate_string_list(execution["environmentKeys"], code="INVOCATION_ENV_INVALID", field="execution.environmentKeys", allow_empty=True)
    allowlist = set(invocation_policy.get("environmentAllowlist", []))
    require(set(environment_keys) <= allowlist, "INVOCATION_ENV_INVALID", "Invocation record contains environment keys outside the allowlist", unauthorized=sorted(set(environment_keys) - allowlist))
    started_at = parse_utc_timestamp(execution["startedAt"], code="INVOCATION_TIME_INVALID", field="startedAt")
    finished_at = parse_utc_timestamp(execution["finishedAt"], code="INVOCATION_TIME_INVALID", field="finishedAt")
    require(started_at <= finished_at <= recorded_at, "INVOCATION_TIME_INVALID", "Invocation timestamps are not monotonically ordered")
    require(execution["status"] in {"COMPLETED", "FAILED", "INTERRUPTED"}, "INVOCATION_STATUS_INVALID", "Invocation status is invalid")
    require(execution["exitCode"] is None or isinstance(execution["exitCode"], int), "INVOCATION_EXIT_INVALID", "Invocation exit code must be integer or null")
    if execution["status"] == "COMPLETED":
        require(execution["exitCode"] == 0, "INVOCATION_EXIT_INVALID", "A completed invocation must have exit code zero")
    elif execution["status"] == "FAILED":
        require(isinstance(execution["exitCode"], int) and execution["exitCode"] != 0, "INVOCATION_EXIT_INVALID", "A failed invocation must have a non-zero exit code")


def evidence_status(directory: Path, task: dict[str, Any], *, include_cleanup: bool) -> dict[str, Any]:
    required = set(task["requiredEvidence"])
    considered = set(required)
    if not include_cleanup:
        considered.discard("cleanup-disposition")
    present: list[str] = []
    missing: list[str] = []
    for evidence_id in sorted(considered):
        if evidence_id == "qualification-records":
            qualification_dir = directory / "qualification"
            complete = qualification_dir.is_dir() and all(
                (qualification_dir / f"{item['id']}.json").is_file() and (qualification_dir / f"{item['id']}.log").is_file()
                for item in task["qualificationCommands"]
            )
        else:
            relative = EVIDENCE_FILES.get(evidence_id)
            complete = relative is not None and (directory / relative).is_file()
        (present if complete else missing).append(evidence_id)
    return {
        "required": sorted(considered),
        "present": present,
        "missing": missing,
        "complete": not missing,
        "cleanupIncluded": include_cleanup,
    }


def cmd_record_invocation(args: argparse.Namespace) -> dict[str, Any]:
    context = resolve_context(args.project_root)
    policy = load_pilot_contract(context.current_root)
    directory, run_record = load_run_record(context, args.task_id)
    require(run_record.get("status") == "PREPARED", "INVOCATION_STATE_INVALID", "Invocation can be recorded only for a prepared task", status=run_record.get("status"))
    effect_target = directory / "operator-command-effect.json"
    record_target = directory / "invocation-record.json"
    require(not effect_target.exists() and not record_target.exists(), "INVOCATION_ALREADY_RECORDED", "Invocation evidence is immutable and already exists", taskId=args.task_id)
    task = load_json(directory / "task-contract.json")
    validate_task(task, policy)
    sources: list[Path] = []
    for raw in (args.effect, args.record):
        source_input = Path(raw).expanduser()
        require(source_input.is_absolute(), "INVOCATION_SOURCE_INVALID", "Invocation evidence source must be absolute", path=str(source_input))
        assert_no_symlink_components(source_input)
        source = source_input.resolve()
        require(source.is_file(), "INVOCATION_SOURCE_INVALID", "Invocation evidence source must be a regular file", path=str(source))
        require(path_contains(context.artifact_root, source), "INVOCATION_SOURCE_OUTSIDE_ARTIFACT_ROOT", "Invocation evidence source must be staged below the explicit external artifact root", path=str(source), artifactRoot=str(context.artifact_root))
        sources.append(source)
    effect_source, record_source = sources
    expected_task_hash = (directory / "task-contract.sha256").read_text(encoding="utf-8").split()[0]
    require(sha256_file(directory / "task-contract.json") == expected_task_hash, "TASK_CONTRACT_MUTATED", "Task contract changed before invocation recording")
    effect = load_json(effect_source)
    record = load_json(record_source)
    worktree = Path(run_record["worktreePath"])
    validate_invocation_record(record, task, worktree, policy)
    validate_operator_effect(effect, task, record, worktree, policy)
    require(effect["commandId"] == record["commandId"], "INVOCATION_COMMAND_ID_MISMATCH", "Operator effect and invocation record command IDs differ")
    shutil.copyfile(effect_source, effect_target)
    shutil.copyfile(record_source, record_target)
    effect_hash = sha256_file(effect_target)
    record_hash = sha256_file(record_target)
    atomic_text(directory / "operator-command-effect.sha256", f"{effect_hash}  operator-command-effect.json\n")
    atomic_text(directory / "invocation-record.sha256", f"{record_hash}  invocation-record.json\n")
    run_record["codexInvocation"] = "RECORDED"
    run_record["invocationRecordedAt"] = utc_now()
    run_record["operatorCommandEffectSha256"] = effect_hash
    run_record["invocationRecordSha256"] = record_hash
    atomic_json(directory / "run.json", run_record)
    return {
        "status": "RECORDED",
        "taskId": task["taskId"],
        "operatorCommandEffectSha256": effect_hash,
        "invocationRecordSha256": record_hash,
        "runDirectory": str(directory),
    }


def cmd_validate(args: argparse.Namespace) -> dict[str, Any]:
    root = discover_root(args.project_root)
    policy = load_pilot_contract(root)
    task_path = Path(args.task).expanduser().resolve()
    task = load_json(task_path)
    validate_task(task, policy)
    return {"status": "PASS", "taskId": task["taskId"], "taskPath": str(task_path), "schemaVersion": task["schemaVersion"]}


def cmd_prepare(args: argparse.Namespace) -> dict[str, Any]:
    context = resolve_context(args.project_root)
    policy = load_pilot_contract(context.current_root)
    require(context.project_id == REPOSITORY_ID, "PROJECT_ID_INVALID", "Current project is not Springmaster", projectId=context.project_id)
    task_path = Path(args.task).expanduser().resolve()
    task = load_json(task_path)
    validate_task(task, policy)
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
        "codexInvocation": "NOT_RECORDED",
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
        "codexInvocation": "NOT_RECORDED",
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


def baseline_blob_size(root: Path, base_commit: str, relative: str) -> int:
    completed = run(["git", "cat-file", "-s", f"{base_commit}:{relative}"], cwd=root, check=False)
    if completed.returncode != 0:
        return 0
    try:
        return int(completed.stdout.strip())
    except ValueError as exc:
        raise AgentTaskError("GIT_BLOB_SIZE_INVALID", "Git returned an invalid blob size", path=relative, value=completed.stdout.strip()) from exc


def net_added_bytes(root: Path, base_commit: str, paths: list[str]) -> int:
    total = 0
    for relative in paths:
        candidate = root / relative
        current = candidate.stat().st_size if candidate.is_file() and not candidate.is_symlink() else 0
        baseline = baseline_blob_size(root, base_commit, relative)
        total += max(0, current - baseline)
    return total


def changed_symlinks(root: Path, paths: list[str]) -> list[str]:
    return [relative for relative in paths if (root / relative).is_symlink()]


def validate_post_state(context: Context, directory: Path, record: dict[str, Any]) -> dict[str, Any]:
    policy = load_pilot_contract(context.current_root)
    task = load_json(directory / "task-contract.json")
    validate_task(task, policy)
    expected_hash = (directory / "task-contract.sha256").read_text(encoding="utf-8").split()[0]
    current_hash = sha256_file(directory / "task-contract.json")
    findings: list[dict[str, Any]] = []
    if current_hash != expected_hash:
        findings.append({"code": "TASK_CONTRACT_MUTATED", "expected": expected_hash, "actual": current_hash})
    for evidence_id, relative in (
        ("operator-command-effect", "operator-command-effect.json"),
        ("invocation-record", "invocation-record.json"),
    ):
        file_path = directory / relative
        hash_path = directory / f"{relative.removesuffix('.json')}.sha256"
        if file_path.is_file() and hash_path.is_file():
            expected = hash_path.read_text(encoding="utf-8").split()[0]
            actual = sha256_file(file_path)
            if actual != expected:
                findings.append({"code": "INVOCATION_EVIDENCE_MUTATED", "evidence": evidence_id, "expected": expected, "actual": actual})
        elif record.get("codexInvocation") == "RECORDED":
            findings.append({"code": "INVOCATION_EVIDENCE_MISSING", "evidence": evidence_id})
    invocation_path = directory / "invocation-record.json"
    if invocation_path.is_file():
        invocation = load_json(invocation_path)
        execution = invocation.get("execution") if isinstance(invocation.get("execution"), dict) else {}
        if execution.get("status") != "COMPLETED" or execution.get("exitCode") != 0:
            findings.append({
                "code": "CODEX_INVOCATION_NOT_COMPLETED",
                "status": execution.get("status"),
                "exitCode": execution.get("exitCode"),
            })
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
        mode_policy = policy["taskSemantics"]["modePolicies"][task["mode"]]
        if mode_policy.get("changedPathPolicy") == "forbid" and changed:
            findings.append({"code": "TASK_MODE_WRITE_FORBIDDEN", "mode": task["mode"], "paths": changed})
        if len(changed) > task["limits"]["maxChangedFiles"]:
            findings.append({"code": "CHANGED_FILE_LIMIT_EXCEEDED", "actual": len(changed), "maximum": task["limits"]["maxChangedFiles"]})
        size = net_added_bytes(worktree, task["baseCommit"], changed)
        if size > task["limits"]["maxNetAddedBytes"]:
            findings.append({"code": "NET_ADDED_BYTE_LIMIT_EXCEEDED", "actual": size, "maximum": task["limits"]["maxNetAddedBytes"]})
        path_classes = policy["taskSemantics"]["pathClassifications"]
        if not task["capabilities"]["mayModifyTests"]:
            for path in changed:
                if any(pattern_matches(path, pattern) for pattern in path_classes["tests"]):
                    findings.append({"code": "TEST_CHANGE_FORBIDDEN", "path": path})
        if not task["capabilities"]["mayModifyGovernance"]:
            for path in changed:
                if any(pattern_matches(path, pattern) for pattern in path_classes["governance"]):
                    findings.append({"code": "GOVERNANCE_CHANGE_FORBIDDEN", "path": path})
        if not task["capabilities"]["mayModifyContracts"]:
            for path in changed:
                if any(pattern_matches(path, pattern) for pattern in path_classes["contracts"]):
                    findings.append({"code": "CONTRACT_CHANGE_FORBIDDEN", "path": path})
    report = {
        "schemaVersion": "springmaster.agent-task-changed-path-report.v1",
        "taskId": task["taskId"],
        "checkedAt": utc_now(),
        "status": "PASS" if not findings else "FINDINGS",
        "findingCount": len(findings),
        "findings": findings,
        "changedPaths": changed,
        "netAddedBytes": size if worktree.is_dir() else 0,
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
    require(record.get("codexInvocation") == "RECORDED", "INVOCATION_RECORD_REQUIRED", "Qualification requires immutable Codex invocation evidence", taskId=args.task_id)
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
        "codexInvocation": "RECORDED",
        "completionCriteria": task["completionCriteria"],
        "integrationAuthorized": False,
    }
    atomic_json(directory / "final-result.json", final)
    evidence = evidence_status(directory, task, include_cleanup=False)
    final["requiredEvidence"] = evidence
    if not evidence["complete"]:
        final["status"] = "FAILED"
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
    task = load_json(directory / "task-contract.json")
    result["requiredEvidence"] = evidence_status(directory, task, include_cleanup=(directory / "cleanup-disposition.json").is_file())
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
    task = load_json(directory / "task-contract.json")
    evidence = evidence_status(directory, task, include_cleanup=True)
    disposition["requiredEvidence"] = evidence
    disposition["status"] = "CLEANED" if evidence["complete"] else "CLEANED_INCOMPLETE"
    atomic_json(directory / "cleanup-disposition.json", disposition)
    record["status"] = disposition["status"]
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
    record_invocation = sub.add_parser("record-invocation")
    record_invocation.add_argument("task_id")
    record_invocation.add_argument("--effect", required=True)
    record_invocation.add_argument("--record", required=True)
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
        elif args.command == "record-invocation":
            value = cmd_record_invocation(args)
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
        if args.command == "cleanup" and value.get("status") != "CLEANED":
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
