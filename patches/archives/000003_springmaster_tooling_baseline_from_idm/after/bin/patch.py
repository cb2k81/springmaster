#!/usr/bin/env python3
import fnmatch
import hashlib
import json
import re
import shutil
import sys
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path

USAGE = """Verwendung:
  ./bin/patch.sh --help
  ./bin/patch.sh help
  ./bin/patch.sh apply [--dry-run] <patch.zip>
  ./bin/patch.sh rollback [--dry-run] <patch-id|patch-number|latest>
  ./bin/patch.sh list
  ./bin/patch.sh show <patch-id|patch-number|latest>

Pflichtregeln:
  - manifest.json ist verpflichtend.
  - manifest.scope ist verpflichtend.
  - manifest.name ist verpflichtend.
  - logs/CHANGELOG-*.md ist verpflichtend.
  - Erlaubte ZIP-Wurzelpfade: manifest.json, files/**, delete/**, logs/CHANGELOG-*.md.
  - Legacy-Patches werden abgelehnt.
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

def scope_log_dir(scope):
    mapping = {
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
    return mapping.get(scope)

def scope_patterns(scope):
    table = {
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
            "src/main/java/de/cocondo/platform/core/**",
            "src/test/java/de/cocondo/platform/core/**",
            "PROJECT_DOCS/CORE/**",
            "patches/logs/core/**",
        ],
        "demo": [
            "src/main/java/de/cocondo/platform/demo/**",
            "src/test/java/de/cocondo/platform/demo/**",
            "PROJECT_DOCS/DEMO/**",
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
            "PROJECT_DOCS/TARGET_UPDATES/**",
            "PROJECT_DOCS/TOOLING/PLATFORM_UPDATE.md",
            "patches/logs/platform-update/**",
        ],
    }
    return table.get(scope)

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
    for arg in args:
        if arg == "--dry-run":
            dry_run = True
        else:
            rest.append(arg)
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
    for arg in args:
        if arg == "--dry-run":
            dry_run = True
        else:
            rest.append(arg)
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

def main():
    if COMMAND in ("--help", "-h", "help"):
        print(USAGE)
    elif COMMAND == "apply":
        apply_command(ARGS)
    elif COMMAND == "list":
        list_command()
    elif COMMAND == "show":
        show_command(ARGS)
    elif COMMAND == "rollback":
        rollback_command(ARGS)
    else:
        fail(f"Unbekanntes Kommando: {COMMAND}", 1)

if __name__ == "__main__":
    main()



