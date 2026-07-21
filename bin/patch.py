#!/usr/bin/env python3
import fnmatch
import hashlib
import json
import os
import re
import shlex
import shutil
import socket
import stat
import subprocess
import sys
import tempfile
import zipfile
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

USAGE = """Verwendung:
  ./bin/patch.sh --help
  ./bin/patch.sh help
  ./bin/patch.sh apply [--dry-run] [--wait] <patch.zip>
  ./bin/patch.sh live-baseline <patch.zip>
  ./bin/patch.sh artifact-preflight <patch.zip> [--output <dir>] [--no-export] [--keep-test-copy]
  ./bin/patch.sh accept <patch.zip> [--background] [--wait-for-lock] [--lock-timeout <seconds>] [--profile auto|docs|tooling|code] [--test <MavenTest>] [--full-test|--no-full-test] [--export|--no-export] [--commit] [--push] [--format human|env|json] [--watch] [--watch-interval <seconds>] [--watch-timeout <seconds>]
  ./bin/patch.sh verify <patch-id|patch-number|latest> [--background] [--wait-for-lock] [--lock-timeout <seconds>] [--profile auto|docs|tooling|code] [--test <MavenTest>] [--full-test|--no-full-test] [--export|--no-export] [--format human|env|json] [--watch] [--watch-interval <seconds>] [--watch-timeout <seconds>]
  ./bin/patch.sh status [<run-id|patch-id|patch-number|latest>|--patch <patch-id>] [--format human|env|json]
  ./bin/patch.sh watch [<run-id|patch-id|patch-number|latest>|--patch <patch-id>] [--interval <seconds>] [--timeout <seconds>]
  ./bin/patch.sh wait [<run-id|patch-id|patch-number|latest>|--patch <patch-id>] [--interval <seconds>] [--timeout <seconds>]
  ./bin/patch.sh result [<run-id|patch-id|patch-number|latest>|--patch <patch-id>] [--format human|env|json]
  ./bin/patch.sh diagnose [<run-id|patch-id|patch-number|latest>|--patch <patch-id>] [--output <file>]
  ./bin/patch.sh doctor [--format human|json]
  ./bin/patch.sh rollback [--dry-run] [--wait-for-lock] <patch-id|patch-number|latest>
  ./bin/patch.sh list
  ./bin/patch.sh show <patch-id|patch-number|latest>

Pflichtregeln:
  - manifest.json ist verpflichtend.
  - manifest.schemaVersion muss springmaster.patch-manifest.v2 sein.
  - manifest.artifactId ist als kanonische UUID-URN verpflichtend und repositoryweit eindeutig.
  - manifest.id und manifest.patchId sind verpflichtend und müssen identisch sein.
  - manifest.patchId muss dem Archivnamen ohne .zip entsprechen.
  - manifest.scope ist verpflichtend.
  - manifest.name ist verpflichtend.
  - logs/CHANGELOG-*.md ist verpflichtend.
  - Erlaubte ZIP-Wurzelpfade: manifest.json, files/**, delete/**, logs/CHANGELOG-*.md.
  - Legacy-Patches werden abgelehnt.
  - accept führt vor dem Dry-run einen Live-Baseline-Hash-Preflight aus.
  - artifact-preflight requires a clean Git baseline and validates the patch in an isolated test copy.
  - Mutierende Läufe verwenden einen projektlokalen Write-Lock.
  - Für lange Läufe ist --background --wait-for-lock der empfohlene Startmodus.
  - status, watch und wait beobachten Runs kompakt ohne Log-Streaming.
  - --format env|json liefert beim Background-Start eine maschinenlesbare Run-ID ohne Hilfsdatei.
  - --watch verbindet den Background-Start mit der kompakten Run-Beobachtung.
  - Runtime-Evidence bleibt projektlokal; Downloads ist ausschließlich ein Artefakt-Eingang.
  - Ein bereits angewendetes oder bereits laufendes Artefakt wird idempotent erkannt.
"""

if len(sys.argv) < 3:
    print(USAGE)
    sys.exit(1)

PROJECT_ROOT = Path(sys.argv[1]).resolve()
COMMAND = sys.argv[2]
ARGS = sys.argv[3:]
ARCHIVES_DIR = PROJECT_ROOT / "patches" / "archives"
PATCH_RUN_API_CUTOVER_NUMBER = 164

def fail(message, code=1):
    print(f"Fehler: {message}", file=sys.stderr)
    sys.exit(code)

def now_iso():
    return datetime.now(timezone.utc).astimezone().isoformat()


def atomic_write_text(path, content):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.tmp-{os.getpid()}-{time.time_ns()}")
    try:
        tmp.write_text(content, encoding="utf-8")
        os.replace(tmp, path)
    finally:
        try:
            tmp.unlink()
        except FileNotFoundError:
            pass


def read_summary_fields(path):
    fields = {}
    path = Path(path)
    if not path.is_file():
        return fields
    try:
        for raw_line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            if "=" not in raw_line:
                continue
            key, value = raw_line.split("=", 1)
            if re.fullmatch(r"[A-Z][A-Z0-9_]*", key):
                fields[key] = value
    except OSError:
        return {}
    return fields


def safe_int(value, default=None):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default

def sanitize_name(value):
    value = Path(str(value)).name
    value = re.sub(r"\.zip$", "", value, flags=re.IGNORECASE)
    value = re.sub(r"[^A-Za-z0-9._-]+", "_", value).strip("._-")
    return value or "patch"


VALIDATION_LOG_NAME_MAX_BYTES = 120


def validation_test_log_name(test_selector, used_names):
    """Return a deterministic, bounded and collision-safe test log basename."""
    selector = str(test_selector)
    sanitized = sanitize_name(selector)
    plain_name = f"test-{sanitized}.log"
    plain_name_bytes = len(plain_name.encode("utf-8"))
    if plain_name_bytes <= VALIDATION_LOG_NAME_MAX_BYTES and plain_name not in used_names:
        return plain_name

    digest = hashlib.sha256(selector.encode("utf-8")).hexdigest()[:12]
    duplicate_index = 1
    while True:
        duplicate_suffix = "" if duplicate_index == 1 else f"-{duplicate_index}"
        suffix = f"-{digest}{duplicate_suffix}.log"
        prefix = "test-"
        stem_bytes = VALIDATION_LOG_NAME_MAX_BYTES - len((prefix + suffix).encode("utf-8"))
        if stem_bytes < 1:
            fail("VALIDATION_LOG_NAME_LIMIT_INVALID: configured basename limit is too small.")
        stem = sanitized.encode("ascii")[:stem_bytes].decode("ascii").rstrip("._-") or "selection"
        candidate = f"{prefix}{stem}{suffix}"
        if candidate not in used_names:
            return candidate
        duplicate_index += 1

def validate_relpath(path):
    if not isinstance(path, str) or not path.strip():
        fail(f"Ungültiger leerer Pfad: {path!r}")
    normalized = path.replace("\\", "/")
    while normalized.startswith("./"):
        normalized = normalized[2:]
    if normalized.startswith("/") or normalized.startswith("~"):
        fail(f"Absolute Pfade sind nicht erlaubt: {path}")
    parts = [p for p in normalized.split("/") if p]
    if any(p == ".." for p in parts):
        fail(f"Pfade mit '..' sind nicht erlaubt: {path}")
    if not parts:
        fail(f"Ungültiger leerer Pfad: {path!r}")
    return "/".join(parts)

def ensure_inside_root(target):
    target = target.resolve()
    if target != PROJECT_ROOT and PROJECT_ROOT not in target.parents:
        fail(f"Pfad liegt außerhalb des Repository-Roots: {target}")
    return target

def sha256_file(path):
    if not path.exists() or not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def apply_git_executable_mode(source_abs, target_abs):
    if not source_abs.is_file() or not target_abs.is_file():
        return
    source_mode = stat.S_IMODE(source_abs.stat().st_mode)
    target_mode = stat.S_IMODE(target_abs.stat().st_mode)
    if source_mode & 0o111:
        target_abs.chmod(target_mode | 0o111)
    else:
        target_abs.chmod(target_mode & ~0o111)

def read_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"Kann JSON nicht lesen: {path}: {exc}")

def write_json(path, data):
    atomic_write_text(path, json.dumps(data, indent=2, ensure_ascii=False) + "\n")

def archive_dirs():
    if not ARCHIVES_DIR.exists():
        return []
    return sorted([p for p in ARCHIVES_DIR.iterdir() if p.is_dir() and re.match(r"^\d{6}_", p.name)])

def next_patch_number():
    ARCHIVES_DIR.mkdir(parents=True, exist_ok=True)
    max_num = 0
    for entry in archive_dirs():
        max_num = max(max_num, int(entry.name.split("_", 1)[0]))
    return f"{max_num + 1:06d}"

def patch_number_from_id(patch_id):
    match = re.match(r"^(\d{6})_", str(patch_id or ""))
    return int(match.group(1)) if match else None


def is_historical_pre_run_api_patch(patch_id):
    number = patch_number_from_id(patch_id)
    return number is not None and number < PATCH_RUN_API_CUTOVER_NUMBER


def resolve_patch_ref(ref):
    dirs = archive_dirs()
    if not dirs:
        fail("Keine Patch-Archive vorhanden.")
    if ref == "latest":
        return dirs[-1]
    if re.fullmatch(r"\d+", ref):
        for d in dirs:
            if int(d.name.split("_", 1)[0]) == int(ref):
                return d
    for d in dirs:
        if d.name == ref or d.name.startswith(ref):
            return d
    fail(f"Patch nicht gefunden: {ref}")

def parse_env_file_into(env, env_file):
    if not env_file.exists():
        return
    try:
        lines = env_file.read_text(encoding="utf-8").splitlines()
    except Exception as exc:
        fail(f"Kann Environment-Datei nicht lesen: {env_file}: {exc}")
    for raw_line in lines:
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export "):].strip()
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", key):
            continue
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
            value = value[1:-1]
        env[key] = value


def read_project_env():
    env = dict(os.environ)
    # .env.example is the generated project-local defaults contract. It is read
    # before .env so target projects keep their own names, package roots,
    # database names and patch scopes even after shared tooling updates.
    parse_env_file_into(env, PROJECT_ROOT / ".env.example")
    parse_env_file_into(env, PROJECT_ROOT / ".env")
    return env

_PROJECT_ENV_CACHE = None

def project_env():
    global _PROJECT_ENV_CACHE
    if _PROJECT_ENV_CACHE is None:
        _PROJECT_ENV_CACHE = read_project_env()
    return _PROJECT_ENV_CACHE

def env_value(name, default=None):
    value = project_env().get(name)
    if value is None or str(value).strip() == "":
        return default
    return value

def project_relative_or_absolute_path(value, default_rel):
    raw = value or default_rel
    path = Path(str(raw)).expanduser()
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    return path.resolve()

def patch_lock_root():
    return project_relative_or_absolute_path(env_value("PATCH_LOCK_ROOT"), "patches/runtime/locks")

def project_write_lock_path():
    return patch_lock_root() / "project-write.lock"

def parse_bool_env(name, default=False):
    value = project_env().get(name)
    if value is None:
        return default
    return str(value).strip().lower() in ("1", "true", "yes", "y", "on")

def parse_lock_timeout(args):
    timeout = env_value("PATCH_LOCK_TIMEOUT_SECONDS")
    i = 0
    while i < len(args):
        if args[i] == "--lock-timeout":
            if i + 1 >= len(args):
                fail("--lock-timeout erwartet eine Sekundenangabe.")
            timeout = args[i + 1]
            i += 2
        else:
            i += 1
    if timeout is None:
        return None
    try:
        seconds = int(timeout)
    except ValueError:
        fail(f"Ungültiger Wert für --lock-timeout/PATCH_LOCK_TIMEOUT_SECONDS: {timeout}")
    if seconds < 0:
        fail("Lock-Timeout darf nicht negativ sein.")
    return seconds

def parse_wait_flag(args):
    return (
        "--wait-for-lock" in args
        or "--wait" in args
        or parse_bool_env("PATCH_LOCK_WAIT", False)
    )

class PatchLockBusy(Exception):
    def __init__(self, lock_path, info):
        super().__init__(str(lock_path))
        self.lock_path = lock_path
        self.info = info or {}

def read_lock_info(lock_path):
    try:
        return json.loads(lock_path.read_text(encoding="utf-8"))
    except Exception:
        return {"raw": lock_path.read_text(encoding="utf-8", errors="replace") if lock_path.exists() else ""}

def pid_is_alive(pid):
    try:
        pid_int = int(pid)
    except Exception:
        return False
    if pid_int <= 0:
        return False
    try:
        os.kill(pid_int, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except Exception:
        return True

def lock_is_stale(lock_info):
    host = lock_info.get("host")
    pid = lock_info.get("pid")
    if host and host != socket.gethostname():
        return False
    return not pid_is_alive(pid)

class ProjectWriteLock:
    def __init__(self, command_name, subject=None, wait=False, timeout_seconds=None):
        self.command_name = command_name
        self.subject = subject
        self.wait = wait
        self.timeout_seconds = timeout_seconds
        self.lock_path = project_write_lock_path()
        self.token = f"{os.getpid()}-{time.time_ns()}"
        self.acquired = False
        self.previous_lock_path = None
        self.previous_lock_token = None
        self.reentrant = False

    def __enter__(self):
        active_lock_path = os.environ.get("SPRINGMASTER_PATCH_WRITE_LOCK")
        if active_lock_path and Path(active_lock_path).resolve() == self.lock_path.resolve():
            self.reentrant = True
            return self

        self.lock_path.parent.mkdir(parents=True, exist_ok=True)
        deadline = None if self.timeout_seconds is None else time.monotonic() + self.timeout_seconds
        while True:
            payload = {
                "projectRoot": str(PROJECT_ROOT),
                "pid": os.getpid(),
                "host": socket.gethostname(),
                "command": self.command_name,
                "subject": str(self.subject or "-"),
                "startedAt": now_iso(),
                "token": self.token,
            }
            try:
                fd = os.open(str(self.lock_path), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
                with os.fdopen(fd, "w", encoding="utf-8") as f:
                    json.dump(payload, f, indent=2, ensure_ascii=False)
                    f.write("\n")
                self.acquired = True
                self.previous_lock_path = os.environ.get("SPRINGMASTER_PATCH_WRITE_LOCK")
                self.previous_lock_token = os.environ.get("SPRINGMASTER_PATCH_WRITE_LOCK_TOKEN")
                os.environ["SPRINGMASTER_PATCH_WRITE_LOCK"] = str(self.lock_path)
                os.environ["SPRINGMASTER_PATCH_WRITE_LOCK_TOKEN"] = self.token
                return self
            except FileExistsError:
                info = read_lock_info(self.lock_path)
                if lock_is_stale(info):
                    try:
                        self.lock_path.unlink()
                        continue
                    except FileNotFoundError:
                        continue
                if not self.wait:
                    raise PatchLockBusy(self.lock_path, info)
                if deadline is not None and time.monotonic() >= deadline:
                    raise PatchLockBusy(self.lock_path, info)
                time.sleep(2)

    def __exit__(self, exc_type, exc, tb):
        if self.reentrant:
            return False
        if self.acquired:
            try:
                info = read_lock_info(self.lock_path)
                if info.get("token") == self.token:
                    self.lock_path.unlink()
            except FileNotFoundError:
                pass
            finally:
                if self.previous_lock_path is None:
                    os.environ.pop("SPRINGMASTER_PATCH_WRITE_LOCK", None)
                else:
                    os.environ["SPRINGMASTER_PATCH_WRITE_LOCK"] = self.previous_lock_path
                if self.previous_lock_token is None:
                    os.environ.pop("SPRINGMASTER_PATCH_WRITE_LOCK_TOKEN", None)
                else:
                    os.environ["SPRINGMASTER_PATCH_WRITE_LOCK_TOKEN"] = self.previous_lock_token
        return False

def write_busy_summary(log_dir, command_name, lock_path, lock_info, options=None):
    log_dir = Path(log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)
    owner = f"PID={lock_info.get('pid', '-')} HOST={lock_info.get('host', '-')} COMMAND={lock_info.get('command', '-')}"
    run_data = load_run_record(log_dir)
    lines = [
        "STATUS=BUSY",
        f"COMMAND={command_name}",
        f"RUN_ID={run_data.get('runId', log_dir.name)}",
        f"PATCH_ID={run_data.get('patchId', '-')}",
        "PHASE=WAITING_FOR_LOCK",
        f"LOCK={lock_path}",
        f"OWNER={owner}",
        f"OWNER_STARTED={lock_info.get('startedAt', '-')}",
        f"OWNER_SUBJECT={lock_info.get('subject', '-')}",
        f"LOG_DIR={log_dir}",
        f"UPDATED_AT={now_iso()}",
    ]
    content = "\n".join(lines) + "\n"
    atomic_write_text(log_dir / "summary.log", content)
    atomic_write_text(log_dir / "SUMMARY.txt", content)
    atomic_write_text(log_dir / "STATUS.txt", "BUSY\n")
    write_run_record(log_dir, status="BUSY", phase="WAITING_FOR_LOCK", command=command_name)


def print_busy_result(command_name, log_dir, lock_path, lock_info):
    label = "Patch-Accept" if command_name == "accept" else "Patch-Verify" if command_name == "verify" else f"Patch-{command_name.capitalize()}"
    print(f"{label}:")
    print("  Status:       BUSY")
    print(f"  Lock:         {lock_path}")
    print(f"  Owner:        PID={lock_info.get('pid', '-')} HOST={lock_info.get('host', '-')} COMMAND={lock_info.get('command', '-')}")
    print(f"  Started:      {lock_info.get('startedAt', '-')}")
    print(f"  Subject:      {lock_info.get('subject', '-')}")
    print(f"  Summary:      {log_dir / 'SUMMARY.txt'}")
    print(f"  Log:          {log_dir}")
    print("  Aktion:       Erneut mit --wait-for-lock ausführen oder aktiven Lauf prüfen.")

def normalize_scope_env_name(scope):
    normalized = re.sub(r"[^A-Za-z0-9]+", "_", scope).strip("_").upper()
    return normalized or "SCOPE"

def split_env_list(value):
    if not value:
        return []
    return [part.strip() for part in re.split(r"[;,\n]+", value) if part.strip()]

def split_scope_names(value):
    if not value:
        return []
    return [part.strip() for part in re.split(r"[;,\s]+", value) if part.strip()]


def package_to_path(value, default):
    package = str(value or default).strip() or default
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z_][A-Za-z0-9_]*)+", package):
        fail(f"Ungültiger Java-Package-Name in Projektkonfiguration: {package!r}")
    return package.replace(".", "/")


def configured_app_package_path():
    return package_to_path(project_env().get("APP_BASE_PACKAGE"), "de.cocondo.platform")


def configured_core_package_path():
    return package_to_path(project_env().get("APP_CORE_PACKAGE"), "de.cocondo.system")


def configured_project_scope_name():
    raw = (
        project_env().get("APP_PATCH_PROJECT_SCOPE")
        or project_env().get("APP_EXPORT_PROJECT_KEY")
        or project_env().get("APP_NAME")
    )
    if not raw:
        return None
    return validate_scope_name(str(raw).strip())

