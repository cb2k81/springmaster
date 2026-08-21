#!/usr/bin/env python3
"""Host-local Codex isolation, probe and invocation runner for Springmaster."""
from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import platform
import shutil
import signal
import stat
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

HOST_SCHEMA = "springmaster.codex-host-qualification-contract.v1"
REPORT_SCHEMA = "springmaster.codex-host-qualification-report.v1"
EVIDENCE_SCHEMA = "springmaster.codex-host-qualification-evidence.v1"
SANDBOX_PATH = "/usr/local/bin:/usr/bin:/bin"
CONTROL_PLANE_HOST = "chatgpt.com"
CONTROL_PLANE_URL = "https://chatgpt.com/"


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


def resolve_codex_sandbox_command_form(codex: Path) -> tuple[str | None, dict[str, dict[str, Any]]]:
    candidates = [
        ("direct", [str(codex), "sandbox", "--", "/usr/bin/true"]),
        ("linux-subcommand", [str(codex), "sandbox", "linux", "--", "/usr/bin/true"]),
    ]
    attempts: dict[str, dict[str, Any]] = {}
    for name, argv in candidates:
        result = run(argv, timeout=30)
        attempts[name] = {
            "argv": argv,
            "exitCode": result.returncode,
            "stdout": result.stdout[-1000:],
            "stderr": result.stderr[-1000:],
        }
        if result.returncode == 0:
            return name, attempts
    return None, attempts


def codex_sandbox_argv(codex: Path, command_form: str, command: list[str]) -> list[str]:
    if command_form == "direct":
        return [str(codex), "sandbox", "--", *command]
    if command_form == "linux-subcommand":
        return [str(codex), "sandbox", "linux", "--", *command]
    raise HostError("CODEX_SANDBOX_COMMAND_FORM_INVALID", "Unsupported Codex sandbox command form", commandForm=command_form)


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
    plan_input = value.get("securityBoundary", {}).get("hostCalibrationPlanInput")
    require(isinstance(plan_input, dict), "HOST_CONTRACT_INVALID", "Host calibration plan input contract is missing")
    require(plan_input.get("requiredFor") == "host-requalification-analysis", "HOST_CONTRACT_INVALID", "Host calibration plan input requirement is invalid")
    require(plan_input.get("source") == "agent-task-prepare-record.taskAuthorization", "HOST_CONTRACT_INVALID", "Host calibration plan input source is invalid")
    require(plan_input.get("sandboxPath") == "/run/codex-input/calibration-plan.json", "HOST_CONTRACT_INVALID", "Host calibration plan sandbox path is invalid")
    require(plan_input.get("environmentVariable") == "SPRINGMASTER_CODEX_CALIBRATION_PLAN", "HOST_CONTRACT_INVALID", "Host calibration plan environment variable is invalid")
    require(plan_input.get("sourceSha256MustMatchPrepareRecord") is True and plan_input.get("filesystemSearchForbidden") is True, "HOST_CONTRACT_INVALID", "Host calibration plan input safety policy is invalid")
    durable = value.get("durableInvocation") if isinstance(value.get("durableInvocation"), dict) else {}
    require(durable.get("canonicalStartOperation") == "codex-host-sandbox invoke-start", "HOST_CONTRACT_INVALID", "Durable invocation start operation is invalid")
    require(durable.get("processOwner") == "process-ops/crun" and durable.get("singletonKeyPolicy") == "stable-task-id-derived", "HOST_CONTRACT_INVALID", "Durable invocation process ownership is invalid")
    require(durable.get("observerLossTerminatesWorker") is False, "HOST_CONTRACT_INVALID", "Durable invocation must survive observer loss")
    require(durable.get("activeTimeBudget") is True and durable.get("suspendGapPolicy") == "credit-at-most-max-active-credit-per-heartbeat", "HOST_CONTRACT_INVALID", "Durable invocation active-time policy is invalid")
    require(isinstance(durable.get("heartbeatIntervalSeconds"), int) and isinstance(durable.get("maxActiveCreditPerHeartbeatSeconds"), int) and durable.get("maxActiveCreditPerHeartbeatSeconds") >= durable.get("heartbeatIntervalSeconds"), "HOST_CONTRACT_INVALID", "Durable invocation heartbeat policy is invalid")
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


def write_private_codex_config(private_home: Path, *, writable_task: bool) -> dict[str, str]:
    require(private_home.is_dir() and not private_home.is_symlink(), "PRIVATE_CODEX_HOME_INVALID", "Private Codex home must be an existing non-symlink directory", path=str(private_home))
    auth_path = private_home / "auth.json"
    require(auth_path.is_file() and not auth_path.is_symlink(), "CODEX_AUTH_MISSING", "Private Codex auth.json is missing or unsafe", path=str(auth_path))
    config_path = private_home / "config.toml"
    require(not config_path.exists() and not config_path.is_symlink(), "PRIVATE_CODEX_CONFIG_EXISTS", "Private Codex config must not pre-exist", path=str(config_path))
    permission_profile = "springmaster-workspace" if writable_task else "springmaster-read-only"
    permission_profile_base = ":workspace" if writable_task else ":read-only"
    sandbox_auth_path = "/run/codex-home/auth.json"
    content = (
        f'default_permissions = "{permission_profile}"\n\n'
        f'[permissions.{permission_profile}]\n'
        f'extends = "{permission_profile_base}"\n\n'
        f'[permissions.{permission_profile}.filesystem]\n'
        f'"{sandbox_auth_path}" = "deny"\n'
    )
    config_path.write_text(content, encoding="utf-8")
    config_path.chmod(0o600)
    return {
        "permissionProfile": permission_profile,
        "permissionProfileBase": permission_profile_base,
        "permissionConfigSha256": sha256_file(config_path),
        "sandboxAuthPath": sandbox_auth_path,
        "sandboxAuthAccess": "deny",
    }


def prepare_resolver_dependency(
    private_home: Path,
    *,
    resolv_conf: Path = Path("/etc/resolv.conf"),
    host_run: Path = Path("/run"),
) -> dict[str, Any]:
    require(private_home.is_dir() and not private_home.is_symlink(), "PRIVATE_CODEX_HOME_INVALID", "Private Codex home must be an existing non-symlink directory", path=str(private_home))
    require(resolv_conf.exists() or resolv_conf.is_symlink(), "HOST_RESOLVER_INVALID", "Host resolv.conf is missing", path=str(resolv_conf))
    try:
        canonical = resolv_conf.resolve(strict=True)
    except (FileNotFoundError, RuntimeError) as exc:
        raise HostError("HOST_RESOLVER_INVALID", "Host resolv.conf cannot be resolved", path=str(resolv_conf)) from exc
    require(canonical.is_file() and not canonical.is_symlink(), "HOST_RESOLVER_INVALID", "Host resolver target must be a regular file", path=str(canonical))
    size = canonical.stat().st_size
    require(0 < size <= 64 * 1024, "HOST_RESOLVER_INVALID", "Host resolver file size is outside the allowed range", path=str(canonical), size=size)
    metadata: dict[str, Any] = {
        "resolverSourcePath": str(resolv_conf),
        "resolverCanonicalPath": str(canonical),
        "resolverReexposedReadOnly": False,
    }
    if contains(host_run.resolve(), canonical):
        relative = canonical.relative_to(host_run.resolve())
        sandbox_path = Path("/run") / relative
        require(not contains(Path("/run/codex-home"), sandbox_path), "HOST_RESOLVER_INVALID", "Host resolver target collides with private Codex home", path=str(sandbox_path))
        copied = private_home / "host-resolv.conf"
        require(not copied.exists() and not copied.is_symlink(), "PRIVATE_RESOLVER_COPY_EXISTS", "Private resolver copy must not pre-exist", path=str(copied))
        shutil.copyfile(canonical, copied)
        copied.chmod(0o600)
        metadata.update({
            "resolverSandboxPath": str(sandbox_path),
            "resolverCopiedSha256": sha256_file(copied),
            "resolverReexposedReadOnly": True,
        })
    return metadata


