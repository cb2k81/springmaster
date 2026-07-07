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
import json
import os
import re
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

root = Path(sys.argv[1]).resolve()
config_file = Path(sys.argv[2]).resolve()
args = sys.argv[3:]

USAGE = """Usage:
  ./bin/export.sh <profile> [--zip]
  ./bin/export.sh --full-parts <split-profile> [--zip]
  ./bin/export.sh --list

Examples:
  ./bin/export.sh full --zip
  ./bin/export.sh tooling
  ./bin/export.sh --full-parts baseline --zip
"""

def fail(msg: str, code: int = 1) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)

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
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        included = match_any(rel, includes)
        excluded = match_any(rel, excludes)
        unexcluded = match_any(rel, negated)
        if included and (not excluded or unexcluded):
            result.append(rel)
    return result

def read_file_for_export(path: Path, max_size: int) -> str:
    if max_size > 0 and path.stat().st_size > max_size:
        return f"[file skipped: size {path.stat().st_size} exceeds maxFileSizeBytes {max_size}]\n"
    try:
        return path.read_text(encoding="utf-8") + "\n"
    except UnicodeDecodeError:
        return "[binary file skipped]\n"

def write_profile_export(cfg: dict, profile: str, out_dir: Path, generated: str) -> dict:
    project, project_key_source = configured_project_key(cfg)
    files = collect_files(cfg, profile)
    max_size = int(cfg.get("maxFileSizeBytes") or 0)
    txt = out_dir / f"{project}_export_{profile}.txt"
    with txt.open("w", encoding="utf-8") as fh:
        fh.write(f"# {project} Text Export\n\n")
        fh.write(f"GeneratedAt: {generated}\n")
        fh.write(f"RepositoryRoot: {root}\n")
        fh.write(f"Profiles: {profile}\n")
        fh.write(f"Files: {len(files)}\n\n")
        fh.write("## Files\n")
        for rel in files:
            fh.write(f"- {rel}\n")
        for rel in files:
            fh.write("\n" + "=" * 80 + f"\nFILE: {rel}\n" + "=" * 80 + "\n")
            fh.write(read_file_for_export(root / rel, max_size))

    meta = {
        "profile": profile,
        "generatedAt": generated,
        "repositoryRoot": str(root),
        "configFile": str(config_file),
        "outputFile": txt.name,
        "projectKey": project,
        "projectKeySource": project_key_source,
        "fileCount": len(files),
        "includedFiles": files,
    }
    meta_path = out_dir / f"{project}_export_{profile}.meta.json"
    meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return meta

def stamp_from_iso(value: str) -> str:
    return value.replace(":", "-").replace(".", "-").replace("+00-00", "Z").replace("+00:00", "Z")

def zip_directory(directory: Path) -> Path:
    zip_path = directory.with_suffix(".zip")
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(directory.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(directory.parent).as_posix())
    return zip_path

def output_base(cfg: dict) -> Path:
    return root / (cfg.get("outputDirectory") or "exports/text")

def write_single(cfg: dict, profile: str, zip_output: bool) -> None:
    generated = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    project, _project_key_source = configured_project_key(cfg)
    out_root = output_base(cfg)
    out_root.mkdir(parents=True, exist_ok=True)
    out_dir = out_root / f"{project}_export_{profile}_{stamp_from_iso(generated)}"
    out_dir.mkdir(parents=True, exist_ok=False)
    write_profile_export(cfg, profile, out_dir, generated)
    result = zip_directory(out_dir) if zip_output else out_dir / f"{project}_export_{profile}.txt"
    print(result.relative_to(root))

def write_parts(cfg: dict, group: str, zip_output: bool) -> None:
    split_profiles = cfg.get("splitProfiles") or {}
    if group not in split_profiles:
        fail(f"Unknown split profile: {group}", 2)
    profiles = as_list(split_profiles[group])
    generated = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    project, _project_key_source = configured_project_key(cfg)
    out_root = output_base(cfg)
    out_root.mkdir(parents=True, exist_ok=True)
    out_dir = out_root / f"{project}_export_full_parts_{group}_{stamp_from_iso(generated)}"
    out_dir.mkdir(parents=True, exist_ok=False)

    metas = []
    for profile in profiles:
        metas.append(write_profile_export(cfg, profile, out_dir, generated))

    index = {
        "projectKey": project,
        "projectKeySource": _project_key_source,
        "generatedAt": generated,
        "repositoryRoot": str(root),
        "splitProfile": group,
        "profiles": profiles,
        "parts": metas,
    }
    (out_dir / "export.index.json").write_text(json.dumps(index, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    result = zip_directory(out_dir) if zip_output else out_dir / "export.index.json"
    print(result.relative_to(root))

def list_profiles(cfg: dict) -> None:
    print("Profiles:")
    for name in sorted((cfg.get("profiles") or {}).keys()):
        print(f"  {name}")
    print("Split profiles:")
    for name in sorted((cfg.get("splitProfiles") or {}).keys()):
        print(f"  {name}")

def main() -> None:
    cfg = load_config()
    if not args or args[0] in {"help", "--help", "-h"}:
        print(USAGE)
        return
    if args[0] == "--list":
        list_profiles(cfg)
        return

    zip_output = "--zip" in args
    filtered = [arg for arg in args if arg != "--zip"]

    if filtered[0] in {"--full-parts", "--parts"}:
        if len(filtered) != 2:
            fail("--full-parts expects exactly one split profile name", 2)
        write_parts(cfg, filtered[1], zip_output)
        return

    if len(filtered) != 1:
        fail("Expected exactly one profile name", 2)
    write_single(cfg, filtered[0], zip_output)

if __name__ == "__main__":
    main()
PYEXPORT


