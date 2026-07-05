#!/usr/bin/env python3
import fnmatch
import hashlib
import json
import os
import re
import shlex
import shutil
import socket
import subprocess
import sys
import tempfile
import zipfile
import time
from datetime import datetime, timezone
from pathlib import Path

USAGE = """Verwendung:
  ./bin/patch.sh --help
  ./bin/patch.sh help
  ./bin/patch.sh apply [--dry-run] [--wait] <patch.zip>
  ./bin/patch.sh accept <patch.zip> [--background] [--wait] [--lock-timeout <seconds>] [--profile auto|docs|tooling|code] [--test <MavenTest>] [--full-test|--no-full-test] [--export|--no-export]
  ./bin/patch.sh verify <patch-id|patch-number|latest> [--background] [--wait] [--lock-timeout <seconds>] [--profile auto|docs|tooling|code] [--test <MavenTest>] [--full-test|--no-full-test] [--export|--no-export]
  ./bin/patch.sh rollback [--dry-run] [--wait] <patch-id|patch-number|latest>
  ./bin/patch.sh list
  ./bin/patch.sh show <patch-id|patch-number|latest>

Pflichtregeln:
  - manifest.json ist verpflichtend.
  - manifest.scope ist verpflichtend.
  - manifest.name ist verpflichtend.
  - logs/CHANGELOG-*.md ist verpflichtend.
  - Erlaubte ZIP-Wurzelpfade: manifest.json, files/**, delete/**, logs/CHANGELOG-*.md.
  - Legacy-Patches werden abgelehnt.
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

def restore_executable_bit(target_rel, target_abs):
    if target_rel.startswith("bin/") and (target_rel.endswith(".sh") or target_rel.endswith(".py")) and target_abs.exists():
        target_abs.chmod(target_abs.stat().st_mode | 0o111)

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

def read_project_env():
    env = dict(os.environ)
    env_file = PROJECT_ROOT / ".env"
    if not env_file.exists():
        return env
    try:
        lines = env_file.read_text(encoding="utf-8").splitlines()
    except Exception as exc:
        fail(f"Kann .env nicht lesen: {env_file}: {exc}")
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
            "src/main/java/de/cocondo/platform/app/**",
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
            "src/main/java/de/cocondo/system/**",
            "src/test/java/de/cocondo/system/**",
            "PROJECT_DOCS/CORE/**",
            "PROJECT_DOCS/CONCEPT/SPRINGMASTER_VERSION_POLICY.md",
            "patches/logs/core/**",
        ],
        "demo": [
            "platform/versions/platform.env",
            "src/main/java/de/cocondo/platform/demo/**",
            "src/test/java/de/cocondo/platform/demo/**",
            "PROJECT_DOCS/DEMO/**",
            "PROJECT_DOCS/CONCEPT/SPRINGMASTER_VERSION_POLICY.md",
            "patches/logs/demo/**",
        ],
        "app": [
            "src/main/java/de/cocondo/platform/app/**",
            "src/test/java/de/cocondo/platform/app/**",
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
    return [validate_scope_name(scope) for scope in split_scope_names(project_env().get("PATCH_LOCAL_SCOPES", ""))]

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
        return tmp_dir
    except Exception:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        raise

def validate_manifest(manifest):
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
    return scope.strip(), name.strip()

def collect_patch(tmp_dir):
    manifest_path = tmp_dir / "manifest.json"
    if not manifest_path.exists():
        fail("manifest.json ist verpflichtend. Legacy-Patches werden nicht mehr akzeptiert.")
    manifest = read_json(manifest_path)
    scope, name = validate_manifest(manifest)
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
    return manifest, scope, name, operations

def classify_operation(op, tmp_dir):
    target = ensure_inside_root(PROJECT_ROOT / op["target"])
    if op["type"] == "delete":
        return "deleted" if target.exists() else "delete_missing"
    source = tmp_dir / op["source"]
    if not target.exists():
        return "new"
    if target.is_dir():
        fail(f"Ziel ist ein Verzeichnis und kann nicht überschrieben werden: {op['target']}")
    return "unchanged" if sha256_file(target) == sha256_file(source) else "modified"

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
            shutil.copy2(source_abs, after)
            target_abs.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_abs, target_abs)
            restore_executable_bit(target_rel, target_abs)
        elif op["type"] == "delete":
            if target_abs.exists():
                if target_abs.is_dir():
                    fail(f"Delete für Verzeichnisse wird nicht unterstützt: {target_rel}")
                copy_before(target_rel, before_root)
                target_abs.unlink()

    return summary, entries

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
        manifest, scope, name, operations = collect_patch(tmp_dir)
        patch_number = next_patch_number()
        patch_id = f"{patch_number}_{sanitize_name(name)}"
        archive_dir = ARCHIVES_DIR / patch_id

        if archive_dir.exists():
            fail(f"Patch-Archiv existiert bereits: {archive_dir}")

        if not dry_run:
            archive_dir.mkdir(parents=True, exist_ok=False)
            (archive_dir / "source").mkdir(parents=True, exist_ok=True)
            shutil.copy2(zip_path, archive_dir / "source" / zip_path.name)
            write_json(archive_dir / "manifest.json", manifest)

        summary, entries = apply_operations(operations, tmp_dir, archive_dir, dry_run)

        log = {
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
                restore_executable_bit(rel, target)
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
        _manifest, _scope, _name, operations = collect_patch(tmp_dir)
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
        manifest, scope, name, operations = collect_patch(tmp_dir)
        summary, entries = apply_operations(operations, tmp_dir, ARCHIVES_DIR / "__dry_run_inspection__", True)
        return {
            "manifest": manifest,
            "scope": scope,
            "name": name,
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

def run_process_step(step_name, cmd, log_file, shell=False):
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

def write_accept_summary(log_dir, status, command_name, patch_id=None, failed_step=None, latest_export_path=None, options=None, git_commit_script=None):
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

def print_accept_result(status, command_name, log_dir, patch_id=None, latest_export_path=None, failed_step=None, options=None, git_commit_script=None):
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
    print(f"  Summary:      {log_dir / 'SUMMARY.txt'}")
    print(f"  Log:          {log_dir}")
    if latest_export_path:
        print(f"  Export-Pfad:  {latest_export_path}")
    if git_commit_script:
        print(f"  Git-Commit:   {git_commit_script}")
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
        )
        if rc != 0:
            return f"test:{test_selector}", None

    if options["fullTest"]:
        rc = run_process_step(
            "Configured full test",
            configured_full_test_command(),
            log_dir / "full-test.log",
            shell=True,
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
        )
        if rc != 0:
            return "export", None
        latest = latest_full_export()
        latest_export_path = str(latest) if latest else None

    return None, latest_export_path

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

    log_dir, fixed_log_dir = make_accept_log_dir(zip_path.name)

    script_path = Path(__file__).resolve()
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
        write_accept_summary(log_dir, "ALREADY_APPLIED", "accept", patch_id=patch_id, latest_export_path=latest_export_path, options=options, git_commit_script=git_commit_script)
        print_accept_result("ALREADY_APPLIED", "accept", log_dir, patch_id=patch_id, latest_export_path=latest_export_path, options=options, git_commit_script=git_commit_script)
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
    write_accept_summary(log_dir, "SUCCESS", "accept", patch_id=patch_id, latest_export_path=latest_export_path, options=options, git_commit_script=git_commit_script)
    print_accept_result("SUCCESS", "accept", log_dir, patch_id=patch_id, latest_export_path=latest_export_path, options=options, git_commit_script=git_commit_script)
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