def resolver_bwrap_args(private_home: Path, resolver: dict[str, Any]) -> list[str]:
    if resolver.get("resolverReexposedReadOnly") is not True:
        return []
    sandbox_path = Path(str(resolver.get("resolverSandboxPath", "")))
    require(sandbox_path.is_absolute() and contains(Path("/run"), sandbox_path), "HOST_RESOLVER_INVALID", "Sandbox resolver path must be below /run", path=str(sandbox_path))
    copied = private_home / "host-resolv.conf"
    require(copied.is_file() and not copied.is_symlink(), "PRIVATE_RESOLVER_COPY_MISSING", "Private resolver copy is missing", path=str(copied))
    require(sha256_file(copied) == resolver.get("resolverCopiedSha256"), "PRIVATE_RESOLVER_COPY_DRIFT", "Private resolver copy hash changed", path=str(copied))
    args: list[str] = []
    current = Path("/run")
    for part in sandbox_path.relative_to(Path("/run")).parts[:-1]:
        current /= part
        args += ["--dir", str(current)]
    args += ["--ro-bind", str(copied), str(sandbox_path)]
    return args


def network_sandbox_prefix(*, bwrap: Path, ctx: dict[str, Path], private_home: Path, resolver: dict[str, Any]) -> list[str]:
    args = [
        str(bwrap), "--die-with-parent", "--new-session", "--unshare-pid", "--unshare-ipc", "--unshare-uts", "--unshare-cgroup-try",
        "--ro-bind", "/", "/", "--dev", "/dev", "--proc", "/proc", "--tmpfs", "/tmp", "--tmpfs", "/var/tmp", "--tmpfs", "/run",
    ]
    args += resolver_bwrap_args(private_home, resolver)
    args += ["--tmpfs", str(ctx["operatorHome"]), "--clearenv"]
    for key, value in sorted({"HOME": "/nonexistent", "LANG": os.environ.get("LANG", "C.UTF-8"), "LC_ALL": "C.UTF-8", "PATH": SANDBOX_PATH, "TZ": os.environ.get("TZ", "UTC")}.items()):
        args += ["--setenv", key, value]
    args += ["--"]
    return args


def control_plane_checks(*, bwrap: Path, ctx: dict[str, Path]) -> tuple[dict[str, Any], dict[str, Any]]:
    getent = executable("getent", None)
    curl = executable("curl", None)
    scratch = Path(tempfile.mkdtemp(prefix="codex-network-preflight-", dir=ctx["artifactRoot"]))
    try:
        resolver = prepare_resolver_dependency(scratch)
        prefix = network_sandbox_prefix(bwrap=bwrap, ctx=ctx, private_home=scratch, resolver=resolver)
        checks: dict[str, Any] = {}
        for name, argv, timeout in (
            ("outerSandboxDns", [str(getent), "ahosts", CONTROL_PLANE_HOST], 20),
            ("outerSandboxHttps", [str(curl), "-q", "-sS", "-o", "/dev/null", "--connect-timeout", "8", "--max-time", "20", CONTROL_PLANE_URL], 30),
        ):
            result = run(prefix + argv, timeout=timeout)
            checks[name] = {"exitCode": result.returncode, "stdout": result.stdout[-1000:], "stderr": result.stderr[-1000:]}
        resolver_public = {key: value for key, value in resolver.items() if key != "resolverCopiedSha256"}
        if "resolverCopiedSha256" in resolver:
            resolver_public["resolverCopiedSha256"] = resolver["resolverCopiedSha256"]
        return checks, resolver_public
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


def remove_empty_probe_scratch(parent: Path, run_root: Path) -> None:
    require(contains(run_root.resolve(), parent.resolve()), "PROBE_SCRATCH_PATH_INVALID", "Probe scratch path must remain below the external run root", path=str(parent), root=str(run_root))
    current = parent
    while current != run_root:
        try:
            current.rmdir()
        except OSError:
            break
        current = current.parent


def bwrap_prefix(*, bwrap: Path, ctx: dict[str, Path], task: Path, private_home: Path, resolver: dict[str, Any], writable_task: bool, extra_env: dict[str, str] | None = None, readonly_inputs: list[tuple[Path, Path]] | None = None) -> list[str]:
    require(task.is_dir() and not task.is_symlink(), "TASK_WORKTREE_INVALID", "Task worktree must be an existing non-symlink directory", path=str(task))
    task = task.resolve()
    require(contains(ctx["worktreeRoot"], task), "TASK_WORKTREE_OUTSIDE_ROOT", "Task worktree is outside the configured worktree root", path=str(task), root=str(ctx["worktreeRoot"]))
    args = [
        str(bwrap), "--die-with-parent", "--new-session", "--unshare-pid", "--unshare-ipc", "--unshare-uts", "--unshare-cgroup-try",
        "--ro-bind", "/", "/", "--dev", "/dev", "--proc", "/proc", "--tmpfs", "/tmp", "--tmpfs", "/var/tmp", "--tmpfs", "/run",
    ]
    args += resolver_bwrap_args(private_home, resolver)
    args += [
        "--tmpfs", str(ctx["operatorHome"]),
        "--bind", str(private_home), "/run/codex-home",
    ]
    if writable_task:
        args += ["--bind", str(task), str(task)]
    else:
        args += ["--ro-bind", str(task), str(task)]
    for source, target in readonly_inputs or []:
        require(source.is_file() and not source.is_symlink(), "READONLY_INPUT_INVALID", "Read-only sandbox input is missing or unsafe", path=str(source))
        require(target.is_absolute() and str(target).startswith("/run/codex-input/"), "READONLY_INPUT_TARGET_INVALID", "Read-only sandbox input target is outside the dedicated input root", path=str(target))
        args += ["--dir", str(target.parent), "--ro-bind", str(source), str(target)]
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
        "gitVersion": ["git", "--version"],
        "pythonVersion": [sys.executable, "--version"],
    }.items():
        result = run(argv, timeout=30)
        checks[name] = {"exitCode": result.returncode, "stdout": result.stdout[-1000:], "stderr": result.stderr[-1000:]}
        if result.returncode != 0:
            findings.append({"code": "HOST_INSPECTION_COMMAND_FAILED", "check": name, "exitCode": result.returncode})
    sandbox_form, sandbox_attempts = resolve_codex_sandbox_command_form(codex)
    checks["codexInnerSandboxSmoke"] = {
        "exitCode": 0 if sandbox_form is not None else 1,
        "commandForm": sandbox_form,
        "attempts": sandbox_attempts,
        "stdout": "",
        "stderr": "" if sandbox_form is not None else "No supported Codex sandbox command form succeeded",
    }
    supported_forms = set(contract.get("securityBoundary", {}).get("supportedInnerSandboxCommandForms", []))
    if sandbox_form is None or sandbox_form not in supported_forms:
        findings.append({"code": "CODEX_SANDBOX_COMMAND_FORM_UNSUPPORTED", "check": "codexInnerSandboxSmoke", "commandForm": sandbox_form, "supported": sorted(supported_forms)})
    network_checks, resolver = control_plane_checks(bwrap=bwrap, ctx=ctx)
    checks.update(network_checks)
    for name, result in network_checks.items():
        if result["exitCode"] != 0:
            findings.append({"code": "CONTROL_PLANE_PREFLIGHT_FAILED", "check": name, "exitCode": result["exitCode"]})
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
        "resolver": resolver,
        "checks": checks,
        "codexSandboxCommandForm": sandbox_form,
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
        auth.update(write_private_codex_config(private_home, writable_task=True))
        resolver = prepare_resolver_dependency(private_home)
        auth.update(resolver)
        prefix_rw = bwrap_prefix(bwrap=bwrap, ctx=ctx, task=task, private_home=private_home, resolver=resolver, writable_task=True)
        prefix_ro = bwrap_prefix(bwrap=bwrap, ctx=ctx, task=task, private_home=private_home, resolver=resolver, writable_task=False)
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
        sandbox_form, sandbox_attempts = resolve_codex_sandbox_command_form(codex)
        require(sandbox_form is not None, "CODEX_SANDBOX_COMMAND_FORM_UNSUPPORTED", "No supported Codex sandbox command form succeeded", attempts=sandbox_attempts)
        supported_forms = set(contract.get("securityBoundary", {}).get("supportedInnerSandboxCommandForms", []))
        require(sandbox_form in supported_forms, "CODEX_SANDBOX_COMMAND_FORM_UNSUPPORTED", "Resolved Codex sandbox command form is not allowed by the host contract", commandForm=sandbox_form, supported=sorted(supported_forms))
        inner_cases = [
            ("inner-sandbox-smoke", "PASS", codex_sandbox_argv(codex, sandbox_form, ["/usr/bin/true"])),
            ("inner-worktree-write", "PASS", codex_sandbox_argv(codex, sandbox_form, ["/bin/sh", "-eu", "-c", f"printf PASS > {json.dumps(str(task / '.codex-inner-write'))}"])),
            ("inner-auth-read", "DENIED", codex_sandbox_argv(codex, sandbox_form, ["/bin/cat", "/run/codex-home/auth.json"])),
            ("inner-network-egress", "DENIED", codex_sandbox_argv(codex, sandbox_form, ["/bin/sh", "-eu", "-c", "exec 3<>/dev/tcp/1.1.1.1/53"])),
            ("inner-git-common-write", "DENIED", codex_sandbox_argv(codex, sandbox_form, ["/bin/sh", "-eu", "-c", f"printf X > {json.dumps(str(ctx['gitCommon'] / '.codex-inner-denied'))}"])),
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
            "codexSandboxCommandForm": sandbox_form,
            "probes": results,
            "findings": findings,
        }
    finally:
        shutil.rmtree(private_home, ignore_errors=True)
        remove_empty_probe_scratch(parent, ctx["runRoot"])


