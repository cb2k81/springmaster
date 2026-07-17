#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import re
import shlex
import shutil
import stat
import subprocess
import sys
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path

USAGE = """Usage:
  ./bin/patch.sh artifact-preflight <patch.zip> [--output <dir>] [--no-export] [--keep-test-copy] [--engine <patch.py>]

The command is non-mutating for the live repository. It requires a clean Git
working tree, validates the complete live baseline and payload hygiene, then
applies the patch in an isolated Git worktree. By default the isolated copy
also creates and verifies one full ZIP export.
"""

MISSING_MARKERS = {"", "-", "missing", "absent", "none", "null", "not-exists", "not_exists"}
ALLOWED_ROOTS = ("files/", "delete/", "logs/")
BASE_SCOPE_LOG_DIRS = {
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


class PreflightError(RuntimeError):
    pass


def fail(message: str, code: int = 1) -> None:
    raise PreflightError(message)


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat()


def timestamp() -> str:
    return datetime.now(timezone.utc).astimezone().strftime("%Y%m%d_%H%M%S")


def allocate_output_directory(
    project_root: Path, configured_output: str | None, patch_id: str
) -> Path:
    if configured_output:
        output_dir = Path(configured_output).expanduser()
        if not output_dir.is_absolute():
            output_dir = project_root / output_dir
        output_dir = output_dir.resolve()
        output_dir.mkdir(parents=True, exist_ok=False)
        return output_dir

    output_parent = (project_root / "build" / "patch-artifact-preflight").resolve()
    output_parent.mkdir(parents=True, exist_ok=True)
    return Path(
        tempfile.mkdtemp(
            prefix=f"{timestamp()}_{patch_id}_",
            dir=str(output_parent),
        )
    ).resolve()


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


def validate_relpath(value: object) -> str:
    if not isinstance(value, str) or not value.strip():
        fail(f"PATCH_ARTIFACT_PATH_INVALID: invalid empty path {value!r}")
    normalized = value.replace("\\", "/")
    while normalized.startswith("./"):
        normalized = normalized[2:]
    if normalized.startswith(("/", "~")):
        fail(f"PATCH_ARTIFACT_PATH_INVALID: absolute path is forbidden: {value}")
    parts = [part for part in normalized.split("/") if part]
    if not parts or any(part == ".." for part in parts):
        fail(f"PATCH_ARTIFACT_PATH_INVALID: unsafe path: {value}")
    return "/".join(parts)


def read_json_bytes(data: bytes, label: str) -> dict:
    try:
        value = json.loads(data.decode("utf-8"))
    except Exception as exc:
        fail(f"PATCH_ARTIFACT_JSON_INVALID: cannot read {label}: {exc}")
    if not isinstance(value, dict):
        fail(f"PATCH_ARTIFACT_JSON_INVALID: {label} must contain a JSON object")
    return value


def normalize_expected(value: object, path: str) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        normalized = value.strip()
        if normalized.lower() in MISSING_MARKERS:
            return None
        if re.fullmatch(r"[A-Fa-f0-9]{64}", normalized):
            return normalized.lower()
    fail(
        "PATCH_ARTIFACT_BASELINE_INVALID: "
        f"expectedBeforeSha256 for {path} must be a SHA-256 or null/missing, got {value!r}"
    )


def expected_map(manifest: dict) -> dict[str, str | None]:
    raw = None
    baseline = manifest.get("baseline")
    if isinstance(baseline, dict):
        raw = baseline.get("expectedBeforeSha256")
        if raw is None:
            raw = baseline.get("expectedBefore")
    if raw is None:
        raw = manifest.get("expectedBeforeSha256")
    if raw is None:
        raw = manifest.get("expectedBefore")
    if raw is None:
        fail("PATCH_ARTIFACT_BASELINE_MISSING: manifest baseline preconditions are required")
    result: dict[str, str | None] = {}
    if isinstance(raw, dict):
        for raw_path, value in raw.items():
            path = validate_relpath(raw_path)
            result[path] = normalize_expected(value, path)
        return result
    if isinstance(raw, list):
        for item in raw:
            if not isinstance(item, dict) or "path" not in item:
                fail("PATCH_ARTIFACT_BASELINE_INVALID: baseline.expectedBefore entries require a path")
            path = validate_relpath(item["path"])
            if "sha256" in item:
                value = item.get("sha256")
            elif "sha256Before" in item:
                value = item.get("sha256Before")
            elif "expectedBeforeSha256" in item:
                value = item.get("expectedBeforeSha256")
            elif item.get("exists") is False:
                value = None
            else:
                fail(f"PATCH_ARTIFACT_BASELINE_INVALID: missing hash/exists=false for {path}")
            result[path] = normalize_expected(value, path)
        return result
    fail("PATCH_ARTIFACT_BASELINE_INVALID: baseline preconditions must be an object or list")


def parse_patch(
    zip_path: Path,
    extract_root: Path,
    project_root: Path,
) -> tuple[dict, list[dict], dict[str, bytes], dict[str, int]]:
    try:
        with zipfile.ZipFile(zip_path, "r") as archive:
            bad = archive.testzip()
            if bad:
                fail(f"PATCH_ARTIFACT_ZIP_INVALID: CRC failure in {bad}")
            names = archive.namelist()
            if "manifest.json" not in names:
                fail("PATCH_ARTIFACT_MANIFEST_MISSING: manifest.json is required")
            if len(names) != len(set(names)):
                fail("PATCH_ARTIFACT_ZIP_INVALID: duplicate ZIP entries are forbidden")
            for name in names:
                validate_relpath(name.rstrip("/"))
                if name.endswith("/"):
                    continue
                if name != "manifest.json" and not name.startswith(ALLOWED_ROOTS):
                    fail(f"PATCH_ARTIFACT_ZIP_ROOT_INVALID: unsupported ZIP entry {name}")
            archive.extractall(extract_root)
            manifest = read_json_bytes(archive.read("manifest.json"), "manifest.json")
            payload = {name: archive.read(name) for name in names if not name.endswith("/")}
            payload_modes = {
                info.filename: info.external_attr >> 16
                for info in archive.infolist()
                if not info.is_dir()
            }
    except zipfile.BadZipFile as exc:
        fail(f"PATCH_ARTIFACT_ZIP_INVALID: {exc}")

    patch_id = manifest.get("patchId")
    legacy_id = manifest.get("id")
    name = manifest.get("name")
    scope = manifest.get("scope")
    if not all(isinstance(value, str) and value.strip() for value in (patch_id, legacy_id, name, scope)):
        fail("PATCH_ARTIFACT_IDENTITY_INVALID: id, patchId, name and scope are required non-empty strings")
    if patch_id != legacy_id:
        fail("PATCH_ARTIFACT_IDENTITY_INVALID: manifest.id and manifest.patchId differ")
    expected_id = f"{patch_id.split('_', 1)[0]}_{name}"
    if not re.fullmatch(r"\d{6}_[A-Za-z0-9][A-Za-z0-9._-]*", patch_id) or expected_id != patch_id:
        fail("PATCH_ARTIFACT_IDENTITY_INVALID: patchId must be <six digits>_<name>")
    if zip_path.stem != patch_id:
        fail(
            "PATCH_ARTIFACT_IDENTITY_INVALID: archive filename must equal manifest.patchId "
            f"({zip_path.name} != {patch_id}.zip)"
        )

    scope_log_dir = BASE_SCOPE_LOG_DIRS.get(scope)
    if scope_log_dir is None:
        env = project_environment(project_root)
        env_name = re.sub(r"[^A-Za-z0-9]", "_", scope).upper()
        configured = env.get(f"PATCH_SCOPE_{env_name}_LOG_DIR")
        local_scopes = {
            item.strip()
            for item in re.split(r"[;,\s]+", env.get("PATCH_LOCAL_SCOPES", ""))
            if item.strip()
        }
        if scope not in local_scopes and configured is None:
            fail(f"PATCH_ARTIFACT_SCOPE_UNKNOWN: {scope}")
        scope_log_dir = validate_relpath(configured or scope)

    operations: list[dict] = []
    changelogs = 0
    for entry in sorted(payload):
        if entry == "manifest.json":
            continue
        if entry.startswith("files/"):
            operations.append({"type": "file", "source": entry, "target": validate_relpath(entry[6:])})
        elif entry.startswith("delete/"):
            operations.append({"type": "delete", "source": entry, "target": validate_relpath(entry[7:])})
        elif entry.startswith("logs/"):
            filename = Path(entry).name
            if not re.fullmatch(r"CHANGELOG-[A-Za-z0-9._-]+\.md", filename):
                fail(f"PATCH_ARTIFACT_CHANGELOG_INVALID: invalid changelog name {entry}")
            operations.append(
                {
                    "type": "file",
                    "source": entry,
                    "target": f"patches/logs/{scope_log_dir}/{filename}",
                }
            )
            changelogs += 1
    if not operations:
        fail("PATCH_ARTIFACT_EMPTY: patch contains no operations")
    if changelogs == 0:
        fail("PATCH_ARTIFACT_CHANGELOG_MISSING: logs/CHANGELOG-*.md is required")
    targets = [operation["target"] for operation in operations]
    if len(targets) != len(set(targets)):
        fail("PATCH_ARTIFACT_DUPLICATE_TARGET: multiple operations address the same target")
    return manifest, operations, payload, payload_modes


def validate_payload_hygiene(operations: list[dict], payload: dict[str, bytes]) -> dict:
    checked = 0
    binary = 0
    findings: list[str] = []
    for operation in operations:
        if operation["type"] != "file":
            continue
        source = operation["source"]
        data = payload[source]
        if b"\x00" in data:
            binary += 1
            continue
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            binary += 1
            continue
        checked += 1
        if b"\r" in data:
            findings.append(f"PATCH_PAYLOAD_CRLF_FORBIDDEN: {source}")
        if data and not data.endswith(b"\n"):
            findings.append(f"PATCH_PAYLOAD_FINAL_NEWLINE_MISSING: {source}")
        if data.endswith(b"\n\n"):
            findings.append(f"PATCH_PAYLOAD_EOF_BLANK_LINE: {source}")
        for line_number, line in enumerate(text.splitlines(), start=1):
            if line.endswith((" ", "\t")):
                findings.append(f"PATCH_PAYLOAD_TRAILING_WHITESPACE: {source}:{line_number}")
    if findings:
        fail("PATCH_PAYLOAD_HYGIENE_FAILED:\n  " + "\n  ".join(findings))
    return {"textFilesChecked": checked, "binaryFilesSkipped": binary}


def parse_env_file(path: Path, env: dict[str, str]) -> None:
    if not path.is_file():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:].strip()
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", key):
            continue
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
            value = value[1:-1]
        env[key] = value


