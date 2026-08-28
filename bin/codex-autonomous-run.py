#!/usr/bin/env python3
"""Durable ADR-0019 Logical Run orchestration to the human accept boundary."""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import time
from typing import Any
import zipfile

SCHEMA = "springmaster.codex-autonomous-run.v1"
STATE_SCHEMA = "springmaster.codex-autonomous-run-state.v1"
PACKET_SCHEMA = "springmaster.codex-autonomous-repair-packet.v1"
TERMINAL = {"PREACCEPT", "STOPPED"}
REPAIRABLE = {"QUALIFICATION_FAILURE", "POSTCHECK_REPAIRABLE"}
STREAM_LAG = re.compile(r"^in-process app-server event stream lagged; dropped [1-9][0-9]* events$")
LOG_TAIL_BYTES = 8192


class RunError(RuntimeError):
    def __init__(self, code: str, message: str, **details: Any):
        super().__init__(message)
        self.code, self.message, self.details = code, message, details


def fail(condition: bool, code: str, message: str, **details: Any) -> None:
    if not condition:
        raise RunError(code, message, **details)


def canonical(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")


def sha_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha_file(path: Path) -> str:
    return sha_bytes(path.read_bytes())


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RunError("MALFORMED_EVIDENCE", "JSON evidence cannot be read", path=str(path), error=str(exc)) from exc
    fail(isinstance(value, dict), "MALFORMED_EVIDENCE", "JSON evidence must be an object", path=str(path))
    return value


def atomic(path: Path, value: Any, mode: int = 0o644) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(canonical(value))
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(name, mode)
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def run(argv: list[str], cwd: Path, *, timeout: int | None = None, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    fail(bool(argv) and all(isinstance(x, str) and x for x in argv), "ORACLE_CHANGE_REQUIRED", "Command must remain a non-empty argv array")
    try:
        return subprocess.run(argv, cwd=cwd, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise RunError("HOST_TOOL_ERROR", "Public primitive could not execute", argv=argv, error=str(exc)) from exc


def git_blob(project: Path, revision: str, relative: str) -> bytes | None:
    completed = subprocess.run(["git", "cat-file", "blob", f"{revision}:{relative}"], cwd=project, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    return completed.stdout if completed.returncode == 0 else None


def run_json(argv: list[str], cwd: Path, *, timeout: int | None = None) -> tuple[dict[str, Any], subprocess.CompletedProcess[str]]:
    result = run(argv, cwd, timeout=timeout)
    try:
        value = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise RunError("HOST_TOOL_ERROR", "Public primitive returned malformed JSON", argv=argv, exitCode=result.returncode, stdout=result.stdout[-2000:], stderr=result.stderr[-2000:]) from exc
    fail(isinstance(value, dict), "HOST_TOOL_ERROR", "Public primitive JSON is not an object", argv=argv)
    return value, result


def root(path: str | None) -> Path:
    candidate = Path(path).resolve() if path else Path(__file__).resolve().parents[1]
    completed = run(["git", "rev-parse", "--show-toplevel"], candidate)
    fail(completed.returncode == 0, "HOST_TOOL_ERROR", "Project root is not a Git worktree")
    return Path(completed.stdout.strip()).resolve()


def artifact_root() -> Path:
    raw = os.environ.get("COCONDO_ARTIFACT_ROOT")
    fail(bool(raw), "HOST_TOOL_ERROR", "COCONDO_ARTIFACT_ROOT is required")
    value = Path(str(raw)).expanduser()
    fail(value.is_absolute() and value.is_dir() and not value.is_symlink(), "HOST_TOOL_ERROR", "External artifact root is missing or unsafe", path=str(value))
    return value.resolve()


def run_dir(logical_id: str) -> Path:
    return artifact_root() / "codex-autonomous-runs" / logical_id.lower()


def match(path: str, pattern: str) -> bool:
    if pattern.endswith("/**"):
        prefix = pattern[:-3].rstrip("/")
        return path == prefix or path.startswith(prefix + "/")
    return fnmatch.fnmatchcase(path, pattern.rstrip("/"))


def validate_task(task: dict[str, Any]) -> None:
    required = {"schemaVersion", "taskId", "pilotId", "repositoryId", "mode", "baseCommit", "integrationBranch", "riskClass", "changeClasses", "allowedPaths", "forbiddenPaths", "limits", "capabilities", "qualificationCommands", "requiredEvidence", "completionCriteria"}
    fail(required.issubset(task), "MALFORMED_EVIDENCE", "Task template is incomplete", missing=sorted(required - set(task)))
    fail(task["schemaVersion"] == "springmaster.agent-task.v2" and task["mode"] == "implementation", "CAPABILITY_EXPANSION_REQUIRED", "Logical runs require implementation Agent Task V2")
    fail(task["capabilities"].get("mayCommit") is False and task["capabilities"].get("mayPush") is False and task["capabilities"].get("network") == "disabled", "SECURITY_BOUNDARY_VIOLATION", "Task capabilities exceed the pilot boundary")
    for item in task["qualificationCommands"]:
        fail(isinstance(item.get("argv"), list) and item["argv"] and all(isinstance(x, str) and x for x in item["argv"]), "ORACLE_CHANGE_REQUIRED", "Qualification must use immutable argv arrays")


def validate_contract(value: dict[str, Any]) -> None:
    required = {"schemaVersion", "logicalRunId", "taskTemplate", "prompt", "model", "budgets", "patch"}
    fail(set(value) == required, "MALFORMED_EVIDENCE", "Logical Run contract fields differ", expected=sorted(required), actual=sorted(value))
    fail(value["schemaVersion"] == SCHEMA, "MALFORMED_EVIDENCE", "Logical Run schema version is unsupported")
    logical_id = value["logicalRunId"]
    fail(isinstance(logical_id, str) and re.fullmatch(r"[A-Z][A-Z0-9-]{2,50}", logical_id) is not None, "MALFORMED_EVIDENCE", "logicalRunId is invalid")
    fail(len(f"{logical_id}-A999") <= 64, "MALFORMED_EVIDENCE", "logicalRunId is too long for deterministic task IDs")
    fail(isinstance(value["prompt"], str) and value["prompt"].strip(), "MALFORMED_EVIDENCE", "prompt is required")
    fail(isinstance(value["model"], str) and value["model"].strip(), "MALFORMED_EVIDENCE", "model is required")
    budgets = value["budgets"]
    fail(set(budgets) == {"maxAttempts", "activeTimeSeconds", "attemptActiveTimeoutSeconds", "noProgressTimeoutSeconds"}, "MALFORMED_EVIDENCE", "Budget fields differ")
    fail(isinstance(budgets["maxAttempts"], int) and 1 <= budgets["maxAttempts"] <= 20, "MALFORMED_EVIDENCE", "maxAttempts is outside 1..20")
    for key in ("activeTimeSeconds", "attemptActiveTimeoutSeconds", "noProgressTimeoutSeconds"):
        fail(isinstance(budgets[key], int) and 1 <= budgets[key] <= 86400, "MALFORMED_EVIDENCE", "Time budget is outside 1..86400", field=key)
    patch = value["patch"]
    fail(set(patch) == {"name", "title", "scope"} and all(isinstance(patch[k], str) and patch[k] for k in patch), "MALFORMED_EVIDENCE", "Patch identity is incomplete")
    validate_task(value["taskTemplate"])


def state_summary(state: dict[str, Any]) -> dict[str, Any]:
    keys = ("logicalRunId", "state", "attemptOrdinal", "attemptId", "lastFailureClass", "blockerClass", "processRunId", "patchId", "patchArtifactId", "dryRunId", "nextAction")
    return {key: state.get(key) for key in keys if state.get(key) is not None}


def save_state(directory: Path, state: dict[str, Any]) -> None:
    state["schemaVersion"] = STATE_SCHEMA
    atomic(directory / "state.json", state)


def initial_state(contract: dict[str, Any], request_sha: str) -> dict[str, Any]:
    return {"schemaVersion": STATE_SCHEMA, "logicalRunId": contract["logicalRunId"], "requestSha256": request_sha, "state": "READY", "attemptOrdinal": 0, "attemptId": None, "attempts": [], "lastFailureClass": None, "blockerClass": None, "processRunId": None, "patchId": None, "patchArtifactId": None, "dryRunId": None, "nextAction": "START_WORKER", "activeSeconds": 0}


def task_for(contract: dict[str, Any], ordinal: int) -> dict[str, Any]:
    task = json.loads(json.dumps(contract["taskTemplate"]))
    task["taskId"] = f"{contract['logicalRunId']}-A{ordinal:03d}"
    return task


def authorization_snapshot(task: dict[str, Any]) -> bytes:
    fields = ("baseCommit", "integrationBranch", "riskClass", "changeClasses", "allowedPaths", "forbiddenPaths", "capabilities", "limits", "qualificationCommands", "completionCriteria")
    return canonical({key: task[key] for key in fields})


def integration_guard(project: Path, base: str) -> None:
    head = run(["git", "rev-parse", "HEAD"], project)
    status = run(["git", "status", "--porcelain=v1", "--untracked-files=all"], project)
    fail(head.returncode == 0 and head.stdout.strip() == base, "INTEGRATION_BASE_DRIFT", "Integration HEAD differs from Logical Run base", expected=base, actual=head.stdout.strip())
    fail(status.returncode == 0 and status.stdout == "", "INTEGRATION_BASE_DRIFT", "Integration tree is not clean", status=status.stdout.splitlines()[:20])


def changed_paths(worktree: Path) -> list[str]:
    result = run(["git", "status", "--porcelain=v1", "-z", "--untracked-files=all"], worktree)
    fail(result.returncode == 0, "HOST_TOOL_ERROR", "Cannot inspect attempt worktree")
    values, entries, index = [], result.stdout.split("\0"), 0
    while index < len(entries) and entries[index]:
        entry = entries[index]
        fail(len(entry) >= 4, "MALFORMED_EVIDENCE", "Git path evidence is malformed")
        code, path = entry[:2], entry[3:]
        if "R" in code or "C" in code:
            index += 1
            fail(index < len(entries) and bool(entries[index]), "MALFORMED_EVIDENCE", "Rename evidence is incomplete")
            path = entries[index]
        values.append(path.replace("\\", "/")); index += 1
    return sorted(set(values))


def fingerprint(worktree: Path, paths: list[str]) -> str:
    digest = hashlib.sha256()
    for relative in paths:
        candidate = worktree / relative
        digest.update(relative.encode() + b"\0")
        if candidate.is_file() and not candidate.is_symlink():
            digest.update(f"{stat.S_IMODE(candidate.stat().st_mode):04o}".encode() + b"\0" + candidate.read_bytes())
        else:
            digest.update(b"MISSING\0")
    return digest.hexdigest()


def classify_postcheck(report: dict[str, Any]) -> str:
    codes = {str(x.get("code")) for x in report.get("findings", []) if isinstance(x, dict)}
    if not codes:
        return "PASS"
    if codes & {"INTEGRATION_HEAD_CHANGED", "INTEGRATION_TREE_CHANGED", "WORKTREE_HEAD_CHANGED"}:
        return "INTEGRATION_BASE_DRIFT"
    if codes & {"FORBIDDEN_PATH_CHANGED", "CHANGED_SYMLINK_FORBIDDEN", "ROOT_WRITE_NOT_EXACTLY_ALLOWED"}:
        return "SECURITY_BOUNDARY_VIOLATION"
    if codes & {"UNDECLARED_PATH_CHANGED", "CHANGED_FILE_LIMIT_EXCEEDED", "NET_ADDED_BYTE_LIMIT_EXCEEDED"}:
        return "SCOPE_EXPANSION_REQUIRED"
    if codes & {"TEST_CHANGE_FORBIDDEN", "GOVERNANCE_CHANGE_FORBIDDEN", "CONTRACT_CHANGE_FORBIDDEN", "TASK_MODE_WRITE_FORBIDDEN"}:
        return "CAPABILITY_EXPANSION_REQUIRED"
    return "HOST_TOOL_ERROR"


def stream_lag_only(invocation: dict[str, Any]) -> bool:
    execution = invocation.get("execution") if isinstance(invocation.get("execution"), dict) else {}
    invocation_ref = invocation.get("invocation") if isinstance(invocation.get("invocation"), dict) else {}
    if not execution and isinstance(invocation_ref.get("path"), str):
        raw_record = load_json(Path(invocation_ref["path"]))
        execution = raw_record.get("execution") if isinstance(raw_record.get("execution"), dict) else {}
    validation = invocation.get("jsonlValidation") if isinstance(invocation.get("jsonlValidation"), dict) else {}
    validation_ref = invocation.get("codexJsonlValidation") if isinstance(invocation.get("codexJsonlValidation"), dict) else {}
    if not validation and isinstance(validation_ref.get("path"), str):
        validation = load_json(Path(validation_ref["path"]))
    findings = validation.get("findings") if isinstance(validation.get("findings"), list) else []
    error_items = [x for x in findings if isinstance(x, dict) and x.get("code") == "CODEX_ERROR_ITEM"]
    return bool(error_items) and invocation.get("status") == "FAILED" and execution.get("exitCode") == 0 and execution.get("status") == "COMPLETED" and validation.get("parseErrorCount") == 0 and validation.get("turnCompletedCount", 0) >= 1 and validation.get("turnFailedCount") == 0 and all(isinstance(x.get("message"), str) and STREAM_LAG.fullmatch(x["message"]) for x in error_items) and len(findings) == len(error_items)


def diagnostic_qualification(project: Path, task: dict[str, Any], worktree: Path, attempt_dir: Path) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    qdir = attempt_dir / "diagnostic-qualification"; qdir.mkdir(parents=True, exist_ok=True)
    env = {key: value for key, value in os.environ.items() if key in {"PATH", "HOME", "USER", "LANG", "LC_ALL", "TZ", "JAVA_HOME", "MAVEN_OPTS"}}
    env.update({"CI": "true", "GIT_TERMINAL_PROMPT": "0"})
    for item in task["qualificationCommands"]:
        log = qdir / f"{item['id']}.log"
        result = run(item["argv"], worktree, timeout=item["timeoutSeconds"], env=env)
        data = (result.stdout + ("\n--- STDERR ---\n" if result.stderr else "") + result.stderr).encode()
        log.write_bytes(data); log.chmod(0o644)
        record = {"id": item["id"], "argv": item["argv"], "timeoutSeconds": item["timeoutSeconds"], "status": "PASS" if result.returncode == 0 else "FAIL", "exitCode": result.returncode, "logPath": str(log), "logSha256": sha_bytes(data), "logTail": data[-LOG_TAIL_BYTES:].decode("utf-8", "replace")}
        atomic(qdir / f"{item['id']}.json", record); output.append(record)
    return output


def create_bundle(project: Path, task: dict[str, Any], worktree: Path, paths: list[str], target: Path) -> dict[str, Any]:
    fail(bool(paths), "NO_PROGRESS", "Failed attempt produced no changed bytes")
    allowed = task["allowedPaths"]
    fail(all(any(match(path, pattern) for pattern in allowed) and not any(match(path, pattern) for pattern in task["forbiddenPaths"]) for path in paths), "SCOPE_EXPANSION_REQUIRED", "Bundle contains unauthorized paths", changedPaths=paths)
    operations, payload = [], {}
    for relative in paths:
        candidate = worktree / relative
        source = git_blob(project, task["baseCommit"], relative)
        if candidate.is_file() and not candidate.is_symlink():
            data = candidate.read_bytes(); mode = "100755" if candidate.stat().st_mode & stat.S_IXUSR else "100644"
            operation = "replace" if source is not None else "create"; target_hash = sha_bytes(data); payload[relative] = data
        else:
            fail(source is not None, "MALFORMED_EVIDENCE", "Changed path has neither base nor regular target", path=relative)
            operation, mode, target_hash = "delete", None, None
        operations.append({"path": relative, "operation": operation, "sourceSha256": sha_bytes(source) if source is not None else None, "targetSha256": target_hash, "mode": mode})
    manifest = {"schemaVersion": "springmaster.codex-change-bundle.v1", "bundleId": f"{task['taskId'].lower()}-{fingerprint(worktree, paths)[:16]}", "taskId": task["taskId"], "repositoryId": task["repositoryId"], "baseCommit": task["baseCommit"], "operations": operations}
    # The bundle is retargeted to its immutable successor before creation.
    target.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        def put(name: str, data: bytes, mode: int) -> None:
            info = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0)); info.external_attr = (mode & 0xFFFF) << 16; info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, data)
        put("manifest.json", canonical(manifest), 0o644)
        for relative in sorted(payload): put(f"payload/{relative}", payload[relative], 0o644)
    target.chmod(0o444)
    return {"bundleId": manifest["bundleId"], "bundlePath": str(target), "bundleSha256": sha_file(target), "operations": operations}


def failure_fingerprint(post: dict[str, Any], qualifications: list[dict[str, Any]]) -> str:
    stable_post = {key: post.get(key) for key in ("status", "findingCount", "findings", "changedPaths", "netAddedBytes")}
    stable = {"postcheck": stable_post, "qualificationResults": [{k: x.get(k) for k in ("id", "argv", "timeoutSeconds", "status", "exitCode", "logSha256", "logTail")} for x in qualifications]}
    return sha_bytes(canonical(stable))


def repair_packet(contract: dict[str, Any], task: dict[str, Any], ordinal: int, successor: str, paths: list[str], worktree: Path, post: dict[str, Any], qualifications: list[dict[str, Any]], bundle: dict[str, Any], previous: str | None) -> dict[str, Any]:
    failure = failure_fingerprint(post, qualifications)
    return {"schemaVersion": PACKET_SCHEMA, "logicalRunId": contract["logicalRunId"], "failedAttemptId": task["taskId"], "failedAttemptOrdinal": ordinal, "successorAttemptId": successor, "baseCommit": task["baseCommit"], "worktreeFingerprint": fingerprint(worktree, paths), "changedPaths": paths, "postcheckResult": post, "qualificationResults": qualifications, "failureFingerprint": failure, "previousFailureFingerprint": previous, "authorizationOraclesUnchanged": True, "predecessorChangeBundle": {k: bundle[k] for k in ("bundleId", "bundlePath", "bundleSha256")}}


def invoke_attempt(project: Path, contract: dict[str, Any], state: dict[str, Any], directory: Path, ordinal: int, bundle: dict[str, Any] | None, packet_path: Path | None) -> tuple[dict[str, Any], dict[str, Any], Path]:
    task = task_for(contract, ordinal); attempt_id = task["taskId"]; attempt_dir = directory / "attempts" / f"A{ordinal:03d}"; attempt_dir.mkdir(parents=True, exist_ok=True)
    task_path = attempt_dir / "task-contract.json"; atomic(task_path, task)
    validate, completed = run_json([str(project / "bin/agent-task.sh"), "--project-root", str(project), "--format", "json", "validate", str(task_path)], project)
    fail(completed.returncode == 0 and validate.get("status") == "PASS", "HOST_TOOL_ERROR", "Successor Agent Task validation failed", evidence=validate)
    prepared, completed = run_json([str(project / "bin/agent-task.sh"), "--project-root", str(project), "--format", "json", "prepare", str(task_path)], project)
    fail(completed.returncode == 0 and prepared.get("status") == "PREPARED", "HOST_TOOL_ERROR", "Agent Task preparation failed", evidence=prepared)
    worktree = Path(prepared["worktreePath"]); prompt = contract["prompt"]
    if bundle is not None:
        # Change-bundle manifests are successor-bound; raw predecessor evidence is retained in the packet.
        prompt = "Apply the bound predecessor bundle first by running exactly ./bin/codex-change-bundle.sh apply. Then repair every finding in the immutable repair packet without changing authorization or oracle boundaries.\nRepair packet: " + str(packet_path) + "\n\n" + prompt
    prompt_path = attempt_dir / "prompt.txt"; prompt_path.write_text(prompt, encoding="utf-8"); prompt_path.chmod(0o444)
    invocation_path = attempt_dir / "host-invocation.json"
    argv = [str(project / "bin/codex-host-sandbox.sh"), "--project-root", str(project), "--format", "json", "invoke-start", "--task-id", attempt_id, "--prompt", str(prompt_path), "--model", contract["model"], "--active-timeout-seconds", str(contract["budgets"]["attemptActiveTimeoutSeconds"]), "--no-progress-timeout-seconds", str(contract["budgets"]["noProgressTimeoutSeconds"]), "--out", str(invocation_path)]
    if bundle is not None: argv.extend(["--change-bundle", bundle["bundlePath"]])
    started, completed = run_json(argv, project)
    fail(completed.returncode == 0 and started.get("runId"), "HOST_TOOL_ERROR", "Durable Codex invocation did not start", evidence=started)
    state.update({"state": "ATTEMPT_RUNNING", "attemptOrdinal": ordinal, "attemptId": attempt_id, "processRunId": started["runId"], "nextAction": "OBSERVE_ATTEMPT"}); save_state(directory, state)
    observed, completed = run_json([str(project / "bin/process-ops.sh"), "--project-root", str(project), "--format", "json", "wait", str(started["runId"]), "--timeout", str(contract["budgets"]["activeTimeSeconds"])], project)
    fail(completed.returncode == 0, "HOST_TOOL_ERROR", "Durable invocation observation failed", evidence=observed)
    fail(invocation_path.is_file(), "HOST_TOOL_ERROR", "Host invocation evidence is missing", path=str(invocation_path))
    invocation = load_json(invocation_path)
    return task, invocation, worktree


def resume_attempt(project: Path, contract: dict[str, Any], state: dict[str, Any], directory: Path, ordinal: int) -> tuple[dict[str, Any], dict[str, Any], Path]:
    """Reconnect to an already consumed physical attempt without invoking it again."""
    task = task_for(contract, ordinal)
    status, completed = run_json([str(project / "bin/agent-task.sh"), "--project-root", str(project), "--format", "json", "status", task["taskId"]], project)
    fail(completed.returncode == 0 and status.get("taskId") == task["taskId"], "HOST_TOOL_ERROR", "Persisted physical attempt cannot be resolved", evidence=status)
    worktree = Path(status["worktreePath"])
    invocation_path = directory / "attempts" / f"A{ordinal:03d}" / "host-invocation.json"
    if not invocation_path.is_file():
        process_id = state.get("processRunId")
        fail(isinstance(process_id, str), "MALFORMED_EVIDENCE", "Running attempt has no process binding")
        observed, result = run_json([str(project / "bin/process-ops.sh"), "--project-root", str(project), "--format", "json", "wait", process_id, "--timeout", str(contract["budgets"]["activeTimeSeconds"])], project)
        fail(result.returncode == 0, "HOST_TOOL_ERROR", "Resumed invocation observation failed", evidence=observed)
    fail(invocation_path.is_file(), "HOST_TOOL_ERROR", "Resumed host invocation evidence is missing")
    return task, load_json(invocation_path), worktree


def promote(project: Path, contract: dict[str, Any], state: dict[str, Any], directory: Path, task: dict[str, Any]) -> None:
    promotion = state.setdefault("promotion", {})
    task_status, completed = run_json([str(project / "bin/agent-task.sh"), "--project-root", str(project), "--format", "json", "status", task["taskId"]], project)
    fail(completed.returncode == 0, "HOST_TOOL_ERROR", "Qualified task status cannot be resolved", evidence=task_status)
    if task_status.get("status") == "HANDED_OFF":
        handoff = {"status": "HANDED_OFF", "handoffManifest": task_status.get("handoffManifest")}
        manifest_path = Path(str(handoff["handoffManifest"]))
        handoff_manifest = load_json(manifest_path)
        handoff["patchPath"] = str(manifest_path.parent / handoff_manifest["patch"]["path"])
        handoff["patchSha256"] = handoff_manifest["patch"]["sha256"]
    else:
        handoff, completed = run_json([str(project / "bin/agent-task.sh"), "--project-root", str(project), "--format", "json", "handoff", task["taskId"]], project)
        fail(completed.returncode == 0 and handoff.get("status") == "HANDED_OFF", "HOST_TOOL_ERROR", "Immutable handoff failed", evidence=handoff)
    manifest = load_json(Path(handoff["handoffManifest"])); patch_path = Path(handoff["patchPath"])
    fail(manifest.get("isolatedApplyCheck") == "PASS" and sha_file(patch_path) == handoff["patchSha256"], "MALFORMED_EVIDENCE", "Handoff bytes were not verified")
    promotion.update({"stage": "HANDOFF_VERIFIED", "handoffManifest": str(handoff["handoffManifest"]), "handoffManifestSha256": sha_file(Path(handoff["handoffManifest"]))}); save_state(directory, state)
    worktree_root = Path(os.environ.get("COCONDO_WORKTREE_ROOT", ""))
    fail(worktree_root.is_absolute() and worktree_root.is_dir(), "HOST_TOOL_ERROR", "COCONDO_WORKTREE_ROOT is required for trusted candidate")
    candidate = worktree_root / f"{contract['logicalRunId'].lower()}-candidate"
    branch = f"candidate/{contract['logicalRunId'].lower()}"
    if not candidate.exists():
        created = run(["git", "worktree", "add", "-b", branch, str(candidate), task["baseCommit"]], project)
        fail(created.returncode == 0, "HOST_TOOL_ERROR", "Trusted candidate worktree creation failed", stderr=created.stderr[-2000:])
    candidate_head_before = run(["git", "rev-parse", "HEAD"], candidate).stdout.strip()
    candidate_status = run(["git", "status", "--porcelain=v1", "--untracked-files=all"], candidate).stdout
    if candidate_head_before == task["baseCommit"] and not candidate_status:
        applied = run(["git", "apply", "--binary", "--index", str(patch_path)], candidate)
        fail(applied.returncode == 0, "HOST_TOOL_ERROR", "Trusted handoff application failed", stderr=applied.stderr[-2000:])
    if candidate_head_before == task["baseCommit"]:
        candidate_paths = changed_paths(candidate)
    else:
        diff_names = run(["git", "diff", "--name-only", task["baseCommit"], candidate_head_before, "--"], candidate)
        fail(diff_names.returncode == 0, "HOST_TOOL_ERROR", "Committed candidate path set cannot be resolved")
        candidate_paths = sorted(set(x for x in diff_names.stdout.splitlines() if x))
    fail(candidate_paths == manifest.get("changedPaths"), "MALFORMED_EVIDENCE", "Candidate materialization path set differs from handoff", expected=manifest.get("changedPaths"), actual=candidate_paths)
    for source in manifest.get("sourceFiles", []):
        target = candidate / source["path"]
        if source.get("status") == "deleted":
            fail(not target.exists(), "MALFORMED_EVIDENCE", "Candidate retained a handoff deletion", path=source["path"])
        else:
            actual_mode = f"{stat.S_IMODE(target.stat().st_mode):04o}" if target.is_file() else None
            fail(target.is_file() and sha_file(target) == source.get("sha256") and actual_mode == source.get("mode"), "MALFORMED_EVIDENCE", "Candidate bytes or mode differ from handoff", path=source["path"], expectedMode=source.get("mode"), actualMode=actual_mode)
    if candidate_head_before == task["baseCommit"]:
        commit = run(["git", "-c", "user.name=Springmaster Autonomous Run", "-c", "user.email=autonomous-run@invalid", "commit", "-m", contract["patch"]["title"]], candidate)
        fail(commit.returncode == 0, "HOST_TOOL_ERROR", "Trusted candidate commit failed", stderr=commit.stderr[-2000:])
    candidate_head = run(["git", "rev-parse", "HEAD"], candidate).stdout.strip()
    fail(candidate_head != task["baseCommit"] and run(["git", "status", "--porcelain=v1", "--untracked-files=all"], candidate).stdout == "", "HOST_TOOL_ERROR", "Trusted candidate is not a clean committed handoff")
    promotion.update({"stage": "CANDIDATE_COMMITTED", "candidatePath": str(candidate), "candidateCommit": candidate_head}); save_state(directory, state)
    delivery = directory / "delivery"; delivery.mkdir(mode=0o755)
    artifacts = sorted(delivery.glob("*.zip"))
    created_patch: dict[str, Any] = {}
    if not artifacts:
        ws, completed = run_json([str(project / "bin/cpatch"), "workspace", "init", "--name", contract["patch"]["name"], "--scope", contract["patch"]["scope"], "--format", "json"], candidate)
        fail(completed.returncode == 0, "HOST_TOOL_ERROR", "cpatch workspace binding failed", evidence=ws)
        created_patch, completed = run_json([str(project / "bin/cpatch"), "create", "--base", task["baseCommit"], "--head", candidate_head, "--scope", contract["patch"]["scope"], "--patch-id", contract["patch"]["name"], "--title", contract["patch"]["title"], "--output", str(delivery), "--format", "json"], candidate)
        fail(completed.returncode == 0, "HOST_TOOL_ERROR", "cpatch create failed", evidence=created_patch)
        artifacts = sorted(delivery.glob("*.zip"))
    fail(len(artifacts) == 1 and artifacts[0].is_file(), "MALFORMED_EVIDENCE", "cpatch create output cardinality is not exactly one immutable ZIP", artifacts=[str(x) for x in artifacts], evidence=created_patch)
    artifact = str(artifacts[0])
    inspect, completed = run_json([str(project / "bin/cpatch"), "inspect", artifact, "--format", "json"], project); fail(completed.returncode == 0, "HOST_TOOL_ERROR", "cpatch inspect failed", evidence=inspect)
    plan, completed = run_json([str(project / "bin/cpatch"), "plan", artifact, "--format", "json"], project); fail(completed.returncode == 0, "HOST_TOOL_ERROR", "cpatch plan failed", evidence=plan)
    promotion.update({"stage": "PATCH_PLANNED", "artifactPath": artifact, "artifactSha256": sha_file(Path(artifact))}); save_state(directory, state)
    if isinstance(promotion.get("dryRunId"), str):
        dry = {"runId": promotion["dryRunId"]}
    else:
        dry, completed = run_json([str(project / "bin/process-ops.sh"), "--project-root", str(project), "--format", "json", "patch-dry-run", artifact], project)
        fail(completed.returncode == 0 and dry.get("runId"), "HOST_TOOL_ERROR", "Canonical patch dry-run did not start", evidence=dry)
        promotion.update({"stage": "DRY_RUN_STARTED", "dryRunId": dry["runId"]}); save_state(directory, state)
    dry_result, completed = run_json([str(project / "bin/process-ops.sh"), "--project-root", str(project), "--format", "json", "wait", str(dry["runId"]), "--strict-exit"], project)
    fail(completed.returncode == 0, "HOST_TOOL_ERROR", "Canonical patch dry-run failed", evidence=dry_result)
    integration_guard(project, task["baseCommit"])
    inspect_manifest = inspect.get("manifest") if isinstance(inspect.get("manifest"), dict) else {}
    patch_id = created_patch.get("patchId") or inspect.get("patchId") or inspect_manifest.get("patchId")
    artifact_id = created_patch.get("artifactId") or inspect.get("artifactId") or inspect_manifest.get("artifactId")
    fail(isinstance(patch_id, str) and patch_id and isinstance(dry.get("runId"), str), "MALFORMED_EVIDENCE", "Pre-Accept identities are incomplete", patchId=patch_id, artifactId=artifact_id, dryRunId=dry.get("runId"))
    state.update({"state": "PREACCEPT", "patchId": patch_id, "patchArtifactId": artifact_id, "dryRunId": dry["runId"], "lastFailureClass": None, "blockerClass": None, "nextAction": "HUMAN_ACCEPT_REQUIRED"}); save_state(directory, state)


def worker(project: Path, directory: Path) -> int:
    contract = load_json(directory / "request.json"); validate_contract(contract)
    fail(sha_file(directory / "request.json") == (directory / "request.sha256").read_text().split()[0], "MALFORMED_EVIDENCE", "Immutable request hash changed")
    state = load_json(directory / "state.json"); base = contract["taskTemplate"]["baseCommit"]
    if state["state"] in TERMINAL: return 0
    started = time.monotonic(); previous_fingerprint = state.get("lastFailureFingerprint"); previous_work = state.get("lastWorktreeFingerprint")
    try:
        integration_guard(project, base)
        if state.get("state") == "PROMOTING":
            task = task_for(contract, int(state["attemptOrdinal"])); promote(project, contract, state, directory, task); return 0
        resume_current = state.get("state") == "ATTEMPT_RUNNING"
        ordinal = int(state.get("attemptOrdinal", 0)) if resume_current else int(state.get("attemptOrdinal", 0)) + 1
        bundle = None; packet_path = None
        if state.get("state") == "REPAIR_PENDING":
            predecessor = ordinal - 1
            packet_path = directory / "repair-packets" / f"A{predecessor:03d}.json"
            packet = load_json(packet_path)
            bundle = packet.get("predecessorChangeBundle")
            fail(isinstance(bundle, dict) and sha_file(Path(bundle["bundlePath"])) == bundle.get("bundleSha256"), "MALFORMED_EVIDENCE", "Persisted successor bundle is missing or changed")
        while ordinal <= contract["budgets"]["maxAttempts"]:
            if time.monotonic() - started + state.get("activeSeconds", 0) > contract["budgets"]["activeTimeSeconds"]:
                raise RunError("REPAIR_BUDGET_EXHAUSTED", "Logical Run active-time budget exhausted")
            if resume_current:
                task, invocation, worktree = resume_attempt(project, contract, state, directory, ordinal)
                resume_current = False
            else:
                task, invocation, worktree = invoke_attempt(project, contract, state, directory, ordinal, bundle, packet_path)
            consumed = state.setdefault("attempts", [])
            if task["taskId"] not in consumed:
                consumed.append(task["taskId"]); save_state(directory, state)
            if invocation.get("status") != "PASS" and not stream_lag_only(invocation):
                raise RunError("HOST_TOOL_ERROR", "Raw Codex invocation failed outside the exact stream-lag exception", rawStatus=invocation.get("status"))
            transport = "TRANSPORT_DEGRADED_CONTINUE" if invocation.get("status") != "PASS" else "PASS"
            post, _ = run_json([str(project / "bin/agent-task.sh"), "--project-root", str(project), "--format", "json", "postcheck", task["taskId"]], project)
            classification = classify_postcheck(post)
            if classification != "PASS": raise RunError(classification, "Canonical postcheck blocked the Logical Run", findings=post.get("findings"))
            qualifications = diagnostic_qualification(project, task, worktree, directory / "attempts" / f"A{ordinal:03d}")
            failing = [x for x in qualifications if x["status"] != "PASS"]
            if not failing:
                final, completed = run_json([str(project / "bin/agent-task.sh"), "--project-root", str(project), "--format", "json", "qualify", task["taskId"]], project)
                fail(completed.returncode == 0 and final.get("status") == "QUALIFIED" and len(final.get("qualificationResults", [])) == len(task["qualificationCommands"]), "NONDETERMINISTIC_FAILURE", "Fresh canonical qualification disagreed with diagnostic PASS", evidence=final)
                state.update({"state": "PROMOTING", "lastFailureClass": transport if transport != "PASS" else None, "processRunId": None, "nextAction": "TRUSTED_HANDOFF"}); save_state(directory, state)
                promote(project, contract, state, directory, task); return 0
            # Canonical qualify records its normal fail-closed evidence; the diagnostic sweep remains additive.
            run_json([str(project / "bin/agent-task.sh"), "--project-root", str(project), "--format", "json", "qualify", task["taskId"]], project)
            paths = changed_paths(worktree); work_fp = fingerprint(worktree, paths)
            stable_failure = failure_fingerprint(post, qualifications)
            if stable_failure == previous_fingerprint and work_fp == previous_work:
                raise RunError("NO_PROGRESS", "Failure fingerprint repeated without byte progress", failureFingerprint=stable_failure)
            if ordinal >= contract["budgets"]["maxAttempts"]:
                raise RunError("REPAIR_BUDGET_EXHAUSTED", "Maximum physical attempts exhausted", maxAttempts=ordinal)
            successor = task_for(contract, ordinal + 1); fail(authorization_snapshot(successor) == authorization_snapshot(task), "ORACLE_CHANGE_REQUIRED", "Successor authorization or oracle fields changed")
            bundle_path = directory / "bundles" / f"A{ordinal:03d}-to-A{ordinal+1:03d}.zip"
            # Existing bundle apply validates successor task identity, so bind the manifest to it.
            bundle_task = dict(successor); bundle = create_bundle(project, bundle_task, worktree, paths, bundle_path)
            packet = repair_packet(contract, task, ordinal, successor["taskId"], paths, worktree, post, qualifications, bundle, previous_fingerprint)
            packet_path = directory / "repair-packets" / f"A{ordinal:03d}.json"; atomic(packet_path, packet); packet_path.chmod(0o444)
            previous_fingerprint, previous_work = packet["failureFingerprint"], packet["worktreeFingerprint"]
            state.update({"state": "REPAIR_PENDING", "lastFailureClass": "QUALIFICATION_FAILURE", "lastFailureFingerprint": previous_fingerprint, "lastWorktreeFingerprint": previous_work, "processRunId": None, "nextAction": "CREATE_SUCCESSOR"}); save_state(directory, state)
            ordinal += 1
        raise RunError("REPAIR_BUDGET_EXHAUSTED", "Maximum attempts exhausted")
    except RunError as exc:
        state.update({"state": "STOPPED", "blockerClass": exc.code, "lastFailureClass": exc.code, "processRunId": None, "nextAction": "STOP_AND_REPLAN", "blocker": {"message": exc.message, "details": exc.details}}); save_state(directory, state)
        return 20
    finally:
        state = load_json(directory / "state.json"); state["activeSeconds"] = int(state.get("activeSeconds", 0) + max(0, time.monotonic() - started)); save_state(directory, state)


def command_start(args: argparse.Namespace, project: Path) -> int:
    source = Path(args.contract).resolve(); contract = load_json(source); validate_contract(contract); directory = run_dir(contract["logicalRunId"])
    request_bytes = canonical(contract); request_sha = sha_bytes(request_bytes)
    if directory.exists():
        fail((directory / "request.sha256").is_file() and (directory / "request.sha256").read_text().split()[0] == request_sha, "MALFORMED_EVIDENCE", "Logical Run ID is bound to a different immutable request")
    else:
        directory.mkdir(parents=True, mode=0o700); atomic(directory / "request.json", contract); (directory / "request.sha256").write_text(f"{request_sha}  request.json\n", encoding="ascii"); (directory / "request.sha256").chmod(0o444); (directory / "request.json").chmod(0o444); save_state(directory, initial_state(contract, request_sha))
    state = load_json(directory / "state.json")
    argv = [str(project / "bin/process-ops.sh"), "--project-root", str(project), "--format", "json", "run-start", "--name", "codex-autonomous-run", "--cwd", str(project), "--singleton-key", f"logical-{contract['logicalRunId'].lower()}"]
    if state["state"] in TERMINAL:
        print(json.dumps(state_summary(state), sort_keys=True)); return 0
    argv.extend(["--", str(project / "bin/codex-autonomous-run.sh"), "--project-root", str(project), "worker", "--run-dir", str(directory)])
    started, completed = run_json(argv, project); fail(completed.returncode == 0 and started.get("runId"), "HOST_TOOL_ERROR", "Logical Run worker did not start", evidence=started)
    state = load_json(directory / "state.json")
    if state["state"] not in TERMINAL:
        state["processRunId"] = started["runId"]; save_state(directory, state)
    print(json.dumps(state_summary(state), sort_keys=True)); return 0


def command_observe(args: argparse.Namespace, project: Path, result: bool = False) -> int:
    directory = run_dir(args.logical_run_id); state = load_json(directory / "state.json")
    if result and state["state"] not in TERMINAL: raise RunError("LOGICAL_RUN_NOT_TERMINAL", "Logical Run result is not terminal")
    print(json.dumps(state_summary(state), sort_keys=True)); return 0


def command_resume(args: argparse.Namespace, project: Path) -> int:
    directory = run_dir(args.logical_run_id); state = load_json(directory / "state.json")
    if state["state"] in TERMINAL:
        print(json.dumps(state_summary(state), sort_keys=True)); return 0
    argv = [str(project / "bin/process-ops.sh"), "--project-root", str(project), "--format", "json", "run-start", "--name", "codex-autonomous-run", "--cwd", str(project), "--singleton-key", f"logical-{args.logical_run_id.lower()}", "--restart-terminal", "--", str(project / "bin/codex-autonomous-run.sh"), "--project-root", str(project), "worker", "--run-dir", str(directory)]
    started, completed = run_json(argv, project); fail(completed.returncode == 0 and started.get("runId"), "HOST_TOOL_ERROR", "Logical Run resume did not acquire durable ownership", evidence=started)
    state = load_json(directory / "state.json")
    if state["state"] not in TERMINAL:
        state["processRunId"] = started["runId"]; save_state(directory, state)
    print(json.dumps(state_summary(state), sort_keys=True)); return 0


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__); p.add_argument("--project-root")
    sub = p.add_subparsers(dest="command", required=True)
    start = sub.add_parser("start"); start.add_argument("--contract", required=True)
    for name in ("status", "result", "resume"):
        item = sub.add_parser(name); item.add_argument("logical_run_id")
    worker_p = sub.add_parser("worker", help=argparse.SUPPRESS); worker_p.add_argument("--run-dir", required=True)
    return p


def main() -> int:
    args = parser().parse_args()
    try:
        project = root(args.project_root)
        if args.command == "start": return command_start(args, project)
        if args.command == "status": return command_observe(args, project)
        if args.command == "result": return command_observe(args, project, True)
        if args.command == "resume": return command_resume(args, project)
        return worker(project, Path(args.run_dir).resolve())
    except RunError as exc:
        print(json.dumps({"state": "TOOL_ERROR", "blockerClass": exc.code, "message": exc.message, **exc.details}, sort_keys=True))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