def status_json(root: Path, task_id: str) -> dict[str, Any]:
    completed = run([str(root / "bin/agent-task.sh"), "--project-root", str(root), "--format", "json", "status", task_id], cwd=root)
    require(completed.returncode == 0, "AGENT_TASK_STATUS_FAILED", "Cannot resolve prepared task", taskId=task_id, stderr=completed.stderr[-2000:], stdout=completed.stdout[-2000:])
    try:
        value = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise HostError("AGENT_TASK_STATUS_INVALID", "Agent task status is not JSON", taskId=task_id) from exc
    require(isinstance(value, dict) and value.get("worktreePath"), "AGENT_TASK_NOT_PREPARED", "Agent task is not prepared", taskId=task_id)
    return value


def validate_codex_jsonl(stdout: str, mode: str, contract: dict[str, Any]) -> dict[str, Any]:
    security = contract.get("securityBoundary") if isinstance(contract.get("securityBoundary"), dict) else {}
    policy = security.get("codexExecJsonlValidation") if isinstance(security.get("codexExecJsonlValidation"), dict) else {}
    require(policy.get("required") is True, "HOST_CONTRACT_INVALID", "Codex JSONL validation policy is missing or disabled")
    required_true_flags = (
        "jsonObjectPerNonemptyLineRequired",
        "turnCompletedRequired",
        "turnFailedForbidden",
        "errorEventsForbidden",
        "startedCommandMustComplete",
        "completedCommandTerminalStatusRequired",
        "completedCommandExitCodeRequired",
        "implementationIntermediateCommandFailureAllowed",
        "outerProcessExitCodeZeroRequired",
    )
    for key in required_true_flags:
        require(policy.get(key) is True, "HOST_CONTRACT_INVALID", "Codex JSONL validation invariant must be enabled", invariant=key)
    require(mode in {"analysis", "implementation", "qualification"}, "TASK_MODE_INVALID", "Unsupported task mode", mode=mode)
    zero_required_modes = policy.get("completedCommandExitCodeZeroRequiredModes")
    require(
        isinstance(zero_required_modes, list)
        and zero_required_modes
        and all(isinstance(item, str) and item in {"analysis", "qualification"} for item in zero_required_modes)
        and len(set(zero_required_modes)) == len(zero_required_modes),
        "HOST_CONTRACT_INVALID",
        "Completed-command zero-exit modes must be a unique non-empty subset of analysis/qualification",
        modes=zero_required_modes,
    )
    strict_command_success = mode in set(zero_required_modes)

    findings: list[dict[str, Any]] = []
    nonempty_line_count = 0
    parse_error_count = 0
    error_event_count = 0
    turn_started_count = 0
    turn_completed_count = 0
    turn_failed_count = 0
    command_started_ids: set[str] = set()
    command_completed_ids: set[str] = set()
    command_completed_count = 0
    command_failed_count = 0

    for line_number, raw in enumerate(stdout.splitlines(), 1):
        if not raw.strip():
            continue
        nonempty_line_count += 1
        try:
            event = json.loads(raw)
        except json.JSONDecodeError as exc:
            parse_error_count += 1
            findings.append({
                "code": "CODEX_JSONL_PARSE_ERROR",
                "line": line_number,
                "column": exc.colno,
            })
            continue
        if not isinstance(event, dict):
            findings.append({"code": "CODEX_JSONL_EVENT_INVALID", "line": line_number})
            continue

        event_type = event.get("type")
        item = event.get("item") if isinstance(event.get("item"), dict) else {}
        item_type = item.get("type")
        item_id = item.get("id") if isinstance(item.get("id"), str) and item.get("id") else None

        if event_type == "turn.started":
            turn_started_count += 1
        elif event_type == "turn.completed":
            turn_completed_count += 1
        elif event_type == "turn.failed":
            turn_failed_count += 1
            findings.append({"code": "CODEX_TURN_FAILED", "line": line_number})
        elif event_type == "error":
            error_event_count += 1
            findings.append({"code": "CODEX_ERROR_EVENT", "line": line_number})

        if item_type == "error":
            error_event_count += 1
            finding: dict[str, Any] = {"code": "CODEX_ERROR_ITEM", "line": line_number}
            message = item.get("message")
            if isinstance(message, str) and message:
                finding["message"] = message[-1000:]
            findings.append(finding)

        if item_type != "command_execution":
            continue

        if event_type == "item.started":
            if item_id is None:
                findings.append({"code": "CODEX_COMMAND_ID_MISSING", "line": line_number, "phase": "started"})
            else:
                command_started_ids.add(item_id)
            continue

        if event_type != "item.completed":
            continue

        command_completed_count += 1
        if item_id is None:
            findings.append({"code": "CODEX_COMMAND_ID_MISSING", "line": line_number, "phase": "completed"})
        else:
            command_completed_ids.add(item_id)

        status = item.get("status")
        exit_code = item.get("exit_code")
        terminal_status = status in {"completed", "failed"}
        exit_code_present = isinstance(exit_code, int)
        command_failed = status == "failed" or (exit_code_present and exit_code != 0)

        if not terminal_status:
            findings.append({
                "code": "CODEX_COMMAND_STATUS_NOT_TERMINAL",
                "line": line_number,
                "itemId": item_id,
                "status": status,
            })
        if not exit_code_present:
            findings.append({
                "code": "CODEX_COMMAND_EXIT_CODE_MISSING",
                "line": line_number,
                "itemId": item_id,
                "exitCode": exit_code,
            })

        if command_failed:
            command_failed_count += 1
            if strict_command_success:
                if status == "failed":
                    findings.append({
                        "code": "CODEX_COMMAND_STATUS_FAILED",
                        "line": line_number,
                        "itemId": item_id,
                        "status": status,
                    })
                if exit_code_present and exit_code != 0:
                    findings.append({
                        "code": "CODEX_COMMAND_EXIT_NONZERO",
                        "line": line_number,
                        "itemId": item_id,
                        "exitCode": exit_code,
                    })

    if turn_completed_count < 1:
        findings.append({"code": "CODEX_TURN_COMPLETED_MISSING"})

    incomplete_commands = sorted(command_started_ids - command_completed_ids)
    if incomplete_commands:
        findings.append({"code": "CODEX_COMMAND_COMPLETION_MISSING", "itemIds": incomplete_commands})

    minimum = policy.get("implementationCompletedCommandExecutionMinimum", 0)
    require(isinstance(minimum, int) and minimum >= 0, "HOST_CONTRACT_INVALID", "Implementation command minimum is invalid")
    if mode == "implementation" and command_completed_count < minimum:
        findings.append({
            "code": "CODEX_IMPLEMENTATION_COMMAND_EXECUTION_MISSING",
            "minimum": minimum,
            "actual": command_completed_count,
        })

    return {
        "schemaVersion": "springmaster.codex-jsonl-validation.v1",
        "status": "PASS" if not findings else "FAILED",
        "mode": mode,
        "nonemptyLineCount": nonempty_line_count,
        "parseErrorCount": parse_error_count,
        "errorEventCount": error_event_count,
        "turnStartedCount": turn_started_count,
        "turnCompletedCount": turn_completed_count,
        "turnFailedCount": turn_failed_count,
        "commandExecutionStartedCount": len(command_started_ids),
        "commandExecutionCompletedCount": command_completed_count,
        "commandExecutionFailedCount": command_failed_count,
        "intermediateCommandFailureAllowed": mode == "implementation",
        "findings": findings,
    }


