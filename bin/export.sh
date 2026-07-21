#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
PROJECT_DIR="${PROJECT_ROOT}"
export PROJECT_DIR

# shellcheck source=/dev/null
source "${SCRIPT_DIR}/init.env.sh"

CONFIG_FILE="${APP_EXPORT_CONFIG_FILE:-${PROJECT_ROOT}/export.config.json}"

python3 - "${PROJECT_ROOT}" "${CONFIG_FILE}" "$@" <<'PYEXPORT'
from __future__ import annotations
import fnmatch
import hashlib
import fcntl
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

root = Path(sys.argv[1]).resolve()
config_file = Path(sys.argv[2]).resolve()
args = sys.argv[3:]

USAGE = """Usage:
  ./bin/export.sh <profile> [--zip] [--allow-dirty] [--evidence <json-file>]
  ./bin/export.sh --full-parts <split-profile> [--zip] [--allow-dirty] [--evidence <json-file>]
  ./bin/export.sh --current
  ./bin/export.sh --list

Examples:
  ./bin/export.sh full --zip
  ./bin/export.sh full --zip --evidence patches/logs/validation/run/EXPORT_EVIDENCE.json
  ./bin/export.sh tooling
  ./bin/export.sh --full-parts baseline --zip
  ./bin/export.sh --current

ZIP exports publish exactly two current artifacts: the ZIP and its portable
<zip>.sha256 sidecar. Metadata and split indexes are members of the ZIP; the
unpacked staging directory is removed after verification. Older project export
artifacts are moved to exports/text/Archiv before the verified new set is
published. Baseline exports require a clean Git working tree unless
--allow-dirty is explicitly supplied.

Every metadata file contains an authoritative raw-byte file manifest with size
and SHA-256 for each source file. Text-export separators are presentation only
and must never be used to derive baseline hashes.
"""


def fail(msg: str, code: int = 1) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_digest(value) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return sha256_bytes(encoded)


def load_config() -> dict:
    try:
        data = json.loads(config_file.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"Cannot read export config {config_file}: {exc}", 2)
    if not isinstance(data, dict):
        fail("export.config.json must contain a JSON object", 2)
    return data


def sanitize_project_key(value: str) -> str:
    key = re.sub(r"[^A-Za-z0-9._-]+", "-", value.strip())
    key = key.strip("-._")
    if not key:
        fail(f"Invalid empty export project key derived from {value!r}", 2)
    return key


def configured_project_key(cfg: dict) -> tuple[str, str]:
    candidates = [
        ("APP_EXPORT_PROJECT_KEY", os.environ.get("APP_EXPORT_PROJECT_KEY")),
        ("APP_NAME", os.environ.get("APP_NAME")),
        ("export.config.json:projectKey", cfg.get("projectKey")),
        ("repositoryRoot", root.name),
    ]
    for source, value in candidates:
        if isinstance(value, str) and value.strip():
            return sanitize_project_key(value), source
    return sanitize_project_key(root.name), "repositoryRoot"


def as_list(value) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value]
    if isinstance(value, str):
        return [part for part in value.split() if part]
    fail(f"Invalid list value in export config: {value!r}", 2)


def match_any(rel: str, patterns: list[str]) -> bool:
    candidates = [rel, "/" + rel]
    return any(fnmatch.fnmatchcase(candidate, pattern) for pattern in patterns for candidate in candidates)


def literal_excluded_subtree(rel: str, excludes: list[str], negated: list[str]) -> bool:
    for pattern in excludes:
        normalized = pattern.lstrip("/")
        if not normalized.endswith("/**"):
            continue
        base = normalized[:-3].rstrip("/")
        if not base or any(token in base for token in ("*", "?", "[")):
            continue
        if rel != base and not rel.startswith(base + "/"):
            continue
        if any(item.lstrip("/").startswith(base + "/") for item in negated):
            continue
        return True
    return False