def validate_scope_name(scope):
    if not isinstance(scope, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", scope):
        fail(f"Ungültiger lokaler Patch-Scope in .env: {scope!r}")
    return scope

def base_scope_log_dirs():
    return {
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

def base_scope_patterns():
    app_package_path = configured_app_package_path()
    core_package_path = configured_core_package_path()
    return {
        "root": [
            "README.md",
            "pom.xml",
            ".gitignore",
            ".env",
            ".env.example",
            "export.config.json",
            "bin/**",
            "PROJECT_DOCS/**",
            "platform/**",
            f"src/main/java/{app_package_path}/app/**",
            "src/main/resources/**",
            "src/test/**",
            "patches/logs/root/**",
            "patches/logs/bootstrap/**",
        ],
        "bin": [
            "bin/**",
            "patches/logs/bin/**",
        ],
        "tooling": [
            "bin/**",
            "platform/versions/platform.env",
            "platform/update/managed-state.json",
            "platform/update/compatibility-decision.json",
            "export.config.json",
            ".env.example",
            "PROJECT_DOCS/TOOLING/**",
            "PROJECT_DOCS/CONFIG/**",
            "patches/logs/tooling/**",
        ],
        "platform": [
            "platform/**",
            "PROJECT_DOCS/ADR/**",
            "PROJECT_DOCS/CONCEPT/**",
            "PROJECT_DOCS/TARGET_UPDATES/**",
            "patches/logs/platform/**",
        ],
        "core": [
            "pom.xml",
            "platform/versions/platform.env",
            "platform/update/managed-state.json",
            "platform/update/compatibility-decision.json",
            f"src/main/java/{core_package_path}/**",
            f"src/test/java/{core_package_path}/**",
            "PROJECT_DOCS/CORE/**",
            "PROJECT_DOCS/CONCEPT/SPRINGMASTER_VERSION_POLICY.md",
            "patches/logs/core/**",
        ],
        "demo": [
            "platform/versions/platform.env",
            "platform/update/managed-state.json",
            "platform/update/compatibility-decision.json",
            f"src/main/java/{app_package_path}/demo/**",
            f"src/test/java/{app_package_path}/demo/**",
            "PROJECT_DOCS/DEMO/**",
            "PROJECT_DOCS/CONCEPT/SPRINGMASTER_VERSION_POLICY.md",
            "patches/logs/demo/**",
        ],
        "app": [
            f"src/main/java/{app_package_path}/app/**",
            f"src/test/java/{app_package_path}/app/**",
            "patches/logs/app/**",
        ],
        "resources": [
            "src/main/resources/**",
            "patches/logs/resources/**",
        ],
        "tests": [
            "src/test/**",
            "patches/logs/tests/**",
        ],
        "docs": [
            "AGENTS.md",
            "platform/versions/platform.env",
            "platform/update/managed-state.json",
            "platform/update/compatibility-decision.json",
            "docs/**",
            "PROJECT_DOCS/**",
            "README.md",
            "patches/logs/docs/**",
        ],
        "db": [
            "src/main/resources/db/**",
            "patches/logs/db/**",
        ],
        "templates": [
            "PROJECT_DOCS/TEMPLATES/**",
            "platform/templates/**",
            "patches/logs/templates/**",
        ],
        "planning": [
            "PROJECT_DOCS/PLANNING/**",
            "patches/logs/planning/**",
        ],
        "target-registry": [
            "platform/update/targets/**",
            "PROJECT_DOCS/TARGET_UPDATES/**",
            "patches/logs/target-registry/**",
        ],
        "platform-update": [
            "bin/platform-update.sh",
            "platform/update/**",
            "platform/versions/platform.env",
            "PROJECT_DOCS/TARGET_UPDATES/**",
            "PROJECT_DOCS/TOOLING/PLATFORM_UPDATE.md",
            "PROJECT_DOCS/TOOLING/PLATFORM_UPDATE_*.md",
            "PROJECT_DOCS/CONCEPT/SPRINGMASTER_VERSION_POLICY.md",
            "patches/logs/platform-update/**",
        ],
    }

def local_scope_names():
    names = [validate_scope_name(scope) for scope in split_scope_names(project_env().get("PATCH_LOCAL_SCOPES", ""))]
    implicit = configured_project_scope_name()
    if implicit and implicit not in base_scope_log_dirs() and implicit not in names:
        names.append(implicit)
    return names

def local_scope_log_dir(scope):
    if scope not in local_scope_names():
        return None
    env_name = normalize_scope_env_name(scope)
    value = project_env().get(f"PATCH_SCOPE_{env_name}_LOG_DIR", scope)
    return validate_relpath(value)

def env_scope_paths(scope, suffix):
    env_name = normalize_scope_env_name(scope)
    key = f"PATCH_SCOPE_{env_name}_{suffix}"
    return [validate_relpath(path) for path in split_env_list(project_env().get(key, ""))]

def scope_log_dir(scope):
    base = base_scope_log_dirs().get(scope)
    if base is not None:
        return base
    return local_scope_log_dir(scope)

def scope_patterns(scope):
    base = base_scope_patterns().get(scope)
    if base is not None:
        return base + env_scope_paths(scope, "EXTRA_PATHS")

    if scope in local_scope_names():
        log_dir = local_scope_log_dir(scope)
        paths = env_scope_paths(scope, "PATHS") + env_scope_paths(scope, "EXTRA_PATHS")
        if not paths and scope == configured_project_scope_name():
            app_package_path = configured_app_package_path()
            paths = [
                f"src/main/java/{app_package_path}/**",
                f"src/test/java/{app_package_path}/**",
                "src/main/resources/db/**",
                "PROJECT_DOCS/CONCEPT/**",
                "PROJECT_DOCS/DOMAIN/**",
                "PROJECT_DOCS/STANDARDS/**",
            ]
        if not paths:
            fail(f"Lokaler Patch-Scope {scope!r} ist in PATCH_LOCAL_SCOPES registriert, hat aber keine PATCH_SCOPE_{normalize_scope_env_name(scope)}_PATHS.")
        return paths + [f"patches/logs/{log_dir}/**"]

    return None

def path_matches(rel, patterns):
    return any(fnmatch.fnmatchcase(rel, pat) for pat in patterns)

def validate_scope(scope, target_paths):
    patterns = scope_patterns(scope)
    if patterns is None:
        fail(f"Unbekannter Patch-Scope im manifest.json: {scope}")
    violations = [
        rel for rel in target_paths
        if not rel.startswith("patches/archives/") and not path_matches(rel, patterns)
    ]
    if violations:
        fail("Scope-Verletzung für Scope " + scope + ":\n  " + "\n  ".join(sorted(violations)))

def extract_archive(zip_path):
    if not zip_path.exists() or not zip_path.is_file():
        fail(f"Patch-ZIP nicht gefunden: {zip_path}")
    tmp_dir = Path(tempfile.mkdtemp(prefix="springmaster-patch-"))
    try:
        with zipfile.ZipFile(zip_path, "r") as z:
            for info in z.infolist():
                if info.is_dir():
                    continue
                name = info.filename.replace("\\", "/")
                if name.startswith("__MACOSX/") or name.endswith(".DS_Store"):
                    continue
                safe_name = validate_relpath(name)
                out = tmp_dir / safe_name
                out.parent.mkdir(parents=True, exist_ok=True)
                with z.open(info) as src, out.open("wb") as dst:
                    shutil.copyfileobj(src, dst)
                archive_mode = stat.S_IMODE(info.external_attr >> 16)
                current_mode = stat.S_IMODE(out.stat().st_mode)
                if archive_mode & 0o111:
                    out.chmod(current_mode | 0o111)
                else:
                    out.chmod(current_mode & ~0o111)
        return tmp_dir
    except Exception:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        raise

PATCH_ID_PATTERN = re.compile(r"^\d{6}_[A-Za-z0-9._-]+$")
PATCH_MANIFEST_SCHEMA = "springmaster.patch-manifest.v2"
ARTIFACT_ID_PREFIX = "urn:uuid:"


def validate_artifact_id(value):
    if not isinstance(value, str) or not value.strip():
        fail("PATCH_ARTIFACT_IDENTITY_INVALID: manifest.artifactId is required.")
    artifact_id = value.strip()
    if not artifact_id.startswith(ARTIFACT_ID_PREFIX):
        fail(
            "PATCH_ARTIFACT_IDENTITY_INVALID: manifest.artifactId must be a canonical "
            f"UUID URN ({ARTIFACT_ID_PREFIX}<uuid>)."
        )
    raw_uuid = artifact_id[len(ARTIFACT_ID_PREFIX):]
    try:
        parsed = uuid.UUID(raw_uuid)
    except (ValueError, AttributeError) as exc:
        fail(f"PATCH_ARTIFACT_IDENTITY_INVALID: invalid artifactId {artifact_id!r}: {exc}")
    canonical = f"{ARTIFACT_ID_PREFIX}{parsed}"
    if artifact_id != canonical or parsed.int == 0:
        fail(
            "PATCH_ARTIFACT_IDENTITY_INVALID: manifest.artifactId must use canonical "
            f"lowercase UUID-URN form, got {artifact_id!r}."
        )
    return artifact_id


def archived_artifact_conflict(artifact_id):
    for patch_dir in archive_dirs():
        for candidate in (patch_dir / "manifest.json", patch_dir / "patch-log.json"):
            if not candidate.is_file():
                continue
            try:
                data = json.loads(candidate.read_text(encoding="utf-8"))
            except Exception:
                continue
            archived_id = data.get("artifactId")
            if archived_id is None and isinstance(data.get("manifest"), dict):
                archived_id = data["manifest"].get("artifactId")
            if archived_id == artifact_id:
                return patch_dir.name
    return None

def manifest_required_string(manifest, field):
    value = manifest.get(field)
    if not isinstance(value, str) or not value.strip():
        fail(f"manifest.{field} ist verpflichtend und muss ein nicht-leerer String sein.")
    return value.strip()

def validate_manifest_identity(manifest, name, zip_path=None):
    schema_version = manifest.get("schemaVersion")
    if not isinstance(schema_version, str) or schema_version != PATCH_MANIFEST_SCHEMA:
        fail(
            "PATCH_ARTIFACT_IDENTITY_INVALID: manifest.schemaVersion must be "
            f"{PATCH_MANIFEST_SCHEMA}, got {schema_version!r}."
        )
    artifact_id = validate_artifact_id(manifest.get("artifactId"))
    patch_id = manifest_required_string(manifest, "patchId")
    legacy_id = manifest_required_string(manifest, "id")
    conflict = archived_artifact_conflict(artifact_id)
    if conflict is not None and conflict != patch_id:
        fail(
            "PATCH_ARTIFACT_IDENTITY_CONFLICT: manifest.artifactId is already archived.\n"
            f"  artifactId: {artifact_id}\n"
            f"  archivedPatch: {conflict}"
        )
    if patch_id != legacy_id:
        fail(
            "PATCH_IDENTITY_CONFLICT: manifest.patchId und manifest.id müssen identisch sein.\n"
            f"  patchId: {patch_id}\n"
            f"  id:      {legacy_id}"
        )
    if not PATCH_ID_PATTERN.fullmatch(patch_id):
        fail(
            "PATCH_IDENTITY_CONFLICT: manifest.patchId muss dem Format "
            "000000_name entsprechen.\n"
            f"  patchId: {patch_id}"
        )
    expected_patch_id = f"{patch_id.split('_', 1)[0]}_{sanitize_name(name)}"
    if patch_id != expected_patch_id:
        fail(
            "PATCH_IDENTITY_CONFLICT: manifest.patchId muss aus Nummer und "
            "manifest.name abgeleitet sein.\n"
            f"  patchId:      {patch_id}\n"
            f"  manifest.name: {name}\n"
            f"  expected:     {expected_patch_id}"
        )
    if zip_path is not None:
        expected_archive = f"{patch_id}.zip"
        actual_archive = Path(zip_path).name
        if actual_archive != expected_archive:
            fail(
                "PATCH_IDENTITY_CONFLICT: Archivname und manifest.patchId müssen "
                "identisch sein.\n"
                f"  archive: {actual_archive}\n"
                f"  patchId: {patch_id}\n"
                f"  expectedArchive: {expected_archive}"
            )
    return patch_id

def validate_manifest(manifest, zip_path=None):
    if not isinstance(manifest, dict):
        fail("manifest.json muss ein JSON-Objekt sein.")
    scope = manifest.get("scope")
    name = manifest.get("name")
    if not isinstance(scope, str) or not scope.strip():
        fail("manifest.scope ist verpflichtend und muss ein nicht-leerer String sein.")
    if not isinstance(name, str) or not name.strip():
        fail("manifest.name ist verpflichtend und muss ein nicht-leerer String sein.")
    if scope_log_dir(scope) is None:
        fail(f"Unbekannter Patch-Scope im manifest.json: {scope}")
    patch_id = validate_manifest_identity(manifest, name.strip(), zip_path=zip_path)
    return scope.strip(), name.strip(), patch_id

def collect_patch(tmp_dir, zip_path=None):
    manifest_path = tmp_dir / "manifest.json"
    if not manifest_path.exists():
        fail("manifest.json ist verpflichtend. Legacy-Patches werden nicht mehr akzeptiert.")
    manifest = read_json(manifest_path)
    scope, name, patch_id = validate_manifest(manifest, zip_path=zip_path)
    changelog_sources = []
    invalid_roots = []
    operations = []

    for file in sorted(tmp_dir.rglob("*")):
        if not file.is_file():
            continue
        rel = file.relative_to(tmp_dir).as_posix().lstrip("./")
        if rel == "manifest.json":
            continue
        if rel.startswith("files/"):
            target = validate_relpath(rel[len("files/"):])
            operations.append({"type": "file", "source": rel, "target": target})
        elif rel.startswith("delete/"):
            target = validate_relpath(rel[len("delete/"):])
            operations.append({"type": "delete", "source": rel, "target": target})
        elif rel.startswith("logs/"):
            filename = Path(rel).name
            if not re.match(r"^CHANGELOG-[A-Za-z0-9._-]+\.md$", filename):
                fail(f"Changelog-Dateien unter logs/ müssen CHANGELOG-*.md heißen: {rel}")
            target = validate_relpath(f"patches/logs/{scope_log_dir(scope)}/{filename}")
            operations.append({"type": "file", "source": rel, "target": target})
            changelog_sources.append(rel)
        else:
            invalid_roots.append(rel)

    if invalid_roots:
        fail(
            "Patch-ZIP enthält nicht erlaubte Pfade. Erlaubt sind nur manifest.json, files/**, delete/** und logs/CHANGELOG-*.md:\n  "
            + "\n  ".join(sorted(invalid_roots))
        )
    if not changelog_sources:
        fail("logs/CHANGELOG-*.md ist verpflichtend.")
    if not operations:
        fail("Patch-ZIP enthält keine anwendbaren Dateien.")

    validate_scope(scope, [op["target"] for op in operations])
    return manifest, scope, name, patch_id, operations


BASELINE_MISSING_MARKERS = {"", "-", "missing", "absent", "none", "null", "not-exists", "not_exists"}

def normalize_expected_before_sha256(value, path):
    if value is None:
        return None
    if isinstance(value, str):
        normalized = value.strip()
        if normalized.lower() in BASELINE_MISSING_MARKERS:
            return None
        if re.fullmatch(r"[A-Fa-f0-9]{64}", normalized):
            return normalized.lower()
    fail(f"Ungültiger expectedBeforeSha256-Wert für {path}: {value!r}. Erwartet: 64-stelliger SHA-256 oder null/missing.")

def expected_before_sha256_map(manifest):
    raw = None
    if isinstance(manifest.get("baseline"), dict):
        baseline = manifest.get("baseline")
        raw = baseline.get("expectedBeforeSha256")
        if raw is None:
            raw = baseline.get("expectedBefore")
    if raw is None:
        raw = manifest.get("expectedBeforeSha256")
    if raw is None:
        raw = manifest.get("expectedBefore")
    if raw is None:
        return {}

    expected = {}
    if isinstance(raw, dict):
        for path, value in raw.items():
            rel = validate_relpath(path)
            expected[rel] = normalize_expected_before_sha256(value, rel)
        return expected

    if isinstance(raw, list):
        for item in raw:
            if not isinstance(item, dict):
                fail("baseline.expectedBefore muss eine Liste von JSON-Objekten sein.")
            if "path" not in item:
                fail("baseline.expectedBefore-Einträge benötigen ein Feld 'path'.")
            rel = validate_relpath(item.get("path"))
            if "sha256" in item:
                value = item.get("sha256")
            elif "sha256Before" in item:
                value = item.get("sha256Before")
            elif "expectedBeforeSha256" in item:
                value = item.get("expectedBeforeSha256")
            elif item.get("exists") is False:
                value = None
            else:
                fail(f"baseline.expectedBefore-Eintrag für {rel} benötigt sha256/sha256Before/expectedBeforeSha256 oder exists=false.")
            expected[rel] = normalize_expected_before_sha256(value, rel)
        return expected

    fail("manifest.expectedBeforeSha256 bzw. baseline.expectedBeforeSha256 muss ein Objekt oder baseline.expectedBefore eine Liste sein.")

def format_expected_sha(value):
    return "<missing>" if value is None else value

def baseline_precondition_conflicts(expected, operations, require_complete=False):
    operation_targets = {op["target"] for op in operations}
    unsupported = sorted(path for path in expected if path not in operation_targets)
    missing_expected = sorted(path for path in operation_targets if path not in expected) if require_complete else []

    conflicts = []
    for rel in sorted(expected):
        target = ensure_inside_root(PROJECT_ROOT / rel)
        expected_sha = expected[rel]
        actual_sha = sha256_file(target)
        if actual_sha != expected_sha:
            conflicts.append((rel, expected_sha, actual_sha))

    return unsupported, missing_expected, conflicts

def validate_baseline_preconditions(manifest, operations):
    expected = expected_before_sha256_map(manifest)
    if not expected:
        return expected

    unsupported, _missing_expected, conflicts = baseline_precondition_conflicts(expected, operations)
    if unsupported:
        fail(
            "BASELINE_CONFLICT: expectedBeforeSha256 enthält Pfade ohne Patch-Operation:\n  "
            + "\n  ".join(unsupported)
        )

    if conflicts:
        lines = ["BASELINE_CONFLICT: Aktueller Dateistand passt nicht zum vom Patch erwarteten Vorzustand."]
        for rel, expected_sha, actual_sha in conflicts:
            lines.append(f"  {rel}")
            lines.append(f"    expectedBeforeSha256: {format_expected_sha(expected_sha)}")
            lines.append(f"    actualSha256:         {format_expected_sha(actual_sha)}")
        fail("\n".join(lines))

    return expected

def validate_live_baseline_preflight(manifest, operations, require_complete=True):
    expected = expected_before_sha256_map(manifest)
    if not expected:
        fail(
            "LIVE_BASELINE_HASH_MISSING: manifest.baseline.expectedBeforeSha256 ist für "
            "den Live-Baseline-Preflight verpflichtend."
        )

    unsupported, missing_expected, conflicts = baseline_precondition_conflicts(
        expected, operations, require_complete=require_complete
    )
    if unsupported:
        fail(
            "LIVE_BASELINE_HASH_UNSUPPORTED: expectedBeforeSha256 enthält Pfade ohne Patch-Operation:\n  "
            + "\n  ".join(unsupported)
        )
    if missing_expected:
        fail(
            "LIVE_BASELINE_HASH_INCOMPLETE: Für diese Patch-Operationen fehlt expectedBeforeSha256:\n  "
            + "\n  ".join(missing_expected)
        )
    if conflicts:
        lines = [
            "LIVE_BASELINE_HASH_MISMATCH: Aktueller Live-Dateistand passt nicht zum "
            "vom Patch erwarteten Vorzustand."
        ]
        for rel, expected_sha, actual_sha in conflicts:
            lines.append(f"  {rel}")
            lines.append(f"    expectedBeforeSha256: {format_expected_sha(expected_sha)}")
            lines.append(f"    actualSha256:         {format_expected_sha(actual_sha)}")
        fail("\n".join(lines))

    return expected

def classify_operation(op, tmp_dir):
    target = ensure_inside_root(PROJECT_ROOT / op["target"])
    if op["type"] == "delete":
        return "deleted" if target.exists() else "delete_missing"
    source = tmp_dir / op["source"]
    if not target.exists():
        return "new"
    if target.is_dir():
        fail(f"Ziel ist ein Verzeichnis und kann nicht überschrieben werden: {op['target']}")
    same_bytes = sha256_file(target) == sha256_file(source)
    source_executable = bool(stat.S_IMODE(source.stat().st_mode) & 0o111)
    target_executable = bool(stat.S_IMODE(target.stat().st_mode) & 0o111)
    return "unchanged" if same_bytes and source_executable == target_executable else "modified"

def copy_before(target_rel, before_root):
    target = PROJECT_ROOT / target_rel
    if target.exists():
        before = before_root / target_rel
        before.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(target, before)

def apply_operations(operations, tmp_dir, archive_dir, dry_run):
    summary = {"new": 0, "modified": 0, "unchanged": 0, "deleted": 0, "delete_missing": 0}
    entries = []
    before_root = archive_dir / "before"
    after_root = archive_dir / "after"

    for op in operations:
        status = classify_operation(op, tmp_dir)
        summary[status] += 1

        target_rel = op["target"]
        target_abs = ensure_inside_root(PROJECT_ROOT / target_rel)
        source_abs = tmp_dir / op["source"] if op["type"] == "file" else None

        entry = {
            "operation": op["type"],
            "path": target_rel,
            "status": status,
            "sha256Before": sha256_file(target_abs),
            "sha256After": sha256_file(source_abs) if source_abs else None,
        }
        entries.append(entry)

        if dry_run:
            continue

        if op["type"] == "file":
            if status in ("modified", "unchanged"):
                copy_before(target_rel, before_root)
            after = after_root / target_rel
            after.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source_abs, after)
            apply_git_executable_mode(source_abs, after)
            target_abs.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source_abs, target_abs)
            apply_git_executable_mode(source_abs, target_abs)
        elif op["type"] == "delete":
            if target_abs.exists():
                if target_abs.is_dir():
                    fail(f"Delete für Verzeichnisse wird nicht unterstützt: {target_rel}")
                copy_before(target_rel, before_root)
                target_abs.unlink()

    return summary, entries

