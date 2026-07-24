#!/usr/bin/env python3
"""Project-neutral operational facade for detached Cocondo Toolkit runs."""

from __future__ import annotations

import argparse
import fcntl
import json
import os
import re
import shutil
import subprocess
import sys
import time
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
    artifact_root: Path | None
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
        return path.resolve()
    parts = path.parts
    if parts and parts[0] == ".git":
        return git_common_dir.joinpath(*parts[1:]).resolve()
    return (project_root / path).resolve()


def optional_path(value: str | None) -> Path | None:
    if not value:
        return None
    return Path(value).expanduser().resolve()


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

    artifact_root = optional_path(
        os.environ.get("COCONDO_ARTIFACT_ROOT")
        or git(current_root, "config", "--get", "cocondo.artifactRoot", check=False)
        or None
    )
    worktree_root = optional_path(
        os.environ.get("COCONDO_WORKTREE_ROOT")
        or git(current_root, "config", "--get", "cocondo.worktreeRoot", check=False)
        or None
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
        artifact_root=artifact_root,
        worktree_root=worktree_root,
    )


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
    if candidate.is_absolute():
        path = candidate.resolve()
    elif candidate.exists():
        path = candidate.resolve()
    elif context.artifact_root is not None:
        path = (context.artifact_root / candidate).resolve()
    else:
        path = candidate.resolve()
    if not path.is_file():
        raise ProcessOpsError("ARTIFACT_NOT_FOUND", "Patch artifact does not exist", artifact=str(path))
    return path


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
        "artifactRoot": str(context.artifact_root) if context.artifact_root else None,
        "worktreeRoot": str(context.worktree_root) if context.worktree_root else None,
    }
    emit(value, args.format)
    return 0


def command_patch_start(args: argparse.Namespace, context: Context, *, accept: bool) -> int:
    assert_integration_clean(context)
    artifact = resolve_artifact(args.artifact, context)
    if accept:
        command = ["accept", str(artifact), "--profile", args.profile]
        if args.no_commit:
            command.append("--no-commit")
        name = "patch-accept"
    else:
        command = ["apply", str(artifact), "--dry-run", "--profile", args.profile]
        name = "patch-dry-run"
    payload = cpatch_json(context, command)
    payload["operation"] = name
    payload["artifactFileName"] = artifact.name
    payload["integrationRoot"] = str(context.integration_root)
    report = persist_operation(context, name, payload)
    summary = compact(payload)
    summary["operationReport"] = str(report)
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
    report = persist_operation(context, "status", payload)
    summary = compact(payload)
    summary["operationReport"] = str(report)
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
    summary = compact(payload)
    summary["recommendedAction"] = recommendation(str(summary.get("status") or "UNKNOWN"))
    report = persist_operation(context, "resume", payload)
    summary["operationReport"] = str(report)
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
            if verbose and signature != last_signature:
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
    report = persist_operation(context, "result", payload)
    summary = compact(payload)
    summary["operationReport"] = str(report)
    emit(payload if args.verbose else summary, args.format)
    if args.strict_exit and str(summary.get("status")) in FAILURE_STATES:
        return int(summary.get("exitCode") or 1)
    return 0


def command_diagnose(args: argparse.Namespace, context: Context) -> int:
    output = Path(args.output).expanduser().resolve() if args.output else context.process_state_root / "diagnostics" / f"{utc_stamp()}-{args.reference}.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = cpatch_json(context, ["diagnose", args.reference, "--output", str(output)])
    summary = compact(payload)
    summary["diagnosticFile"] = str(output)
    emit(summary, args.format)
    return 0


def copy_if_file(source: Path, destination: Path) -> None:
    if source.is_file():
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)


def command_incident(args: argparse.Namespace, context: Context) -> int:
    payload = status_payload(context, args.reference)
    run_id = str(payload.get("runId") or args.reference)
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
    summary["recommendedAction"] = recommendation(str(summary.get("status") or "UNKNOWN"))
    atomic_json(incident_dir / "summary.json", summary)
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
        raise ProcessOpsError("COMMAND_UNSUPPORTED", "Unsupported command", command=args.command_name)
    except ProcessOpsError as exc:
        error = {"ok": False, "errorCode": exc.code, "message": exc.message, **exc.details}
        emit(error, getattr(args, "format", "human"))
        return 9


if __name__ == "__main__":
    raise SystemExit(main())