def collect_files(cfg: dict, profile: str) -> list[str]:
    profiles = cfg.get("profiles") or {}
    if profile not in profiles:
        fail(f"Unknown export profile: {profile}", 2)
    spec = profiles[profile] or {}
    includes = as_list(spec.get("include")) or ["**/*"]
    excludes = as_list(cfg.get("globalExclude")) + as_list(spec.get("exclude"))
    negated = [pattern[1:] for pattern in excludes if pattern.startswith("!")]
    excludes = [pattern for pattern in excludes if not pattern.startswith("!")]

    result: list[str] = []
    for current_root, dirnames, filenames in os.walk(root):
        current = Path(current_root)
        rel_dir = current.relative_to(root).as_posix()
        if rel_dir == ".":
            rel_dir = ""
        kept_dirs = []
        for dirname in sorted(dirnames):
            rel = f"{rel_dir}/{dirname}" if rel_dir else dirname
            if not literal_excluded_subtree(rel, excludes, negated):
                kept_dirs.append(dirname)
        dirnames[:] = kept_dirs
        for filename in sorted(filenames):
            path = current / filename
            rel = path.relative_to(root).as_posix()
            included = match_any(rel, includes)
            excluded = match_any(rel, excludes)
            unexcluded = match_any(rel, negated)
            if included and (not excluded or unexcluded):
                result.append(rel)
    return sorted(result)


def source_file_record(rel: str) -> dict:
    path = root / rel
    data = path.read_bytes()
    return {
        "path": rel,
        "sizeBytes": len(data),
        "sha256": sha256_bytes(data),
    }


def read_file_for_export(path: Path, max_size: int) -> tuple[str, str]:
    if max_size > 0 and path.stat().st_size > max_size:
        return (
            f"[file skipped: size {path.stat().st_size} exceeds maxFileSizeBytes {max_size}]\n",
            "size-skipped",
        )
    try:
        text = path.read_text(encoding="utf-8")
        if text and not text.endswith("\n"):
            text += "\n"
        return text, "utf-8-presentation"
    except UnicodeDecodeError:
        return "[binary file skipped]\n", "binary-skipped"