def live_baseline_command(args):
    rest = []
    i = 0
    while i < len(args):
        arg = args[i]
        if arg == "--wait":
            i += 1
        elif arg == "--lock-timeout":
            if i + 1 >= len(args):
                fail("--lock-timeout erwartet eine Sekundenangabe.")
            i += 2
        else:
            rest.append(arg)
            i += 1
    if len(rest) != 1:
        fail("live-baseline erwartet genau ein Patch-ZIP.")

    zip_path = Path(rest[0]).expanduser().resolve()
    tmp_dir = extract_archive(zip_path)
    try:
        manifest, scope, name, patch_id, operations = collect_patch(tmp_dir, zip_path=zip_path)
        expected = validate_live_baseline_preflight(manifest, operations, require_complete=True)
        print("Patch-Live-Baseline-Preflight:")
        print(f"  Projekt:      {PROJECT_ROOT}")
        print(f"  Archiv:       {zip_path}")
        print(f"  Artifact-ID:  {manifest['artifactId']}")
        print(f"  Patch-ID:     {patch_id}")
        print(f"  Scope:        {scope}")
        print(f"  Operationen:  {len(operations)}")
        print(f"  Hash-Regeln:  {len(expected)}")
        print()
        for op in sorted(operations, key=lambda item: item["target"]):
            rel = op["target"]
            expected_sha = expected.get(rel)
            actual_sha = sha256_file(ensure_inside_root(PROJECT_ROOT / rel))
            state = "OK" if expected_sha == actual_sha else "MISMATCH"
            print(f"  [{state}] {rel}")
            print(f"    expectedBeforeSha256: {format_expected_sha(expected_sha)}")
            print(f"    actualSha256:         {format_expected_sha(actual_sha)}")
        print()
        print("Live-Baseline-Preflight abgeschlossen. Alle erwarteten Vorzustands-Hashes passen zum Working Tree.")
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

def apply_command(args):
    dry_run = False
    rest = []
    i = 0
    while i < len(args):
        arg = args[i]
        if arg == "--dry-run":
            dry_run = True
            i += 1
        elif arg == "--wait":
            i += 1
        elif arg == "--lock-timeout":
            if i + 1 >= len(args):
                fail("--lock-timeout erwartet eine Sekundenangabe.")
            i += 2
        else:
            rest.append(arg)
            i += 1
    if len(rest) != 1:
        fail("apply erwartet genau ein Patch-ZIP.")

    zip_path = Path(rest[0]).expanduser().resolve()
    tmp_dir = extract_archive(zip_path)
    try:
        manifest, scope, name, patch_id, operations = collect_patch(tmp_dir, zip_path=zip_path)
        patch_number = patch_id.split("_", 1)[0]
        archive_dir = ARCHIVES_DIR / patch_id

        if archive_dir.exists():
            fail(f"Patch-Archiv existiert bereits: {archive_dir}")

        if not dry_run:
            archive_dir.mkdir(parents=True, exist_ok=False)
            (archive_dir / "source").mkdir(parents=True, exist_ok=True)
            shutil.copy2(zip_path, archive_dir / "source" / zip_path.name)
            write_json(archive_dir / "manifest.json", manifest)

        preview_summary, preview_entries = apply_operations(operations, tmp_dir, archive_dir, True)
        expected_before = {}
        if summary_has_effect(preview_summary):
            expected_before = validate_baseline_preconditions(manifest, operations)
        if dry_run:
            summary, entries = preview_summary, preview_entries
        else:
            summary, entries = apply_operations(operations, tmp_dir, archive_dir, False)
        if expected_before:
            for entry in entries:
                if entry.get("path") in expected_before:
                    entry["expectedBeforeSha256"] = expected_before[entry["path"]]

        log = {
            "schemaVersion": PATCH_MANIFEST_SCHEMA,
            "artifactId": manifest["artifactId"],
            "patchId": patch_id,
            "patchNumber": patch_number,
            "archiveName": zip_path.name,
            "name": name,
            "scope": scope,
            "status": "dry-run" if dry_run else "applied",
            "createdAt": now_iso(),
            "projectRoot": str(PROJECT_ROOT),
            "summary": summary,
            "entries": entries,
            "manifest": manifest,
        }

        if not dry_run:
            write_json(archive_dir / "patch-log.json", log)

        print("Patch-Apply:")
        print(f"  Projekt:      {PROJECT_ROOT}")
        print(f"  Archiv:       {zip_path}")
        print(f"  Artifact-ID:  {manifest['artifactId']}")
        print(f"  Patch-ID:     {patch_id}")
        print(f"  Scope:        {scope}")
        print(f"  Modus:        {'DRY-RUN' if dry_run else 'AUSFÜHREN'}")
        print()
        for entry in entries:
            marker = {
                "new": "[NEW]",
                "modified": "[MODIFIED]",
                "unchanged": "[UNCHANGED]",
                "deleted": "[DELETED]",
                "delete_missing": "[DELETE_MISSING]",
            }.get(entry["status"], "[?]")
            print(f"  {marker:<16}{entry['path']}")
        print()
        print("Zusammenfassung:")
        for key in ["new", "modified", "unchanged", "deleted", "delete_missing"]:
            print(f"  {key}: {summary[key]}")
        if dry_run:
            print("\nDry-run abgeschlossen. Es wurden keine Dateien geändert.")
        else:
            print(f"\nPatch-Log: {archive_dir / 'patch-log.json'}")
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

def list_command():
    dirs = archive_dirs()
    if not dirs:
        print("Keine Patch-Archive vorhanden.")
        return
    print(f"{'NUMMER':<8} {'STATUS':<12} {'NEU':<6} {'GEÄNDERT':<10} {'UNVERÄNDERT':<12} {'GELÖSCHT':<10} {'SCOPE':<30} PATCH")
    for d in dirs:
        log_path = d / "patch-log.json"
        status, summary, scope = "unknown", {}, "-"
        if log_path.exists():
            data = read_json(log_path)
            status = data.get("status", "unknown")
            summary = data.get("summary", {})
            scope = data.get("scope") or "-"
        if (d / "ROLLBACK_DONE").exists():
            status = "rolled_back"
        num = d.name.split("_", 1)[0]
        name = d.name.split("_", 1)[1] if "_" in d.name else d.name
        print(f"{num:<8} {status:<12} {summary.get('new', 0):<6} {summary.get('modified', 0):<10} {summary.get('unchanged', 0):<12} {summary.get('deleted', 0):<10} {scope:<30} {name}")

def show_command(args):
    if len(args) != 1:
        fail("show erwartet genau eine Patch-Referenz.")
    d = resolve_patch_ref(args[0])
    log_path = d / "patch-log.json"
    if not log_path.exists():
        fail(f"Patch-Log fehlt: {log_path}")
    data = read_json(log_path)
    summary = data.get("summary", {})
    artifact_id = data.get("artifactId")
    if artifact_id is None and isinstance(data.get("manifest"), dict):
        artifact_id = data["manifest"].get("artifactId")
    print(f"Artifact-ID:   {artifact_id or '<legacy-v1-missing>'}")
    print(f"Patch-ID:      {data.get('patchId', d.name)}")
    print(f"Archiv:        {data.get('archiveName', '-')}")
    print(f"Erstellt am:   {data.get('createdAt', '-')}")
    print(f"Status:        {'rolled_back' if (d / 'ROLLBACK_DONE').exists() else data.get('status', '-')}")
    print(f"Scope:         {data.get('scope') or '-'}")
    print("Summary:")
    for key in ["new", "modified", "unchanged", "deleted", "delete_missing"]:
        print(f"  {key}: {summary.get(key, 0)}")
    print("\nDateien:")
    for entry in data.get("entries", []):
        print(f"  {entry.get('status','?'):<14}{entry.get('path','?')}")

def rollback_command(args):
    dry_run = False
    rest = []
    i = 0
    while i < len(args):
        arg = args[i]
        if arg == "--dry-run":
            dry_run = True
            i += 1
        elif arg == "--wait":
            i += 1
        elif arg == "--lock-timeout":
            if i + 1 >= len(args):
                fail("--lock-timeout erwartet eine Sekundenangabe.")
            i += 2
        else:
            rest.append(arg)
            i += 1
    if len(rest) != 1:
        fail("rollback erwartet genau eine Patch-Referenz.")
    d = resolve_patch_ref(rest[0])
    log_path = d / "patch-log.json"
    if not log_path.exists():
        fail(f"Patch-Log fehlt: {log_path}")
    if (d / "ROLLBACK_DONE").exists():
        fail(f"Patch wurde bereits zurückgesetzt: {d.name}")

    data = read_json(log_path)
    entries = list(reversed(data.get("entries", [])))

    print("Patch-Rollback:")
    print(f"  Projekt:      {PROJECT_ROOT}")
    print(f"  Patch-ID:     {data.get('patchId', d.name)}")
    print(f"  Modus:        {'DRY-RUN' if dry_run else 'AUSFÜHREN'}\n")

    for entry in entries:
        status = entry.get("status")
        rel = validate_relpath(entry.get("path", ""))
        target = ensure_inside_root(PROJECT_ROOT / rel)
        before = d / "before" / rel

        if status == "new":
            print(f"  [REMOVE]      {rel}")
            if not dry_run and target.exists():
                if target.is_dir():
                    fail(f"Rollback kann Verzeichnis nicht entfernen: {rel}")
                target.unlink()
        elif status in ("modified", "deleted"):
            print(f"  [RESTORE]     {rel}")
            if not before.exists():
                fail(f"Rollback-Snapshot fehlt: {before}")
            if not dry_run:
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(before, target)
        elif status in ("unchanged", "delete_missing"):
            print(f"  [SKIP]        {rel}")
        else:
            fail(f"Unbekannter Entry-Status im Patch-Log: {status}")

    if dry_run:
        print("\nDry-run abgeschlossen. Es wurden keine Dateien geändert.")
    else:
        (d / "ROLLBACK_DONE").write_text(now_iso() + "\n", encoding="utf-8")
        data["status"] = "rolled_back"
        data["rolledBackAt"] = now_iso()
        write_json(log_path, data)
        print("\nRollback abgeschlossen.")


ERROR_SUMMARY_PATTERNS = [
    "ERROR",
    "FAILURE",
    "Failures:",
    "Errors:",
    "Exception",
    "Caused by:",
    "BUILD FAILURE",
    "Failed to execute",
    "Name for argument",
    "AssertionError",
]

AUTO_FULL_TEST_PATTERNS = [
    "pom.xml",
    "build.gradle",
    "build.gradle.kts",
    "settings.gradle",
    "settings.gradle.kts",
    "src/main/java/**",
    "src/test/java/**",
    "src/main/kotlin/**",
    "src/test/kotlin/**",
]

ACCEPT_VERIFY_PROFILES = {"auto", "docs", "tooling", "code"}

def parse_accept_verify_args(args, subject_name):
    subject = None
    tests = []
    full_test = None
    export = True
    tooling_selfcheck = True
    profile = "auto"
    background = False
    wait = False
    lock_timeout = None
    git_commit = False
    git_push = False
    output_format = "human"
    watch_after_start = False
    watch_interval = 5
    watch_timeout = None
    rest = list(args)
    i = 0
    while i < len(rest):
        arg = rest[i]
        if arg == "--test":
            if i + 1 >= len(rest):
                fail("--test erwartet einen Maven-Testselektor.")
            tests.append(rest[i + 1])
            i += 2
        elif arg == "--full-test":
            full_test = True
            i += 1
        elif arg in ("--no-full-test", "--skip-full-test"):
            full_test = False
            i += 1
        elif arg == "--profile":
            if i + 1 >= len(rest):
                fail("--profile erwartet einen Wert: auto, docs, tooling oder code.")
            profile = rest[i + 1]
            if profile not in ACCEPT_VERIFY_PROFILES:
                fail(f"Unbekanntes Profil für {COMMAND}: {profile}")
            i += 2
        elif arg == "--export":
            export = True
            i += 1
        elif arg == "--no-export":
            export = False
            i += 1
        elif arg in ("--skip-tooling-selfcheck", "--no-tooling-selfcheck"):
            tooling_selfcheck = False
            i += 1
        elif arg == "--commit":
            if COMMAND != "accept":
                fail("--commit ist nur für accept erlaubt.")
            git_commit = True
            i += 1
        elif arg == "--push":
            if COMMAND != "accept":
                fail("--push ist nur für accept erlaubt.")
            git_commit = True
            git_push = True
            i += 1
        elif arg == "--background":
            background = True
            i += 1
        elif arg in ("--wait", "--wait-for-lock"):
            wait = True
            i += 1
        elif arg == "--format":
            if i + 1 >= len(rest):
                fail("--format erwartet human, env oder json.", 2)
            output_format = rest[i + 1]
            if output_format not in ("human", "env", "json"):
                fail(f"Nicht unterstuetztes Startformat: {output_format}", 2)
            i += 2
        elif arg == "--watch":
            watch_after_start = True
            i += 1
        elif arg == "--watch-interval":
            if i + 1 >= len(rest):
                fail("--watch-interval erwartet Sekunden.", 2)
            watch_interval = safe_int(rest[i + 1])
            if watch_interval is None or watch_interval < 1:
                fail("--watch-interval muss mindestens eine Sekunde betragen.", 2)
            i += 2
        elif arg == "--watch-timeout":
            if i + 1 >= len(rest):
                fail("--watch-timeout erwartet Sekunden.", 2)
            watch_timeout = safe_int(rest[i + 1])
            if watch_timeout is None or watch_timeout < 0:
                fail("--watch-timeout darf nicht negativ sein.", 2)
            i += 2
        elif arg == "--lock-timeout":
            if i + 1 >= len(rest):
                fail("--lock-timeout erwartet eine Sekundenangabe.")
            try:
                lock_timeout = int(rest[i + 1])
            except ValueError:
                fail(f"Ungültiger Wert für --lock-timeout: {rest[i + 1]}")
            if lock_timeout < 0:
                fail("--lock-timeout darf nicht negativ sein.")
            i += 2
        elif arg.startswith("--"):
            fail(f"Unbekannte Option für {COMMAND}: {arg}")
        else:
            if subject is not None:
                fail(f"{COMMAND} erwartet genau ein {subject_name}. Unerwartet: {arg}")
            subject = arg
            i += 1
    if subject is None:
        fail(f"{COMMAND} erwartet genau ein {subject_name}.")
    if not background and (output_format != "human" or watch_after_start):
        fail("--format und --watch sind nur zusammen mit --background zulaessig.", 2)
    if watch_after_start and output_format != "human":
        fail("--watch verwendet kompakte Human-Ausgabe; --format env|json ohne --watch verwenden.", 2)
    return {
        "subject": subject,
        "tests": tests,
        "fullTest": full_test,
        "export": export,
        "toolingSelfcheck": tooling_selfcheck,
        "profile": profile,
        "background": background,
        "wait": wait,
        "lockTimeout": lock_timeout,
        "gitCommit": git_commit,
        "gitPush": git_push,
        "outputFormat": output_format,
        "watchAfterStart": watch_after_start,
        "watchInterval": watch_interval,
        "watchTimeout": watch_timeout,
    }

def needs_full_test_for_targets(target_paths):
    return any(
        path_matches(target, AUTO_FULL_TEST_PATTERNS)
        for target in target_paths
    )

def resolve_validation_profile(options, target_paths):
    options = dict(options)
    profile = options["profile"]
    if options["fullTest"] is None:
        if profile == "code":
            options["fullTest"] = True
        elif profile in ("docs", "tooling"):
            options["fullTest"] = False
        else:
            options["fullTest"] = needs_full_test_for_targets(target_paths)
    return options

def target_paths_from_zip(zip_path):
    tmp_dir = extract_archive(zip_path)
    try:
        _manifest, _scope, _name, _patch_id, operations = collect_patch(tmp_dir, zip_path=zip_path)
        return [op["target"] for op in operations]
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

def target_paths_from_patch_dir(patch_dir):
    log_path = patch_dir / "patch-log.json"
    if not log_path.exists():
        return []
    data = read_json(log_path)
    entries = data.get("entries", [])
    paths = []
    for entry in entries:
        path = entry.get("path")
        if isinstance(path, str):
            paths.append(path)
    return paths

