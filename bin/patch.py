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
  ./bin/patch.sh accept <patch.zip> [--background] [--wait] [--lock-timeout <seconds>] [--profile auto|docs|tooling|code] [--test <MavenTest>] [--full-test|--no-full-test] [--export|--no-export] [--commit] [--push]
  ./bin/patch.sh verify <patch-id|patch-number|latest> [--background] [--wait] [--lock-timeout <seconds>] [--profile auto|docs|tooling|code] [--test <MavenTest>] [--full-test|--no-full-test] [--export|--no-export]
  ./bin/patch.sh rollback [--dry-run] [--wait] <patch-id|patch-number|latest>
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
  - Für lange Läufe ist --background --wait der empfohlene Modus.
"""

if len(sys.argv) < 3:
    print(USAGE)
    sys.exit(1)

PROJECT_ROOT = Path(sys.argv[1]).resolve()
COMMAND = sys.argv[2]
ARGS = sys.argv[3:]
ARCHIVES_DIR = PROJECT_ROOT / "patches" / "archives"

def fail(message, code=1):
    print(f"Fehler: {message}", file=sys.stderr)
    sys.exit(code)

def now_iso():
    return datetime.now(timezone.utc).astimezone().isoformat()

def sanitize_name(value):
    value = Path(str(value)).name
    value = re.sub(r"\.zip$", "", value, flags=re.IGNORECASE)
    value = re.sub(r"[^A-Za-z0-9._-]+", "_", value).strip("._-")
    return value or "patch"

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
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

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
    return "--wait" in args or parse_bool_env("PATCH_LOCK_WAIT", False)

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
    log_dir.mkdir(parents=True, exist_ok=True)
    owner = f"PID={lock_info.get('pid', '-')} HOST={lock_info.get('host', '-')} COMMAND={lock_info.get('command', '-')}"
    lines = [
        "STATUS=BUSY",
        f"COMMAND={command_name}",
        f"LOCK={lock_path}",
        f"OWNER={owner}",
        f"OWNER_STARTED={lock_info.get('startedAt', '-')}",
        f"OWNER_SUBJECT={lock_info.get('subject', '-')}",
        f"LOG_DIR={log_dir}",
    ]
    for name in ("summary.log", "SUMMARY.txt"):
        (log_dir / name).write_text("\n".join(lines) + "\n", encoding="utf-8")
    (log_dir / "STATUS.txt").write_text("BUSY\n", encoding="utf-8")

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
    print("  Aktion:       Erneut mit --wait ausführen oder aktiven Lauf prüfen.")

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
        elif arg == "--wait":
            wait = True
            i += 1
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

def write_accept_summary(log_dir, status, command_name, patch_id=None, failed_step=None, latest_export_path=None, options=None, git_commit_script=None, git_commit_result=None):
    summary_path = log_dir / "summary.log"
    error_summary = extract_error_summary(log_dir) if status not in ("SUCCESS", "ALREADY_APPLIED") else ""
    options = options or {}
    lines = [
        f"STATUS={status}",
        f"COMMAND={command_name}",
        f"PATCH_ID={patch_id or '-'}",
        f"FAILED_STEP={failed_step or '-'}",
        f"PROFILE={options.get('profile', '-')}",
        f"FULL_TEST={options.get('fullTest', '-')}",
        f"EXPORT={options.get('export', '-')}",
        f"BACKGROUND={options.get('background', '-')}",
        f"WAIT={options.get('wait', '-')}",
        f"LOG_DIR={log_dir}",
        f"LATEST_EXPORT={latest_export_path or '-'}",
        f"GIT_COMMIT_SCRIPT={git_commit_script or '-'}",
        f"GIT_COMMIT_STATUS={(git_commit_result or {}).get('status', '-')}",
        f"GIT_COMMIT_HASH={(git_commit_result or {}).get('hash', '-')}",
        f"GIT_PUSH_STATUS={(git_commit_result or {}).get('pushStatus', '-')}",
    ]
    if error_summary:
        lines.append("")
        lines.append("ERROR_SUMMARY:")
        lines.append(error_summary)
    content = "\n".join(lines) + "\n"
    summary_path.write_text(content, encoding="utf-8")
    (log_dir / "SUMMARY.txt").write_text(content, encoding="utf-8")
    (log_dir / "STATUS.txt").write_text(status + "\n", encoding="utf-8")
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

def make_accept_log_dir(subject):
    configured_log_dir = os.environ.get("PATCH_ACCEPT_LOG_DIR")
    if configured_log_dir:
        log_dir = Path(configured_log_dir).expanduser()
        if not log_dir.is_absolute():
            log_dir = PROJECT_ROOT / log_dir
        log_dir.mkdir(parents=True, exist_ok=True)
        return log_dir.resolve(), True
    run_id = datetime.now(timezone.utc).astimezone().strftime("%Y%m%d_%H%M%S") + "_" + sanitize_name(subject)
    log_dir = accept_log_base() / run_id
    log_dir.mkdir(parents=True, exist_ok=False)
    return log_dir, False

def args_without_background(args):
    return [arg for arg in args if arg != "--background"]

def start_background_command(command_name, args, subject):
    log_dir, _fixed = make_accept_log_dir(subject)
    run_log = log_dir / "run.log"
    summary_content = "\n".join([
        "STATUS=RUNNING",
        f"COMMAND={command_name}",
        f"PATCH_ID=-",
        f"LOG_DIR={log_dir}",
        f"RUN_LOG={run_log}",
    ]) + "\n"
    (log_dir / "summary.log").write_text(summary_content, encoding="utf-8")
    (log_dir / "SUMMARY.txt").write_text(summary_content, encoding="utf-8")
    (log_dir / "STATUS.txt").write_text("RUNNING\n", encoding="utf-8")

    env = dict(os.environ)
    env["PATCH_BACKGROUND_CHILD"] = "1"
    env["PATCH_ACCEPT_LOG_DIR"] = str(log_dir)
    child_args = args_without_background(args)
    cmd = [sys.executable, str(Path(__file__).resolve()), str(PROJECT_ROOT), command_name] + child_args
    out = run_log.open("a", encoding="utf-8")
    out.write(f"== Background {command_name} ==\n")
    out.write(f"$ {command_to_text(cmd)}\n\n")
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
    out.close()

    label = "Patch-Accept" if command_name == "accept" else "Patch-Verify"
    print(f"{label}:")
    print("  Status:       RUNNING")
    print(f"  PID:          {proc.pid}")
    print(f"  Summary:      {log_dir / 'SUMMARY.txt'}")
    print(f"  Log:          {run_log}")
    print(f"  Follow:       tail --pid={proc.pid} -F {log_dir / 'SUMMARY.txt'}")

def run_validation_steps(log_dir, options):
    validation_env = validation_subprocess_env()
    if options["toolingSelfcheck"]:
        rc = run_tooling_verification(log_dir)
        if rc != 0:
            return "tooling", None

    for test_selector in options["tests"]:
        rc = run_process_step(
            f"Configured test {test_selector}",
            configured_test_selector_command(test_selector),
            log_dir / f"test-{sanitize_name(test_selector)}.log",
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
        if arg in ("--background", "--wait", "--push"):
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
    baseline_head = git_output_at(PROJECT_ROOT, "rev-parse", "HEAD")
    log_dir, fixed_log_dir = make_accept_log_dir(f"transaction-{patch_id}")
    ensure_git_clean_before_commit(log_dir)

    transaction_parent = Path(tempfile.mkdtemp(prefix=f"springmaster-accept-{patch_id}-"))
    worktree = transaction_parent / "worktree"
    child_log = log_dir / "worktree-child.log"
    worktree_added = False
    child_rc = 1

    try:
        add_result = subprocess.run(
            ["git", "worktree", "add", "--detach", str(worktree), baseline_head],
            cwd=PROJECT_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        (log_dir / "worktree-add.log").write_text(add_result.stdout or "", encoding="utf-8")
        if add_result.returncode != 0:
            fail(f"PATCH_ACCEPT_WORKTREE_CREATE_FAILED: see {log_dir / 'worktree-add.log'}")
        worktree_added = True

        child_env = dict(os.environ)
        child_env["PATCH_ACCEPT_WORKTREE_CHILD"] = "1"
        child_env.pop("PATCH_ACCEPT_LOG_DIR", None)
        child_command = [
            sys.executable,
            str(worktree / "bin" / "patch.py"),
            str(worktree),
            "accept",
            *transaction_child_args(args),
        ]
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
            fail(
                "PATCH_ACCEPT_LIVE_STATE_CHANGED_DURING_VALIDATION: the live repository "
                "must remain unchanged while the worktree is validated."
            )

        child_accept = worktree / "patches" / "logs" / "accept" / patch_id
        if child_rc != 0:
            copy_tree_if_present(child_accept, log_dir / "child-accept")
            write_accept_summary(
                log_dir,
                "FAILED",
                "accept",
                patch_id=patch_id,
                failed_step="worktree-validation",
                options=options,
            )
            print_accept_result(
                "FAILED",
                "accept",
                log_dir,
                patch_id=patch_id,
                failed_step="worktree-validation",
                options=options,
            )
            raise SystemExit(child_rc)

        child_head = git_output_at(worktree, "rev-parse", "HEAD")
        child_parent = git_output_at(worktree, "rev-parse", "HEAD^")
        if child_parent != baseline_head:
            fail(
                "PATCH_ACCEPT_WORKTREE_PARENT_MISMATCH: qualified commit does not descend "
                "directly from the live baseline."
            )

        cherry_pick_args = ["cherry-pick", child_head]
        if not options.get("gitCommit"):
            cherry_pick_args = ["cherry-pick", "--no-commit", child_head]
        cherry = git_run(cherry_pick_args, log_dir=log_dir)
        if cherry.returncode != 0:
            git_run(["cherry-pick", "--abort"], log_dir=log_dir)
            fail("PATCH_ACCEPT_CHERRY_PICK_FAILED: qualified commit could not be transferred to live.")

        live_archive = ARCHIVES_DIR / patch_id
        if live_archive.exists():
            fail(f"PATCH_ACCEPT_ARCHIVE_CONFLICT_AFTER_VALIDATION: {live_archive}")
        copy_tree_if_present(worktree / "patches" / "archives" / patch_id, live_archive)

        final_log_dir = accept_log_base() / patch_id
        if final_log_dir.exists() and final_log_dir != log_dir:
            shutil.rmtree(final_log_dir)
        if final_log_dir != log_dir:
            final_log_dir.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(log_dir), str(final_log_dir))
            log_dir = final_log_dir
        copy_tree_if_present(child_accept, log_dir / "child-accept")
        copy_tree_if_present(worktree / "exports", PROJECT_ROOT / "exports")

        latest_export = latest_full_export()
        latest_export_path = str(latest_export) if latest_export else None
        git_commit_result = {
            "status": "COMMITTED" if options.get("gitCommit") else "VALIDATED_NOT_COMMITTED",
            "hash": git_output_at(PROJECT_ROOT, "rev-parse", "--short", "HEAD") if options.get("gitCommit") else None,
            "pushStatus": "SKIPPED",
            "message": f"qualified in isolated worktree: {child_head[:12]}",
        }
        if options.get("gitPush"):
            push_result = git_run(["push"], log_dir=log_dir)
            if push_result.returncode != 0:
                fail("PATCH_ACCEPT_PUSH_FAILED: qualified live commit was not pushed.")
            git_commit_result["pushStatus"] = "PUSHED"

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


def accept_command(args):
    options = parse_accept_verify_args(args, "Patch-ZIP")
    zip_path = Path(options["subject"]).expanduser().resolve()
    if not zip_path.exists() or not zip_path.is_file():
        fail(f"Patch-ZIP nicht gefunden: {zip_path}")

    if options.get("background") and os.environ.get("PATCH_BACKGROUND_CHILD") != "1":
        start_background_command("accept", args, zip_path.name)
        return

    patch_info = inspect_patch_zip(zip_path)
    target_paths = patch_info["targetPaths"]
    options = resolve_validation_profile(options, target_paths)

    if os.environ.get("PATCH_ACCEPT_WORKTREE_CHILD") != "1" and summary_has_effect(patch_info["summary"]):
        transactional_accept_command(args, options, zip_path, patch_info)
        return

    log_dir, fixed_log_dir = make_accept_log_dir(zip_path.name)

    if options.get("gitCommit"):
        ensure_git_clean_before_commit(log_dir)

    script_path = Path(__file__).resolve()
    live_baseline_rc = run_process_step(
        "Patch live baseline preflight",
        [sys.executable, str(script_path), str(PROJECT_ROOT), "live-baseline", str(zip_path)],
        log_dir / "live-baseline.log",
    )
    if live_baseline_rc != 0:
        write_accept_summary(log_dir, "FAILED", "accept", failed_step="live-baseline", options=options)
        print_accept_result("FAILED", "accept", log_dir, failed_step="live-baseline", options=options)
        sys.exit(live_baseline_rc)

    dry_run_rc = run_process_step(
        "Patch dry-run",
        [sys.executable, str(script_path), str(PROJECT_ROOT), "apply", "--dry-run", str(zip_path)],
        log_dir / "dry-run.log",
    )
    if dry_run_rc != 0:
        write_accept_summary(log_dir, "FAILED", "accept", failed_step="dry-run", options=options)
        print_accept_result("FAILED", "accept", log_dir, failed_step="dry-run", options=options)
        sys.exit(dry_run_rc)

    if not summary_has_effect(patch_info["summary"]):
        existing_patch_dir = find_applied_patch_by_name(patch_info["name"])
        if existing_patch_dir is None:
            write_accept_summary(log_dir, "FAILED", "accept", failed_step="no-effective-change", options=options)
            print_accept_result("FAILED", "accept", log_dir, failed_step="no-effective-change", options=options)
            sys.exit(3)

        patch_id = existing_patch_dir.name
        reaccept_stamp = datetime.now(timezone.utc).astimezone().strftime("reaccept-%Y%m%d_%H%M%S")
        final_log_dir = accept_log_base() / patch_id / reaccept_stamp
        if not fixed_log_dir:
            final_log_dir.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(log_dir), str(final_log_dir))
            log_dir = final_log_dir

        failed_step, latest_export_path = run_validation_steps(log_dir, options)
        if failed_step:
            write_accept_summary(log_dir, "FAILED", "accept", patch_id=patch_id, failed_step=failed_step, options=options)
            print_accept_result("FAILED", "accept", log_dir, patch_id=patch_id, failed_step=failed_step, options=options)
            sys.exit(1)

        git_commit_script = generate_git_commit_script(log_dir, patch_id)
        git_commit_result = None
        if options.get("gitCommit"):
            git_commit_result = execute_git_commit(log_dir, patch_id, latest_export_path=latest_export_path, push=options.get("gitPush", False))
        write_accept_summary(log_dir, "ALREADY_APPLIED", "accept", patch_id=patch_id, latest_export_path=latest_export_path, options=options, git_commit_script=git_commit_script, git_commit_result=git_commit_result)
        print_accept_result("ALREADY_APPLIED", "accept", log_dir, patch_id=patch_id, latest_export_path=latest_export_path, options=options, git_commit_script=git_commit_script, git_commit_result=git_commit_result)
        return

    apply_rc = run_process_step(
        "Patch apply",
        [sys.executable, str(script_path), str(PROJECT_ROOT), "apply", str(zip_path)],
        log_dir / "apply.log",
    )
    if apply_rc != 0:
        write_accept_summary(log_dir, "FAILED", "accept", failed_step="apply", options=options)
        print_accept_result("FAILED", "accept", log_dir, failed_step="apply", options=options)
        sys.exit(apply_rc)

    applied_patch_dir = archive_dirs()[-1]
    patch_id = applied_patch_dir.name
    final_log_dir = accept_log_base() / patch_id
    if not fixed_log_dir and final_log_dir != log_dir:
        if final_log_dir.exists():
            shutil.rmtree(final_log_dir)
        shutil.move(str(log_dir), str(final_log_dir))
        log_dir = final_log_dir

    show_rc = run_process_step(
        "Patch show latest",
        [sys.executable, str(script_path), str(PROJECT_ROOT), "show", "latest"],
        log_dir / "show.log",
    )
    if show_rc != 0:
        write_accept_summary(log_dir, "FAILED", "accept", patch_id=patch_id, failed_step="show", options=options)
        print_accept_result("FAILED", "accept", log_dir, patch_id=patch_id, failed_step="show", options=options)
        sys.exit(show_rc)

    failed_step, latest_export_path = run_validation_steps(log_dir, options)
    if failed_step:
        write_accept_summary(log_dir, "FAILED", "accept", patch_id=patch_id, failed_step=failed_step, options=options)
        print_accept_result("FAILED", "accept", log_dir, patch_id=patch_id, failed_step=failed_step, options=options)
        sys.exit(1)

    git_commit_script = generate_git_commit_script(log_dir, patch_id)
    git_commit_result = None
    if options.get("gitCommit"):
        git_commit_result = execute_git_commit(log_dir, patch_id, latest_export_path=latest_export_path, push=options.get("gitPush", False))
    write_accept_summary(log_dir, "SUCCESS", "accept", patch_id=patch_id, latest_export_path=latest_export_path, options=options, git_commit_script=git_commit_script, git_commit_result=git_commit_result)
    print_accept_result("SUCCESS", "accept", log_dir, patch_id=patch_id, latest_export_path=latest_export_path, options=options, git_commit_script=git_commit_script, git_commit_result=git_commit_result)
def verify_command(args):
    options = parse_accept_verify_args(args, "Patch-Referenz")
    if options.get("background") and os.environ.get("PATCH_BACKGROUND_CHILD") != "1":
        start_background_command("verify", args, str(options["subject"]))
        return
    patch_dir = resolve_patch_ref(options["subject"])
    patch_id = patch_dir.name
    target_paths = target_paths_from_patch_dir(patch_dir)
    options = resolve_validation_profile(options, target_paths)

    log_dir = accept_log_base() / patch_id
    log_dir.mkdir(parents=True, exist_ok=True)
    verify_stamp = datetime.now(timezone.utc).astimezone().strftime("%Y%m%d_%H%M%S")
    verify_marker = log_dir / f"verify-{verify_stamp}.log"
    verify_marker.write_text(f"VERIFY_STARTED={now_iso()}\nPATCH_ID={patch_id}\n", encoding="utf-8")

    failed_step, latest_export_path = run_validation_steps(log_dir, options)
    if failed_step:
        write_accept_summary(log_dir, "FAILED", "verify", patch_id=patch_id, failed_step=failed_step, options=options)
        print_accept_result("FAILED", "verify", log_dir, patch_id=patch_id, failed_step=failed_step, options=options)
        sys.exit(1)

    write_accept_summary(log_dir, "SUCCESS", "verify", patch_id=patch_id, latest_export_path=latest_export_path, options=options)
    print_accept_result("SUCCESS", "verify", log_dir, patch_id=patch_id, latest_export_path=latest_export_path, options=options)
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
    try:
        with ProjectWriteLock(COMMAND, subject=subject, wait=wait, timeout_seconds=timeout_seconds):
            dispatch_command()
    except PatchLockBusy as exc:
        stamp = datetime.now(timezone.utc).astimezone().strftime("%Y%m%d_%H%M%S")
        log_dir = accept_log_base() / f"busy-{stamp}_{COMMAND}"
        write_busy_summary(log_dir, COMMAND, exc.lock_path, exc.info)
        print_busy_result(COMMAND, log_dir, exc.lock_path, exc.info)
        sys.exit(2)

if __name__ == "__main__":
    main()