def git_state() -> dict:
    def command(*arguments: str) -> tuple[int, str]:
        result = subprocess.run(
            ["git", *arguments],
            cwd=root,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        return result.returncode, (result.stdout or "").strip()

    head_rc, head = command("rev-parse", "HEAD")
    branch_rc, branch = command("rev-parse", "--abbrev-ref", "HEAD")
    status_rc, status = command("status", "--porcelain=v1", "--untracked-files=all")
    if head_rc != 0:
        return {"available": False}
    return {
        "available": True,
        "head": head,
        "branch": branch if branch_rc == 0 else None,
        "dirty": bool(status) if status_rc == 0 else None,
    }


def require_stable_git_state(allow_dirty: bool) -> dict:
    state = git_state()
    if not state.get("available"):
        fail("A Git repository is required for a baseline export", 3)
    if state.get("dirty") and not allow_dirty:
        fail("Git working tree is dirty; commit or stash changes, or use --allow-dirty explicitly", 3)
    return state


def ensure_git_state_unchanged(expected: dict) -> None:
    actual = git_state()
    if actual != expected:
        fail(
            "Git state changed during export: "
            f"expected={json.dumps(expected, sort_keys=True)} "
            f"actual={json.dumps(actual, sort_keys=True)}",
            3,
        )


def load_evidence(path: Path | None) -> dict | None:
    if path is None:
        return None
    try:
        raw = path.read_bytes()
        value = json.loads(raw.decode("utf-8"))
    except Exception as exc:
        fail(f"Cannot read closure evidence JSON {path}: {exc}", 2)
    if not isinstance(value, dict):
        fail("Closure evidence JSON must contain an object", 2)
    return value


def write_closure_evidence(out_dir: Path, generated: str, source_evidence: dict | None) -> str | None:
    if source_evidence is None:
        return None
    filename = "closure-evidence.json"
    payload = {
        "schemaVersion": "springmaster.export-closure-evidence.v1",
        "exportStatus": "COMPLETE",
        "generatedAt": generated,
        "sourceEvidenceSha256": canonical_digest(source_evidence),
        "sourceEvidence": source_evidence,
    }
    (out_dir / filename).write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return filename


def write_profile_export(
    cfg: dict,
    profile: str,
    out_dir: Path,
    generated: str,
    closure_evidence_file: str | None,
    repository_git_state: dict,
) -> dict:
    project, project_key_source = configured_project_key(cfg)
    files = collect_files(cfg, profile)
    file_manifest = [source_file_record(rel) for rel in files]
    manifest_by_path = {entry["path"]: entry for entry in file_manifest}
    max_size = int(cfg.get("maxFileSizeBytes") or 0)
    txt = out_dir / f"{project}_export_{profile}.txt"
    with txt.open("w", encoding="utf-8") as fh:
        fh.write(f"# {project} Text Export\n\n")
        fh.write(f"GeneratedAt: {generated}\n")
        fh.write(f"RepositoryRoot: {root}\n")
        fh.write(f"Profiles: {profile}\n")
        fh.write(f"Files: {len(files)}\n")
        fh.write("SourceHashPolicy: sha256-raw-repository-bytes\n\n")
        fh.write("## Files\n")
        for rel in files:
            record = manifest_by_path[rel]
            fh.write(f"- {rel} | size={record['sizeBytes']} | sha256={record['sha256']}\n")
        for rel in files:
            record = manifest_by_path[rel]
            content, representation = read_file_for_export(root / rel, max_size)
            fh.write("\n" + "=" * 80 + f"\nFILE: {rel}\n")
            fh.write(f"SOURCE_SIZE_BYTES: {record['sizeBytes']}\n")
            fh.write(f"SOURCE_SHA256: {record['sha256']}\n")
            fh.write(f"TEXT_EXPORT_REPRESENTATION: {representation}\n")
            fh.write("=" * 80 + "\n")
            fh.write(content)

    final_files = collect_files(cfg, profile)
    if final_files != files:
        fail("Source file set changed during export", 3)
    for record in file_manifest:
        current = source_file_record(record["path"])
        if current != record:
            fail(f"Source file changed during export: {record['path']}", 3)

    meta = {
        "exportFormatVersion": 2,
        "exportStatus": "COMPLETE",
        "sourceHashPolicy": "sha256-raw-repository-bytes",
        "textExportBoundaryPolicy": "presentation-only-use-fileManifest-for-source-hashes",
        "profile": profile,
        "generatedAt": generated,
        "repositoryRoot": str(root),
        "configFile": str(config_file),
        "outputFile": txt.name,
        "projectKey": project,
        "projectKeySource": project_key_source,
        "fileCount": len(files),
        "includedFiles": files,
        "fileManifest": file_manifest,
        "fileManifestSha256": canonical_digest(file_manifest),
        "sourceGit": repository_git_state,
        "closureEvidenceFile": closure_evidence_file,
    }
    meta_path = out_dir / f"{project}_export_{profile}.meta.json"
    meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return meta


def stamp_from_iso(value: str) -> str:
    return value.replace(":", "-").replace(".", "-").replace("+00-00", "Z").replace("+00:00", "Z")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def portable_checksum_path(zip_path: Path) -> Path:
    return Path(str(zip_path) + ".sha256")


def write_portable_checksum(zip_path: Path) -> Path:
    checksum_path = portable_checksum_path(zip_path)
    checksum_path.write_text(
        f"{sha256_file(zip_path)}  {zip_path.name}\n",
        encoding="utf-8",
    )
    return checksum_path


def verify_portable_checksum(zip_path: Path, checksum_path: Path | None = None) -> str:
    checksum_path = checksum_path or portable_checksum_path(zip_path)
    try:
        raw = checksum_path.read_text(encoding="utf-8")
    except Exception as exc:
        fail(f"Cannot read checksum file {checksum_path}: {exc}", 3)
    match = re.fullmatch(r"([0-9a-f]{64})  ([^/\\\r\n]+)\n?", raw)
    if not match:
        fail(f"Invalid portable checksum format: {checksum_path}", 3)
    expected, filename = match.groups()
    if filename != zip_path.name:
        fail(
            f"Checksum filename mismatch: expected {zip_path.name!r}, found {filename!r}",
            3,
        )
    actual = sha256_file(zip_path)
    if actual != expected:
        fail(
            f"ZIP checksum mismatch for {zip_path}: expected {expected}, actual {actual}",
            3,
        )
    return actual


def verify_zip_structure(zip_path: Path) -> None:
    try:
        with zipfile.ZipFile(zip_path, "r") as archive:
            bad_member = archive.testzip()
            if bad_member:
                fail(f"ZIP CRC failure in {bad_member}", 3)
            names = archive.namelist()
            if len(names) != len(set(names)):
                fail(f"Duplicate ZIP members are forbidden: {zip_path}", 3)
            if not any(name.endswith(".meta.json") for name in names):
                fail(f"ZIP contains no metadata member: {zip_path}", 3)
    except zipfile.BadZipFile as exc:
        fail(f"Invalid ZIP {zip_path}: {exc}", 3)


def zip_directory(directory: Path, zip_path: Path) -> Path:
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(directory.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(directory.parent).as_posix())
    verify_zip_structure(zip_path)
    checksum_path = write_portable_checksum(zip_path)
    verify_portable_checksum(zip_path, checksum_path)
    return zip_path


def output_base(cfg: dict) -> Path:
    configured = root / (cfg.get("outputDirectory") or "exports/text")
    resolved = configured.resolve()
    if resolved == root or root not in resolved.parents:
        fail(f"Export outputDirectory must stay below the repository root: {configured}", 2)
    return resolved


def current_export_entries(out_root: Path, project: str) -> list[Path]:
    prefix = f"{project}_export_"
    if not out_root.exists():
        return []
    return sorted(
        path
        for path in out_root.iterdir()
        if path.name != "Archiv" and not path.name.startswith(".") and path.name.startswith(prefix)
    )


def archive_existing_exports(out_root: Path, project: str) -> list[tuple[Path, Path]]:
    existing = current_export_entries(out_root, project)
    if not existing:
        return []
    archive_root = out_root / "Archiv"
    archive_root.mkdir(parents=True, exist_ok=True)
    planned = [(source, archive_root / source.name) for source in existing]
    for _source, target in planned:
        if target.exists():
            fail(f"Cannot archive export because target already exists: {target}", 3)
    moved: list[tuple[Path, Path]] = []
    try:
        for source, target in planned:
            os.replace(source, target)
            moved.append((source, target))
        return moved
    except BaseException:
        rollback_archive_moves(moved)
        raise


def rollback_archive_moves(moves: list[tuple[Path, Path]]) -> None:
    for source, target in reversed(moves):
        if target.exists() and not source.exists():
            os.replace(target, source)


def publish_staged_entries(out_root: Path, project: str, entries: list[Path]) -> list[Path]:
    if not entries:
        fail("No staged export artifacts to publish", 3)
    out_root.mkdir(parents=True, exist_ok=True)
    archive_moves: list[tuple[Path, Path]] = []
    published: list[Path] = []
    try:
        archive_moves = archive_existing_exports(out_root, project)
        for source in entries:
            target = out_root / source.name
            if target.exists():
                fail(f"Current export target already exists: {target}", 3)
            os.replace(source, target)
            published.append(target)
        return published
    except BaseException:
        for target in reversed(published):
            if target.is_dir():
                shutil.rmtree(target, ignore_errors=True)
            else:
                target.unlink(missing_ok=True)
        rollback_archive_moves(archive_moves)
        raise


@contextmanager
def export_lock(out_root: Path):
    lock_root = out_root.parent / "runtime"
    lock_root.mkdir(parents=True, exist_ok=True)
    lock_path = lock_root / "export.lock"
    with lock_path.open("a+", encoding="utf-8") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def list_current(cfg: dict) -> None:
    project, _project_key_source = configured_project_key(cfg)
    out_root = output_base(cfg)
    entries = current_export_entries(out_root, project)
    primary = [entry for entry in entries if entry.is_dir() or entry.suffix == ".zip"]
    if not primary:
        fail(f"No current export found below {out_root}", 4)
    if len(primary) != 1:
        fail(
            "Ambiguous current export set; run a new export to normalize the lifecycle: "
            + ", ".join(path.name for path in primary),
            4,
        )
    print(primary[0].relative_to(root))


def write_single(
    cfg: dict,
    profile: str,
    zip_output: bool,
    source_evidence: dict | None,
    repository_git_state: dict,
) -> None:
    generated = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    project, _project_key_source = configured_project_key(cfg)
    out_root = output_base(cfg)
    out_root.mkdir(parents=True, exist_ok=True)
    base_name = f"{project}_export_{profile}_{stamp_from_iso(generated)}"
    staging_root = Path(tempfile.mkdtemp(prefix=f".{project}-export-staging-", dir=out_root))
    out_dir = staging_root / base_name
    out_dir.mkdir(parents=True, exist_ok=False)
    try:
        closure_evidence_file = write_closure_evidence(out_dir, generated, source_evidence)
        write_profile_export(cfg, profile, out_dir, generated, closure_evidence_file, repository_git_state)
        ensure_git_state_unchanged(repository_git_state)
        if zip_output:
            staged_zip = zip_directory(out_dir, staging_root / f"{base_name}.zip")
            shutil.rmtree(out_dir)
            staged_checksum = portable_checksum_path(staged_zip)
            published = publish_staged_entries(out_root, project, [staged_zip, staged_checksum])
            print(published[0].relative_to(root))
        else:
            published = publish_staged_entries(out_root, project, [out_dir])
            print((published[0] / f"{project}_export_{profile}.txt").relative_to(root))
    finally:
        shutil.rmtree(staging_root, ignore_errors=True)


def write_parts(
    cfg: dict,
    group: str,
    zip_output: bool,
    source_evidence: dict | None,
    repository_git_state: dict,
) -> None:
    split_profiles = cfg.get("splitProfiles") or {}
    if group not in split_profiles:
        fail(f"Unknown split profile: {group}", 2)
    profiles = as_list(split_profiles[group])
    generated = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    project, project_key_source = configured_project_key(cfg)
    out_root = output_base(cfg)
    out_root.mkdir(parents=True, exist_ok=True)
    base_name = f"{project}_export_full_parts_{group}_{stamp_from_iso(generated)}"
    staging_root = Path(tempfile.mkdtemp(prefix=f".{project}-export-staging-", dir=out_root))
    out_dir = staging_root / base_name
    out_dir.mkdir(parents=True, exist_ok=False)
    try:
        closure_evidence_file = write_closure_evidence(out_dir, generated, source_evidence)
        metas = []
        for profile in profiles:
            metas.append(
                write_profile_export(
                    cfg,
                    profile,
                    out_dir,
                    generated,
                    closure_evidence_file,
                    repository_git_state,
                )
            )

        index = {
            "exportFormatVersion": 2,
            "exportStatus": "COMPLETE",
            "projectKey": project,
            "projectKeySource": project_key_source,
            "generatedAt": generated,
            "repositoryRoot": str(root),
            "splitProfile": group,
            "profiles": profiles,
            "parts": metas,
            "sourceGit": repository_git_state,
            "closureEvidenceFile": closure_evidence_file,
        }
        (out_dir / "export.index.json").write_text(
            json.dumps(index, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        ensure_git_state_unchanged(repository_git_state)
        if zip_output:
            staged_zip = zip_directory(out_dir, staging_root / f"{base_name}.zip")
            shutil.rmtree(out_dir)
            staged_checksum = portable_checksum_path(staged_zip)
            published = publish_staged_entries(out_root, project, [staged_zip, staged_checksum])
            print(published[0].relative_to(root))
        else:
            published = publish_staged_entries(out_root, project, [out_dir])
            print((published[0] / "export.index.json").relative_to(root))
    finally:
        shutil.rmtree(staging_root, ignore_errors=True)

def list_profiles(cfg: dict) -> None:
    print("Profiles:")
    for name in sorted((cfg.get("profiles") or {}).keys()):
        print(f"  {name}")
    print("Split profiles:")
    for name in sorted((cfg.get("splitProfiles") or {}).keys()):
        print(f"  {name}")


def parse_cli() -> tuple[list[str], bool, Path | None, bool]:
    zip_output = False
    allow_dirty = False
    evidence_value = os.environ.get("PATCH_EXPORT_EVIDENCE_FILE")
    filtered: list[str] = []
    i = 0
    while i < len(args):
        arg = args[i]
        if arg == "--zip":
            zip_output = True
            i += 1
        elif arg == "--allow-dirty":
            allow_dirty = True
            i += 1
        elif arg == "--evidence":
            if i + 1 >= len(args):
                fail("--evidence expects a JSON file", 2)
            evidence_value = args[i + 1]
            i += 2
        else:
            filtered.append(arg)
            i += 1
    evidence_path = None
    if evidence_value:
        evidence_path = Path(evidence_value).expanduser()
        if not evidence_path.is_absolute():
            evidence_path = root / evidence_path
        evidence_path = evidence_path.resolve()
        if not evidence_path.is_file():
            fail(f"Closure evidence file not found: {evidence_path}", 2)
    return filtered, zip_output, evidence_path, allow_dirty


def main() -> None:
    cfg = load_config()
    filtered, zip_output, evidence_path, allow_dirty = parse_cli()
    if not filtered or filtered[0] in {"help", "--help", "-h"}:
        print(USAGE)
        return
    if filtered[0] == "--list":
        if len(filtered) != 1:
            fail("--list does not accept additional arguments", 2)
        list_profiles(cfg)
        return
    if filtered[0] == "--current":
        if len(filtered) != 1 or zip_output or evidence_path is not None or allow_dirty:
            fail("--current does not accept export options", 2)
        list_current(cfg)
        return

    source_evidence = load_evidence(evidence_path)
    out_root = output_base(cfg)
    with export_lock(out_root):
        repository_git_state = require_stable_git_state(allow_dirty)
        if filtered[0] in {"--full-parts", "--parts"}:
            if len(filtered) != 2:
                fail("--full-parts expects exactly one split profile name", 2)
            write_parts(
                cfg,
                filtered[1],
                zip_output,
                source_evidence,
                repository_git_state,
            )
            return

        if len(filtered) != 1:
            fail("Expected exactly one profile name", 2)
        write_single(
            cfg,
            filtered[0],
            zip_output,
            source_evidence,
            repository_git_state,
        )


if __name__ == "__main__":
    main()
PYEXPORT