def inspect_patch_identity(zip_path):
    tmp_dir = extract_archive(zip_path)
    try:
        manifest, scope, name, patch_id, operations = collect_patch(tmp_dir, zip_path=zip_path)
        return {
            "manifest": manifest,
            "artifactId": manifest["artifactId"],
            "scope": scope,
            "name": name,
            "patchId": patch_id,
            "operations": operations,
            "targetPaths": [op["target"] for op in operations],
            "patchSha256": sha256_file(zip_path),
        }
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


def inspect_patch_zip(zip_path):
    tmp_dir = extract_archive(zip_path)
    try:
        manifest, scope, name, patch_id, operations = collect_patch(tmp_dir, zip_path=zip_path)
        summary, entries = apply_operations(operations, tmp_dir, ARCHIVES_DIR / "__dry_run_inspection__", True)
        return {
            "manifest": manifest,
            "artifactId": manifest["artifactId"],
            "scope": scope,
            "name": name,
            "patchId": patch_id,
            "operations": operations,
            "targetPaths": [op["target"] for op in operations],
            "summary": summary,
            "entries": entries,
            "patchSha256": sha256_file(zip_path),
        }
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

def summary_has_effect(summary):
    return any(summary.get(key, 0) > 0 for key in ("new", "modified", "deleted"))

def patch_log_has_effect(data):
    return summary_has_effect(data.get("summary", {}))

def find_applied_patch_by_name(name):
    fallback = None
    effective = None
    for patch_dir in archive_dirs():
        if (patch_dir / "ROLLBACK_DONE").exists():
            continue
        log_path = patch_dir / "patch-log.json"
        if not log_path.exists():
            continue
        data = read_json(log_path)
        if data.get("status") != "applied" or data.get("name") != name:
            continue
        fallback = patch_dir
        if patch_log_has_effect(data):
            effective = patch_dir
    return effective or fallback


def git_commit_exists(commit_ref):
    if not commit_ref:
        return False
    result = subprocess.run(
        ["git", "cat-file", "-e", f"{commit_ref}^{{commit}}"],
        cwd=PROJECT_ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return result.returncode == 0


def canonical_accept_fields(patch_id):
    return read_summary_fields(accept_log_base() / patch_id / "SUMMARY.txt")


def archived_patch_data(patch_id):
    patch_dir = ARCHIVES_DIR / patch_id
    log_path = patch_dir / "patch-log.json"
    if not log_path.is_file() or (patch_dir / "ROLLBACK_DONE").exists():
        return None
    try:
        return json.loads(log_path.read_text(encoding="utf-8"))
    except Exception:
        return None


def applied_identity_state(patch_identity):
    patch_id = patch_identity["patchId"]
    artifact_id = patch_identity["artifactId"]
    data = archived_patch_data(patch_id)
    if data is None or data.get("status") != "applied":
        return None
    archived_id = data.get("artifactId")
    if archived_id is None and isinstance(data.get("manifest"), dict):
        archived_id = data["manifest"].get("artifactId")
    if archived_id != artifact_id:
        fail(
            "PATCH_IDENTITY_CONFLICT: patchId is already archived with another artifactId.\n"
            f"  patchId: {patch_id}\n"
            f"  requestedArtifactId: {artifact_id}\n"
            f"  archivedArtifactId:  {archived_id}"
        )
    fields = canonical_accept_fields(patch_id)
    commit_status = fields.get("GIT_COMMIT_STATUS", "-")
    commit_hash = fields.get("GIT_COMMIT_HASH", "-")
    commit_ok = commit_status != "COMMITTED" or git_commit_exists(commit_hash)
    return {
        "status": "ALREADY_APPLIED",
        "patchId": patch_id,
        "artifactId": artifact_id,
        "summary": str(accept_log_base() / patch_id / "SUMMARY.txt"),
        "acceptStatus": fields.get("STATUS", "ARCHIVED"),
        "commitStatus": commit_status,
        "commitHash": commit_hash,
        "commitVerified": commit_ok,
    }


def find_active_run(patch_id, artifact_id=None):
    candidates = []
    pointer_path = run_pointer_dir() / f"{sanitize_name(patch_id)}.json"
    if pointer_path.is_file():
        try:
            pointer = json.loads(pointer_path.read_text(encoding="utf-8"))
            log_dir = Path(pointer.get("logDir", ""))
            if log_dir.is_dir():
                candidates.append(load_run_record(log_dir))
        except Exception:
            pass
    for base in (accept_log_base(), validation_log_base()):
        for run_file in base.glob("*/run.json"):
            data = load_run_record(run_file.parent)
            if data.get("patchId") == patch_id:
                candidates.append(data)
    candidates = [
        data for data in candidates
        if data and (artifact_id is None or data.get("artifactId") in (None, artifact_id))
    ]
    candidates.sort(key=lambda data: data.get("updatedAt", ""), reverse=True)
    for data in candidates:
        if run_is_active(data):
            return data
    return None

def start_state_env_lines(state):
    keys = (
        ("STATUS", "status"),
        ("COMMAND", "command"),
        ("RUN_ID", "runId"),
        ("PATCH_ID", "patchId"),
        ("ARTIFACT_ID", "artifactId"),
        ("PID", "pid"),
        ("PHASE", "phase"),
        ("GIT_COMMIT_STATUS", "commitStatus"),
        ("GIT_COMMIT_HASH", "commitHash"),
        ("SUMMARY", "summary"),
        ("LOG_DIR", "logDir"),
        ("WATCH_COMMAND", "watchCommand"),
        ("WAIT_COMMAND", "waitCommand"),
    )
    return [f"{name}={state.get(key, '-')}" for name, key in keys]


def print_start_state(state, output_format="human", label="Patch-Accept"):
    if output_format == "json":
        print(json.dumps(state, indent=2, ensure_ascii=False, sort_keys=True))
        sys.stdout.flush()
        return
    if output_format == "env":
        print("\n".join(start_state_env_lines(state)))
        sys.stdout.flush()
        return

    print(f"{label}:")
    print(f"  Status:       {state.get('status', '-')}")
    if state.get("runId") not in (None, "-"):
        print(f"  Run-ID:       {state.get('runId')}")
    print(f"  Patch-ID:     {state.get('patchId', '-')}")
    if state.get("artifactId") not in (None, "-"):
        print(f"  Artifact-ID:  {state.get('artifactId')}")
    if state.get("pid") not in (None, "-"):
        print(f"  PID:          {state.get('pid')}")
    if state.get("phase") not in (None, "-"):
        print(f"  Phase:        {state.get('phase')}")
    if state.get("commitStatus") not in (None, "-"):
        print(f"  Git-Status:   {state.get('commitStatus')}")
    if state.get("commitHash") not in (None, "-"):
        print(f"  Git-Commit:   {state.get('commitHash')}")
    if state.get("summary") not in (None, "-"):
        print(f"  Summary:      {state.get('summary')}")
    if state.get("watchCommand") not in (None, "-"):
        print(f"  Watch:        {state.get('watchCommand')}")
    if state.get("waitCommand") not in (None, "-"):
        print(f"  Wait:         {state.get('waitCommand')}")
    sys.stdout.flush()


def print_already_applied_state(state, output_format="human"):
    start_state = {
        "status": "ALREADY_APPLIED",
        "command": "accept",
        "runId": state.get("runId", "-"),
        "patchId": state.get("patchId", "-"),
        "artifactId": state.get("artifactId", "-"),
        "pid": "-",
        "phase": "COMPLETE",
        "commitStatus": state.get("commitStatus", "-"),
        "commitHash": state.get("commitHash", "-"),
        "summary": state.get("summary", "-"),
        "logDir": str(Path(state.get("summary", "-")).parent) if state.get("summary") not in (None, "-") else "-",
        "watchCommand": "-",
        "waitCommand": "-",
    }
    print_start_state(start_state, output_format, label="Patch-Accept")
    return start_state


def print_already_running_state(state, output_format="human", command_name="accept"):
    run_id = state.get("runId", state.get("patchId", "-"))
    start_state = {
        "status": "ALREADY_RUNNING",
        "command": command_name,
        "runId": run_id,
        "patchId": state.get("patchId", "-"),
        "artifactId": state.get("artifactId", "-"),
        "pid": state.get("pid", "-"),
        "phase": state.get("phase", "-"),
        "commitStatus": state.get("commitStatus", "-"),
        "commitHash": state.get("commitHash", "-"),
        "summary": state.get("summary", "-"),
        "logDir": state.get("logDir", "-"),
        "watchCommand": f"./bin/patch.sh watch {run_id}",
        "waitCommand": f"./bin/patch.sh wait {run_id}",
    }
    label = "Patch-Verify" if command_name == "verify" else "Patch-Accept"
    print_start_state(start_state, output_format, label=label)
    return start_state

def latest_full_export():
    export_dir = PROJECT_ROOT / "exports" / "text"
    if not export_dir.exists():
        return None
    exports = sorted(export_dir.glob("*_export_full_*.zip"), key=lambda p: p.stat().st_mtime, reverse=True)
    return exports[0] if exports else None

def accept_log_base():
    base = PROJECT_ROOT / "patches" / "logs" / "accept"
    base.mkdir(parents=True, exist_ok=True)
    return base


def validation_log_base():
    base = PROJECT_ROOT / "patches" / "logs" / "validation"
    base.mkdir(parents=True, exist_ok=True)
    return base


def run_state_root():
    root = project_relative_or_absolute_path(env_value("PATCH_RUN_STATE_ROOT"), "patches/runtime/patch-runs")
    root.mkdir(parents=True, exist_ok=True)
    return root


def run_pointer_dir():
    path = run_state_root() / "by-patch"
    path.mkdir(parents=True, exist_ok=True)
    return path


def make_run_id(command_name, patch_id):
    stamp = datetime.now(timezone.utc).astimezone().strftime("%Y%m%dT%H%M%S")
    return f"{stamp}-{sanitize_name(command_name)}-{sanitize_name(patch_id)}-{uuid.uuid4().hex[:8]}"


def write_invocation_record(log_dir, command_name, subject, patch_identity, options):
    log_dir = Path(log_dir).resolve()
    path = log_dir / "invocation.json"
    if path.is_file():
        return path
    patch_identity = patch_identity or {}
    subject_name = Path(str(subject)).name
    data = {
        "schemaVersion": "springmaster.patch-invocation.v1",
        "runId": log_dir.name,
        "command": command_name,
        "subjectType": "patch-zip" if command_name == "accept" else "patch-ref",
        "subjectName": subject_name,
        "patchFileName": subject_name if command_name == "accept" else None,
        "patchId": patch_identity.get("patchId"),
        "artifactId": patch_identity.get("artifactId"),
        "patchSha256": patch_identity.get("patchSha256"),
        "profileRequested": options.get("profile"),
        "testsRequested": list(options.get("tests") or []),
        "fullTestRequested": options.get("fullTest"),
        "exportRequested": bool(options.get("export")),
        "toolingSelfcheckRequested": bool(options.get("toolingSelfcheck")),
        "commitRequested": bool(options.get("gitCommit")),
        "pushRequested": bool(options.get("gitPush")),
        "backgroundRequested": bool(options.get("background")),
        "waitForLockRequested": bool(options.get("wait")),
        "lockTimeoutSeconds": options.get("lockTimeout"),
        "startFormat": options.get("outputFormat", "human"),
        "watchAfterStart": bool(options.get("watchAfterStart")),
        "requestedAt": now_iso(),
    }
    write_json(path, {key: value for key, value in data.items() if value is not None})
    return path


def run_record_path(log_dir):
    return Path(log_dir) / "run.json"


def current_git_head():
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=PROJECT_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
    )
    return result.stdout.strip() if result.returncode == 0 else None


def write_run_record(log_dir, **updates):
    log_dir = Path(log_dir).resolve()
    path = run_record_path(log_dir)
    data = {}
    if path.is_file():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            data = {}
    now = now_iso()
    data.setdefault("schemaVersion", "springmaster.patch-run.v1")
    data.setdefault("runId", log_dir.name)
    data.setdefault("startedAt", now)
    data.setdefault("projectRoot", str(PROJECT_ROOT))
    data.setdefault("host", socket.gethostname())
    data.setdefault("pid", os.getpid())
    data.setdefault("baselineHead", current_git_head())
    data.update({key: value for key, value in updates.items() if value is not None})
    data["updatedAt"] = now
    write_json(path, data)

    patch_id = data.get("patchId")
    if patch_id and patch_id != "-":
        pointer = {
            "schemaVersion": "springmaster.patch-run-pointer.v1",
            "patchId": patch_id,
            "artifactId": data.get("artifactId"),
            "runId": data.get("runId"),
            "command": data.get("command"),
            "status": data.get("status"),
            "phase": data.get("phase"),
            "pid": data.get("pid"),
            "logDir": str(log_dir),
            "summary": str(log_dir / "SUMMARY.txt"),
            "updatedAt": now,
        }
        write_json(run_pointer_dir() / f"{sanitize_name(patch_id)}.json", pointer)
    return data


def load_run_record(log_dir):
    path = run_record_path(log_dir)
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def run_is_active(data):
    if data.get("status") != "RUNNING":
        return False
    if data.get("host") and data.get("host") != socket.gethostname():
        return True
    return pid_is_alive(data.get("pid"))


def command_to_text(cmd, shell=False):
    return cmd if shell else " ".join(str(part) for part in cmd)

def validation_subprocess_env():
    env = dict(os.environ)
    for key in ("PATCH_ACCEPT_WORKTREE_CHILD", "PATCH_ACCEPT_LOG_DIR", "PATCH_BACKGROUND_CHILD"):
        env.pop(key, None)
    return env


def run_process_step(step_name, cmd, log_file, shell=False, env=None):
    log_file.parent.mkdir(parents=True, exist_ok=True)
    with log_file.open("w", encoding="utf-8") as out:
        out.write(f"== {step_name} ==\n")
        out.write(f"$ {command_to_text(cmd, shell=shell)}\n\n")
        out.flush()
        result = subprocess.run(
            cmd,
            cwd=PROJECT_ROOT,
            shell=shell,
            stdout=out,
            stderr=subprocess.STDOUT,
            text=True,
            env=env,
        )
    return result.returncode

def existing_relative_files(patterns):
    files = []
    for pattern in patterns:
        files.extend(sorted(PROJECT_ROOT.glob(pattern)))
    result = []
    for path in files:
        if path.is_file():
            result.append(path.relative_to(PROJECT_ROOT).as_posix())
    return result

def configured_tooling_selfcheck_command():
    configured = env_value("PATCH_TOOLING_SELFCHECK_COMMAND")
    if configured is not None:
        if str(configured).strip().lower() in ("none", "skip", "false", "0"):
            return None
        return str(configured)
    if (PROJECT_ROOT / "bin" / "tooling-selfcheck.sh").is_file():
        return "./bin/tooling-selfcheck.sh --no-export"
    return None

def run_tooling_verification(log_dir):
    tooling_log = log_dir / "tooling.log"
    steps = []
    shell_files = existing_relative_files(["bin/*.sh", "bin/lib/core/*.sh", "bin/lib/dbtool/*.sh"])
    if shell_files:
        steps.append(("Shell syntax", ["bash", "-n"] + shell_files, False))
    if (PROJECT_ROOT / "bin" / "patch.py").is_file():
        steps.append(("Python syntax", ["python3", "-m", "py_compile", "./bin/patch.py"], False))
    tooling_cmd = configured_tooling_selfcheck_command()
    if tooling_cmd:
        steps.append(("Tooling selfcheck", tooling_cmd, True))

    with tooling_log.open("w", encoding="utf-8") as out:
        if not steps:
            out.write("No project-local tooling verification steps configured.\n")
            return 0
        for step_name, cmd, shell in steps:
            out.write(f"\n== {step_name} ==\n")
            out.write(f"$ {command_to_text(cmd, shell=shell)}\n\n")
            out.flush()
            result = subprocess.run(
                cmd,
                cwd=PROJECT_ROOT,
                shell=shell,
                stdout=out,
                stderr=subprocess.STDOUT,
                text=True,
                env=validation_subprocess_env(),
            )
            if result.returncode != 0:
                return result.returncode
    return 0

def extract_first_failure_line(log_dir):
    preferred = (
        "<<< FAILURE!",
        "<<< ERROR!",
        "AssertionError",
        "Caused by:",
        "BUILD FAILURE",
        "Failed to execute goal",
        "[ERROR]",
    )
    log_files = sorted(Path(log_dir).rglob("*.log"), key=lambda path: path.stat().st_mtime if path.exists() else 0)
    for marker in preferred:
        for log_file in log_files:
            if log_file.name == "summary.log":
                continue
            try:
                for raw_line in log_file.read_text(encoding="utf-8", errors="replace").splitlines():
                    line = raw_line.strip()
                    if marker in line:
                        return line[:500], str(log_file)
            except OSError:
                continue
    return None, None


def extract_error_summary(log_dir):
    lines = []
    for log_file in sorted(log_dir.glob("*.log")):
        if log_file.name == "summary.log":
            continue
        try:
            content = log_file.read_text(encoding="utf-8", errors="replace").splitlines()
        except Exception:
            continue
        matches = []
        for idx, line in enumerate(content):
            if any(pattern in line for pattern in ERROR_SUMMARY_PATTERNS):
                start = max(0, idx - 2)
                end = min(len(content), idx + 3)
                matches.extend(content[start:end])
        if matches:
            lines.append(f"## {log_file.name}")
            compact = []
            for line in matches:
                if line not in compact:
                    compact.append(line)
            lines.extend(compact[:80])
    return "\n".join(lines[-120:])

def bash_single_quote(value):
    return "'" + str(value).replace("'", "'\"'\"'") + "'"

def commit_candidate_paths_from_patch(patch_id):
    paths = []
    try:
        patch_dir = resolve_patch_ref(patch_id)
        data = read_json(patch_dir / "patch-log.json")
    except Exception:
        return []
    excluded_prefixes = ("exports/", "target/", "build/", "patches/runtime/")
    for entry in data.get("entries", []):
        path = entry.get("path")
        if not isinstance(path, str):
            continue
        rel = validate_relpath(path)
        if rel.startswith(excluded_prefixes):
            continue
        if rel not in paths:
            paths.append(rel)
    return sorted(paths)