def host_calibration_plan_input(
    *,
    ctx: dict[str, Path],
    root: Path,
    run_dir: Path,
    task_contract: dict[str, Any],
    task_id: str,
    mode: str,
    contract: dict[str, Any],
) -> tuple[Path, Path, str] | None:
    prepare_record = load_json(run_dir / "prepare-record.json")
    authorization = prepare_record.get("taskAuthorization") if isinstance(prepare_record.get("taskAuthorization"), dict) else {}
    if authorization.get("source") != "sibling-host-calibration-plan":
        return None
    if mode != "analysis":
        return None
    input_contract = contract["securityBoundary"]["hostCalibrationPlanInput"]
    plan_path = Path(str(authorization.get("calibrationPlanPath", ""))).expanduser()
    require(plan_path.is_absolute(), "CALIBRATION_PLAN_INPUT_INVALID", "Prepared calibration plan path must be absolute", path=str(plan_path))
    plan_path = plan_path.resolve()
    require(plan_path.is_file() and not plan_path.is_symlink(), "CALIBRATION_PLAN_INPUT_INVALID", "Prepared calibration plan is missing or unsafe", path=str(plan_path))
    require(contains(ctx["artifactRoot"], plan_path), "CALIBRATION_PLAN_INPUT_OUTSIDE_ARTIFACT_ROOT", "Prepared calibration plan must remain below the external artifact root", path=str(plan_path), root=str(ctx["artifactRoot"]))
    expected_plan_sha = authorization.get("calibrationPlanSha256")
    require(isinstance(expected_plan_sha, str) and sha256_file(plan_path) == expected_plan_sha, "CALIBRATION_PLAN_INPUT_HASH_MISMATCH", "Prepared calibration plan hash changed after task preparation", path=str(plan_path))
    plan = load_json(plan_path)
    require(plan.get("schemaVersion") == "springmaster.codex-calibration-plan.v2" and plan.get("purpose") == "HOST_REQUALIFICATION", "CALIBRATION_PLAN_INPUT_SCHEMA_INVALID", "Prepared calibration plan is not a host requalification plan", path=str(plan_path))
    require(plan.get("baselineCommit") == task_contract.get("baseCommit") == git(root, "rev-parse", "HEAD"), "CALIBRATION_PLAN_INPUT_BASELINE_MISMATCH", "Prepared calibration plan baseline does not match the task and repository", path=str(plan_path))
    require(plan.get("hostId") == host_id(), "CALIBRATION_PLAN_INPUT_HOST_MISMATCH", "Prepared calibration plan is bound to another host", path=str(plan_path))
    matches = [entry for entry in plan.get("tasks", []) if isinstance(entry, dict) and entry.get("taskId") == task_id]
    require(len(matches) == 1 and matches[0].get("mode") == "analysis", "CALIBRATION_PLAN_INPUT_TASK_MISMATCH", "Prepared calibration plan does not uniquely authorize the analysis task", taskId=task_id)
    return plan_path, Path(str(input_contract["sandboxPath"])), str(input_contract["environmentVariable"])


def boot_id() -> str:
    path = Path("/proc/sys/kernel/random/boot_id")
    if path.is_file():
        value = path.read_text(encoding="utf-8").strip()
        if value:
            return value
    return f"host-{host_id()}"


def active_time_credit(raw_delta: float, maximum_credit: float) -> tuple[float, float]:
    require(raw_delta >= 0.0, "ACTIVE_TIME_DELTA_INVALID", "Active-time delta must not be negative", rawDelta=raw_delta)
    require(maximum_credit > 0.0, "ACTIVE_TIME_CREDIT_INVALID", "Maximum active-time credit must be positive", maximumCredit=maximum_credit)
    credited = min(raw_delta, maximum_credit)
    return credited, max(0.0, raw_delta - credited)