def project_environment(root: Path) -> dict[str, str]:
    env: dict[str, str] = {}
    parse_env_file(root / ".env.example", env)
    parse_env_file(root / ".env", env)
    env.update(os.environ)
    return env


def run_logged(
    command: list[str] | str,
    cwd: Path,
    log_path: Path,
    *,
    env: dict[str, str] | None = None,
    shell: bool = False,
) -> subprocess.CompletedProcess[str]:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    display = command if isinstance(command, str) else " ".join(shlex.quote(part) for part in command)
    result = subprocess.run(
        command,
        cwd=cwd,
        env=env,
        shell=shell,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    log_path.write_text(f"$ {display}\n\n{result.stdout or ''}rc={result.returncode}\n", encoding="utf-8")
    return result


def require_success(result: subprocess.CompletedProcess[str], code: str, log_path: Path) -> None:
    if result.returncode != 0:
        fail(f"{code}: command failed with rc={result.returncode}; see {log_path}")


def git_output(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=root,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    if result.returncode != 0:
        fail(f"PATCH_ARTIFACT_GIT_REQUIRED: git {' '.join(args)} failed: {result.stdout.strip()}")
    return result.stdout.strip()


def require_clean_git(root: Path) -> str:
    status = git_output(root, "status", "--porcelain=v1", "--untracked-files=all")
    if status:
        fail("PATCH_ARTIFACT_WORKTREE_DIRTY: artifact preflight requires a clean Git working tree\n" + status)
    return git_output(root, "rev-parse", "HEAD")


def validate_live_hashes(root: Path, manifest: dict, operations: list[dict]) -> dict:
    expected = expected_map(manifest)
    targets = {operation["target"] for operation in operations}
    unsupported = sorted(set(expected) - targets)
    missing = sorted(targets - set(expected))
    if unsupported:
        fail("PATCH_ARTIFACT_BASELINE_UNSUPPORTED: hashes without operation:\n  " + "\n  ".join(unsupported))
    if missing:
        fail("PATCH_ARTIFACT_BASELINE_INCOMPLETE: operations without hash:\n  " + "\n  ".join(missing))
    mismatches: list[str] = []
    for path in sorted(targets):
        actual = sha256_file(root / path)
        if actual != expected[path]:
            mismatches.extend(
                [
                    path,
                    f"    expectedBeforeSha256: {expected[path] or '<missing>'}",
                    f"    actualSha256:         {actual or '<missing>'}",
                ]
            )
    if mismatches:
        fail("PATCH_ARTIFACT_LIVE_BASELINE_MISMATCH:\n  " + "\n  ".join(mismatches))
    return {"operationCount": len(targets), "hashCount": len(expected)}


def classify_live_operations(
    root: Path,
    operations: list[dict],
    payload: dict[str, bytes],
    payload_modes: dict[str, int],
) -> dict:
    summary = {"new": 0, "modified": 0, "deleted": 0, "unchanged": 0, "deleteMissing": 0}
    redundant: list[str] = []
    for operation in operations:
        target = root / operation["target"]
        if operation["type"] == "delete":
            if target.is_file():
                summary["deleted"] += 1
            else:
                summary["deleteMissing"] += 1
                redundant.append(f"delete target missing: {operation['target']}")
            continue
        if not target.exists():
            summary["new"] += 1
        elif target.is_file():
            bytes_equal = sha256_file(target) == sha256_bytes(payload[operation["source"]])
            declared_mode = stat.S_IMODE(payload_modes.get(operation["source"], 0))
            expected_executable = bool(declared_mode & 0o111)
            actual_executable = bool(stat.S_IMODE(target.stat().st_mode) & 0o111)
            if bytes_equal and expected_executable == actual_executable:
                summary["unchanged"] += 1
                redundant.append(f"unchanged payload: {operation['target']}")
            else:
                summary["modified"] += 1
        else:
            summary["modified"] += 1
    if redundant:
        fail("PATCH_ARTIFACT_REDUNDANT_OPERATION:\n  " + "\n  ".join(redundant))
    return summary


def changed_paths(root: Path) -> set[str]:
    tracked = git_output(root, "diff", "--name-only", "--no-renames", "HEAD")
    untracked = git_output(root, "ls-files", "--others", "--exclude-standard")
    return {line for line in (tracked + "\n" + untracked).splitlines() if line}


def verify_applied_payload(
    root: Path,
    operations: list[dict],
    payload: dict[str, bytes],
    payload_modes: dict[str, int],
) -> dict:
    mismatches: list[str] = []
    for operation in operations:
        target = root / operation["target"]
        if operation["type"] == "delete":
            if target.exists():
                mismatches.append(f"delete target still exists: {operation['target']}")
        else:
            expected = sha256_bytes(payload[operation["source"]])
            actual = sha256_file(target)
            if actual != expected:
                mismatches.append(
                    f"payload mismatch: {operation['target']} expected={expected} actual={actual or '<missing>'}"
                )
            declared_mode = stat.S_IMODE(payload_modes.get(operation["source"], 0))
            actual_mode = stat.S_IMODE(target.stat().st_mode) if target.is_file() else 0
            expected_executable = bool(declared_mode & 0o111)
            actual_executable = bool(actual_mode & 0o111)
            if actual_executable != expected_executable:
                expected_git_mode = "100755" if expected_executable else "100644"
                actual_git_mode = "100755" if actual_executable else "100644"
                mismatches.append(
                    f"payload Git mode mismatch: {operation['target']} "
                    f"expected={expected_git_mode} actual={actual_git_mode} "
                    f"filesystemMode={oct(actual_mode)}"
                )
    if mismatches:
        fail("PATCH_ARTIFACT_APPLIED_PAYLOAD_MISMATCH:\n  " + "\n  ".join(mismatches))
    expected_paths = {operation["target"] for operation in operations}
    actual_paths = changed_paths(root)
    if actual_paths != expected_paths:
        unexpected = sorted(actual_paths - expected_paths)
        missing = sorted(expected_paths - actual_paths)
        lines = []
        if unexpected:
            lines.append("unexpected changed paths:\n    " + "\n    ".join(unexpected))
        if missing:
            lines.append("expected changed paths missing:\n    " + "\n    ".join(missing))
        fail("PATCH_ARTIFACT_TESTCOPY_SCOPE_MISMATCH:\n  " + "\n  ".join(lines))
    return {"expectedChangedPaths": len(expected_paths), "actualChangedPaths": len(actual_paths)}


def resolve_export_path(root: Path, output: str) -> Path:
    lines = [line.strip() for line in output.splitlines() if line.strip()]
    for line in reversed(lines):
        candidate = Path(line)
        if not candidate.is_absolute():
            candidate = root / candidate
        if candidate.is_file() and candidate.suffix.lower() == ".zip":
            return candidate.resolve()
    fail("PATCH_ARTIFACT_EXPORT_PATH_MISSING: export command did not print an existing ZIP path")


def write_report(path: Path, report: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def parse_args(args: list[str]) -> dict:
    if not args or args[0] in {"help", "--help", "-h"}:
        print(USAGE)
        raise SystemExit(0)
    subject = None
    output = None
    run_export = True
    keep_test_copy = False
    engine = None
    i = 0
    while i < len(args):
        arg = args[i]
        if arg == "--output":
            if i + 1 >= len(args):
                fail("PATCH_ARTIFACT_ARGUMENT_INVALID: --output requires a path")
            output = args[i + 1]
            i += 2
        elif arg == "--no-export":
            run_export = False
            i += 1
        elif arg == "--export":
            run_export = True
            i += 1
        elif arg == "--keep-test-copy":
            keep_test_copy = True
            i += 1
        elif arg == "--engine":
            if i + 1 >= len(args):
                fail("PATCH_ARTIFACT_ARGUMENT_INVALID: --engine requires a path")
            engine = args[i + 1]
            i += 2
        elif arg.startswith("--"):
            fail(f"PATCH_ARTIFACT_ARGUMENT_INVALID: unknown option {arg}")
        elif subject is None:
            subject = arg
            i += 1
        else:
            fail("PATCH_ARTIFACT_ARGUMENT_INVALID: expected exactly one patch ZIP")
    if subject is None:
        fail("PATCH_ARTIFACT_ARGUMENT_INVALID: patch ZIP is required")
    return {
        "subject": subject,
        "output": output,
        "runExport": run_export,
        "keepTestCopy": keep_test_copy,
        "engine": engine,
    }


def main() -> None:
    if len(sys.argv) < 3:
        print(USAGE, file=sys.stderr)
        raise SystemExit(2)
    project_root = Path(sys.argv[1]).resolve()
    options = parse_args(sys.argv[2:])
    zip_path = Path(options["subject"]).expanduser().resolve()
    if not zip_path.is_file():
        fail(f"PATCH_ARTIFACT_ZIP_MISSING: {zip_path}")

    extract_parent = Path(tempfile.mkdtemp(prefix="springmaster-artifact-extract-"))
    extract_root = extract_parent / "patch"
    extract_root.mkdir()
    test_parent: Path | None = None
    test_root: Path | None = None
    worktree_added = False
    output_dir: Path | None = None
    report: dict = {
        "schemaVersion": "springmaster.patch-artifact-preflight.v1",
        "status": "RUNNING",
        "startedAt": now_iso(),
        "projectRoot": str(project_root),
        "sourcePatch": str(zip_path),
        "sourcePatchSha256": sha256_file(zip_path),
        "checks": {},
    }

    try:
        manifest, operations, payload, payload_modes = parse_patch(zip_path, extract_root, project_root)
        patch_id = manifest["patchId"]
        output_dir = allocate_output_directory(
            project_root, options["output"], patch_id
        )
        report["patchId"] = patch_id
        report["scope"] = manifest["scope"]
        report["outputDirectory"] = str(output_dir)
        report["checks"]["zipAndIdentity"] = "PASS"

        report["checks"]["payloadHygiene"] = validate_payload_hygiene(operations, payload)
        head = require_clean_git(project_root)
        report["sourceGitHead"] = head
        report["checks"]["cleanGitBaseline"] = "PASS"
        report["checks"]["liveBaseline"] = validate_live_hashes(project_root, manifest, operations)
        report["checks"]["operationEffect"] = classify_live_operations(
            project_root, operations, payload, payload_modes
        )

        engine = (
            Path(options["engine"]).expanduser().resolve()
            if options.get("engine")
            else project_root / "bin" / "patch.py"
        )
        if not engine.is_file():
            fail(f"PATCH_ARTIFACT_ENGINE_MISSING: {engine}")
        report["engine"] = str(engine)
        live_result = run_logged(
            [sys.executable, str(engine), str(project_root), "live-baseline", str(zip_path)],
            project_root,
            output_dir / "01_live_baseline.log",
        )
        require_success(live_result, "PATCH_ARTIFACT_LIVE_BASELINE_FAILED", output_dir / "01_live_baseline.log")
        dry_result = run_logged(
            [sys.executable, str(engine), str(project_root), "apply", "--dry-run", str(zip_path)],
            project_root,
            output_dir / "02_live_dry_run.log",
        )
        require_success(dry_result, "PATCH_ARTIFACT_LIVE_DRY_RUN_FAILED", output_dir / "02_live_dry_run.log")
        report["checks"]["liveEnginePreflight"] = "PASS"

        test_parent = Path(tempfile.mkdtemp(prefix=f"springmaster-artifact-{patch_id}-"))
        test_root = test_parent / "repository"
        worktree_result = run_logged(
            ["git", "worktree", "add", "--detach", str(test_root), head],
            project_root,
            output_dir / "03_worktree_add.log",
        )
        require_success(worktree_result, "PATCH_ARTIFACT_TESTCOPY_CREATE_FAILED", output_dir / "03_worktree_add.log")
        worktree_added = True
        if (project_root / ".env").is_file():
            shutil.copy2(project_root / ".env", test_root / ".env")

        test_engine = engine if options.get("engine") else test_root / "bin" / "patch.py"
        steps = [
            ("04_testcopy_live_baseline.log", [sys.executable, str(test_engine), str(test_root), "live-baseline", str(zip_path)]),
            ("05_testcopy_dry_run.log", [sys.executable, str(test_engine), str(test_root), "apply", "--dry-run", str(zip_path)]),
            ("06_testcopy_apply.log", [sys.executable, str(test_engine), str(test_root), "apply", str(zip_path)]),
            ("07_testcopy_show_latest.log", [sys.executable, str(test_engine), str(test_root), "show", "latest"]),
        ]
        for log_name, command in steps:
            result = run_logged(command, test_root, output_dir / log_name)
            require_success(result, "PATCH_ARTIFACT_TESTCOPY_PATCH_FAILED", output_dir / log_name)
        show_output = (output_dir / "07_testcopy_show_latest.log").read_text(encoding="utf-8")
        if f"Patch-ID:      {patch_id}" not in show_output or "Status:        applied" not in show_output:
            fail("PATCH_ARTIFACT_TESTCOPY_LATEST_MISMATCH: applied patch is not latest/applied")

        report["checks"]["testCopyPayload"] = verify_applied_payload(
            test_root,
            operations,
            payload,
            payload_modes,
        )
        diff_result = run_logged(
            ["git", "diff", "--check"],
            test_root,
            output_dir / "08_testcopy_diff_check.log",
        )
        require_success(diff_result, "PATCH_ARTIFACT_TESTCOPY_DIFF_CHECK_FAILED", output_dir / "08_testcopy_diff_check.log")
        report["checks"]["testCopyApplyAndDiff"] = "PASS"

        if options["runExport"]:
            evidence_dir = test_root / "patches" / "logs" / "validation" / f"artifact-preflight-{patch_id}"
            evidence_dir.mkdir(parents=True, exist_ok=True)
            evidence_path = evidence_dir / "EXPORT_EVIDENCE.json"
            evidence_payload = {
                "schemaVersion": "springmaster.patch-export-evidence.v1",
                "status": "PRIOR_GATES_PASSED",
                "patchId": patch_id,
                "sourcePatchSha256": report["sourcePatchSha256"],
                "sourceGitHead": head,
                "recordedAt": now_iso(),
            }
            write_report(evidence_path, evidence_payload)
            env = project_environment(test_root)
            env["PATCH_EXPORT_EVIDENCE_FILE"] = str(evidence_path)
            export_command = env.get("PATCH_EXPORT_COMMAND", "./bin/export.sh full --zip")
            export_result = run_logged(
                export_command,
                test_root,
                output_dir / "09_testcopy_export.log",
                env=env,
                shell=True,
            )
            require_success(export_result, "PATCH_ARTIFACT_TESTCOPY_EXPORT_FAILED", output_dir / "09_testcopy_export.log")
            export_zip = resolve_export_path(test_root, export_result.stdout or "")
            checker = test_root / "bin" / "export-integrity-check.py"
            if not checker.is_file():
                fail(f"PATCH_ARTIFACT_EXPORT_CHECKER_MISSING: {checker}")
            integrity_result = run_logged(
                [sys.executable, str(checker), str(export_zip), "--source-root", str(test_root), "--require-evidence"],
                test_root,
                output_dir / "10_testcopy_export_integrity.log",
            )
            require_success(
                integrity_result,
                "PATCH_ARTIFACT_TESTCOPY_EXPORT_INTEGRITY_FAILED",
                output_dir / "10_testcopy_export_integrity.log",
            )
            retained_export = output_dir / export_zip.name
            shutil.copy2(export_zip, retained_export)
            report["checks"]["testCopyExport"] = {
                "status": "PASS",
                "path": str(retained_export),
                "sha256": sha256_file(retained_export),
            }
        else:
            report["checks"]["testCopyExport"] = "SKIPPED_BY_OPTION"

        report["status"] = "PASS"
        report["completedAt"] = now_iso()
        report_path = output_dir / "REPORT.json"
        write_report(report_path, report)
        (output_dir / "SUMMARY.txt").write_text(
            "\n".join(
                [
                    f"STATUS=PASS",
                    f"PATCH_ID={patch_id}",
                    f"SOURCE_PATCH_SHA256={report['sourcePatchSha256']}",
                    f"SOURCE_GIT_HEAD={head}",
                    f"REPORT={report_path}",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        print("ARTIFACT_PREFLIGHT=PASS")
        print(f"PATCH_ID={patch_id}")
        print(f"SOURCE_PATCH_SHA256={report['sourcePatchSha256']}")
        print(f"REPORT={report_path}")
    except PreflightError as exc:
        if output_dir is not None:
            report["status"] = "FAIL"
            report["completedAt"] = now_iso()
            report["error"] = str(exc)
            write_report(output_dir / "REPORT.json", report)
            (output_dir / "SUMMARY.txt").write_text(
                f"STATUS=FAIL\nERROR={str(exc).replace(chr(10), ' | ')}\nREPORT={output_dir / 'REPORT.json'}\n",
                encoding="utf-8",
            )
        print(f"Fehler: {exc}", file=sys.stderr)
        raise SystemExit(1)
    finally:
        shutil.rmtree(extract_parent, ignore_errors=True)
        if worktree_added and test_root is not None and not options["keepTestCopy"]:
            subprocess.run(
                ["git", "worktree", "remove", "--force", str(test_root)],
                cwd=project_root,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        if test_parent is not None and not options["keepTestCopy"]:
            shutil.rmtree(test_parent, ignore_errors=True)
        subprocess.run(
            ["git", "worktree", "prune"],
            cwd=project_root,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )


if __name__ == "__main__":
    main()