def generate_git_commit_script(log_dir, patch_id):
    if not patch_id:
        return None
    paths = commit_candidate_paths_from_patch(patch_id)
    if not paths:
        return None
    commit_message = f"Apply {patch_id}"
    script_path = log_dir / "git-commit.sh"
    array_lines = "\n".join(f"  {bash_single_quote(path)}" for path in paths)
    script = (
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n\n"
        f"cd {bash_single_quote(PROJECT_ROOT)}\n\n"
        "echo \"Git-Status vor Commit:\"\n"
        "git status --short\n\n"
        "files=(\n"
        f"{array_lines}\n"
        ")\n\n"
        "allowed_file=\"$(mktemp)\"\n"
        "trap 'rm -f \"${allowed_file}\"' EXIT\n"
        "printf '%s\\n' \"${files[@]}\" > \"${allowed_file}\"\n\n"
        "unexpected_staged=()\n"
        "while IFS= read -r staged_path; do\n"
        "  [[ -z \"${staged_path}\" ]] && continue\n"
        "  if ! grep -Fx -- \"${staged_path}\" \"${allowed_file}\" >/dev/null; then\n"
        "    unexpected_staged+=(\"${staged_path}\")\n"
        "  fi\n"
        "done < <(git diff --cached --name-only)\n\n"
        "if (( ${#unexpected_staged[@]} > 0 )); then\n"
        "  echo \"GIT_INDEX_DIRTY: staged files outside this patch would be committed.\"\n"
        "  printf '  %s\\n' \"${unexpected_staged[@]}\"\n"
        "  echo \"Bitte fremde staged Änderungen committen oder unstagen und dieses Skript danach erneut ausführen.\"\n"
        "  exit 23\n"
        "fi\n\n"
        "echo \"Stage patchbezogene Dateien:\"\n"
        "printf '  %s\\n' \"${files[@]}\"\n"
        "git add -- \"${files[@]}\"\n\n"
        "echo \"Git-Status nach Staging:\"\n"
        "git status --short\n\n"
        f"git commit -m {bash_single_quote(commit_message)}\n"
    )
    script_path.write_text(script, encoding="utf-8")
    script_path.chmod(0o755)
    return script_path


def git_log_path(log_dir):
    return log_dir / "git.log"

def git_run(args, log_dir=None, check=False):
    cmd = ["git"] + list(args)
    result = subprocess.run(
        cmd,
        cwd=PROJECT_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    if log_dir is not None:
        with git_log_path(log_dir).open("a", encoding="utf-8") as out:
            out.write(f"$ {command_to_text(cmd)}\n")
            out.write(result.stdout or "")
            if result.stdout and not result.stdout.endswith("\n"):
                out.write("\n")
            out.write(f"rc={result.returncode}\n\n")
    if check and result.returncode != 0:
        raise RuntimeError(f"Git command failed rc={result.returncode}: {command_to_text(cmd)}")
    return result

def is_git_worktree(log_dir=None):
    result = git_run(["rev-parse", "--is-inside-work-tree"], log_dir=log_dir)
    return result.returncode == 0 and result.stdout.strip() == "true"

def parse_git_porcelain_paths(output):
    paths = []
    for line in output.splitlines():
        if not line:
            continue
        raw = line[3:] if len(line) > 3 else ""
        if " -> " in raw:
            raw = raw.split(" -> ", 1)[1]
        raw = raw.strip()
        if raw.startswith('"') and raw.endswith('"'):
            raw = raw[1:-1]
        if raw:
            paths.append(raw)
    return paths

def relative_log_prefix(log_dir):
    try:
        rel = log_dir.resolve().relative_to(PROJECT_ROOT).as_posix()
    except Exception:
        return None
    return rel.rstrip("/") + "/"

def git_status_paths(log_dir=None, ignore_accept_log=True):
    result = git_run(["status", "--porcelain=v1", "--untracked-files=all"], log_dir=log_dir)
    if result.returncode != 0:
        raise RuntimeError("Git status failed")
    paths = parse_git_porcelain_paths(result.stdout)
    if not ignore_accept_log:
        return paths
    log_prefix = relative_log_prefix(log_dir) if log_dir is not None else None
    ignored_prefixes = ["patches/runtime/"]
    if log_prefix:
        ignored_prefixes.append(log_prefix)
    return [path for path in paths if not any(path.startswith(prefix) for prefix in ignored_prefixes)]

def validate_patch_scoped_whitespace(log_dir, paths, staged=False):
    paths = sorted({validate_relpath(path) for path in paths if isinstance(path, str)})
    if not paths or not is_git_worktree(log_dir=log_dir):
        return 0

    if not staged:
        untracked = git_run(
            ["ls-files", "--others", "--exclude-standard", "--", *paths],
            log_dir=log_dir,
        )
        if untracked.returncode != 0:
            return untracked.returncode
        intent_paths = [line.strip() for line in untracked.stdout.splitlines() if line.strip()]
        if intent_paths:
            intent = git_run(["add", "-N", "--", *intent_paths], log_dir=log_dir)
            if intent.returncode != 0:
                return intent.returncode

    cmd = ["git", "diff"]
    if staged:
        cmd.append("--cached")
    cmd.extend(["--check", "--", *paths])
    return run_process_step(
        "Patch-scoped whitespace check",
        cmd,
        Path(log_dir) / ("whitespace-staged.log" if staged else "whitespace.log"),
        env=validation_subprocess_env(),
    )


def ensure_git_clean_before_commit(log_dir):
    if not is_git_worktree(log_dir=log_dir):
        fail("GIT_NOT_AVAILABLE: --commit erfordert ein Git-Repository im Projektroot.")
    dirty = git_status_paths(log_dir=log_dir, ignore_accept_log=True)
    if dirty:
        with git_log_path(log_dir).open("a", encoding="utf-8") as out:
            out.write("GIT_WORKTREE_DIRTY before patch accept --commit:\n")
            for path in dirty:
                out.write(f"  {path}\n")
        fail("GIT_WORKTREE_DIRTY: --commit erfordert einen sauberen Working Tree vor dem Patch. Details stehen in git.log.")

def git_commit_metadata(patch_id):
    patch_dir = resolve_patch_ref(patch_id)
    data = read_json(patch_dir / "patch-log.json")
    scope = data.get("scope") or "patch"
    name = data.get("name") or patch_id
    return data, scope, name

def execute_git_commit(log_dir, patch_id, latest_export_path=None, push=False):
    if not is_git_worktree(log_dir=log_dir):
        fail("GIT_NOT_AVAILABLE: --commit erfordert ein Git-Repository im Projektroot.")
    paths = commit_candidate_paths_from_patch(patch_id)
    if not paths:
        return {"status": "SKIPPED", "hash": None, "pushStatus": "SKIPPED", "message": "no patch candidate paths"}

    data, scope, name = git_commit_metadata(patch_id)
    commit_message = f"patch({scope}): {patch_id}"
    commit_body = "\n".join([
        f"Artifact-ID: {data.get('artifactId') or data.get('manifest', {}).get('artifactId', '-')}",
        f"Patch-ID: {patch_id}",
        f"Name: {name}",
        f"Scope: {scope}",
        f"Archive: {data.get('archiveName', '-')}",
        f"Export: {latest_export_path or '-'}",
    ])

    allowed = set(paths)
    git_run(["add", "--"] + paths, log_dir=log_dir, check=True)
    whitespace_rc = validate_patch_scoped_whitespace(log_dir, paths, staged=True)
    if whitespace_rc != 0:
        fail(
            "GIT_WHITESPACE_ERROR: staged patch lines contain trailing whitespace or "
            "space-before-tab errors. Details stehen in whitespace-staged.log."
        )
    staged_result = git_run(["diff", "--cached", "--name-only"], log_dir=log_dir, check=True)
    staged = [path for path in staged_result.stdout.splitlines() if path.strip()]
    unexpected = [path for path in staged if path not in allowed]
    if unexpected:
        with git_log_path(log_dir).open("a", encoding="utf-8") as out:
            out.write("GIT_INDEX_DIRTY after patch staging:\n")
            for path in unexpected:
                out.write(f"  {path}\n")
        fail("GIT_INDEX_DIRTY: Der Git-Index enthält Dateien außerhalb der Patch-Dateiliste. Details stehen in git.log.")
    if not staged:
        return {"status": "NO_CHANGES", "hash": None, "pushStatus": "SKIPPED", "message": "nothing staged"}

    git_run(["commit", "-m", commit_message, "-m", commit_body], log_dir=log_dir, check=True)
    head = git_run(["rev-parse", "--short", "HEAD"], log_dir=log_dir, check=True).stdout.strip()
    push_status = "SKIPPED"
    if push:
        git_run(["push"], log_dir=log_dir, check=True)
        push_status = "PUSHED"
    return {"status": "COMMITTED", "hash": head, "pushStatus": push_status, "message": commit_message}

def write_accept_summary(
    log_dir,
    status,
    command_name,
    patch_id=None,
    failed_step=None,
    latest_export_path=None,
    options=None,
    git_commit_script=None,
    git_commit_result=None,
    extra_fields=None,
):
    log_dir = Path(log_dir)
    summary_path = log_dir / "summary.log"
    error_summary = extract_error_summary(log_dir) if status not in ("SUCCESS", "ALREADY_APPLIED") else ""
    options = options or {}
    extra_fields = extra_fields or {}
    run_data = load_run_record(log_dir)
    phase = extra_fields.get("PHASE") or ("COMPLETE" if status in ("SUCCESS", "ALREADY_APPLIED") else "FAILED")
    resolved_patch_id = patch_id or run_data.get("patchId") or "-"
    lines = [
        f"STATUS={status}",
        f"COMMAND={command_name}",
        f"RUN_ID={run_data.get('runId', log_dir.name)}",
        f"PATCH_ID={resolved_patch_id}",
        f"ARTIFACT_ID={options.get('artifactId') or run_data.get('artifactId') or '-'}",
        f"PATCH_SHA256={options.get('patchSha256') or run_data.get('patchSha256') or '-'}",
        f"FAILED_STEP={failed_step or '-'}",
        f"PHASE={phase}",
        f"PROFILE={options.get('profile', '-')}",
        f"FULL_TEST={options.get('fullTest', '-')}",
        f"EXPORT={options.get('export', '-')}",
        f"BACKGROUND={options.get('background', '-')}",
        f"WAIT_FOR_LOCK={options.get('wait', '-')}",
        f"PID={run_data.get('pid', os.getpid())}",
        f"BASELINE_HEAD={options.get('baselineHead') or run_data.get('baselineHead') or '-'}",
        f"LOG_DIR={log_dir}",
        f"LATEST_EXPORT={latest_export_path or '-'}",
        f"GIT_COMMIT_SCRIPT={git_commit_script or '-'}",
        f"GIT_COMMIT_STATUS={(git_commit_result or {}).get('status', '-')}",
        f"GIT_COMMIT_HASH={(git_commit_result or {}).get('hash', '-')}",
        f"GIT_PUSH_STATUS={(git_commit_result or {}).get('pushStatus', '-')}",
        f"UPDATED_AT={now_iso()}",
    ]
    for key, value in extra_fields.items():
        if key == "PHASE":
            continue
        normalized_key = str(key).strip().upper()
        if not re.fullmatch(r"[A-Z][A-Z0-9_]*", normalized_key):
            continue
        normalized_value = str(value).replace("\r", " ").replace("\n", " ")
        lines.append(f"{normalized_key}={normalized_value}")
    if error_summary:
        lines.append("")
        lines.append("ERROR_SUMMARY:")
        lines.append(error_summary)
    content = "\n".join(lines) + "\n"
    atomic_write_text(summary_path, content)
    atomic_write_text(log_dir / "SUMMARY.txt", content)
    atomic_write_text(log_dir / "STATUS.txt", status + "\n")
    write_run_record(
        log_dir,
        command=command_name,
        status=status,
        phase=phase,
        patchId=resolved_patch_id,
        artifactId=options.get("artifactId") or run_data.get("artifactId"),
        patchSha256=options.get("patchSha256") or run_data.get("patchSha256"),
        failedStep=failed_step,
        commitStatus=(git_commit_result or {}).get("status"),
        commitHash=(git_commit_result or {}).get("hash"),
        pushStatus=(git_commit_result or {}).get("pushStatus"),
        summary=str(log_dir / "SUMMARY.txt"),
    )
    return summary_path


def print_accept_result(status, command_name, log_dir, patch_id=None, latest_export_path=None, failed_step=None, options=None, git_commit_script=None, git_commit_result=None):
    label = "Patch-Accept" if command_name == "accept" else "Patch-Verify"
    options = options or {}
    print(f"{label}:")
    print(f"  Status:       {status}")
    if patch_id:
        print(f"  Patch-ID:     {patch_id}")
    if failed_step:
        print(f"  Failed-Step:  {failed_step}")
    if options:
        print(f"  Profile:      {options.get('profile')}")
        print(f"  Full-Test:    {options.get('fullTest')}")
        print(f"  Export:       {options.get('export')}")
        if command_name == "accept":
            print(f"  Git-Commit:   {options.get('gitCommit')}")
            print(f"  Git-Push:     {options.get('gitPush')}")
    print(f"  Summary:      {log_dir / 'SUMMARY.txt'}")
    print(f"  Log:          {log_dir}")
    if latest_export_path:
        print(f"  Export-Pfad:  {latest_export_path}")
    if git_commit_script:
        print(f"  Git-Script:   {git_commit_script}")
    if git_commit_result:
        print(f"  Git-Status:   {git_commit_result.get('status')}")
        if git_commit_result.get('hash'):
            print(f"  Git-Commit:   {git_commit_result.get('hash')}")
        print(f"  Git-Push:     {git_commit_result.get('pushStatus')}")
    if status not in ("SUCCESS", "ALREADY_APPLIED"):
        error_summary = extract_error_summary(log_dir)
        if error_summary:
            print()
            print("Fehlerauszug:")
            print(error_summary)

def configured_test_selector_command(test_selector):
    template = env_value("PATCH_TEST_SELECTOR_COMMAND_TEMPLATE", "mvn -B -ntp test -Dtest={test}")
    return str(template).replace("{test}", shlex.quote(test_selector))

def configured_full_test_command():
    return env_value("PATCH_FULL_TEST_COMMAND", "mvn -B -ntp test")

def configured_export_command():
    return env_value("PATCH_EXPORT_COMMAND", "./bin/export.sh full --zip")

def make_accept_log_dir(subject, command_name=None):
    command_name = command_name or COMMAND
    configured_log_dir = os.environ.get("PATCH_ACCEPT_LOG_DIR")
    if configured_log_dir:
        log_dir = Path(configured_log_dir).expanduser()
        if not log_dir.is_absolute():
            log_dir = PROJECT_ROOT / log_dir
        log_dir.mkdir(parents=True, exist_ok=True)
        return log_dir.resolve(), True
    run_id = os.environ.get("PATCH_RUN_ID") or make_run_id(command_name, subject)
    base = validation_log_base() if command_name == "verify" else accept_log_base()
    log_dir = base / run_id
    log_dir.mkdir(parents=True, exist_ok=False)
    return log_dir, False


def args_for_background_child(args):
    parent_only_flags = {"--background", "--watch"}
    parent_only_values = {"--format", "--watch-interval", "--watch-timeout"}
    result = []
    i = 0
    while i < len(args):
        arg = args[i]
        if arg in parent_only_flags:
            i += 1
            continue
        if arg in parent_only_values:
            if i + 1 >= len(args):
                fail(f"{arg} erwartet einen Wert.", 2)
            i += 2
            continue
        result.append(arg)
        i += 1
    return result


def write_running_summary(log_dir, command_name, patch_identity, run_log, pid=None, phase="STARTING"):
    patch_identity = patch_identity or {}
    fields = [
        "STATUS=RUNNING",
        f"COMMAND={command_name}",
        f"RUN_ID={Path(log_dir).name}",
        f"PATCH_ID={patch_identity.get('patchId', '-')}",
        f"ARTIFACT_ID={patch_identity.get('artifactId', '-')}",
        f"PATCH_SHA256={patch_identity.get('patchSha256', '-')}",
        f"PHASE={phase}",
        f"PID={pid or '-'}",
        f"BASELINE_HEAD={current_git_head() or '-'}",
        f"LOG_DIR={log_dir}",
        f"RUN_LOG={run_log}",
        f"UPDATED_AT={now_iso()}",
    ]
    content = "\n".join(fields) + "\n"
    atomic_write_text(Path(log_dir) / "summary.log", content)
    atomic_write_text(Path(log_dir) / "SUMMARY.txt", content)
    atomic_write_text(Path(log_dir) / "STATUS.txt", "RUNNING\n")


def start_background_command(command_name, args, subject, patch_identity=None, options=None):
    patch_identity = patch_identity or {}
    options = options or {}
    patch_id = patch_identity.get("patchId") or sanitize_name(subject)
    run_id = make_run_id(command_name, patch_id)
    os.environ["PATCH_RUN_ID"] = run_id
    try:
        log_dir, _fixed = make_accept_log_dir(patch_id, command_name=command_name)
    finally:
        os.environ.pop("PATCH_RUN_ID", None)
    run_log = log_dir / "run.log"
    write_running_summary(log_dir, command_name, patch_identity, run_log, phase="SPAWNING")
    write_run_record(
        log_dir,
        runId=run_id,
        command=command_name,
        status="RUNNING",
        phase="SPAWNING",
        patchId=patch_identity.get("patchId", patch_id),
        artifactId=patch_identity.get("artifactId"),
        patchSha256=patch_identity.get("patchSha256"),
        logDir=str(log_dir),
        summary=str(log_dir / "SUMMARY.txt"),
    )
    write_invocation_record(log_dir, command_name, subject, patch_identity, options)

    env = dict(os.environ)
    env["PATCH_BACKGROUND_CHILD"] = "1"
    env["PATCH_ACCEPT_LOG_DIR"] = str(log_dir)
    env["PATCH_RUN_ID"] = run_id
    child_args = args_for_background_child(args)
    cmd = [sys.executable, str(Path(__file__).resolve()), str(PROJECT_ROOT), command_name] + child_args
    logged_cmd = list(cmd)
    raw_subject = str(options.get("subject") or "")
    if raw_subject:
        logged_cmd = [Path(part).name if part == raw_subject else part for part in logged_cmd]
    with run_log.open("a", encoding="utf-8") as out:
        out.write(f"== Background {command_name} ==\n")
        out.write(f"$ {command_to_text(logged_cmd)}\n\n")
        out.flush()
        proc = subprocess.Popen(
            cmd,
            cwd=PROJECT_ROOT,
            stdin=subprocess.DEVNULL,
            stdout=out,
            stderr=subprocess.STDOUT,
            text=True,
            env=env,
            start_new_session=True,
        )

    current_fields = read_summary_fields(log_dir / "SUMMARY.txt")
    if current_fields.get("STATUS") == "RUNNING":
        write_running_summary(log_dir, command_name, patch_identity, run_log, pid=proc.pid, phase="STARTED")
        write_run_record(log_dir, status="RUNNING", phase="STARTED", pid=proc.pid, processGroupId=proc.pid)
    else:
        write_run_record(log_dir, pid=proc.pid, processGroupId=proc.pid)

    state = {
        "status": "STARTED",
        "command": command_name,
        "runId": run_id,
        "patchId": patch_identity.get("patchId", "-"),
        "artifactId": patch_identity.get("artifactId", "-"),
        "pid": proc.pid,
        "phase": "STARTED",
        "commitStatus": "PENDING" if options.get("gitCommit") else "SKIPPED",
        "commitHash": "-",
        "summary": str(log_dir / "SUMMARY.txt"),
        "logDir": str(log_dir),
        "watchCommand": f"./bin/patch.sh watch {run_id}",
        "waitCommand": f"./bin/patch.sh wait {run_id}",
    }
    label = "Patch-Accept" if command_name == "accept" else "Patch-Verify"
    print_start_state(state, options.get("outputFormat", "human"), label=label)
    return state


def run_validation_steps(log_dir, options):
    validation_env = validation_subprocess_env()
    if options["toolingSelfcheck"]:
        rc = run_tooling_verification(log_dir)
        if rc != 0:
            return "tooling", None

    used_test_log_names = set()
    for test_selector in options["tests"]:
        test_log_name = validation_test_log_name(test_selector, used_test_log_names)
        used_test_log_names.add(test_log_name)
        rc = run_process_step(
            f"Configured test {test_selector}",
            configured_test_selector_command(test_selector),
            log_dir / test_log_name,
            shell=True,
            env=validation_env,
        )
        if rc != 0:
            return f"test:{test_selector}", None

    if options["fullTest"]:
        rc = run_process_step(
            "Configured full test",
            configured_full_test_command(),
            log_dir / "full-test.log",
            shell=True,
            env=validation_env,
        )
        if rc != 0:
            return "full-test", None

    latest_export_path = None
    if options["export"]:
        rc = run_process_step(
            "Configured export",
            configured_export_command(),
            log_dir / "export.log",
            shell=True,
            env=validation_env,
        )
        if rc != 0:
            return "export", None
        latest = latest_full_export()
        latest_export_path = str(latest) if latest else None

    return None, latest_export_path


def transaction_child_args(args):
    result = []
    i = 0
    while i < len(args):
        arg = args[i]
        if arg in ("--background", "--wait", "--wait-for-lock", "--push"):
            i += 1
            continue
        if arg == "--lock-timeout":
            i += 2
            continue
        result.append(arg)
        i += 1
    if "--commit" not in result:
        result.append("--commit")
    return result


def copy_tree_if_present(source, target):
    source = Path(source)
    target = Path(target)
    if not source.exists():
        return
    if source.is_dir():
        shutil.copytree(source, target, dirs_exist_ok=True)
    else:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)