def worktree_progress_fingerprint(worktree: Path) -> str:
    completed = subprocess.run(
        ["git", "status", "--porcelain=v1", "-z", "--untracked-files=all"],
        cwd=worktree,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        return sha256_bytes(b"git-status-error\0" + completed.stderr[-2000:])
    digest = hashlib.sha256(completed.stdout)
    for entry in completed.stdout.split(b"\0"):
        if len(entry) < 4 or entry[2:3] != b" ":
            continue
        raw_path = entry[3:]
        try:
            relative = raw_path.decode("utf-8", errors="surrogateescape")
            candidate = worktree / relative
            stat_result = candidate.lstat()
            digest.update(relative.encode("utf-8", errors="surrogateescape"))
            digest.update(f"\0{stat_result.st_mode}\0{stat_result.st_size}\0{stat_result.st_mtime_ns}\0".encode("ascii"))
        except (FileNotFoundError, OSError):
            continue
    return digest.hexdigest()


def terminate_process_group(process: subprocess.Popen[bytes], *, grace_seconds: float = 10.0) -> None:
    if process.poll() is not None:
        return
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    deadline = time.monotonic() + grace_seconds
    while process.poll() is None and time.monotonic() < deadline:
        time.sleep(0.1)
    if process.poll() is None:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            pass


def invocation_evidence_dir(ctx: dict[str, Path], task_id: str, base_commit: str) -> Path:
    return ctx["artifactRoot"] / "codex-host-qualification" / host_id() / base_commit / task_id.lower()


def invocation_preflight(
    root: Path,
    task_id: str,
    prompt_file: Path,
    model: str,
    change_bundle: Path | None,
    *,
    allowed_invocation_states: set[str] | None = None,
) -> tuple[dict[str, Path], dict[str, Any], dict[str, Any], Path, Path, str, list[str], list[tuple[Path, Path]], dict[str, str]]:
    ctx = context(root)
    _, contract = load_contract(root)
    state = status_json(root, task_id)
    allowed_states = allowed_invocation_states or {"NOT_RECORDED"}
    require(state.get("codexInvocation") in allowed_states, "INVOCATION_TASK_ALREADY_CONSUMED", "Task invocation lifecycle state is not valid for this operation", taskId=task_id, codexInvocation=state.get("codexInvocation"), allowedInvocationStates=sorted(allowed_states))
    task = Path(state["worktreePath"]).resolve()
    run_dir = Path(state["runDirectory"]).resolve()
    task_contract = load_json(run_dir / "task-contract.json")
    mode = task_contract.get("mode")
    require(mode in {"analysis", "implementation", "qualification"}, "TASK_MODE_INVALID", "Unsupported task mode", mode=mode)
    require(task_contract.get("baseCommit") == git(ctx["integration"], "rev-parse", "HEAD"), "INTEGRATION_BASE_DRIFT", "Integration HEAD changed after task preparation", taskBase=task_contract.get("baseCommit"), integrationHead=git(ctx["integration"], "rev-parse", "HEAD"))
    require(prompt_file.is_file() and not prompt_file.is_symlink(), "PROMPT_INVALID", "Prompt file is missing or unsafe", path=str(prompt_file))
    require(isinstance(model, str) and model.strip(), "MODEL_INVALID", "Codex model is required")
    extra_env = {
        "SPRINGMASTER_AGENT_TASK_ID": task_id,
        "SPRINGMASTER_AGENT_TASK_CONTRACT": str(run_dir / "task-contract.json"),
    }
    reads = ["task-worktree"]
    readonly_inputs: list[tuple[Path, Path]] = []
    plan_input = host_calibration_plan_input(
        ctx=ctx,
        root=root,
        run_dir=run_dir,
        task_contract=task_contract,
        task_id=task_id,
        mode=mode,
        contract=contract,
    )
    if plan_input is not None:
        plan_path, sandbox_plan_path, environment_variable = plan_input
        readonly_inputs.append((plan_path, sandbox_plan_path))
        extra_env[environment_variable] = str(sandbox_plan_path)
        reads.append("host-calibration-plan-read-only")
    if change_bundle is not None:
        require(mode == "implementation", "CHANGE_BUNDLE_MODE_INVALID", "Change bundles require an implementation task", mode=mode)
        resolved_bundle = change_bundle.expanduser().resolve()
        require(resolved_bundle.is_file() and not resolved_bundle.is_symlink(), "CHANGE_BUNDLE_INVALID", "Change bundle is missing or unsafe", path=str(resolved_bundle))
        require(contains(ctx["artifactRoot"], resolved_bundle), "CHANGE_BUNDLE_OUTSIDE_ARTIFACT_ROOT", "Change bundle must be below the external artifact root", path=str(resolved_bundle), root=str(ctx["artifactRoot"]))
        extra_env["SPRINGMASTER_CODEX_CHANGE_BUNDLE"] = str(resolved_bundle)
        reads.append("external-artifact-root-read-only")
    return ctx, contract, task_contract, task, run_dir, str(mode), reads, readonly_inputs, extra_env


def invoke_process(
    root: Path,
    bwrap: Path,
    codex: Path,
    task_id: str,
    prompt_file: Path,
    model: str,
    change_bundle: Path | None,
    *,
    active_timeout_seconds: int,
    no_progress_timeout_seconds: int | None,
    process_binding: dict[str, Any],
    evidence_dir: Path | None = None,
) -> dict[str, Any]:
    require(1 <= active_timeout_seconds <= 86400, "ACTIVE_TIMEOUT_INVALID", "Active-time budget must be between 1 and 86400 seconds", activeTimeoutSeconds=active_timeout_seconds)
    require(no_progress_timeout_seconds is None or 1 <= no_progress_timeout_seconds <= 86400, "NO_PROGRESS_TIMEOUT_INVALID", "No-progress budget must be between 1 and 86400 seconds when enabled", noProgressTimeoutSeconds=no_progress_timeout_seconds)
    ctx, contract, task_contract, task, run_dir, mode, reads, readonly_inputs, extra_env = invocation_preflight(root, task_id, prompt_file, model, change_bundle)
    base_commit = str(task_contract["baseCommit"])
    target_evidence_dir = evidence_dir or invocation_evidence_dir(ctx, task_id, base_commit)
    if evidence_dir is None:
        require(not target_evidence_dir.exists(), "EVIDENCE_DIRECTORY_EXISTS", "Invocation evidence directory already exists", path=str(target_evidence_dir))
        target_evidence_dir.mkdir(parents=True, mode=0o700)
    else:
        require(target_evidence_dir.is_dir() and not target_evidence_dir.is_symlink(), "EVIDENCE_DIRECTORY_INVALID", "Durable invocation evidence directory is missing or unsafe", path=str(target_evidence_dir))
    stdout_path = target_evidence_dir / "codex.stdout.jsonl"
    stderr_path = target_evidence_dir / "codex.stderr.log"
    heartbeat_path = target_evidence_dir / "heartbeat.json"
    validation_path = target_evidence_dir / "codex-jsonl-validation.json"
    effect_path = target_evidence_dir / "operator-command-effect.json"
    start_path = target_evidence_dir / "codex-invocation-start.json"
    invocation_path = target_evidence_dir / "codex-invocation.json"
    result_path = target_evidence_dir / "host-invocation.json"
    for path in (stdout_path, stderr_path, heartbeat_path, validation_path, effect_path, start_path, invocation_path, result_path):
        require(not path.exists() and not path.is_symlink(), "INVOCATION_EVIDENCE_ALREADY_EXISTS", "Invocation evidence already exists", path=str(path))
    source_home = resolve_codex_home()
    private_home = Path(tempfile.mkdtemp(prefix="private-codex-home-", dir=target_evidence_dir))
    process: subprocess.Popen[bytes] | None = None
    lifecycle_started = False
    effect: dict[str, Any] | None = None
    invocation: dict[str, Any] | None = None
    auth: dict[str, Any] = {}
    timeout_reason: str | None = None
    requested_signal: int | None = None
    started_at = utc_now()
    finished_at = started_at
    codex_cli_version = "unknown"
    record_sandbox = "linux-bwrap-workspace-write" if mode == "implementation" else "linux-bwrap-read-only"
    platform_sandbox = {
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
    }
    try:
        auth = copy_codex_auth(source_home, private_home)
        auth.update(write_private_codex_config(private_home, writable_task=mode == "implementation"))
        resolver = prepare_resolver_dependency(private_home)
        auth.update(resolver)
        codex_argv = [str(codex), "--ask-for-approval", "never", "exec", "--ephemeral", "--ignore-rules", "--json", "--model", model, "--cd", str(task), "-"]
        outer = bwrap_prefix(bwrap=bwrap, ctx=ctx, task=task, private_home=private_home, resolver=resolver, writable_task=mode == "implementation", extra_env=extra_env, readonly_inputs=readonly_inputs)
        codex_cli_version = run([str(codex), "--version"], timeout=30).stdout.strip()
        writes = ["task-worktree"] if mode == "implementation" else []
        mutation = "task-worktree-only" if mode == "implementation" else "none"
        effect = {
            "schemaVersion": "springmaster.operator-command-effect.v1",
            "commandId": "codex-host-sandbox",
            "taskId": task_id,
            "purpose": "Host-confined Springmaster Codex invocation",
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
        stdout_path.touch(mode=0o600, exist_ok=False)
        stderr_path.touch(mode=0o600, exist_ok=False)
        start_record = {
            "schemaVersion": "springmaster.codex-invocation-start.v1",
            "taskId": task_id,
            "commandId": "codex-host-sandbox",
            "recordedAt": utc_now(),
            "agent": {
                "name": "codex",
                "cliVersion": codex_cli_version,
                "model": model,
                "executablePath": str(codex),
                "executableSha256": sha256_file(codex),
            },
            "process": {
                "owner": process_binding["owner"],
                "runId": process_binding.get("runId"),
                "singletonKey": process_binding.get("singletonKey"),
                "workerPid": os.getpid(),
                "workerPgid": os.getpgrp(),
                "bootId": boot_id(),
            },
            "execution": {
                "argv": effect["argv"],
                "workingDirectory": str(task),
                "sandboxProfile": record_sandbox,
                "approvalPolicy": "never",
                "platformSandbox": platform_sandbox,
                "environmentKeys": sorted(sanitized_env(Path("/run/codex-home"), extra_env).keys()),
                "startedAt": started_at,
                "stdoutPath": str(stdout_path),
                "stderrPath": str(stderr_path),
                "heartbeatPath": str(heartbeat_path),
                "activeTimeoutSeconds": active_timeout_seconds,
                "noProgressTimeoutSeconds": no_progress_timeout_seconds,
            },
        }
        atomic_json(effect_path, effect)
        atomic_json(start_path, start_record)
        start_record_result = run(
            [str(root / "bin/agent-task.sh"), "--project-root", str(root), "record-invocation-start", task_id, "--effect", str(effect_path), "--start", str(start_path)],
            cwd=root,
            timeout=60,
        )
        require(start_record_result.returncode == 0, "INVOCATION_START_RECORD_REJECTED", "Agent task rejected invocation start evidence", stdout=start_record_result.stdout[-2000:], stderr=start_record_result.stderr[-2000:])
        lifecycle_started = True
        atomic_json(heartbeat_path, {
            "schemaVersion": "springmaster.codex-invocation-heartbeat.v1",
            "taskId": task_id,
            "processRunId": process_binding.get("runId"),
            "singletonKey": process_binding.get("singletonKey"),
            "bootId": boot_id(),
            "workerPid": os.getpid(),
            "workerPgid": os.getpgrp(),
            "codexPid": None,
            "codexPgid": None,
            "status": "INVOCATION_STARTED",
            "wallClockTimestamp": utc_now(),
            "activeElapsedSeconds": 0.0,
            "excludedGapSeconds": 0.0,
            "stdoutBytes": 0,
            "stderrBytes": 0,
            "worktreeFingerprint": worktree_progress_fingerprint(task),
            "lastProgressAt": utc_now(),
            "lastProgressActiveSeconds": 0.0,
        })
        old_handlers: dict[int, Any] = {}
        def handle_signal(signum: int, _frame: Any) -> None:
            nonlocal requested_signal
            requested_signal = signum
        for signum in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
            old_handlers[signum] = signal.getsignal(signum)
            signal.signal(signum, handle_signal)
        try:
            with prompt_file.open("rb") as prompt_handle, stdout_path.open("ab", buffering=0) as stdout_handle, stderr_path.open("ab", buffering=0) as stderr_handle:
                process = subprocess.Popen(
                    outer + codex_argv,
                    cwd=task,
                    stdin=prompt_handle,
                    stdout=stdout_handle,
                    stderr=stderr_handle,
                    start_new_session=True,
                )
                heartbeat_contract = contract.get("durableInvocation") if isinstance(contract.get("durableInvocation"), dict) else {}
                heartbeat_interval = float(heartbeat_contract.get("heartbeatIntervalSeconds", 2))
                maximum_credit = float(heartbeat_contract.get("maxActiveCreditPerHeartbeatSeconds", 10))
                require(0.1 <= heartbeat_interval <= 60.0, "HEARTBEAT_INTERVAL_INVALID", "Heartbeat interval is invalid", heartbeatIntervalSeconds=heartbeat_interval)
                require(heartbeat_interval <= maximum_credit <= 300.0, "ACTIVE_TIME_CREDIT_INVALID", "Maximum active-time heartbeat credit is invalid", maximumCredit=maximum_credit)
                last_tick = time.monotonic()
                active_elapsed = 0.0
                excluded_gap = 0.0
                stdout_bytes = stdout_path.stat().st_size
                stderr_bytes = stderr_path.stat().st_size
                fingerprint = worktree_progress_fingerprint(task)
                last_progress_active = 0.0
                last_progress_at = utc_now()
                while True:
                    returncode = process.poll()
                    now = time.monotonic()
                    raw_delta = max(0.0, now - last_tick)
                    credited, excluded = active_time_credit(raw_delta, maximum_credit)
                    active_elapsed += credited
                    excluded_gap += excluded
                    last_tick = now
                    new_stdout_bytes = stdout_path.stat().st_size
                    new_stderr_bytes = stderr_path.stat().st_size
                    new_fingerprint = worktree_progress_fingerprint(task)
                    if (new_stdout_bytes, new_stderr_bytes, new_fingerprint) != (stdout_bytes, stderr_bytes, fingerprint):
                        last_progress_active = active_elapsed
                        last_progress_at = utc_now()
                        stdout_bytes, stderr_bytes, fingerprint = new_stdout_bytes, new_stderr_bytes, new_fingerprint
                    status = "RUNNING" if returncode is None else "PROCESS_EXITED"
                    atomic_json(heartbeat_path, {
                        "schemaVersion": "springmaster.codex-invocation-heartbeat.v1",
                        "taskId": task_id,
                        "processRunId": process_binding.get("runId"),
                        "singletonKey": process_binding.get("singletonKey"),
                        "bootId": boot_id(),
                        "workerPid": os.getpid(),
                        "workerPgid": os.getpgrp(),
                        "codexPid": process.pid,
                        "codexPgid": process.pid,
                        "status": status,
                        "wallClockTimestamp": utc_now(),
                        "activeElapsedSeconds": round(active_elapsed, 6),
                        "excludedGapSeconds": round(excluded_gap, 6),
                        "stdoutBytes": new_stdout_bytes,
                        "stderrBytes": new_stderr_bytes,
                        "worktreeFingerprint": new_fingerprint,
                        "lastProgressAt": last_progress_at,
                        "lastProgressActiveSeconds": round(last_progress_active, 6),
                    })
                    if returncode is not None:
                        break
                    if requested_signal is not None:
                        timeout_reason = f"SIGNAL_{requested_signal}"
                        terminate_process_group(process)
                        break
                    if active_elapsed >= float(active_timeout_seconds):
                        timeout_reason = "ACTIVE_TIME_TIMEOUT"
                        terminate_process_group(process)
                        break
                    if no_progress_timeout_seconds is not None and (active_elapsed - last_progress_active) >= float(no_progress_timeout_seconds):
                        timeout_reason = "NO_PROGRESS_TIMEOUT"
                        terminate_process_group(process)
                        break
                    time.sleep(heartbeat_interval)
                if process.poll() is None:
                    process.wait(timeout=5)
        finally:
            for signum, previous in old_handlers.items():
                signal.signal(signum, previous)
        finished_at = utc_now()
        exit_code = process.returncode if process is not None else None
        if timeout_reason is not None:
            execution_status = "INTERRUPTED"
        elif exit_code == 0:
            execution_status = "COMPLETED"
        else:
            execution_status = "FAILED"
        invocation = {
            "schemaVersion": "springmaster.codex-invocation-record.v1",
            "taskId": task_id,
            "commandId": "codex-host-sandbox",
            "recordedAt": utc_now(),
            "agent": {"name": "codex", "cliVersion": codex_cli_version, "model": model},
            "execution": {
                "argv": effect["argv"],
                "workingDirectory": str(task),
                "sandboxProfile": record_sandbox,
                "approvalPolicy": "never",
                "platformSandbox": platform_sandbox,
                "environmentKeys": sorted(sanitized_env(Path("/run/codex-home"), extra_env).keys()),
                "startedAt": started_at,
                "finishedAt": finished_at,
                "status": execution_status,
                "exitCode": exit_code,
            },
        }
        atomic_json(invocation_path, invocation)
        record_result = run(
            [str(root / "bin/agent-task.sh"), "--project-root", str(root), "record-invocation", task_id, "--effect", str(effect_path), "--record", str(invocation_path)],
            cwd=root,
            timeout=60,
        )
        require(record_result.returncode == 0, "INVOCATION_RECORD_REJECTED", "Agent task rejected terminal invocation evidence", stdout=record_result.stdout[-2000:], stderr=record_result.stderr[-2000:])
        stdout_text = stdout_path.read_text(encoding="utf-8", errors="replace")
        jsonl_validation = validate_codex_jsonl(stdout_text, mode, contract)
        atomic_json(validation_path, jsonl_validation)
        governed_pass = timeout_reason is None and exit_code == 0 and jsonl_validation["status"] == "PASS"
        heartbeat = load_json(heartbeat_path)
        heartbeat["status"] = "COMPLETED" if governed_pass else "FAILED"
        heartbeat["wallClockTimestamp"] = utc_now()
        heartbeat["terminalReason"] = timeout_reason
        heartbeat["exitCode"] = exit_code
        atomic_json(heartbeat_path, heartbeat)
        result = {
            "schemaVersion": REPORT_SCHEMA,
            "operation": "invoke",
            "status": "PASS" if governed_pass else "FAILED",
            "generatedAt": utc_now(),
            "hostId": host_id(),
            "baselineCommit": base_commit,
            "taskId": task_id,
            "taskMode": mode,
            "worktreePath": str(task),
            "model": model,
            "codexCliVersion": codex_cli_version,
            "exitCode": exit_code,
            "terminalReason": timeout_reason,
            "processRunId": process_binding.get("runId"),
            "singletonKey": process_binding.get("singletonKey"),
            "activeElapsedSeconds": heartbeat.get("activeElapsedSeconds"),
            "excludedGapSeconds": heartbeat.get("excludedGapSeconds"),
            "sandboxArgvSha256": sha256_bytes(json.dumps(outer, separators=(",", ":")).encode("utf-8")),
            "authHandling": auth,
            "effect": {"path": str(effect_path), "sha256": sha256_file(effect_path)},
            "invocationStart": {"path": str(start_path), "sha256": sha256_file(start_path)},
            "invocation": {"path": str(invocation_path), "sha256": sha256_file(invocation_path)},
            "heartbeat": {"path": str(heartbeat_path), "sha256": sha256_file(heartbeat_path)},
            "stdout": {"path": str(stdout_path), "sha256": sha256_file(stdout_path)},
            "stderr": {"path": str(stderr_path), "sha256": sha256_file(stderr_path)},
            "codexJsonlValidation": {
                "path": str(validation_path),
                "sha256": sha256_file(validation_path),
                "status": jsonl_validation["status"],
                "commandExecutionCompletedCount": jsonl_validation["commandExecutionCompletedCount"],
                "errorEventCount": jsonl_validation["errorEventCount"],
            },
        }
        atomic_json(result_path, result)
        return result
    except Exception:
        if lifecycle_started and process is not None and process.poll() is None:
            terminate_process_group(process)
        if lifecycle_started and effect is not None and not invocation_path.exists():
            finished_at = utc_now()
            exit_code = process.returncode if process is not None else None
            emergency_invocation = {
                "schemaVersion": "springmaster.codex-invocation-record.v1",
                "taskId": task_id,
                "commandId": "codex-host-sandbox",
                "recordedAt": utc_now(),
                "agent": {"name": "codex", "cliVersion": codex_cli_version, "model": model},
                "execution": {
                    "argv": effect["argv"],
                    "workingDirectory": str(task),
                    "sandboxProfile": record_sandbox,
                    "approvalPolicy": "never",
                    "platformSandbox": platform_sandbox,
                    "environmentKeys": sorted(sanitized_env(Path("/run/codex-home"), extra_env).keys()),
                    "startedAt": started_at,
                    "finishedAt": finished_at,
                    "status": "INTERRUPTED",
                    "exitCode": exit_code,
                },
            }
            try:
                atomic_json(invocation_path, emergency_invocation)
                run(
                    [str(root / "bin/agent-task.sh"), "--project-root", str(root), "record-invocation", task_id, "--effect", str(effect_path), "--record", str(invocation_path)],
                    cwd=root,
                    timeout=60,
                )
            except Exception:
                pass
        raise
    finally:
        shutil.rmtree(private_home, ignore_errors=True)


def invoke(
    root: Path,
    bwrap: Path,
    codex: Path,
    task_id: str,
    prompt_file: Path,
    model: str,
    change_bundle: Path | None = None,
    *,
    active_timeout_seconds: int = 21600,
    no_progress_timeout_seconds: int | None = None,
) -> dict[str, Any]:
    return invoke_process(
        root,
        bwrap,
        codex,
        task_id,
        prompt_file,
        model,
        change_bundle,
        active_timeout_seconds=active_timeout_seconds,
        no_progress_timeout_seconds=no_progress_timeout_seconds,
        process_binding={"owner": "foreground-compatibility", "runId": None, "singletonKey": None},
    )


def durable_request_identity(
    *,
    task_id: str,
    base_commit: str,
    model: str,
    prompt_sha256: str,
    change_bundle: Path | None,
    change_bundle_sha256: str | None,
    bwrap: Path,
    codex: Path,
    active_timeout_seconds: int,
    no_progress_timeout_seconds: int | None,
) -> dict[str, Any]:
    return {
        "taskId": task_id,
        "baseCommit": base_commit,
        "model": model,
        "promptSha256": prompt_sha256,
        "changeBundlePath": str(change_bundle) if change_bundle is not None else None,
        "changeBundleSha256": change_bundle_sha256,
        "bwrapPath": str(bwrap),
        "bwrapSha256": sha256_file(bwrap),
        "codexPath": str(codex),
        "codexSha256": sha256_file(codex),
        "activeTimeoutSeconds": active_timeout_seconds,
        "noProgressTimeoutSeconds": no_progress_timeout_seconds,
    }


def invoke_start(
    root: Path,
    bwrap: Path,
    codex: Path,
    task_id: str,
    prompt_file: Path,
    model: str,
    change_bundle: Path | None = None,
    *,
    active_timeout_seconds: int = 21600,
    no_progress_timeout_seconds: int | None = None,
) -> dict[str, Any]:
    require(1 <= active_timeout_seconds <= 86400, "ACTIVE_TIMEOUT_INVALID", "Active-time budget must be between 1 and 86400 seconds", activeTimeoutSeconds=active_timeout_seconds)
    require(no_progress_timeout_seconds is None or 1 <= no_progress_timeout_seconds <= 86400, "NO_PROGRESS_TIMEOUT_INVALID", "No-progress budget must be between 1 and 86400 seconds when enabled", noProgressTimeoutSeconds=no_progress_timeout_seconds)
    ctx, _, task_contract, _, _, _, _, _, _ = invocation_preflight(
        root,
        task_id,
        prompt_file,
        model,
        change_bundle,
        allowed_invocation_states={"NOT_RECORDED", "STARTED", "RECORDED"},
    )
    base_commit = str(task_contract["baseCommit"])
    evidence_dir = invocation_evidence_dir(ctx, task_id, base_commit)
    evidence_dir.mkdir(parents=True, mode=0o700, exist_ok=True)
    require(evidence_dir.is_dir() and not evidence_dir.is_symlink(), "EVIDENCE_DIRECTORY_INVALID", "Invocation evidence directory is unsafe", path=str(evidence_dir))
    lock_path = evidence_dir / ".invoke-start.lock"
    with lock_path.open("a+b") as lock_handle:
        fcntl.flock(lock_handle.fileno(), fcntl.LOCK_EX)
        prompt_copy = evidence_dir / "invocation-prompt.txt"
        request_path = evidence_dir / "invocation-request.json"
        binding_path = evidence_dir / "process-run-binding.json"
        durable_run_path = evidence_dir / "durable-run.json"
        prompt_sha = sha256_file(prompt_file)
        bundle_path = change_bundle.expanduser().resolve() if change_bundle is not None else None
        bundle_sha = sha256_file(bundle_path) if bundle_path is not None else None
        identity = durable_request_identity(
            task_id=task_id,
            base_commit=base_commit,
            model=model,
            prompt_sha256=prompt_sha,
            change_bundle=bundle_path,
            change_bundle_sha256=bundle_sha,
            bwrap=bwrap,
            codex=codex,
            active_timeout_seconds=active_timeout_seconds,
            no_progress_timeout_seconds=no_progress_timeout_seconds,
        )
        request_sha = sha256_bytes(json.dumps(identity, sort_keys=True, separators=(",", ":")).encode("utf-8"))
        if request_path.exists():
            existing = load_json(request_path)
            require(existing.get("requestSha256") == request_sha and existing.get("identity") == identity, "DURABLE_INVOCATION_REQUEST_MISMATCH", "Existing durable invocation request differs from this start request", taskId=task_id)
            require(prompt_copy.is_file() and sha256_file(prompt_copy) == prompt_sha, "DURABLE_PROMPT_MISMATCH", "Persisted durable prompt differs from the requested prompt", taskId=task_id)
        else:
            require(not any(path.exists() for path in (binding_path, durable_run_path, evidence_dir / "codex-invocation-start.json", evidence_dir / "codex-invocation.json")), "DURABLE_EVIDENCE_ORPHANED", "Durable evidence exists without an immutable invocation request", taskId=task_id)
            shutil.copyfile(prompt_file, prompt_copy)
            prompt_copy.chmod(0o600)
            atomic_json(request_path, {"schemaVersion": "springmaster.codex-durable-invocation-request.v1", "requestSha256": request_sha, "identity": identity, "promptPath": str(prompt_copy), "createdAt": utc_now()})
        singleton_key = f"codex-task-{task_id.lower()}"
        worker_command = [
            str(root / "bin/codex-host-sandbox.sh"),
            "--project-root", str(root),
            "--bwrap", str(bwrap),
            "--codex", str(codex),
            "--format", "json",
            "invoke-worker",
            "--request", str(request_path),
            "--binding", str(binding_path),
            "--out", str(evidence_dir / "host-invocation.json"),
        ]
        process_ops = run(
            [
                str(root / "bin/process-ops.sh"), "--format", "json", "run-start",
                "--name", "codex-invocation",
                "--cwd", str(root),
                "--singleton-key", singleton_key,
                "--", *worker_command,
            ],
            cwd=root,
            timeout=60,
        )
        require(process_ops.returncode == 0, "DURABLE_WORKER_START_FAILED", "process-ops rejected the durable Codex worker", stdout=process_ops.stdout[-4000:], stderr=process_ops.stderr[-4000:])
        try:
            process_value = json.loads(process_ops.stdout)
        except json.JSONDecodeError as exc:
            raise HostError("DURABLE_WORKER_START_INVALID", "process-ops returned invalid JSON", stdout=process_ops.stdout[-4000:]) from exc
        run_id = process_value.get("runId")
        require(isinstance(run_id, str) and run_id.strip(), "DURABLE_WORKER_RUN_ID_MISSING", "process-ops did not return a persistent run ID", payload=process_value)
        binding = {
            "schemaVersion": "springmaster.codex-process-run-binding.v1",
            "taskId": task_id,
            "requestSha256": request_sha,
            "owner": "process-ops-crun",
            "runId": run_id,
            "singletonKey": singleton_key,
            "startDisposition": process_value.get("startDisposition"),
            "boundAt": utc_now(),
        }
        if binding_path.exists():
            existing_binding = load_json(binding_path)
            require(existing_binding.get("requestSha256") == request_sha and existing_binding.get("runId") == run_id and existing_binding.get("singletonKey") == singleton_key, "DURABLE_RUN_BINDING_MISMATCH", "Existing durable run binding differs from the canonical singleton run", existing=existing_binding, current=binding)
        else:
            atomic_json(binding_path, binding)
        durable = {
            "schemaVersion": "springmaster.codex-durable-run.v1",
            "taskId": task_id,
            "baseCommit": base_commit,
            "requestSha256": request_sha,
            "runId": run_id,
            "singletonKey": singleton_key,
            "startDisposition": process_value.get("startDisposition"),
            "processStatus": process_value.get("status"),
            "processPhase": process_value.get("phase"),
            "evidenceDirectory": str(evidence_dir),
            "resultPath": str(evidence_dir / "host-invocation.json"),
            "bindingPath": str(binding_path),
            "updatedAt": utc_now(),
        }
        atomic_json(durable_run_path, durable)
        return {
            "schemaVersion": REPORT_SCHEMA,
            "operation": "invoke-start",
            "status": "RUNNING" if process_value.get("startDisposition") in {"STARTED", "RESTARTED", "REUSED_ACTIVE"} else "TERMINAL",
            "generatedAt": utc_now(),
            "hostId": host_id(),
            "baselineCommit": base_commit,
            "taskId": task_id,
            "runId": run_id,
            "singletonKey": singleton_key,
            "startDisposition": process_value.get("startDisposition"),
            "processStatus": process_value.get("status"),
            "evidenceDirectory": str(evidence_dir),
            "resultPath": str(evidence_dir / "host-invocation.json"),
            "durableRunPath": str(durable_run_path),
        }


def wait_for_binding(binding_path: Path, request_sha: str, *, timeout_seconds: float = 120.0) -> dict[str, Any]:
    started = time.monotonic()
    while True:
        if binding_path.is_file():
            binding = load_json(binding_path)
            require(binding.get("requestSha256") == request_sha, "DURABLE_RUN_BINDING_MISMATCH", "Durable run binding does not match invocation request")
            require(binding.get("owner") == "process-ops-crun" and isinstance(binding.get("runId"), str) and binding.get("runId"), "DURABLE_RUN_BINDING_INVALID", "Durable run binding is incomplete")
            return binding
        if time.monotonic() - started >= timeout_seconds:
            raise HostError("DURABLE_RUN_BINDING_TIMEOUT", "Durable worker did not receive its canonical process run binding before the start barrier expired", path=str(binding_path))
        time.sleep(0.2)


def invoke_worker(root: Path, request_path: Path, binding_path: Path) -> dict[str, Any]:
    request = load_json(request_path)
    require(request.get("schemaVersion") == "springmaster.codex-durable-invocation-request.v1", "DURABLE_REQUEST_INVALID", "Durable invocation request schema is invalid")
    identity = request.get("identity")
    require(isinstance(identity, dict), "DURABLE_REQUEST_INVALID", "Durable invocation request identity is missing")
    request_sha = sha256_bytes(json.dumps(identity, sort_keys=True, separators=(",", ":")).encode("utf-8"))
    require(request.get("requestSha256") == request_sha, "DURABLE_REQUEST_HASH_MISMATCH", "Durable invocation request hash is invalid")
    prompt_path = Path(str(request.get("promptPath", ""))).resolve()
    require(prompt_path.is_file() and not prompt_path.is_symlink() and sha256_file(prompt_path) == identity.get("promptSha256"), "DURABLE_PROMPT_INVALID", "Persisted durable prompt is missing or changed")
    change_bundle_raw = identity.get("changeBundlePath")
    change_bundle = Path(change_bundle_raw).resolve() if isinstance(change_bundle_raw, str) and change_bundle_raw else None
    if change_bundle is not None:
        require(change_bundle.is_file() and not change_bundle.is_symlink() and sha256_file(change_bundle) == identity.get("changeBundleSha256"), "DURABLE_CHANGE_BUNDLE_INVALID", "Durable change bundle is missing or changed")
    bwrap = Path(str(identity.get("bwrapPath", ""))).resolve()
    codex = Path(str(identity.get("codexPath", ""))).resolve()
    require(bwrap.is_file() and sha256_file(bwrap) == identity.get("bwrapSha256"), "DURABLE_BWRAP_CHANGED", "Bound bubblewrap executable changed before worker start")
    require(codex.is_file() and sha256_file(codex) == identity.get("codexSha256"), "DURABLE_CODEX_CHANGED", "Bound Codex executable changed before worker start")
    binding = wait_for_binding(binding_path, request_sha)
    evidence_dir = request_path.parent.resolve()
    return invoke_process(
        root,
        bwrap,
        codex,
        str(identity["taskId"]),
        prompt_path,
        str(identity["model"]),
        change_bundle,
        active_timeout_seconds=int(identity["activeTimeoutSeconds"]),
        no_progress_timeout_seconds=identity.get("noProgressTimeoutSeconds"),
        process_binding=binding,
        evidence_dir=evidence_dir,
    )


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
    inspect_form = inspect_value.get("codexSandboxCommandForm")
    probe_form = probe_value.get("codexSandboxCommandForm")
    if inspect_form not in set(contract.get("securityBoundary", {}).get("supportedInnerSandboxCommandForms", [])):
        findings.append({"code": "CODEX_SANDBOX_COMMAND_FORM_NOT_BOUND", "evidence": "inspect", "commandForm": inspect_form})
    if probe_form != inspect_form:
        findings.append({"code": "CODEX_SANDBOX_COMMAND_FORM_MISMATCH", "inspect": inspect_form, "probe": probe_form})
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
        "codexSandboxCommandForm": inspect_form,
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
    v = sub.add_parser("invoke"); v.add_argument("--task-id", required=True); v.add_argument("--prompt", required=True, type=Path); v.add_argument("--model", required=True); v.add_argument("--change-bundle", type=Path); v.add_argument("--active-timeout-seconds", type=int, default=21600); v.add_argument("--no-progress-timeout-seconds", type=int); v.add_argument("--out", type=Path)
    vs = sub.add_parser("invoke-start"); vs.add_argument("--task-id", required=True); vs.add_argument("--prompt", required=True, type=Path); vs.add_argument("--model", required=True); vs.add_argument("--change-bundle", type=Path); vs.add_argument("--active-timeout-seconds", type=int, default=21600); vs.add_argument("--no-progress-timeout-seconds", type=int); vs.add_argument("--out", type=Path)
    vw = sub.add_parser("invoke-worker"); vw.add_argument("--request", required=True, type=Path); vw.add_argument("--binding", required=True, type=Path); vw.add_argument("--out", type=Path)
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
        elif args.command == "invoke": report = invoke(root, bwrap, codex, args.task_id, args.prompt.resolve(), args.model, args.change_bundle, active_timeout_seconds=args.active_timeout_seconds, no_progress_timeout_seconds=args.no_progress_timeout_seconds)
        elif args.command == "invoke-start": report = invoke_start(root, bwrap, codex, args.task_id, args.prompt.resolve(), args.model, args.change_bundle, active_timeout_seconds=args.active_timeout_seconds, no_progress_timeout_seconds=args.no_progress_timeout_seconds)
        elif args.command == "invoke-worker": report = invoke_worker(root, args.request.resolve(), args.binding.resolve())
        else: report = qualify(root, args.inspect.resolve(), args.probe.resolve(), args.analysis_invocation.resolve())
        if getattr(args, "out", None): atomic_json(args.out, report)
        sys.stdout.write(render(report, args.format))
        if args.command == "qualify" and args.check and report["status"] != "PASS": return 1
        return 0 if report.get("status") in {"PASS", "RUNNING", "TERMINAL"} else 1
    except HostError as exc:
        report = {"schemaVersion": REPORT_SCHEMA, "status": "TOOL_ERROR", "errorCode": exc.code, "message": exc.message, "details": exc.details, "writableCodexAuthorized": False, "pilotWriteReady": False}
        if getattr(args, "out", None): atomic_json(args.out, report)
        sys.stdout.write(render(report, args.format))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
