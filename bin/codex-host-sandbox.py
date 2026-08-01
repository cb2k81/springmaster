#!/usr/bin/env python3
"""Host-local Codex isolation, probe and invocation runner for Springmaster."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import shutil
import stat
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

HOST_SCHEMA = "springmaster.codex-host-qualification-contract.v1"
REPORT_SCHEMA = "springmaster.codex-host-qualification-report.v1"
EVIDENCE_SCHEMA = "springmaster.codex-host-qualification-evidence.v1"
SANDBOX_PATH = "/usr/local/bin:/usr/bin:/bin"


class HostError(RuntimeError):
    def __init__(self, code: str, message: str, **details: object) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def atomic_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise HostError("JSON_MISSING", "Required JSON file is missing", path=str(path)) from exc
    except json.JSONDecodeError as exc:
        raise HostError("JSON_INVALID", "JSON file is invalid", path=str(path), line=exc.lineno, column=exc.colno) from exc
    if not isinstance(value, dict):
        raise HostError("JSON_ROOT_INVALID", "JSON root must be an object", path=str(path))
    return value


def run(argv: list[str], *, cwd: Path | None = None, env: dict[str, str] | None = None, input_text: str | None = None, timeout: int = 60) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(argv, cwd=cwd, env=env, input=input_text, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout, check=False)
    except FileNotFoundError as exc:
        raise HostError("EXECUTABLE_MISSING", "Required executable is missing", executable=argv[0]) from exc
    except subprocess.TimeoutExpired as exc:
        raise HostError("COMMAND_TIMEOUT", "Command timed out", argv=argv, timeoutSeconds=timeout) from exc


def require(condition: bool, code: str, message: str, **details: object) -> None:
    if not condition:
        raise HostError(code, message, **details)


def discover_root(explicit: str | None) -> Path:
    start = Path(explicit).expanduser() if explicit else Path.cwd()
    completed = run(["git", "rev-parse", "--show-toplevel"], cwd=start)
    require(completed.returncode == 0 and completed.stdout.strip() != "", "PROJECT_ROOT_NOT_FOUND", "No Git project root could be resolved", start=str(start))
    return Path(completed.stdout.strip()).resolve()


def git(root: Path, *args: str) -> str:
    completed = run(["git", *args], cwd=root)
    require(completed.returncode == 0, "GIT_COMMAND_FAILED", "Git command failed", argv=["git", *args], stderr=completed.stderr[-2000:])
    return completed.stdout.strip()


def executable(name: str, override: str | None) -> Path:
    raw = override or shutil.which(name)
    require(bool(raw), "EXECUTABLE_MISSING", "Required executable is missing", executable=name)
    path = Path(str(raw)).expanduser()
    if not path.is_absolute():
        resolved = shutil.which(str(path))
        require(bool(resolved), "EXECUTABLE_MISSING", "Required executable is missing", executable=str(path))
        path = Path(str(resolved))
    require(path.is_file() and not path.is_symlink(), "EXECUTABLE_INVALID", "Executable must be a regular non-symlink file", executable=name, path=str(path))
    return path.resolve()


def external_root(name: str) -> Path:
    raw = os.environ.get(name)
    require(bool(raw), "EXTERNAL_ROOT_UNSET", "Required external root is not set", variable=name)
    path = Path(str(raw)).expanduser()
    require(path.is_absolute(), "EXTERNAL_ROOT_NOT_ABSOLUTE", "External root must be absolute", variable=name, value=str(path))
    require(path.is_dir() and not path.is_symlink(), "EXTERNAL_ROOT_INVALID", "External root must be an existing non-symlink directory", variable=name, value=str(path))
    return path.resolve()


def integration_root(root: Path) -> Path:
    branch = "main"
    env_path = root / ".cocondo/tooling/project.env"
    if env_path.is_file():
        for raw in env_path.read_text(encoding="utf-8").splitlines():
            if raw.startswith("CPATCH_INTEGRATION_BRANCH="):
                branch = raw.split("=", 1)[1].strip()
    rows = git(root, "worktree", "list", "--porcelain").splitlines()
    candidates: list[Path] = []
    current: dict[str, str] = {}
    for line in rows + [""]:
        if line == "":
            if current.get("branch") == f"refs/heads/{branch}" and current.get("worktree"):
                candidates.append(Path(current["worktree"]).resolve())
            current = {}
            continue
        key, _, value = line.partition(" ")
        current[key] = value
    require(len(candidates) == 1, "INTEGRATION_WORKTREE_UNRESOLVED", "Exactly one integration worktree is required", branch=branch, candidates=[str(x) for x in candidates])
    return candidates[0]


def context(root: Path) -> dict[str, Path]:
    return {
        "project": root,
        "integration": integration_root(root),
        "gitCommon": Path(git(root, "rev-parse", "--path-format=absolute", "--git-common-dir")).resolve(),
        "worktreeRoot": external_root("COCONDO_WORKTREE_ROOT"),
        "runRoot": external_root("COCONDO_AGENT_RUN_ROOT"),
        "artifactRoot": external_root("COCONDO_ARTIFACT_ROOT"),
        "operatorHome": Path.home().resolve(),
        "hostTmp": Path(tempfile.gettempdir()).resolve(),
    }


def contains(parent: Path, child: Path) -> bool:
    try:
        child.relative_to(parent)
        return True
    except ValueError:
        return False


def host_id() -> str:
    machine_id_path = Path("/etc/machine-id")
    machine = machine_id_path.read_text(encoding="utf-8").strip() if machine_id_path.is_file() else platform.node()
    value = f"{machine}\n{platform.machine()}\n{platform.release()}\n".encode("utf-8")
    return sha256_bytes(value)[:24]


def load_contract(root: Path) -> tuple[Path, dict[str, Any]]:
    path = root / "contracts/governance/agent/codex-host-qualification-contract.json"
    value = load_json(path)
    require(value.get("schemaVersion") == HOST_SCHEMA and value.get("status") == "active", "HOST_CONTRACT_INVALID", "Host qualification contract is invalid")
    return path, value


def resolve_codex_home() -> Path:
    path = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))).expanduser()
    require(path.is_absolute() and path.is_dir() and not path.is_symlink(), "CODEX_HOME_INVALID", "CODEX_HOME must be an existing non-symlink directory", path=str(path))
    return path.resolve()


def sanitized_env(private_home: Path, extra: dict[str, str] | None = None) -> dict[str, str]:
    value = {
        "HOME": str(private_home),
        "CODEX_HOME": str(private_home),
        "LANG": os.environ.get("LANG", "C.UTF-8"),
        "LC_ALL": "C.UTF-8",
        "PATH": SANDBOX_PATH,
        "TMPDIR": "/tmp",
        "TZ": os.environ.get("TZ", "UTC"),
        "USER": "codex",
        "LOGNAME": "codex",
    }
    if extra:
        value.update(extra)
    return value


def copy_codex_auth(source_home: Path, private_home: Path) -> dict[str, Any]:
    require(private_home.is_dir() and not private_home.is_symlink(), "PRIVATE_CODEX_HOME_INVALID", "Private Codex home must be an existing non-symlink directory", path=str(private_home))
    require(not any(private_home.iterdir()), "PRIVATE_CODEX_HOME_NOT_EMPTY", "Private Codex home must be empty before auth copy", path=str(private_home))
    private_home.chmod(0o700)
    source = source_home / "auth.json"
    require(source.is_file() and not source.is_symlink(), "CODEX_AUTH_MISSING", "Codex auth.json is missing or unsafe", path=str(source))
    size = source.stat().st_size
    require(0 < size <= 4 * 1024 * 1024, "CODEX_AUTH_SIZE_INVALID", "Codex auth.json size is outside the allowed range", size=size)
    target = private_home / "auth.json"
    shutil.copyfile(source, target)
    target.chmod(0o600)
    return {"sourceSize": size, "copiedSha256": sha256_file(target), "secretValueRecorded": False}


def bwrap_prefix(*, bwrap: Path, ctx: dict[str, Path], task: Path, private_home: Path, writable_task: bool, extra_env: dict[str, str] | None = None) -> list[str]:
    require(task.is_dir() and not task.is_symlink(), "TASK_WORKTREE_INVALID", "Task worktree must be an existing non-symlink directory", path=str(task))
    task = task.resolve()
    require(contains(ctx["worktreeRoot"], task), "TASK_WORKTREE_OUTSIDE_ROOT", "Task worktree is outside the configured worktree root", path=str(task), root=str(ctx["worktreeRoot"]))
    args = [
        str(bwrap), "--die-with-parent", "--new-session", "--unshare-pid", "--unshare-ipc", "--unshare-uts", "--unshare-cgroup-try",
        "--ro-bind", "/", "/", "--dev", "/dev", "--proc", "/proc", "--tmpfs", "/tmp", "--tmpfs", "/var/tmp", "--tmpfs", "/run",
        "--tmpfs", str(ctx["operatorHome"]),
        "--bind", str(private_home), "/run/codex-home",
    ]
    if writable_task:
        args += ["--bind", str(task), str(task)]
    else:
        args += ["--ro-bind", str(task), str(task)]
    args += ["--clearenv"]
    for key, value in sorted(sanitized_env(Path("/run/codex-home"), extra_env).items()):
        args += ["--setenv", key, value]
    args += ["--chdir", str(task), "--"]
    return args


def inspect(root: Path, bwrap: Path, codex: Path) -> dict[str, Any]:
    contract_path, contract = load_contract(root)
    ctx = context(root)
    findings: list[dict[str, Any]] = []
    if platform.system() != contract["supportedHost"]["operatingSystem"]:
        findings.append({"code": "HOST_OS_UNSUPPORTED", "actual": platform.system()})
    if platform.machine() not in contract["supportedHost"]["architectures"]:
        findings.append({"code": "HOST_ARCH_UNSUPPORTED", "actual": platform.machine()})
    for role in ("integration", "gitCommon", "worktreeRoot", "runRoot", "artifactRoot"):
        path = ctx[role]
        if contains(ctx["operatorHome"], path) or contains(ctx["hostTmp"], path):
            findings.append({"code": "ROOT_BELOW_FORBIDDEN_HOST_AREA", "role": role, "path": str(path)})
    if contains(ctx["operatorHome"], codex) or contains(ctx["hostTmp"], codex):
        findings.append({"code": "CODEX_INSTALLATION_BELOW_FORBIDDEN_HOST_AREA", "path": str(codex)})
    checks: dict[str, Any] = {}
    for name, argv in {
        "bubblewrapVersion": [str(bwrap), "--version"],
        "bubblewrapSmoke": [str(bwrap), "--ro-bind", "/", "/", "--proc", "/proc", "--dev", "/dev", "--unshare-pid", "--die-with-parent", "/usr/bin/true"],
        "codexVersion": [str(codex), "--version"],
        "codexExecHelp": [str(codex), "exec", "--help"],
        "codexInnerSandboxSmoke": [str(codex), "sandbox", "--", "/usr/bin/true"],
        "gitVersion": ["git", "--version"],
        "pythonVersion": [sys.executable, "--version"],
    }.items():
        result = run(argv, timeout=30)
        checks[name] = {"exitCode": result.returncode, "stdout": result.stdout[-1000:], "stderr": result.stderr[-1000:]}
        if result.returncode != 0:
            findings.append({"code": "HOST_INSPECTION_COMMAND_FAILED", "check": name, "exitCode": result.returncode})
    return {
        "schemaVersion": REPORT_SCHEMA,
        "operation": "inspect",
        "status": "PASS" if not findings else "FINDINGS",
        "generatedAt": utc_now(),
        "hostId": host_id(),
        "baselineCommit": git(root, "rev-parse", "HEAD"),
        "contractSha256": sha256_file(contract_path),
        "paths": {key: str(value) for key, value in ctx.items()},
        "executables": {"bwrap": str(bwrap), "codex": str(codex)},
        "checks": checks,
        "findings": findings,
    }


def probe_command(prefix: list[str], command: str, *, timeout: int = 20) -> subprocess.CompletedProcess[str]:
    return run(prefix + ["/bin/sh", "-eu", "-c", command], timeout=timeout)


def probes(root: Path, bwrap: Path, codex: Path, task: Path) -> dict[str, Any]:
    _, contract = load_contract(root)
    ctx = context(root)
    source_home = resolve_codex_home()
    parent = ctx["runRoot"] / "codex-host-probes" / host_id() / git(root, "rev-parse", "HEAD")
    parent.mkdir(parents=True, exist_ok=True)
    private_home = Path(tempfile.mkdtemp(prefix="private-codex-home-", dir=parent))
    try:
        auth = copy_codex_auth(source_home, private_home)
        prefix_rw = bwrap_prefix(bwrap=bwrap, ctx=ctx, task=task, private_home=private_home, writable_task=True)
        prefix_ro = bwrap_prefix(bwrap=bwrap, ctx=ctx, task=task, private_home=private_home, writable_task=False)
        results: list[dict[str, Any]] = []
        def record(probe_id: str, expected: str, completed: subprocess.CompletedProcess[str], *, host_path: Path | None = None, should_exist: bool | None = None) -> None:
            actual = "PASS" if completed.returncode == 0 else "DENIED"
            if host_path is not None and should_exist is not None:
                actual = "PASS" if host_path.exists() == should_exist else "DENIED"
            results.append({"id": probe_id, "expectedOutcome": expected, "outcome": actual, "exitCode": completed.returncode, "stdout": completed.stdout[-1000:], "stderr": completed.stderr[-1000:]})
        allowed = task / ".codex-host-allowed-probe"
        completed = probe_command(prefix_rw, f"printf PASS > {json.dumps(str(allowed))}")
        record("allowed-task-worktree-write", "PASS", completed, host_path=allowed, should_exist=True)
        allowed.unlink(missing_ok=True)
        targets = {
            "write-integration-worktree": ctx["integration"] / ".codex-denied",
            "write-other-worktree": ctx["worktreeRoot"] / ".codex-denied",
            "write-git-common-directory": ctx["gitCommon"] / ".codex-denied",
            "write-patches-work": ctx["integration"] / "patches/work/.codex-denied",
            "write-operator-home": ctx["operatorHome"] / ".codex-denied",
            "write-operator-downloads": ctx["operatorHome"] / "Downloads/.codex-denied",
            "write-external-run-root": ctx["runRoot"] / ".codex-denied",
            "write-external-artifact-root": ctx["artifactRoot"] / ".codex-denied",
            "write-host-temporary-directory": ctx["hostTmp"] / ".codex-denied",
        }
        for probe_id, target in targets.items():
            target.parent.mkdir(parents=True, exist_ok=True) if probe_id == "write-patches-work" and target.parent == ctx["integration"] / "patches/work" and target.parent.exists() else None
            target.unlink(missing_ok=True)
            completed = probe_command(prefix_rw, f"printf DENIED > {json.dumps(str(target))}")
            outcome = "DENIED" if not target.exists() else "PASS"
            target.unlink(missing_ok=True)
            results.append({"id": probe_id, "expectedOutcome": "DENIED", "outcome": outcome, "exitCode": completed.returncode, "stdout": completed.stdout[-1000:], "stderr": completed.stderr[-1000:]})
        completed = probe_command(prefix_rw, "printf X > ../.codex-traversal-denied")
        traversal = task.parent / ".codex-traversal-denied"
        results.append({"id": "path-traversal-escape", "expectedOutcome": "DENIED", "outcome": "DENIED" if not traversal.exists() else "PASS", "exitCode": completed.returncode})
        traversal.unlink(missing_ok=True)
        symlink = task / ".codex-escape-link"
        if symlink.exists() or symlink.is_symlink(): symlink.unlink()
        symlink.symlink_to(ctx["integration"])
        completed = probe_command(prefix_rw, f"printf X > {json.dumps(str(symlink / '.codex-symlink-denied'))}")
        symlink_target = ctx["integration"] / ".codex-symlink-denied"
        results.append({"id": "symlink-escape", "expectedOutcome": "DENIED", "outcome": "DENIED" if not symlink_target.exists() else "PASS", "exitCode": completed.returncode})
        symlink_target.unlink(missing_ok=True); symlink.unlink(missing_ok=True)
        completed = probe_command(prefix_rw, "git add -A && git -c user.name=codex -c user.email=codex@example.invalid commit --allow-empty -m denied")
        results.append({"id": "direct-git-commit", "expectedOutcome": "DENIED", "outcome": "DENIED" if completed.returncode != 0 else "PASS", "exitCode": completed.returncode})
        completed = probe_command(prefix_rw, "test ! -x ./bin/process-ops.sh || ./bin/process-ops.sh patch-accept forbidden")
        results.append({"id": "direct-patch-accept", "expectedOutcome": "DENIED", "outcome": "DENIED" if completed.returncode != 0 else "PASS", "exitCode": completed.returncode})
        background = ctx["integration"] / ".codex-background-denied"
        completed = probe_command(prefix_rw, f"(sleep 2; printf X > {json.dumps(str(background))}) & exit 0", timeout=10)
        subprocess.run(["sleep", "3"], check=False)
        results.append({"id": "background-writer", "expectedOutcome": "DENIED", "outcome": "DENIED" if not background.exists() else "PASS", "exitCode": completed.returncode})
        background.unlink(missing_ok=True)
        inner_cases = [
            ("inner-sandbox-smoke", "PASS", [str(codex), "sandbox", "--", "/usr/bin/true"]),
            ("inner-worktree-write", "PASS", [str(codex), "sandbox", "--", "/bin/sh", "-eu", "-c", f"printf PASS > {json.dumps(str(task / '.codex-inner-write'))}"]),
            ("inner-auth-read", "DENIED", [str(codex), "sandbox", "--", "/bin/cat", "/run/codex-home/auth.json"]),
            ("inner-network-egress", "DENIED", [str(codex), "sandbox", "--", "/bin/sh", "-eu", "-c", "exec 3<>/dev/tcp/1.1.1.1/53"]),
            ("inner-git-common-write", "DENIED", [str(codex), "sandbox", "--", "/bin/sh", "-eu", "-c", f"printf X > {json.dumps(str(ctx['gitCommon'] / '.codex-inner-denied'))}"]),
        ]
        for probe_id, expected, argv in inner_cases:
            completed = run(prefix_rw + argv, timeout=30)
            outcome = "PASS" if completed.returncode == 0 else "DENIED"
            results.append({"id": probe_id, "expectedOutcome": expected, "outcome": outcome, "exitCode": completed.returncode, "stdout": completed.stdout[-1000:], "stderr": completed.stderr[-1000:]})
        (task / ".codex-inner-write").unlink(missing_ok=True)
        (ctx["gitCommon"] / ".codex-inner-denied").unlink(missing_ok=True)
        expected = {item["id"]: item["expectedOutcome"] for item in contract["requiredMechanicalProbes"]}
        by_id = {item["id"]: item for item in results}
        findings = []
        for probe_id, outcome in expected.items():
            if probe_id not in by_id:
                findings.append({"code": "PROBE_MISSING", "probeId": probe_id})
            elif by_id[probe_id]["outcome"] != outcome:
                findings.append({"code": "PROBE_FAILED", "probeId": probe_id, "expected": outcome, "actual": by_id[probe_id]["outcome"]})
        return {
            "schemaVersion": REPORT_SCHEMA,
            "operation": "probe",
            "status": "PASS" if not findings else "FINDINGS",
            "generatedAt": utc_now(),
            "hostId": host_id(),
            "baselineCommit": git(root, "rev-parse", "HEAD"),
            "authHandling": auth,
            "sandboxArgvSha256": sha256_bytes(json.dumps(prefix_rw, separators=(",", ":")).encode("utf-8")),
            "probes": results,
            "findings": findings,
        }
    finally:
        shutil.rmtree(private_home, ignore_errors=True)


def status_json(root: Path, task_id: str) -> dict[str, Any]:
    completed = run([str(root / "bin/agent-task.sh"), "--project-root", str(root), "--format", "json", "status", task_id], cwd=root)
    require(completed.returncode == 0, "AGENT_TASK_STATUS_FAILED", "Cannot resolve prepared task", taskId=task_id, stderr=completed.stderr[-2000:], stdout=completed.stdout[-2000:])
    try:
        value = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise HostError("AGENT_TASK_STATUS_INVALID", "Agent task status is not JSON", taskId=task_id) from exc
    require(isinstance(value, dict) and value.get("worktreePath"), "AGENT_TASK_NOT_PREPARED", "Agent task is not prepared", taskId=task_id)
    return value


def invoke(root: Path, bwrap: Path, codex: Path, task_id: str, prompt_file: Path, model: str, change_bundle: Path | None = None) -> dict[str, Any]:
    ctx = context(root)
    state = status_json(root, task_id)
    task = Path(state["worktreePath"]).resolve()
    run_dir = Path(state["runDirectory"]).resolve()
    task_contract = load_json(run_dir / "task-contract.json")
    mode = task_contract.get("mode")
    require(mode in {"analysis", "implementation", "qualification"}, "TASK_MODE_INVALID", "Unsupported task mode", mode=mode)
    require(prompt_file.is_file() and not prompt_file.is_symlink(), "PROMPT_INVALID", "Prompt file is missing or unsafe", path=str(prompt_file))
    extra_env = {
        "SPRINGMASTER_AGENT_TASK_ID": task_id,
        "SPRINGMASTER_AGENT_TASK_CONTRACT": str(run_dir / "task-contract.json"),
    }
    reads = ["task-worktree"]
    if change_bundle is not None:
        require(mode == "implementation", "CHANGE_BUNDLE_MODE_INVALID", "Change bundles require an implementation task", mode=mode)
        resolved_bundle = change_bundle.expanduser().resolve()
        require(resolved_bundle.is_file() and not resolved_bundle.is_symlink(), "CHANGE_BUNDLE_INVALID", "Change bundle is missing or unsafe", path=str(resolved_bundle))
        require(contains(ctx["artifactRoot"], resolved_bundle), "CHANGE_BUNDLE_OUTSIDE_ARTIFACT_ROOT", "Change bundle must be below the external artifact root", path=str(resolved_bundle), root=str(ctx["artifactRoot"]))
        extra_env["SPRINGMASTER_CODEX_CHANGE_BUNDLE"] = str(resolved_bundle)
        reads.append("external-artifact-root")
    source_home = resolve_codex_home()
    evidence_dir = ctx["artifactRoot"] / "codex-host-qualification" / host_id() / git(root, "rev-parse", "HEAD") / task_id.lower()
    require(not evidence_dir.exists(), "EVIDENCE_DIRECTORY_EXISTS", "Invocation evidence directory already exists", path=str(evidence_dir))
    evidence_dir.mkdir(parents=True, mode=0o700)
    private_home = Path(tempfile.mkdtemp(prefix="private-codex-home-", dir=evidence_dir))
    try:
        auth = copy_codex_auth(source_home, private_home)
        cli_sandbox = "workspace-write" if mode == "implementation" else "read-only"
        record_sandbox = "linux-bwrap-workspace-write" if mode == "implementation" else "linux-bwrap-read-only"
        codex_argv = [str(codex), "exec", "--ephemeral", "--ignore-user-config", "--ignore-rules", "--json", "--model", model, "--sandbox", cli_sandbox, "--ask-for-approval", "never", "--cd", str(task), "-"]
        outer = bwrap_prefix(bwrap=bwrap, ctx=ctx, task=task, private_home=private_home, writable_task=mode == "implementation", extra_env=extra_env)
        prompt = prompt_file.read_text(encoding="utf-8")
        started_at = utc_now()
        completed = run(outer + codex_argv, input_text=prompt, timeout=1800)
        finished_at = utc_now()
        (evidence_dir / "codex.stdout.jsonl").write_text(completed.stdout, encoding="utf-8")
        (evidence_dir / "codex.stderr.log").write_text(completed.stderr, encoding="utf-8")
        writes = ["task-worktree"] if mode == "implementation" else []
        mutation = "task-worktree-only" if mode == "implementation" else "none"
        effect = {
            "schemaVersion": "springmaster.operator-command-effect.v1",
            "commandId": "codex-host-sandbox",
            "taskId": task_id,
            "purpose": "Host-confined Springmaster Codex calibration",
            "argv": ["codex" if item == str(codex) else item for item in codex_argv],
            "workingDirectory": str(task),
            "reads": reads,
            "writes": writes,
            "network": "codex-control-plane-only",
            "repositoryMutation": mutation,
            "destructiveActions": [],
            "directoryCreationPolicy": "declared-task-paths-only",
            "overwritePolicy": "declared-task-paths-only",
            "environmentInputs": sorted(sanitized_env(Path("/run/codex-home"), extra_env).keys()),
        }
        invocation = {
            "schemaVersion": "springmaster.codex-invocation-record.v1",
            "taskId": task_id,
            "commandId": "codex-host-sandbox",
            "recordedAt": utc_now(),
            "agent": {"name": "codex", "cliVersion": run([str(codex), "--version"]).stdout.strip(), "model": model},
            "execution": {
                "argv": effect["argv"],
                "workingDirectory": str(task),
                "sandboxProfile": record_sandbox,
                "approvalPolicy": "never",
                "platformSandbox": {
                    "implementation": "linux-bwrap",
                    "workspaceRoot": str(task),
                    "additionalWritableRoots": [],
                    "operatorHomeWritable": False,
                    "operatorDownloadsWritable": False,
                    "integrationWorktreeWritable": False,
                    "gitCommonDirectoryWritable": False,
                    "externalRunRootWritable": False,
                    "externalArtifactRootWritable": False,
                    "temporaryDirectoriesWritable": False,
                },
                "environmentKeys": sorted(sanitized_env(Path("/run/codex-home"), extra_env).keys()),
                "startedAt": started_at,
                "finishedAt": finished_at,
                "status": "COMPLETED" if completed.returncode == 0 else "FAILED",
                "exitCode": completed.returncode,
            },
        }
        effect_path = evidence_dir / "operator-command-effect.json"
        invocation_path = evidence_dir / "codex-invocation.json"
        atomic_json(effect_path, effect)
        atomic_json(invocation_path, invocation)
        record = run([str(root / "bin/agent-task.sh"), "--project-root", str(root), "record-invocation", task_id, "--effect", str(effect_path), "--record", str(invocation_path)], cwd=root)
        require(record.returncode == 0, "INVOCATION_RECORD_REJECTED", "Agent task rejected the invocation evidence", stdout=record.stdout[-2000:], stderr=record.stderr[-2000:])
        result = {
            "schemaVersion": REPORT_SCHEMA,
            "operation": "invoke",
            "status": "PASS" if completed.returncode == 0 else "FAILED",
            "generatedAt": utc_now(),
            "hostId": host_id(),
            "baselineCommit": git(root, "rev-parse", "HEAD"),
            "taskId": task_id,
            "taskMode": mode,
            "worktreePath": str(task),
            "model": model,
            "codexCliVersion": invocation["agent"]["cliVersion"],
            "exitCode": completed.returncode,
            "sandboxArgvSha256": sha256_bytes(json.dumps(outer, separators=(",", ":")).encode("utf-8")),
            "authHandling": auth,
            "effect": {"path": str(effect_path), "sha256": sha256_file(effect_path)},
            "invocation": {"path": str(invocation_path), "sha256": sha256_file(invocation_path)},
            "stdout": {"path": str(evidence_dir / "codex.stdout.jsonl"), "sha256": sha256_file(evidence_dir / "codex.stdout.jsonl")},
            "stderr": {"path": str(evidence_dir / "codex.stderr.log"), "sha256": sha256_file(evidence_dir / "codex.stderr.log")},
        }
        atomic_json(evidence_dir / "host-invocation.json", result)
        return result
    finally:
        shutil.rmtree(private_home, ignore_errors=True)


def qualify(root: Path, inspect_path: Path, probe_path: Path, analysis_invocation_path: Path) -> dict[str, Any]:
    contract_path, contract = load_contract(root)
    inspect_value = load_json(inspect_path)
    probe_value = load_json(probe_path)
    invocation = load_json(analysis_invocation_path)
    findings = []
    if inspect_value.get("status") != "PASS": findings.append({"code": "HOST_INSPECT_NOT_PASS"})
    if probe_value.get("status") != "PASS": findings.append({"code": "MECHANICAL_PROBES_NOT_PASS"})
    if invocation.get("status") != "PASS" or invocation.get("taskMode") != "analysis": findings.append({"code": "REAL_CODEX_ANALYSIS_NOT_PASS"})
    baseline = git(root, "rev-parse", "HEAD")
    for name, value in (("inspect", inspect_value), ("probe", probe_value), ("analysis", invocation)):
        if value.get("baselineCommit") != baseline: findings.append({"code": "BASELINE_BINDING_MISMATCH", "evidence": name})
        if value.get("hostId") != host_id(): findings.append({"code": "HOST_BINDING_MISMATCH", "evidence": name})
    return {
        "schemaVersion": EVIDENCE_SCHEMA,
        "status": "PASS" if not findings else "FINDINGS",
        "generatedAt": utc_now(),
        "hostId": host_id(),
        "baselineCommit": baseline,
        "contractSha256": sha256_file(contract_path),
        "portable": False,
        "realCodex": True,
        "inspect": {"path": str(inspect_path), "sha256": sha256_file(inspect_path)},
        "mechanicalProbes": {"path": str(probe_path), "sha256": sha256_file(probe_path)},
        "analysisInvocation": {"path": str(analysis_invocation_path), "sha256": sha256_file(analysis_invocation_path)},
        "probeCount": len(contract["requiredMechanicalProbes"]),
        "findings": findings,
        "writableCodexAuthorized": False,
        "pilotWriteReady": False,
    }


def render(report: dict[str, Any], fmt: str) -> str:
    if fmt == "json": return json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    lines = [f"CODEX_HOST_OPERATION={report.get('operation', 'qualify')}", f"CODEX_HOST_STATUS={report.get('status')}"]
    for key in ("hostId", "baselineCommit", "taskId", "taskMode", "exitCode", "probeCount"):
        if key in report: lines.append(f"{key.upper()}={report[key]}")
    lines += ["WRITABLE_CODEX_AUTHORIZED=false", "PILOT_WRITE_READY=false"]
    return "\n".join(lines) + "\n"


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--project-root")
    p.add_argument("--bwrap")
    p.add_argument("--codex")
    p.add_argument("--format", choices=("text", "json"), default="text")
    sub = p.add_subparsers(dest="command", required=True)
    i = sub.add_parser("inspect"); i.add_argument("--out", type=Path)
    q = sub.add_parser("probe"); q.add_argument("--task-worktree", required=True, type=Path); q.add_argument("--out", type=Path)
    v = sub.add_parser("invoke"); v.add_argument("--task-id", required=True); v.add_argument("--prompt", required=True, type=Path); v.add_argument("--model", required=True); v.add_argument("--change-bundle", type=Path); v.add_argument("--out", type=Path)
    z = sub.add_parser("qualify"); z.add_argument("--inspect", required=True, type=Path); z.add_argument("--probe", required=True, type=Path); z.add_argument("--analysis-invocation", required=True, type=Path); z.add_argument("--out", required=True, type=Path); z.add_argument("--check", action="store_true")
    return p


def main() -> int:
    args = parser().parse_args()
    try:
        root = discover_root(args.project_root)
        bwrap = executable("bwrap", args.bwrap)
        codex = executable("codex", args.codex)
        if args.command == "inspect": report = inspect(root, bwrap, codex)
        elif args.command == "probe": report = probes(root, bwrap, codex, args.task_worktree.resolve())
        elif args.command == "invoke": report = invoke(root, bwrap, codex, args.task_id, args.prompt.resolve(), args.model, args.change_bundle)
        else: report = qualify(root, args.inspect.resolve(), args.probe.resolve(), args.analysis_invocation.resolve())
        if getattr(args, "out", None): atomic_json(args.out, report)
        sys.stdout.write(render(report, args.format))
        if args.command == "qualify" and args.check and report["status"] != "PASS": return 1
        return 0 if report.get("status") == "PASS" else 1
    except HostError as exc:
        report = {"schemaVersion": REPORT_SCHEMA, "status": "TOOL_ERROR", "errorCode": exc.code, "message": exc.message, "details": exc.details, "writableCodexAuthorized": False, "pilotWriteReady": False}
        if getattr(args, "out", None): atomic_json(args.out, report)
        sys.stdout.write(render(report, args.format))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