def candidate_paths_from_patch_log(log_path):
    data = read_json(Path(log_path))
    excluded_prefixes = ("exports/", "target/", "build/", "patches/runtime/")
    result = []
    for entry in data.get("entries", []):
        if entry.get("status") not in ("new", "modified", "deleted"):
            continue
        path = entry.get("path")
        if not isinstance(path, str):
            continue
        rel = validate_relpath(path)
        if rel.startswith(excluded_prefixes):
            continue
        if rel not in result:
            result.append(rel)
    return sorted(result)


def git_changed_paths_at(root, commit_ref):
    output = git_output_at(
        root,
        "diff-tree",
        "--no-commit-id",
        "--name-only",
        "-r",
        commit_ref,
    )
    return sorted(line.strip() for line in output.splitlines() if line.strip())


def preserve_existing_canonical_acceptance(canonical_dir, patch_id):
    canonical_dir = Path(canonical_dir)
    if not canonical_dir.exists():
        return
    history_dir = accept_log_base() / "history" / patch_id
    history_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).astimezone().strftime("%Y%m%d_%H%M%S_%f")
    shutil.move(str(canonical_dir), str(history_dir / stamp))


def publish_canonical_acceptance(run_log_dir, patch_id, child_accept_dir=None, include_run_logs=False):
    run_log_dir = Path(run_log_dir).resolve()
    canonical_dir = accept_log_base() / patch_id
    existing = read_summary_fields(canonical_dir / "SUMMARY.txt")
    if existing.get("STATUS") in ("SUCCESS", "ALREADY_APPLIED"):
        fail(
            "PATCH_ACCEPT_CANONICAL_CONFLICT: canonical successful acceptance evidence "
            f"already exists for {patch_id}."
        )
    preserve_existing_canonical_acceptance(canonical_dir, patch_id)

    temp_dir = accept_log_base() / f".publish-{patch_id}-{os.getpid()}-{time.time_ns()}"
    temp_dir.mkdir(parents=True, exist_ok=False)
    try:
        if include_run_logs:
            copy_tree_if_present(run_log_dir, temp_dir)
        for name in ("SUMMARY.txt", "summary.log", "STATUS.txt", "invocation.json"):
            source = run_log_dir / name
            if source.is_file():
                shutil.copy2(source, temp_dir / name)
        if child_accept_dir is not None:
            copy_tree_if_present(child_accept_dir, temp_dir / "child-accept")
        fields = read_summary_fields(run_log_dir / "SUMMARY.txt")
        accepted = {
            "schemaVersion": "springmaster.patch-acceptance.v1",
            "patchId": patch_id,
            "artifactId": fields.get("ARTIFACT_ID"),
            "runId": fields.get("RUN_ID", run_log_dir.name),
            "status": fields.get("STATUS"),
            "commitStatus": fields.get("GIT_COMMIT_STATUS"),
            "commitHash": fields.get("GIT_COMMIT_HASH"),
            "pushStatus": fields.get("GIT_PUSH_STATUS"),
            "runLogDir": str(run_log_dir),
            "acceptedAt": now_iso(),
        }
        write_json(temp_dir / "accepted.json", accepted)
        atomic_write_text(temp_dir / "RUN_LOG_DIR.txt", str(run_log_dir) + "\n")
        os.replace(temp_dir, canonical_dir)
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
    return canonical_dir


def remove_canonical_acceptance_for_run(patch_id, run_id):
    canonical_dir = accept_log_base() / patch_id
    accepted_path = canonical_dir / "accepted.json"
    if not accepted_path.is_file():
        return
    try:
        accepted = json.loads(accepted_path.read_text(encoding="utf-8"))
    except Exception:
        return
    if accepted.get("runId") == run_id:
        shutil.rmtree(canonical_dir, ignore_errors=True)


def refresh_canonical_acceptance(run_log_dir, patch_id):
    run_log_dir = Path(run_log_dir)
    canonical_dir = accept_log_base() / patch_id
    accepted_path = canonical_dir / "accepted.json"
    if not canonical_dir.is_dir() or not accepted_path.is_file():
        return
    accepted = json.loads(accepted_path.read_text(encoding="utf-8"))
    fields = read_summary_fields(run_log_dir / "SUMMARY.txt")
    if accepted.get("runId") != fields.get("RUN_ID", run_log_dir.name):
        return
    for name in ("SUMMARY.txt", "summary.log", "STATUS.txt", "invocation.json"):
        source = run_log_dir / name
        if source.is_file():
            atomic_write_text(canonical_dir / name, source.read_text(encoding="utf-8"))
    accepted.update({
        "status": fields.get("STATUS"),
        "commitStatus": fields.get("GIT_COMMIT_STATUS"),
        "commitHash": fields.get("GIT_COMMIT_HASH"),
        "pushStatus": fields.get("GIT_PUSH_STATUS"),
        "updatedAt": now_iso(),
    })
    write_json(accepted_path, accepted)


def find_child_accept_log_dir(worktree, patch_id):
    base = Path(worktree) / "patches" / "logs" / "accept"
    canonical = base / patch_id
    if (canonical / "SUMMARY.txt").is_file():
        return canonical
    candidates = []
    if base.is_dir():
        for summary in base.glob("*/SUMMARY.txt"):
            fields = read_summary_fields(summary)
            if fields.get("PATCH_ID") == patch_id:
                candidates.append(summary.parent)
    if not candidates:
        return canonical
    candidates.sort(
        key=lambda path: path.stat().st_mtime if path.exists() else 0,
        reverse=True,
    )
    return candidates[0]


def git_output_at(root, *args):
    result = subprocess.run(
        ["git", *args],
        cwd=root,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    if result.returncode != 0:
        fail(f"Git command failed in {root}: git {' '.join(args)}\n{result.stdout}")
    return result.stdout.strip()


def transactional_accept_command(args, options, zip_path, patch_info):
    patch_id = patch_info["patchId"]
    options = dict(options)
    baseline_head = git_output_at(PROJECT_ROOT, "rev-parse", "HEAD")
    options["artifactId"] = patch_info.get("artifactId")
    options["patchSha256"] = patch_info.get("patchSha256") or sha256_file(zip_path)
    options["baselineHead"] = baseline_head
    log_dir, _fixed_log_dir = make_accept_log_dir(patch_id, command_name="accept")
    write_run_record(
        log_dir,
        command="accept",
        status="RUNNING",
        phase="WORKTREE_SETUP",
        patchId=patch_id,
        artifactId=options.get("artifactId"),
        patchSha256=options.get("patchSha256"),
        baselineHead=baseline_head,
        logDir=str(log_dir),
        summary=str(log_dir / "SUMMARY.txt"),
    )
    write_invocation_record(log_dir, "accept", zip_path.name, patch_info, options)
    ensure_git_clean_before_commit(log_dir)

    transaction_parent = Path(tempfile.mkdtemp(prefix=f"springmaster-accept-{patch_id}-"))
    worktree = transaction_parent / "worktree"
    child_log = log_dir / "worktree-child.log"
    transfer_root = run_state_root() / "accept-transfer" / log_dir.name
    worktree_added = False
    live_transfer_started = False
    live_archive_created = False
    canonical_published = False
    transfer_finalized = False

    try:
        update = {"status": "RUNNING", "phase": "WORKTREE_CREATE"}
        write_run_record(log_dir, **update)
        add_result = subprocess.run(
            ["git", "worktree", "add", "--detach", str(worktree), baseline_head],
            cwd=PROJECT_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        atomic_write_text(log_dir / "worktree-add.log", add_result.stdout or "")
        if add_result.returncode != 0:
            raise RuntimeError(f"PATCH_ACCEPT_WORKTREE_CREATE_FAILED: see {log_dir / 'worktree-add.log'}")
        worktree_added = True

        child_env = dict(os.environ)
        child_env["PATCH_ACCEPT_WORKTREE_CHILD"] = "1"
        child_env.pop("PATCH_ACCEPT_LOG_DIR", None)
        child_env.pop("PATCH_RUN_ID", None)
        child_engine = worktree / "bin" / "patch.py"
        if not child_engine.is_file():
            # Integration fixtures may invoke the engine from outside the fixture
            # repository. Real Springmaster transactions use the baseline engine in
            # the detached worktree; external fixtures retain their explicit engine.
            child_engine = Path(__file__).resolve()
        child_command = [
            sys.executable,
            str(child_engine),
            str(worktree),
            "accept",
            *transaction_child_args(args),
        ]
        write_run_record(log_dir, status="RUNNING", phase="WORKTREE_VALIDATION")
        with child_log.open("w", encoding="utf-8") as out:
            out.write(f"$ {command_to_text(child_command)}\n\n")
            out.flush()
            child = subprocess.run(
                child_command,
                cwd=worktree,
                env=child_env,
                stdout=out,
                stderr=subprocess.STDOUT,
                text=True,
            )
        child_rc = child.returncode

        current_head = git_output_at(PROJECT_ROOT, "rev-parse", "HEAD")
        current_dirty = git_status_paths(log_dir=log_dir, ignore_accept_log=True)
        if current_head != baseline_head or current_dirty:
            raise RuntimeError(
                "PATCH_ACCEPT_LIVE_STATE_CHANGED_DURING_VALIDATION: the live repository "
                "must remain unchanged while the worktree is validated."
            )

        child_accept = find_child_accept_log_dir(worktree, patch_id)
        if child_rc != 0:
            copy_tree_if_present(child_accept, log_dir / "child-accept")
            child_fields = read_summary_fields(child_accept / "SUMMARY.txt")
            child_failed_step = child_fields.get("FAILED_STEP") or "worktree-validation"
            root_cause, root_log = extract_first_failure_line(log_dir)
            write_accept_summary(
                log_dir,
                "FAILED",
                "accept",
                patch_id=patch_id,
                failed_step=child_failed_step,
                options=options,
                extra_fields={
                    "FAILED_PHASE": "WORKTREE_VALIDATION",
                    "CHILD_FAILED_STEP": child_failed_step,
                    "CHILD_LOG_DIR": child_accept,
                    "ROOT_CAUSE": root_cause or "-",
                    "ROOT_CAUSE_LOG": root_log or "-",
                },
            )
            print_accept_result(
                "FAILED",
                "accept",
                log_dir,
                patch_id=patch_id,
                failed_step=child_failed_step,
                options=options,
            )
            raise SystemExit(child_rc)

        child_head = git_output_at(worktree, "rev-parse", "HEAD")
        child_parent = git_output_at(worktree, "rev-parse", "HEAD^")
        if child_parent != baseline_head:
            raise RuntimeError(
                "PATCH_ACCEPT_WORKTREE_PARENT_MISMATCH: qualified commit does not descend "
                "directly from the live baseline."
            )

        child_archive = worktree / "patches" / "archives" / patch_id
        child_patch_log = child_archive / "patch-log.json"
        if not child_patch_log.is_file():
            raise RuntimeError("PATCH_ACCEPT_CHILD_ARCHIVE_MISSING: qualified child archive is incomplete.")
        expected_paths = candidate_paths_from_patch_log(child_patch_log)
        child_changed_paths = git_changed_paths_at(worktree, child_head)
        if child_changed_paths != expected_paths:
            atomic_write_text(
                log_dir / "path-parity.log",
                "expected:\n  " + "\n  ".join(expected_paths)
                + "\nactual:\n  " + "\n  ".join(child_changed_paths) + "\n",
            )
            raise RuntimeError(
                "PATCH_ACCEPT_CHILD_PATH_PARITY_FAILED: qualified Git commit paths differ "
                "from the patch archive. See path-parity.log."
            )

        child_check = subprocess.run(
            ["git", "show", "--check", "--format=", child_head],
            cwd=worktree,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        atomic_write_text(log_dir / "qualified-commit-check.log", child_check.stdout or "")
        if child_check.returncode != 0:
            raise RuntimeError(
                "PATCH_ACCEPT_QUALIFIED_COMMIT_CHECK_FAILED: qualified commit contains "
                "whitespace errors. See qualified-commit-check.log."
            )

        live_archive = ARCHIVES_DIR / patch_id
        if live_archive.exists():
            raise RuntimeError(f"PATCH_ACCEPT_ARCHIVE_CONFLICT_AFTER_VALIDATION: {live_archive}")
        canonical_fields = canonical_accept_fields(patch_id)
        if canonical_fields.get("STATUS") in ("SUCCESS", "ALREADY_APPLIED"):
            raise RuntimeError(
                "PATCH_ACCEPT_CANONICAL_CONFLICT_AFTER_VALIDATION: successful acceptance "
                f"evidence already exists for {patch_id}."
            )

        shutil.rmtree(transfer_root, ignore_errors=True)
        staged_archive = transfer_root / "archive"
        staged_child_accept = transfer_root / "child-accept"
        copy_tree_if_present(child_archive, staged_archive)
        copy_tree_if_present(child_accept, staged_child_accept)
        if not (staged_archive / "patch-log.json").is_file():
            raise RuntimeError("PATCH_ACCEPT_TRANSFER_STAGE_FAILED: staged archive is incomplete.")

        write_run_record(log_dir, status="RUNNING", phase="LIVE_TRANSFER")
        cherry_pick_args = ["cherry-pick", child_head]
        if not options.get("gitCommit"):
            cherry_pick_args = ["cherry-pick", "--no-commit", child_head]
        cherry = git_run(cherry_pick_args, log_dir=log_dir)
        if cherry.returncode != 0:
            git_run(["cherry-pick", "--abort"], log_dir=log_dir)
            raise RuntimeError(
                "PATCH_ACCEPT_CHERRY_PICK_FAILED: qualified commit could not be transferred to live."
            )
        live_transfer_started = True

        if options.get("gitCommit"):
            live_changed_paths = git_changed_paths_at(PROJECT_ROOT, "HEAD")
        else:
            live_changed_paths = sorted(
                line.strip()
                for line in git_output_at(PROJECT_ROOT, "diff", "--name-only", baseline_head).splitlines()
                if line.strip()
            )
        if live_changed_paths != expected_paths:
            atomic_write_text(
                log_dir / "live-path-parity.log",
                "expected:\n  " + "\n  ".join(expected_paths)
                + "\nactual:\n  " + "\n  ".join(live_changed_paths) + "\n",
            )
            raise RuntimeError(
                "PATCH_ACCEPT_LIVE_PATH_PARITY_FAILED: transferred Git paths differ from "
                "the qualified patch. See live-path-parity.log."
            )

        live_archive.parent.mkdir(parents=True, exist_ok=True)
        os.replace(staged_archive, live_archive)
        live_archive_created = True
        copy_tree_if_present(worktree / "exports", PROJECT_ROOT / "exports")

        latest_export = latest_full_export()
        latest_export_path = str(latest_export) if latest_export else None
        git_commit_result = {
            "status": "COMMITTED" if options.get("gitCommit") else "VALIDATED_NOT_COMMITTED",
            "hash": git_output_at(PROJECT_ROOT, "rev-parse", "--short", "HEAD") if options.get("gitCommit") else None,
            "pushStatus": "SKIPPED",
            "message": f"qualified in isolated worktree: {child_head[:12]}",
        }
        git_commit_script = generate_git_commit_script(log_dir, patch_id)
        write_accept_summary(
            log_dir,
            "SUCCESS",
            "accept",
            patch_id=patch_id,
            latest_export_path=latest_export_path,
            options=options,
            git_commit_script=git_commit_script,
            git_commit_result=git_commit_result,
            extra_fields={
                "QUALIFIED_COMMIT": child_head,
                "LIVE_TRANSFER_PATHS": len(expected_paths),
            },
        )
        publish_canonical_acceptance(log_dir, patch_id, child_accept_dir=staged_child_accept)
        canonical_published = True
        transfer_finalized = True
        live_transfer_started = False

        if options.get("gitPush"):
            push_result = git_run(["push"], log_dir=log_dir)
            git_commit_result["pushStatus"] = "PUSHED" if push_result.returncode == 0 else "FAILED"
            write_accept_summary(
                log_dir,
                "SUCCESS",
                "accept",
                patch_id=patch_id,
                latest_export_path=latest_export_path,
                options=options,
                git_commit_script=git_commit_script,
                git_commit_result=git_commit_result,
                extra_fields={
                    "QUALIFIED_COMMIT": child_head,
                    "LIVE_TRANSFER_PATHS": len(expected_paths),
                    "PUSH_ERROR": "-" if push_result.returncode == 0 else "See git.log",
                },
            )
            refresh_canonical_acceptance(log_dir, patch_id)

        print_accept_result(
            "SUCCESS",
            "accept",
            log_dir,
            patch_id=patch_id,
            latest_export_path=latest_export_path,
            options=options,
            git_commit_script=git_commit_script,
            git_commit_result=git_commit_result,
        )
    except SystemExit:
        raise
    except BaseException as exc:
        if transfer_finalized:
            # The qualified commit, archive and canonical acceptance evidence are already
            # durable. A later reporting or push problem must not invalidate or roll back
            # the local acceptance transaction. Preserve success and record the warning.
            warning_log = log_dir / "post-accept-warning.log"
            atomic_write_text(warning_log, f"{type(exc).__name__}: {exc}\n")
            try:
                fields = read_summary_fields(log_dir / "SUMMARY.txt")
                git_commit_result = {
                    "status": fields.get("GIT_COMMIT_STATUS", "COMMITTED"),
                    "hash": fields.get("GIT_COMMIT_HASH") or None,
                    "pushStatus": fields.get("GIT_PUSH_STATUS", "FAILED"),
                    "message": fields.get("GIT_COMMIT_MESSAGE", "post-accept warning"),
                }
                write_accept_summary(
                    log_dir,
                    "SUCCESS",
                    "accept",
                    patch_id=patch_id,
                    latest_export_path=fields.get("LATEST_EXPORT"),
                    options=options,
                    git_commit_script=fields.get("GIT_COMMIT_SCRIPT"),
                    git_commit_result=git_commit_result,
                    extra_fields={
                        "QUALIFIED_COMMIT": fields.get("QUALIFIED_COMMIT", "-"),
                        "LIVE_TRANSFER_PATHS": fields.get("LIVE_TRANSFER_PATHS", "-"),
                        "POST_ACCEPT_WARNING": str(exc)[:500],
                        "POST_ACCEPT_WARNING_LOG": warning_log,
                    },
                )
                refresh_canonical_acceptance(log_dir, patch_id)
            except BaseException as report_exc:
                with warning_log.open("a", encoding="utf-8") as handle:
                    handle.write(f"reporting: {type(report_exc).__name__}: {report_exc}\n")
            print(
                "PATCH_ACCEPT_POST_ACCEPT_WARNING: local acceptance remains successful; "
                f"see {warning_log}",
                file=sys.stderr,
            )
            return

        if live_transfer_started:
            git_run(["reset", "--hard", baseline_head], log_dir=log_dir)
        if live_archive_created:
            shutil.rmtree(ARCHIVES_DIR / patch_id, ignore_errors=True)
        if canonical_published:
            remove_canonical_acceptance_for_run(patch_id, log_dir.name)
        root_cause, root_log = extract_first_failure_line(log_dir)
        if read_summary_fields(log_dir / "SUMMARY.txt").get("STATUS") != "FAILED":
            write_accept_summary(
                log_dir,
                "FAILED",
                "accept",
                patch_id=patch_id,
                failed_step="transaction",
                options=options,
                extra_fields={
                    "FAILED_PHASE": "TRANSACTION",
                    "ROOT_CAUSE": str(exc)[:500],
                    "ROOT_CAUSE_LOG": root_log or "-",
                },
            )
        print_accept_result(
            "FAILED",
            "accept",
            log_dir,
            patch_id=patch_id,
            failed_step="transaction",
            options=options,
        )
        raise SystemExit(1)
    finally:
        if worktree_added:
            subprocess.run(
                ["git", "worktree", "remove", "--force", str(worktree)],
                cwd=PROJECT_ROOT,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        subprocess.run(
            ["git", "worktree", "prune"],
            cwd=PROJECT_ROOT,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        shutil.rmtree(transaction_parent, ignore_errors=True)
        shutil.rmtree(transfer_root, ignore_errors=True)


def accept_command(args):
    options = parse_accept_verify_args(args, "Patch-ZIP")
    zip_path = Path(options["subject"]).expanduser().resolve()
    if not zip_path.exists() or not zip_path.is_file():
        fail(f"Patch-ZIP nicht gefunden: {zip_path}")

    patch_identity = inspect_patch_identity(zip_path)
    options["artifactId"] = patch_identity.get("artifactId")
    options["patchSha256"] = patch_identity.get("patchSha256")
    options["baselineHead"] = current_git_head()
    if os.environ.get("PATCH_BACKGROUND_CHILD") == "1":
        options["background"] = True

    if os.environ.get("PATCH_ACCEPT_WORKTREE_CHILD") != "1":
        applied_state = applied_identity_state(patch_identity)
        if applied_state is not None:
            if applied_state.get("commitStatus") == "COMMITTED" and not applied_state.get("commitVerified"):
                fail(
                    "PATCH_APPLIED_GIT_COMMIT_MISSING: archive and acceptance evidence exist, "
                    "but the recorded Git commit is not available. Run patch doctor before retrying."
                )
            print_already_applied_state(applied_state, options.get("outputFormat", "human"))
            return

        if os.environ.get("PATCH_BACKGROUND_CHILD") != "1":
            active_run = find_active_run(patch_identity["patchId"], patch_identity.get("artifactId"))
            if active_run is not None:
                state = print_already_running_state(
                    active_run,
                    options.get("outputFormat", "human"),
                    command_name="accept",
                )
                if options.get("watchAfterStart"):
                    observe_run_ref(
                        state["runId"],
                        interval=options.get("watchInterval", 5),
                        timeout=options.get("watchTimeout"),
                    )
                return

    if options.get("background") and os.environ.get("PATCH_BACKGROUND_CHILD") != "1":
        state = start_background_command(
            "accept",
            args,
            zip_path.name,
            patch_identity=patch_identity,
            options=options,
        )
        if options.get("watchAfterStart"):
            observe_run_ref(
                state["runId"],
                interval=options.get("watchInterval", 5),
                timeout=options.get("watchTimeout"),
            )
        return

    patch_info = inspect_patch_zip(zip_path)
    target_paths = patch_info["targetPaths"]
    options = resolve_validation_profile(options, target_paths)
    options["artifactId"] = patch_info.get("artifactId")
    options["patchSha256"] = patch_info.get("patchSha256")
    options["baselineHead"] = current_git_head()

    if os.environ.get("PATCH_ACCEPT_WORKTREE_CHILD") != "1" and summary_has_effect(patch_info["summary"]):
        transactional_accept_command(args, options, zip_path, patch_info)
        return

    log_dir, fixed_log_dir = make_accept_log_dir(patch_info["patchId"], command_name="accept")
    write_run_record(
        log_dir,
        command="accept",
        status="RUNNING",
        phase="LIVE_BASELINE",
        patchId=patch_info["patchId"],
        artifactId=patch_info.get("artifactId"),
        patchSha256=patch_info.get("patchSha256"),
        baselineHead=options.get("baselineHead"),
        logDir=str(log_dir),
        summary=str(log_dir / "SUMMARY.txt"),
    )
    write_invocation_record(log_dir, "accept", zip_path.name, patch_info, options)

    if options.get("gitCommit"):
        ensure_git_clean_before_commit(log_dir)

    script_path = Path(__file__).resolve()
    live_baseline_rc = run_process_step(
        "Patch live baseline preflight",
        [sys.executable, str(script_path), str(PROJECT_ROOT), "live-baseline", str(zip_path)],
        log_dir / "live-baseline.log",
    )
    if live_baseline_rc != 0:
        write_accept_summary(
            log_dir,
            "FAILED",
            "accept",
            patch_id=patch_info["patchId"],
            failed_step="live-baseline",
            options=options,
        )
        print_accept_result(
            "FAILED",
            "accept",
            log_dir,
            patch_id=patch_info["patchId"],
            failed_step="live-baseline",
            options=options,
        )
        sys.exit(live_baseline_rc)

    write_run_record(log_dir, status="RUNNING", phase="DRY_RUN")
    dry_run_rc = run_process_step(
        "Patch dry-run",
        [sys.executable, str(script_path), str(PROJECT_ROOT), "apply", "--dry-run", str(zip_path)],
        log_dir / "dry-run.log",
    )
    if dry_run_rc != 0:
        write_accept_summary(
            log_dir,
            "FAILED",
            "accept",
            patch_id=patch_info["patchId"],
            failed_step="dry-run",
            options=options,
        )
        print_accept_result(
            "FAILED",
            "accept",
            log_dir,
            patch_id=patch_info["patchId"],
            failed_step="dry-run",
            options=options,
        )
        sys.exit(dry_run_rc)

    if not summary_has_effect(patch_info["summary"]):
        existing_patch_dir = find_applied_patch_by_name(patch_info["name"])
        if existing_patch_dir is None:
            write_accept_summary(
                log_dir,
                "FAILED",
                "accept",
                patch_id=patch_info["patchId"],
                failed_step="no-effective-change",
                options=options,
            )
            print_accept_result(
                "FAILED",
                "accept",
                log_dir,
                patch_id=patch_info["patchId"],
                failed_step="no-effective-change",
                options=options,
            )
            sys.exit(3)

        patch_id = existing_patch_dir.name
        write_run_record(log_dir, patchId=patch_id, status="RUNNING", phase="REVALIDATION")
        failed_step, latest_export_path = run_validation_steps(log_dir, options)
        if failed_step:
            write_accept_summary(
                log_dir,
                "FAILED",
                "accept",
                patch_id=patch_id,
                failed_step=failed_step,
                options=options,
            )
            print_accept_result(
                "FAILED",
                "accept",
                log_dir,
                patch_id=patch_id,
                failed_step=failed_step,
                options=options,
            )
            sys.exit(1)

        write_accept_summary(
            log_dir,
            "ALREADY_APPLIED",
            "accept",
            patch_id=patch_id,
            latest_export_path=latest_export_path,
            options=options,
        )
        print_accept_result(
            "ALREADY_APPLIED",
            "accept",
            log_dir,
            patch_id=patch_id,
            latest_export_path=latest_export_path,
            options=options,
        )
        return

    write_run_record(log_dir, status="RUNNING", phase="APPLY")
    apply_rc = run_process_step(
        "Patch apply",
        [sys.executable, str(script_path), str(PROJECT_ROOT), "apply", str(zip_path)],
        log_dir / "apply.log",
    )
    if apply_rc != 0:
        write_accept_summary(
            log_dir,
            "FAILED",
            "accept",
            patch_id=patch_info["patchId"],
            failed_step="apply",
            options=options,
        )
        print_accept_result(
            "FAILED",
            "accept",
            log_dir,
            patch_id=patch_info["patchId"],
            failed_step="apply",
            options=options,
        )
        sys.exit(apply_rc)

    patch_id = patch_info["patchId"]
    write_run_record(log_dir, patchId=patch_id, status="RUNNING", phase="SHOW")
    show_rc = run_process_step(
        "Patch show",
        [sys.executable, str(script_path), str(PROJECT_ROOT), "show", patch_id],
        log_dir / "show.log",
    )
    if show_rc != 0:
        write_accept_summary(
            log_dir,
            "FAILED",
            "accept",
            patch_id=patch_id,
            failed_step="show",
            options=options,
        )
        print_accept_result(
            "FAILED",
            "accept",
            log_dir,
            patch_id=patch_id,
            failed_step="show",
            options=options,
        )
        sys.exit(show_rc)

    patch_paths = commit_candidate_paths_from_patch(patch_id)
    write_run_record(log_dir, status="RUNNING", phase="WHITESPACE")
    whitespace_rc = validate_patch_scoped_whitespace(log_dir, patch_paths, staged=False)
    if whitespace_rc != 0:
        write_accept_summary(
            log_dir,
            "FAILED",
            "accept",
            patch_id=patch_id,
            failed_step="whitespace",
            options=options,
            extra_fields={"WHITESPACE_SCOPE": ",".join(patch_paths)},
        )
        print_accept_result(
            "FAILED",
            "accept",
            log_dir,
            patch_id=patch_id,
            failed_step="whitespace",
            options=options,
        )
        sys.exit(1)

    write_run_record(log_dir, status="RUNNING", phase="VALIDATION")
    failed_step, latest_export_path = run_validation_steps(log_dir, options)
    if failed_step:
        root_cause, root_log = extract_first_failure_line(log_dir)
        write_accept_summary(
            log_dir,
            "FAILED",
            "accept",
            patch_id=patch_id,
            failed_step=failed_step,
            options=options,
            extra_fields={
                "ROOT_CAUSE": root_cause or "-",
                "ROOT_CAUSE_LOG": root_log or "-",
            },
        )
        print_accept_result(
            "FAILED",
            "accept",
            log_dir,
            patch_id=patch_id,
            failed_step=failed_step,
            options=options,
        )
        sys.exit(1)

    write_run_record(log_dir, status="RUNNING", phase="GIT_COMMIT")
    git_commit_script = generate_git_commit_script(log_dir, patch_id)
    git_commit_result = None
    if options.get("gitCommit"):
        git_commit_result = execute_git_commit(
            log_dir,
            patch_id,
            latest_export_path=latest_export_path,
            push=options.get("gitPush", False),
        )
    write_accept_summary(
        log_dir,
        "SUCCESS",
        "accept",
        patch_id=patch_id,
        latest_export_path=latest_export_path,
        options=options,
        git_commit_script=git_commit_script,
        git_commit_result=git_commit_result,
    )
    publish_canonical_acceptance(
        log_dir,
        patch_id,
        include_run_logs=os.environ.get("PATCH_ACCEPT_WORKTREE_CHILD") == "1",
    )
    print_accept_result(
        "SUCCESS",
        "accept",
        log_dir,
        patch_id=patch_id,
        latest_export_path=latest_export_path,
        options=options,
        git_commit_script=git_commit_script,
        git_commit_result=git_commit_result,
    )


def verify_command(args):
    options = parse_accept_verify_args(args, "Patch-Referenz")
    patch_dir = resolve_patch_ref(options["subject"])
    patch_id = patch_dir.name
    patch_data = read_json(patch_dir / "patch-log.json")
    artifact_id = patch_data.get("artifactId")
    if artifact_id is None and isinstance(patch_data.get("manifest"), dict):
        artifact_id = patch_data["manifest"].get("artifactId")
    patch_identity = {
        "patchId": patch_id,
        "artifactId": artifact_id,
        "patchSha256": patch_data.get("sourcePatchSha256"),
    }

    if os.environ.get("PATCH_BACKGROUND_CHILD") != "1":
        active_run = find_active_run(patch_id, artifact_id)
        if active_run is not None:
            state = print_already_running_state(
                active_run,
                options.get("outputFormat", "human"),
                command_name="verify",
            )
            if options.get("watchAfterStart"):
                observe_run_ref(
                    state["runId"],
                    interval=options.get("watchInterval", 5),
                    timeout=options.get("watchTimeout"),
                )
            return

    if options.get("background") and os.environ.get("PATCH_BACKGROUND_CHILD") != "1":
        state = start_background_command(
            "verify",
            args,
            patch_id,
            patch_identity=patch_identity,
            options=options,
        )
        if options.get("watchAfterStart"):
            observe_run_ref(
                state["runId"],
                interval=options.get("watchInterval", 5),
                timeout=options.get("watchTimeout"),
            )
        return

    if os.environ.get("PATCH_BACKGROUND_CHILD") == "1":
        options["background"] = True
    target_paths = target_paths_from_patch_dir(patch_dir)
    options = resolve_validation_profile(options, target_paths)
    options["artifactId"] = artifact_id
    options["patchSha256"] = patch_identity.get("patchSha256")
    options["baselineHead"] = current_git_head()

    log_dir, _fixed = make_accept_log_dir(patch_id, command_name="verify")
    write_run_record(
        log_dir,
        command="verify",
        status="RUNNING",
        phase="VALIDATION",
        patchId=patch_id,
        artifactId=artifact_id,
        patchSha256=patch_identity.get("patchSha256"),
        baselineHead=options.get("baselineHead"),
        logDir=str(log_dir),
        summary=str(log_dir / "SUMMARY.txt"),
    )
    write_invocation_record(log_dir, "verify", options["subject"], patch_identity, options)
    atomic_write_text(
        log_dir / "verify.log",
        f"VERIFY_STARTED={now_iso()}\nPATCH_ID={patch_id}\n",
    )

    failed_step, latest_export_path = run_validation_steps(log_dir, options)
    if failed_step:
        root_cause, root_log = extract_first_failure_line(log_dir)
        write_accept_summary(
            log_dir,
            "FAILED",
            "verify",
            patch_id=patch_id,
            failed_step=failed_step,
            options=options,
            extra_fields={
                "ROOT_CAUSE": root_cause or "-",
                "ROOT_CAUSE_LOG": root_log or "-",
                "CANONICAL_ACCEPTANCE_UNCHANGED": "true",
            },
        )
        print_accept_result(
            "FAILED",
            "verify",
            log_dir,
            patch_id=patch_id,
            failed_step=failed_step,
            options=options,
        )
        sys.exit(1)

    write_accept_summary(
        log_dir,
        "SUCCESS",
        "verify",
        patch_id=patch_id,
        latest_export_path=latest_export_path,
        options=options,
        extra_fields={"CANONICAL_ACCEPTANCE_UNCHANGED": "true"},
    )
    print_accept_result(
        "SUCCESS",
        "verify",
        log_dir,
        patch_id=patch_id,
        latest_export_path=latest_export_path,
        options=options,
    )


TERMINAL_RUN_STATUSES = {
    "SUCCESS",
    "FAILED",
    "ALREADY_APPLIED",
    "APPLIED",
    "BUSY",
    "STALE",
    "ABORTED",
    "INCONSISTENT",
    "INCOMPLETE_TRANSFER",
}


def run_log_candidates():
    candidates = []
    for base in (accept_log_base(), validation_log_base()):
        for run_file in base.glob("*/run.json"):
            candidates.append(run_file.parent)
    return candidates


def resolve_patch_id_for_status(ref):
    if ref == "latest" or re.fullmatch(r"\d+", ref) or (ARCHIVES_DIR / ref).is_dir():
        try:
            return resolve_patch_ref(ref).name
        except SystemExit:
            return None
    if re.fullmatch(PATCH_ID_PATTERN, ref):
        return ref
    return None


def find_run_log_dir(ref):
    path = Path(ref).expanduser()
    if path.is_file():
        return path.parent if path.name in ("SUMMARY.txt", "summary.log", "run.json", "accepted.json") else None
    if path.is_dir():
        return path
    for base in (accept_log_base(), validation_log_base()):
        direct = base / ref
        if direct.is_dir() and (direct / "run.json").is_file():
            return direct
    matches = [
        log_dir for log_dir in run_log_candidates()
        if log_dir.name == ref or load_run_record(log_dir).get("runId") == ref
    ]
    if matches:
        matches.sort(key=lambda item: load_run_record(item).get("updatedAt", ""), reverse=True)
        return matches[0]

    # Successful acceptance may compact or remove the temporary attempt directory.
    # Resolve the original run-id through durable accepted.json evidence instead of
    # requiring callers to retain a raw SUMMARY.txt path.
    if accept_log_base().is_dir():
        for accepted_path in accept_log_base().glob("*/accepted.json"):
            try:
                accepted = json.loads(accepted_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            if accepted.get("runId") == ref:
                return accepted_path.parent
    return None


def snapshot_from_log_dir(log_dir):
    log_dir = Path(log_dir).resolve()
    run = load_run_record(log_dir)
    fields = read_summary_fields(log_dir / "SUMMARY.txt")
    accepted = {}
    accepted_path = log_dir / "accepted.json"
    if accepted_path.is_file():
        try:
            accepted = json.loads(accepted_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            accepted = {}

    status = fields.get("STATUS") or run.get("status") or accepted.get("status") or "UNKNOWN"
    if status == "RUNNING" and run and not run_is_active(run):
        status = "STALE"
    live_phase = run.get("phase") if status == "RUNNING" else None
    patch_id = fields.get("PATCH_ID") or run.get("patchId") or accepted.get("patchId") or "-"
    snapshot = {
        "status": status,
        "command": fields.get("COMMAND") or run.get("command") or ("accept" if accepted else "-"),
        "runId": fields.get("RUN_ID") or run.get("runId") or accepted.get("runId") or log_dir.name,
        "patchId": patch_id,
        "artifactId": fields.get("ARTIFACT_ID") or run.get("artifactId") or accepted.get("artifactId") or "-",
        "phase": live_phase or fields.get("PHASE") or run.get("phase") or ("COMPLETE" if accepted else "-"),
        "failedStep": fields.get("FAILED_STEP") or run.get("failedStep") or "-",
        "pid": fields.get("PID") or run.get("pid") or "-",
        "commitStatus": fields.get("GIT_COMMIT_STATUS") or run.get("commitStatus") or accepted.get("commitStatus") or "-",
        "commitHash": fields.get("GIT_COMMIT_HASH") or run.get("commitHash") or accepted.get("commitHash") or "-",
        "pushStatus": fields.get("GIT_PUSH_STATUS") or run.get("pushStatus") or accepted.get("pushStatus") or "-",
        "rootCause": fields.get("ROOT_CAUSE") or "-",
        "summary": str(log_dir / "SUMMARY.txt"),
        "logDir": str(log_dir),
        "updatedAt": (
            run.get("updatedAt")
            or fields.get("UPDATED_AT")
            or accepted.get("updatedAt")
            or accepted.get("acceptedAt")
            or "-"
        ),
    }
    archive_data = archived_patch_data(patch_id) if patch_id != "-" else None
    if accepted and archive_data and archive_data.get("status") == "applied":
        snapshot["status"] = "APPLIED"
    return snapshot


def status_snapshot(ref):
    run_log_dir = find_run_log_dir(ref)
    if run_log_dir is not None:
        return snapshot_from_log_dir(run_log_dir)

    patch_id = resolve_patch_id_for_status(ref)
    if patch_id is None:
        fail(f"PATCH_RUN_NOT_FOUND: no run or patch matches {ref!r}.", 4)

    canonical_dir = accept_log_base() / patch_id
    canonical_fields = read_summary_fields(canonical_dir / "SUMMARY.txt")
    accepted_path = canonical_dir / "accepted.json"
    archive_data = archived_patch_data(patch_id)
    if accepted_path.is_file() or canonical_fields.get("STATUS") in ("SUCCESS", "ALREADY_APPLIED"):
        snapshot = snapshot_from_log_dir(canonical_dir)
        snapshot["status"] = "APPLIED" if archive_data and archive_data.get("status") == "applied" else snapshot["status"]
        if snapshot.get("commitStatus") == "COMMITTED" and not git_commit_exists(snapshot.get("commitHash")):
            snapshot["status"] = "INCONSISTENT"
            snapshot["rootCause"] = "Recorded Git commit is not available"
        return snapshot

    active = find_active_run(patch_id)
    if active is not None:
        return snapshot_from_log_dir(Path(active["logDir"]))

    candidates = []
    for base in (accept_log_base(), validation_log_base()):
        for run_file in base.glob("*/run.json"):
            run = load_run_record(run_file.parent)
            if run.get("patchId") == patch_id:
                candidates.append(run_file.parent)
    if candidates:
        candidates.sort(key=lambda item: load_run_record(item).get("updatedAt", ""), reverse=True)
        return snapshot_from_log_dir(candidates[0])

    if archive_data and archive_data.get("status") == "applied":
        return {
            "status": "INCOMPLETE_TRANSFER",
            "command": "accept",
            "runId": "-",
            "patchId": patch_id,
            "artifactId": archive_data.get("artifactId", "-"),
            "phase": "EVIDENCE",
            "failedStep": "canonical-acceptance-missing",
            "pid": "-",
            "commitStatus": "-",
            "commitHash": "-",
            "pushStatus": "-",
            "rootCause": "Applied archive exists without canonical successful acceptance evidence",
            "summary": str(canonical_dir / "SUMMARY.txt"),
            "logDir": str(canonical_dir),
            "updatedAt": "-",
        }
    fail(f"PATCH_RUN_NOT_FOUND: no status evidence exists for {patch_id}.", 4)


def parse_run_observer_args(args, require_ref=True, allow_output=False):
    ref = None
    output_format = "human"
    interval = 5
    timeout = None
    output = None
    i = 0
    while i < len(args):
        arg = args[i]
        if arg == "--patch":
            if i + 1 >= len(args):
                fail("--patch expects a patch id.", 2)
            if ref is not None:
                fail("Expected exactly one run or patch reference.", 2)
            ref = args[i + 1]
            i += 2
        elif arg == "--format":
            if i + 1 >= len(args):
                fail("--format expects human, env or json.")
            output_format = args[i + 1]
            if output_format not in ("human", "env", "json"):
                fail(f"Unsupported format: {output_format}")
            i += 2
        elif arg == "--interval":
            if i + 1 >= len(args):
                fail("--interval expects seconds.")
            interval = safe_int(args[i + 1])
            if interval is None or interval < 1:
                fail("--interval must be at least one second.")
            i += 2
        elif arg == "--timeout":
            if i + 1 >= len(args):
                fail("--timeout expects seconds.")
            timeout = safe_int(args[i + 1])
            if timeout is None or timeout < 0:
                fail("--timeout must be non-negative.")
            i += 2
        elif arg == "--output" and allow_output:
            if i + 1 >= len(args):
                fail("--output expects a file path.")
            output = args[i + 1]
            i += 2
        elif arg.startswith("--"):
            fail(f"Unknown run observer option: {arg}")
        else:
            if ref is not None:
                fail(f"Expected exactly one run or patch reference, got {arg!r}.")
            ref = arg
            i += 1
    if ref is not None:
        ref = str(ref).strip()
    if require_ref and not ref:
        fail("Run-ID oder Patch-Referenz darf nicht leer sein.", 2)
    return {
        "ref": ref,
        "format": output_format,
        "interval": interval,
        "timeout": timeout,
        "output": output,
    }


def snapshot_env_lines(snapshot):
    keys = (
        ("STATUS", "status"),
        ("COMMAND", "command"),
        ("RUN_ID", "runId"),
        ("PATCH_ID", "patchId"),
        ("ARTIFACT_ID", "artifactId"),
        ("PHASE", "phase"),
        ("FAILED_STEP", "failedStep"),
        ("PID", "pid"),
        ("GIT_COMMIT_STATUS", "commitStatus"),
        ("GIT_COMMIT_HASH", "commitHash"),
        ("GIT_PUSH_STATUS", "pushStatus"),
        ("ROOT_CAUSE", "rootCause"),
        ("SUMMARY", "summary"),
        ("LOG_DIR", "logDir"),
        ("UPDATED_AT", "updatedAt"),
    )
    return [f"{name}={snapshot.get(key, '-')}" for name, key in keys]


def print_snapshot(snapshot, output_format="human", detailed=False):
    if output_format == "json":
        print(json.dumps(snapshot, indent=2, ensure_ascii=False, sort_keys=True))
        return
    if output_format == "env":
        print("\n".join(snapshot_env_lines(snapshot)))
        return
    if detailed:
        print("Patch-Run-Result:")
        for line in snapshot_env_lines(snapshot):
            name, value = line.split("=", 1)
            print(f"  {name:<19} {value}")
        return
    print(
        f"status={snapshot.get('status', '-')} "
        f"patch={snapshot.get('patchId', '-')} "
        f"run={snapshot.get('runId', '-')} "
        f"phase={snapshot.get('phase', '-')} "
        f"step={snapshot.get('failedStep', '-')} "
        f"commit={snapshot.get('commitHash', '-')}"
    )


def status_command(args):
    options = parse_run_observer_args(args)
    print_snapshot(status_snapshot(options["ref"]), options["format"])


def run_terminal_exit_code(status):
    if status in ("SUCCESS", "ALREADY_APPLIED", "APPLIED"):
        return 0
    if status == "RUNNING":
        return 3
    if status in TERMINAL_RUN_STATUSES:
        return 1
    return 2


def observe_run_ref(ref, interval=5, timeout=None, quiet=False):
    ref = str(ref).strip() if ref is not None else ""
    if not ref:
        fail("Run-ID oder Patch-Referenz darf nicht leer sein.", 2)
    started = time.monotonic()
    last_key = None
    while True:
        snapshot = status_snapshot(ref)
        key = (
            snapshot.get("status"),
            snapshot.get("phase"),
            snapshot.get("failedStep"),
            snapshot.get("commitHash"),
        )
        if not quiet and key != last_key:
            print_snapshot(snapshot, "human")
            sys.stdout.flush()
            last_key = key
        if snapshot.get("status") != "RUNNING":
            if quiet:
                print_snapshot(snapshot, "human")
            raise SystemExit(run_terminal_exit_code(snapshot.get("status")))
        if timeout is not None and time.monotonic() - started >= timeout:
            print(f"status=TIMEOUT ref={ref} timeout={timeout}", file=sys.stderr)
            raise SystemExit(4)
        time.sleep(interval)


def observe_run(args, quiet=False):
    options = parse_run_observer_args(args)
    observe_run_ref(
        options["ref"],
        interval=options["interval"],
        timeout=options["timeout"],
        quiet=quiet,
    )


def watch_command(args):
    observe_run(args, quiet=False)


def wait_command(args):
    observe_run(args, quiet=True)


def result_command(args):
    options = parse_run_observer_args(args)
    snapshot = status_snapshot(options["ref"])
    print_snapshot(snapshot, options["format"], detailed=True)
    raise SystemExit(run_terminal_exit_code(snapshot.get("status")))


def diagnose_command(args):
    options = parse_run_observer_args(args, allow_output=True)
    snapshot = status_snapshot(options["ref"])
    output = options.get("output")
    if output:
        output_path = Path(output).expanduser()
        if not output_path.is_absolute():
            output_path = PROJECT_ROOT / output_path
    else:
        diagnostics = PROJECT_ROOT / "build" / "patch-diagnostics"
        diagnostics.mkdir(parents=True, exist_ok=True)
        output_path = diagnostics / f"{sanitize_name(snapshot.get('runId') or snapshot.get('patchId'))}.txt"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    log_dir = Path(snapshot.get("logDir", ""))
    selected = []
    if log_dir.is_dir():
        logs = sorted(
            log_dir.rglob("*.log"),
            key=lambda path: path.stat().st_mtime,
            reverse=True,
        )
        selected = logs[:12]
    lines = [
        "SPRINGMASTER PATCH RUN DIAGNOSIS",
        "=" * 72,
        "",
        "STATUS",
        "-" * 72,
        *snapshot_env_lines(snapshot),
        "",
        "GIT",
        "-" * 72,
        f"HEAD={current_git_head() or '-'}",
    ]
    if is_git_worktree():
        dirty = git_status_paths(ignore_accept_log=True)
        lines.append(f"DIRTY_PATHS={len(dirty)}")
        lines.extend(f"  {path}" for path in dirty[:100])
    lines.extend(["", "ERROR CANDIDATES", "-" * 72])
    marker_re = re.compile(
        r"(<<< FAILURE!|<<< ERROR!|AssertionError|Caused by:|BUILD FAILURE|"
        r"Failed to execute goal|\[ERROR\]|Traceback|Exception:)"
    )
    found = 0
    for log_file in selected:
        try:
            for number, raw_line in enumerate(
                log_file.read_text(encoding="utf-8", errors="replace").splitlines(),
                start=1,
            ):
                if marker_re.search(raw_line):
                    lines.append(f"{log_file}:{number}:{raw_line[:1000]}")
                    found += 1
                    if found >= 120:
                        break
        except OSError:
            continue
        if found >= 120:
            break
    if found == 0:
        lines.append("No standard error markers found.")
    lines.extend(["", "LATEST LOG TAILS", "-" * 72])
    for log_file in selected[:4]:
        lines.append("")
        lines.append(f"## {log_file}")
        try:
            tail = log_file.read_text(encoding="utf-8", errors="replace").splitlines()[-80:]
            lines.extend(line[:2000] for line in tail)
        except OSError as exc:
            lines.append(f"Cannot read log: {exc}")
    atomic_write_text(output_path, "\n".join(lines) + "\n")
    print(f"DIAGNOSIS={output_path}")
    print(f"BYTES={output_path.stat().st_size}")


def doctor_command(args):
    options = parse_run_observer_args(args, require_ref=False)
    findings = []
    git_available = is_git_worktree()
    dirty = git_status_paths(ignore_accept_log=True) if git_available else []
    lock_path = project_write_lock_path()
    lock_info = read_lock_info(lock_path) if lock_path.exists() else None
    if lock_info and lock_is_stale(lock_info):
        findings.append({"severity": "warning", "code": "STALE_WRITE_LOCK", "path": str(lock_path)})
    elif lock_info:
        findings.append({"severity": "info", "code": "ACTIVE_WRITE_LOCK", "owner": lock_info})

    active_runs = []
    stale_runs = []
    for log_dir in run_log_candidates():
        data = load_run_record(log_dir)
        if data.get("status") != "RUNNING":
            continue
        if run_is_active(data):
            active_runs.append(data)
        else:
            stale_runs.append(data)
            findings.append({
                "severity": "warning",
                "code": "STALE_RUN",
                "runId": data.get("runId"),
                "patchId": data.get("patchId"),
                "logDir": str(log_dir),
            })

    incomplete = []
    historical_without_canonical = []
    for patch_dir in archive_dirs():
        data = archived_patch_data(patch_dir.name)
        if not data or data.get("status") != "applied":
            continue
        fields = canonical_accept_fields(patch_dir.name)
        if fields.get("STATUS") not in ("SUCCESS", "ALREADY_APPLIED"):
            if is_historical_pre_run_api_patch(patch_dir.name):
                historical_without_canonical.append(patch_dir.name)
            else:
                incomplete.append(patch_dir.name)
                findings.append({
                    "severity": "error",
                    "code": "APPLIED_WITHOUT_CANONICAL_ACCEPTANCE",
                    "patchId": patch_dir.name,
                })
        elif fields.get("GIT_COMMIT_STATUS") == "COMMITTED" and not git_commit_exists(fields.get("GIT_COMMIT_HASH")):
            findings.append({
                "severity": "error",
                "code": "ACCEPTANCE_COMMIT_MISSING",
                "patchId": patch_dir.name,
                "commit": fields.get("GIT_COMMIT_HASH"),
            })

    if historical_without_canonical:
        findings.append({
            "severity": "warning",
            "code": "HISTORICAL_APPLIED_WITHOUT_CANONICAL_ACCEPTANCE",
            "count": len(historical_without_canonical),
            "firstPatchId": historical_without_canonical[0],
            "lastPatchId": historical_without_canonical[-1],
            "cutoverPatchNumber": PATCH_RUN_API_CUTOVER_NUMBER,
        })

    report = {
        "schemaVersion": "springmaster.patch-doctor.v1",
        "status": "PASS" if not any(item["severity"] == "error" for item in findings) else "FAIL",
        "projectRoot": str(PROJECT_ROOT),
        "gitAvailable": git_available,
        "gitHead": current_git_head(),
        "gitDirtyPaths": dirty,
        "writeLock": lock_info,
        "activeRuns": active_runs,
        "staleRuns": stale_runs,
        "incompleteAppliedPatches": incomplete,
        "historicalAppliedWithoutCanonicalAcceptance": historical_without_canonical,
        "findings": findings,
    }
    if options["format"] == "json":
        print(json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True))
    else:
        print("Patch-Doctor:")
        print(f"  Status:        {report['status']}")
        print(f"  Git-HEAD:      {report['gitHead'] or '-'}")
        print(f"  Dirty-Paths:   {len(dirty)}")
        print(f"  Active-Runs:   {len(active_runs)}")
        print(f"  Stale-Runs:    {len(stale_runs)}")
        print(f"  Historical-Applied-Without-Canonical: {len(historical_without_canonical)}")
        print(f"  Findings:      {len(findings)}")
        for finding in findings[:30]:
            subject = (
                finding.get("patchId")
                or finding.get("runId")
                or finding.get("path")
                or (f"count={finding.get('count')}" if finding.get("count") is not None else "")
            )
            print(f"  - {finding['severity'].upper()} {finding['code']} {subject}")
    if report["status"] != "PASS":
        raise SystemExit(1)


def first_positional_arg(args):
    value_options = {"--test", "--profile", "--lock-timeout"}
    i = 0
    while i < len(args):
        arg = args[i]
        if arg in value_options:
            i += 2
            continue
        if arg.startswith("--"):
            i += 1
            continue
        return arg
    return None

def is_background_parent_command():
    return COMMAND in ("accept", "verify") and "--background" in ARGS and os.environ.get("PATCH_BACKGROUND_CHILD") != "1"

def command_needs_write_lock():
    if is_background_parent_command():
        return False
    if COMMAND == "apply":
        return "--dry-run" not in ARGS
    if COMMAND == "rollback":
        return "--dry-run" not in ARGS
    if COMMAND in ("accept", "verify"):
        return True
    return False

def dispatch_command():
    if COMMAND in ("--help", "-h", "help"):
        print(USAGE)
    elif COMMAND == "apply":
        apply_command(ARGS)
    elif COMMAND == "live-baseline":
        live_baseline_command(ARGS)
    elif COMMAND == "accept":
        accept_command(ARGS)
    elif COMMAND == "verify":
        verify_command(ARGS)
    elif COMMAND == "status":
        status_command(ARGS)
    elif COMMAND == "watch":
        watch_command(ARGS)
    elif COMMAND == "wait":
        wait_command(ARGS)
    elif COMMAND == "result":
        result_command(ARGS)
    elif COMMAND == "diagnose":
        diagnose_command(ARGS)
    elif COMMAND == "doctor":
        doctor_command(ARGS)
    elif COMMAND == "list":
        list_command()
    elif COMMAND == "show":
        show_command(ARGS)
    elif COMMAND == "rollback":
        rollback_command(ARGS)
    else:
        fail(f"Unbekanntes Kommando: {COMMAND}", 1)

def main():
    if not command_needs_write_lock():
        dispatch_command()
        return

    wait = parse_wait_flag(ARGS)
    timeout_seconds = parse_lock_timeout(ARGS)
    subject = first_positional_arg(ARGS)
    configured_log_dir = os.environ.get("PATCH_ACCEPT_LOG_DIR")
    if configured_log_dir and COMMAND in ("accept", "verify"):
        lock_log_dir = Path(configured_log_dir).expanduser()
        if not lock_log_dir.is_absolute():
            lock_log_dir = PROJECT_ROOT / lock_log_dir
        write_run_record(
            lock_log_dir,
            status="RUNNING",
            phase="WAITING_FOR_LOCK" if wait else "LOCK_ACQUIRE",
        )
    try:
        with ProjectWriteLock(COMMAND, subject=subject, wait=wait, timeout_seconds=timeout_seconds):
            dispatch_command()
    except PatchLockBusy as exc:
        configured_log_dir = os.environ.get("PATCH_ACCEPT_LOG_DIR")
        if configured_log_dir:
            log_dir = Path(configured_log_dir).expanduser()
            if not log_dir.is_absolute():
                log_dir = PROJECT_ROOT / log_dir
        else:
            stamp = datetime.now(timezone.utc).astimezone().strftime("%Y%m%d_%H%M%S")
            base = validation_log_base() if COMMAND == "verify" else accept_log_base()
            log_dir = base / f"busy-{stamp}_{COMMAND}"
        write_busy_summary(log_dir, COMMAND, exc.lock_path, exc.info)
        print_busy_result(COMMAND, log_dir, exc.lock_path, exc.info)
        sys.exit(2)

if __name__ == "__main__":
    main()
