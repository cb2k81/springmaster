#!/usr/bin/env python3
"""Read-only Project Directory Contract gate.

The gate is report-only by default. It validates the selected project profile,
classifies exact transition-baseline findings separately from new findings and
never changes repository content.
"""
from __future__ import annotations

import argparse
import datetime as dt
import fnmatch
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Iterable

CONTRACT_SCHEMA = "springmaster.project-directory-contract.v1"
BASELINE_SCHEMA = "springmaster.directory-transition-baseline.v1"
REPORT_SCHEMA = "springmaster.project-directory-gate-report.v1"


class GateToolError(RuntimeError):
    def __init__(self, code: str, message: str, path: str | None = None):
        super().__init__(message)
        self.code = code
        self.path = path


def read_json(path: Path, schema: str) -> dict[str, Any]:
    if not path.is_file():
        raise GateToolError("CONTRACT_MISSING", f"Required JSON file is missing: {path}", path.as_posix())
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise GateToolError("CONTRACT_INVALID_JSON", f"Cannot parse JSON file {path}: {exc}", path.as_posix()) from exc
    if not isinstance(value, dict):
        raise GateToolError("CONTRACT_INVALID_SHAPE", f"JSON file must contain an object: {path}", path.as_posix())
    if value.get("schemaVersion") != schema:
        raise GateToolError(
            "CONTRACT_SCHEMA_UNSUPPORTED",
            f"Unsupported schema in {path}: expected {schema!r}, got {value.get('schemaVersion')!r}",
            path.as_posix(),
        )
    return value


def canonical_entries_hash(entries: list[dict[str, Any]]) -> str:
    raw = json.dumps(entries, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def matches(path: str, patterns: Iterable[str]) -> bool:
    return any(fnmatch.fnmatchcase(path, pattern) for pattern in patterns)


def suffix_for(path: Path) -> str:
    if path.name.startswith(".") and path.name.count(".") == 1:
        return path.name
    return path.suffix


def finding(code: str, rule_id: str, path: str, message: str, **details: Any) -> dict[str, Any]:
    item: dict[str, Any] = {
        "code": code,
        "ruleId": rule_id,
        "path": path,
        "message": message,
    }
    if details:
        item["details"] = details
    return item


def resolve_profile(contract: dict[str, Any], profile_id: str) -> dict[str, Any]:
    profiles = contract.get("profiles")
    if not isinstance(profiles, dict) or profile_id not in profiles:
        raise GateToolError("PROFILE_UNKNOWN", f"Unknown project profile: {profile_id}")
    raw = profiles[profile_id]
    if not isinstance(raw, dict):
        raise GateToolError("CONTRACT_INVALID_SHAPE", f"Profile must be an object: {profile_id}")
    if raw.get("selectable") is False or raw.get("kind") == "embedded-source":
        raise GateToolError("PROFILE_NOT_SELECTABLE", f"Profile is embedded and cannot be checked as a repository: {profile_id}")
    parent_id = raw.get("extends")
    if parent_id is None:
        return dict(raw)
    if not isinstance(parent_id, str) or parent_id == profile_id:
        raise GateToolError("CONTRACT_INVALID_SHAPE", f"Invalid profile inheritance for {profile_id}")
    parent = resolve_profile(contract, parent_id)
    merged = dict(parent)
    merged.update(raw)
    for key in (
        "requiredRootFiles",
        "allowedRootFiles",
        "requiredRootDirectories",
        "allowedRootDirectories",
        "allowedGeneratedRootDirectories",
    ):
        if key in parent or key in raw:
            merged[key] = sorted(set(parent.get(key, [])) | set(raw.get(key, [])))
    return merged


def list_filesystem_paths(root: Path) -> tuple[list[str], dict[str, os.stat_result]]:
    """List all repository paths when no Git source inventory is available."""
    paths: list[str] = []
    stats: dict[str, os.stat_result] = {}
    ignored_roots = {".git"}
    for current, dirs, files in os.walk(root, topdown=True, followlinks=False):
        current_path = Path(current)
        rel_current = current_path.relative_to(root)
        filtered_dirs: list[str] = []
        for name in sorted(dirs):
            if rel_current == Path(".") and name in ignored_roots:
                continue
            candidate = current_path / name
            rel = candidate.relative_to(root).as_posix()
            try:
                stat_value = candidate.lstat()
            except OSError as exc:
                raise GateToolError("PATH_STAT_ERROR", f"Cannot inspect {rel}: {exc}", rel) from exc
            paths.append(rel)
            stats[rel] = stat_value
            if not candidate.is_symlink():
                filtered_dirs.append(name)
        dirs[:] = filtered_dirs
        for name in sorted(files):
            candidate = current_path / name
            rel = candidate.relative_to(root).as_posix()
            try:
                stat_value = candidate.lstat()
            except OSError as exc:
                raise GateToolError("PATH_STAT_ERROR", f"Cannot inspect {rel}: {exc}", rel) from exc
            paths.append(rel)
            stats[rel] = stat_value
    return sorted(set(paths)), stats


def git_path_set(root: Path, arguments: list[str], error_code: str) -> set[str]:
    completed = subprocess.run(
        ["git", "-C", str(root), *arguments, "-z"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        message = completed.stderr.decode("utf-8", errors="replace").strip()
        raise GateToolError(error_code, message or f"git {' '.join(arguments)} failed")
    return {item.decode("utf-8") for item in completed.stdout.split(b"\0") if item}


def repository_inventory(root: Path, require_git_tracking: bool) -> dict[str, Any]:
    """Build the source inventory used for governance findings.

    In a Git worktree, tracked paths and untracked, non-ignored paths are source
    candidates. Ignored local/build/runtime paths remain visible as bounded
    inventory metadata but cannot become repository-structure findings.
    """
    probe = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "--show-toplevel"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    git_root = Path(probe.stdout.strip()).resolve() if probe.returncode == 0 and probe.stdout.strip() else None
    if probe.returncode != 0 or git_root != root.resolve():
        if require_git_tracking:
            message = probe.stderr.strip() or "Directory is not the root of a Git worktree"
            raise GateToolError("GIT_TRACKING_UNAVAILABLE", message)
        paths, stats = list_filesystem_paths(root)
        return {
            "mode": "filesystem",
            "paths": paths,
            "stats": stats,
            "tracked": set(),
            "untracked": set(paths),
            "ignoredCount": 0,
            "ignoredSamples": [],
        }

    tracked = git_path_set(root, ["ls-files"], "GIT_TRACKING_UNAVAILABLE")
    untracked = git_path_set(
        root,
        ["ls-files", "--others", "--exclude-standard"],
        "GIT_UNTRACKED_PATHS_UNAVAILABLE",
    )
    ignored = git_path_set(
        root,
        ["ls-files", "--others", "--ignored", "--exclude-standard"],
        "GIT_IGNORED_PATHS_UNAVAILABLE",
    )

    relevant_leaf_paths = tracked | untracked
    relevant_paths: set[str] = set()
    stats: dict[str, os.stat_result] = {}
    for rel in sorted(relevant_leaf_paths):
        candidate = root / rel
        if not os.path.lexists(candidate):
            continue
        current = Path(rel)
        while current != Path(".") and current.as_posix() not in {"", "."}:
            current_rel = current.as_posix()
            relevant_paths.add(current_rel)
            current = current.parent
    for rel in sorted(relevant_paths):
        candidate = root / rel
        try:
            stats[rel] = candidate.lstat()
        except OSError as exc:
            raise GateToolError("PATH_STAT_ERROR", f"Cannot inspect {rel}: {exc}", rel) from exc

    return {
        "mode": "git-source",
        "paths": sorted(relevant_paths),
        "stats": stats,
        "tracked": tracked,
        "untracked": untracked,
        "ignoredCount": len(ignored),
        "ignoredSamples": sorted(ignored)[:50],
    }


def git_changed_paths(root: Path) -> list[str]:
    commands = [
        ["git", "-C", str(root), "diff", "--name-only", "--diff-filter=ACDMRTUXB", "HEAD"],
        ["git", "-C", str(root), "diff", "--cached", "--name-only", "--diff-filter=ACDMRTUXB", "HEAD"],
        ["git", "-C", str(root), "ls-files", "--others", "--exclude-standard"],
    ]
    result: set[str] = set()
    for command in commands:
        completed = subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
        if completed.returncode != 0:
            raise GateToolError("GIT_CHANGED_PATHS_UNAVAILABLE", completed.stderr.strip() or "Cannot determine changed paths")
        result.update(line.strip() for line in completed.stdout.splitlines() if line.strip())
    return sorted(result)


def area_for(path: str, profile_id: str, areas: list[dict[str, Any]]) -> dict[str, Any] | None:
    for area in areas:
        profiles = area.get("profiles", [])
        patterns = area.get("patterns", [])
        if profile_id in profiles and isinstance(patterns, list) and matches(path, patterns):
            return area
    return None


def directory_has_registered_descendant(path: str, profile_id: str, areas: list[dict[str, Any]]) -> bool:
    prefix = path.rstrip("/") + "/"
    for area in areas:
        if profile_id not in area.get("profiles", []):
            continue
        for pattern in area.get("patterns", []):
            literal_prefix = pattern.split("*", 1)[0]
            if literal_prefix.startswith(prefix) or prefix.startswith(literal_prefix):
                return True
    return False


def allowed_duplicate(left: str, right: str, policy: dict[str, Any]) -> bool:
    pair = {left, right}
    for item in policy.get("allowedPairs", []):
        if not isinstance(item, dict):
            continue
        if pair == {item.get("left"), item.get("right")}:
            return True
    return False


def validate_deviations(path: Path, contract: dict[str, Any], today: dt.date) -> list[dict[str, Any]]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise GateToolError("DEVIATION_INPUT_INVALID_JSON", f"Cannot parse deviations file {path}: {exc}", path.as_posix()) from exc
    expected = contract.get("managedProjectDeviationInput", {})
    if payload.get("schemaVersion") != expected.get("schemaVersion"):
        raise GateToolError("DEVIATION_SCHEMA_UNSUPPORTED", f"Unsupported deviation schema in {path}", path.as_posix())
    entries = payload.get("deviations")
    if not isinstance(entries, list):
        raise GateToolError("DEVIATION_INPUT_INVALID_SHAPE", "deviations must be a list", path.as_posix())
    findings: list[dict[str, Any]] = []
    expiry_field = expected.get("expiryField", "expiresAt")
    path_field = expected.get("pathField", "path")
    status_field = expected.get("statusField", "status")
    active_statuses = set(expected.get("activeStatuses", []))
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            raise GateToolError("DEVIATION_INPUT_INVALID_SHAPE", f"Deviation #{index} must be an object", path.as_posix())
        status = entry.get(status_field)
        expires = entry.get(expiry_field)
        subject = entry.get(path_field, f"deviation[{index}]")
        if status in active_statuses and isinstance(expires, str):
            try:
                expires_at = dt.date.fromisoformat(expires)
            except ValueError as exc:
                raise GateToolError("DEVIATION_DATE_INVALID", f"Invalid deviation expiry {expires!r}", str(subject)) from exc
            if expires_at < today:
                findings.append(finding(
                    "DEVIATION_EXPIRED",
                    "PDIR-DEV-001",
                    str(subject),
                    "An active directory deviation has expired.",
                    expiresAt=expires,
                    status=status,
                ))
    return findings


def run_gate(
    root: Path,
    contract_path: Path,
    baseline_path_override: Path | None,
    profile_id: str,
    requested_mode: str,
    changed_paths_arg: list[str],
    deviations_path: Path | None,
) -> dict[str, Any]:
    contract = read_json(contract_path, CONTRACT_SCHEMA)
    profile = resolve_profile(contract, profile_id)
    areas = contract.get("areas")
    if not isinstance(areas, list) or not all(isinstance(item, dict) for item in areas):
        raise GateToolError("CONTRACT_INVALID_SHAPE", "areas must be a list of objects", contract_path.as_posix())

    baseline_config = contract.get("transitionBaseline")
    if not isinstance(baseline_config, dict):
        raise GateToolError("CONTRACT_INVALID_SHAPE", "transitionBaseline must be an object", contract_path.as_posix())
    baseline_path = baseline_path_override or root / str(baseline_config.get("path", ""))
    baseline = read_json(baseline_path, BASELINE_SCHEMA)
    entries = baseline.get("entries")
    if not isinstance(entries, list) or not all(isinstance(item, dict) for item in entries):
        raise GateToolError("BASELINE_INVALID_SHAPE", "baseline entries must be a list of objects", baseline_path.as_posix())
    if baseline.get("entryCount") != len(entries):
        raise GateToolError("BASELINE_COUNT_MISMATCH", "baseline entryCount does not match entries", baseline_path.as_posix())
    digest = canonical_entries_hash(entries)
    if baseline.get("entrySetSha256") != digest or baseline_config.get("entrySetSha256") != digest:
        raise GateToolError("BASELINE_DIGEST_MISMATCH", "Directory Transition Baseline digest mismatch", baseline_path.as_posix())
    baseline_map: dict[str, set[str]] = {}
    for entry in entries:
        path = entry.get("path")
        codes = entry.get("findingCodes")
        if not isinstance(path, str) or not isinstance(codes, list) or not all(isinstance(code, str) for code in codes):
            raise GateToolError("BASELINE_INVALID_SHAPE", "Each baseline entry needs path and findingCodes", baseline_path.as_posix())
        if path in baseline_map:
            raise GateToolError("BASELINE_DUPLICATE_PATH", f"Duplicate baseline path: {path}", path)
        baseline_map[path] = set(codes)

    inventory = repository_inventory(root, bool(profile.get("requireGitTracking")))
    all_paths = inventory["paths"]
    stat_map = inventory["stats"]
    tracked = inventory["tracked"]

    scan_mode = "all" if requested_mode in {"all", "report"} else "changed"
    changed_paths = sorted(set(changed_paths_arg))
    if scan_mode == "changed" and not changed_paths:
        changed_paths = git_changed_paths(root)
    contract_rel = contract_path.relative_to(root).as_posix() if contract_path.is_relative_to(root) else contract_path.as_posix()
    baseline_rel = baseline_path.relative_to(root).as_posix() if baseline_path.is_relative_to(root) else baseline_path.as_posix()
    expanded_to_all = scan_mode == "changed" and any(
        path in {contract_rel, baseline_rel} or path.endswith("deviations.json") for path in changed_paths
    )
    effective_scan_mode = "all" if expanded_to_all else scan_mode
    selected = set(all_paths if effective_scan_mode == "all" else changed_paths)

    raw_findings: list[dict[str, Any]] = []
    root_names = {path.split("/", 1)[0] for path in all_paths}
    internal = set(contract.get("internalIgnoredRootNames", []))
    allowed_root_files = set(profile.get("allowedRootFiles", []))
    allowed_root_dirs = set(profile.get("allowedRootDirectories", []))
    allowed_generated_dirs = set(profile.get("allowedGeneratedRootDirectories", []))
    required_root_files = set(profile.get("requiredRootFiles", []))
    required_root_dirs = set(profile.get("requiredRootDirectories", []))

    if effective_scan_mode == "all":
        required_files_to_check = required_root_files
        required_dirs_to_check = required_root_dirs
    else:
        changed_roots = {path.split("/", 1)[0] for path in changed_paths}
        required_files_to_check = required_root_files.intersection(changed_roots)
        required_dirs_to_check = required_root_dirs.intersection(changed_roots)
    for name in sorted(required_files_to_check):
        if not (root / name).is_file():
            raw_findings.append(finding("REQUIRED_ROOT_FILE_MISSING", "PDIR-ROOT-001", name, "Required root file is missing."))
    for name in sorted(required_dirs_to_check):
        if not (root / name).is_dir():
            raw_findings.append(finding("REQUIRED_ROOT_DIRECTORY_MISSING", "PDIR-ROOT-001", name, "Required root directory is missing."))

    for name in sorted(root_names - internal):
        target = root / name
        if target.is_symlink():
            continue
        if target.is_file() and name not in allowed_root_files:
            if effective_scan_mode == "all" or name in selected:
                raw_findings.append(finding("ROOT_PATH_UNREGISTERED", "PDIR-ROOT-002", name, "Root file is not registered for the selected profile."))
        elif target.is_dir() and name not in allowed_root_dirs and name not in allowed_generated_dirs:
            if effective_scan_mode == "all" or name in selected or any(p.startswith(name + "/") for p in selected):
                raw_findings.append(finding("ROOT_PATH_UNREGISTERED", "PDIR-ROOT-002", name, "Root directory is not registered for the selected profile."))

    hygiene = contract.get("globalHygiene", {})
    forbidden_exact = set(hygiene.get("forbiddenExactNames", []))
    forbidden_suffixes = tuple(hygiene.get("forbiddenSuffixes", []))
    try:
        forbidden_patterns = [re.compile(value) for value in hygiene.get("forbiddenNamePatterns", [])]
    except re.error as exc:
        raise GateToolError("CONTRACT_REGEX_INVALID", f"Invalid hygiene regex: {exc}", contract_path.as_posix()) from exc

    technical = contract.get("technicalDocumentation", {})
    technical_root = str(technical.get("root", "PROJECT_DOCS"))
    human_suffixes = set(technical.get("humanSuffixes", [".md"]))
    allowed_technical_area_ids = set(technical.get("allowedTechnicalAreaIds", []))

    for rel in all_paths:
        if effective_scan_mode == "changed" and rel not in selected and not any(item.startswith(rel + "/") for item in selected):
            continue
        path = root / rel
        stat_value = stat_map[rel]
        name = path.name
        if "/" not in rel and rel in allowed_generated_dirs:
            continue
        area = area_for(rel, profile_id, areas) if "/" in rel else None
        if area is not None and area.get("sourceKind") == "generated":
            if path.is_file() and area.get("commitPolicy") == "forbidden" and rel in tracked:
                raw_findings.append(finding("NONCOMMITTABLE_PATH_TRACKED", "PDIR-GIT-001", rel, "A generated, runtime or temporary path is tracked by Git.", areaId=area.get("id")))
            continue
        if path.is_symlink():
            target = os.readlink(path)
            broken = not path.exists()
            resolved = (path.parent / target).resolve(strict=False)
            external = not resolved.is_relative_to(root)
            raw_findings.append(finding(
                "SYMLINK_FORBIDDEN",
                "PDIR-LINK-001",
                rel,
                "Symlinks are not allowed by the selected profile.",
                target=target,
                broken=broken,
                external=external,
            ))
            continue
        if stat_value and (name in forbidden_exact or name.endswith(forbidden_suffixes) or any(rx.fullmatch(name) for rx in forbidden_patterns)):
            raw_findings.append(finding("PATH_HYGIENE_VIOLATION", "PDIR-NAME-001", rel, "Path name matches a forbidden backup, copy, editor or temporary artifact pattern."))
        if "/" not in rel:
            continue
        if area is None:
            if path.is_dir() and directory_has_registered_descendant(rel, profile_id, areas):
                continue
            raw_findings.append(finding("PATH_UNREGISTERED", "PDIR-AREA-001", rel, "Path is not covered by a registered directory area."))
            continue
        if path.is_file():
            allowed_suffixes = area.get("allowedSuffixes", [])
            suffix = suffix_for(path)
            type_allowed = "*" in allowed_suffixes or suffix in set(allowed_suffixes)
            extensionless_executable = suffix == "" and area.get("allowExtensionlessExecutable") is True
            executable = bool(stat_value.st_mode & 0o111)
            if extensionless_executable and executable:
                type_allowed = True
            if not type_allowed:
                raw_findings.append(finding(
                    "FILE_TYPE_NOT_ALLOWED",
                    "PDIR-TYPE-001",
                    rel,
                    "File type is not allowed in the registered area.",
                    areaId=area.get("id"),
                    suffix=suffix,
                    allowed=allowed_suffixes,
                    requiresExecutable=extensionless_executable,
                    executable=executable,
                ))
            if rel.startswith(technical_root + "/") and suffix not in human_suffixes and area.get("id") not in allowed_technical_area_ids:
                raw_findings.append(finding(
                    "TECHNICAL_FILE_UNDER_DOCUMENTATION",
                    "PDIR-DOC-001",
                    rel,
                    "Technical file is placed under a documentation area without an explicit technical area registration.",
                    areaId=area.get("id"),
                ))
            policy = area.get("newPathPolicy")
            if policy == "baseline-only":
                code = "LEGACY_PATH_PRESENT" if area.get("pathClass") in {"legacy-accepted", "migration-candidate"} else "FORBIDDEN_NEW_PATH"
                raw_findings.append(finding(code, "PDIR-TRANS-001", rel, "Path belongs to a baseline-only transition area.", areaId=area.get("id")))
            if area.get("commitPolicy") == "forbidden" and rel in tracked:
                raw_findings.append(finding("NONCOMMITTABLE_PATH_TRACKED", "PDIR-GIT-001", rel, "A generated, runtime or temporary path is tracked by Git.", areaId=area.get("id")))

    # Case collisions are a repository-wide relation; changed mode reports only affected relations.
    by_case: dict[str, list[str]] = {}
    for rel in all_paths:
        relation_area = area_for(rel, profile_id, areas) if "/" in rel else None
        if relation_area is not None and relation_area.get("sourceKind") == "generated":
            continue
        by_case.setdefault(rel.casefold(), []).append(rel)
    for group in sorted(by_case.values(), key=lambda values: values[0]):
        if len(group) > 1 and (effective_scan_mode == "all" or selected.intersection(group)):
            raw_findings.append(finding("CASE_COLLISION", "PDIR-CASE-001", group[0], "Paths differ only by letter case.", paths=sorted(group)))

    duplicate_policy = contract.get("duplicatePolicy", {})
    if effective_scan_mode in set(duplicate_policy.get("enabledModes", [])):
        excluded = duplicate_policy.get("excludedPatterns", [])
        max_size = int(duplicate_policy.get("maxFileSizeBytes", 0) or 0)
        hashes: dict[str, list[str]] = {}
        for rel in all_paths:
            path = root / rel
            if path.is_symlink() or not path.is_file() or matches(rel, excluded):
                continue
            try:
                size = path.stat().st_size
                if size == 0 or (max_size and size > max_size):
                    continue
                digest_value = hashlib.sha256(path.read_bytes()).hexdigest()
            except OSError as exc:
                raise GateToolError("FILE_READ_ERROR", f"Cannot hash {rel}: {exc}", rel) from exc
            hashes.setdefault(digest_value, []).append(rel)
        for digest_value, group in sorted(hashes.items()):
            if len(group) < 2 or (effective_scan_mode == "changed" and not selected.intersection(group)):
                continue
            unapproved: list[list[str]] = []
            for index, left in enumerate(sorted(group)):
                for right in sorted(group)[index + 1:]:
                    if not allowed_duplicate(left, right, duplicate_policy):
                        unapproved.append([left, right])
            if unapproved:
                raw_findings.append(finding(
                    "UNDECLARED_BYTE_DUPLICATE",
                    "PDIR-DUP-001",
                    unapproved[0][0],
                    "Byte-identical files exist without a declared derivation or duplicate allowance.",
                    sha256=digest_value,
                    pairs=unapproved,
                ))

    if deviations_path is not None:
        raw_findings.extend(validate_deviations(deviations_path, contract, dt.date.today()))

    transition_findings: list[dict[str, Any]] = []
    new_findings: list[dict[str, Any]] = []
    for item in raw_findings:
        path = item["path"]
        if item["code"] in baseline_map.get(path, set()):
            transitioned = dict(item)
            transitioned["baselineStatus"] = "existing"
            transition_findings.append(transitioned)
        else:
            current = dict(item)
            current["baselineStatus"] = "new"
            new_findings.append(current)

    status = "PASS" if not new_findings else "FINDINGS"
    return {
        "schemaVersion": REPORT_SCHEMA,
        "status": status,
        "result": "pass" if status == "PASS" else "findings",
        "enforcement": "report-only",
        "profile": profile_id,
        "requestedMode": requested_mode,
        "scanMode": effective_scan_mode,
        "expandedToAll": expanded_to_all,
        "contract": {
            "path": contract_rel,
            "schemaVersion": contract.get("schemaVersion"),
            "contractVersion": contract.get("contractVersion"),
            "status": contract.get("status"),
        },
        "transitionBaseline": {
            "path": baseline_rel,
            "entryCount": len(entries),
            "entrySetSha256": digest,
        },
        "inventory": {
            "mode": inventory["mode"],
            "ignoredPathCount": inventory["ignoredCount"],
            "ignoredSamplePaths": inventory["ignoredSamples"],
        },
        "summary": {
            "repositoryPathCount": len(all_paths),
            "selectedPathCount": len(selected),
            "trackedPathCount": len(tracked),
            "untrackedPathCount": len(inventory["untracked"]),
            "ignoredPathCount": inventory["ignoredCount"],
            "transitionFindingCount": len(transition_findings),
            "newFindingCount": len(new_findings),
            "warningFindingCount": 0,
            "toolErrorCount": 0,
        },
        "changedPaths": changed_paths if scan_mode == "changed" else [],
        "newFindings": sorted(new_findings, key=lambda item: (item["path"], item["code"])),
        "transitionFindings": sorted(transition_findings, key=lambda item: (item["path"], item["code"])),
        "warnings": [],
        "toolErrors": [],
    }


def write_report(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def tool_error_report(profile: str, requested_mode: str, exc: GateToolError) -> dict[str, Any]:
    return {
        "schemaVersion": REPORT_SCHEMA,
        "status": "TOOL_ERROR",
        "result": "tool-error",
        "enforcement": "report-only",
        "profile": profile,
        "requestedMode": requested_mode,
        "scanMode": "unknown",
        "expandedToAll": False,
        "contract": {},
        "transitionBaseline": {},
        "inventory": {
            "mode": "unknown",
            "ignoredPathCount": 0,
            "ignoredSamplePaths": [],
        },
        "summary": {
            "repositoryPathCount": 0,
            "selectedPathCount": 0,
            "trackedPathCount": 0,
            "untrackedPathCount": 0,
            "ignoredPathCount": 0,
            "transitionFindingCount": 0,
            "newFindingCount": 0,
            "warningFindingCount": 0,
            "toolErrorCount": 1,
        },
        "changedPaths": [],
        "newFindings": [],
        "transitionFindings": [],
        "warnings": [],
        "toolErrors": [{"code": exc.code, "path": exc.path, "message": str(exc)}],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a project against the Project Directory Contract.")
    parser.add_argument("--root", help="Repository root; defaults to the parent of bin/")
    parser.add_argument("--contract", default="contracts/governance/project-structure/project-directory-contract.json")
    parser.add_argument("--baseline", help="Override the Directory Transition Baseline path")
    parser.add_argument("--profile", help="Project profile; defaults to the contract defaultProfile")
    parser.add_argument("--mode", choices=["all", "changed", "report"], default="report")
    parser.add_argument("--changed-path", action="append", default=[], help="Explicit changed path; repeatable")
    parser.add_argument("--deviations", help="Optional managed-project deviations JSON")
    parser.add_argument("--out", default="target/project-directory-gate-report.json")
    parser.add_argument("--check", action="store_true", help="Return exit 1 when new findings exist")
    args = parser.parse_args()

    root = Path(args.root).resolve() if args.root else Path(__file__).resolve().parents[1]
    contract_path = Path(args.contract)
    if not contract_path.is_absolute():
        contract_path = root / contract_path
    baseline_path = Path(args.baseline) if args.baseline else None
    if baseline_path is not None and not baseline_path.is_absolute():
        baseline_path = root / baseline_path
    deviations_path = Path(args.deviations) if args.deviations else None
    if deviations_path is not None and not deviations_path.is_absolute():
        deviations_path = root / deviations_path
    out = Path(args.out)
    if not out.is_absolute():
        out = root / out

    profile = args.profile
    if profile is None:
        try:
            preliminary = read_json(contract_path, CONTRACT_SCHEMA)
            profile = str(preliminary.get("defaultProfile", "springmaster-source"))
        except GateToolError as exc:
            report = tool_error_report("unknown", args.mode, exc)
            try:
                write_report(out, report)
            except Exception:
                pass
            print("PROJECT_DIRECTORY_GATE=TOOL_ERROR")
            print(f"REPORT={out}")
            return 2

    try:
        report = run_gate(root, contract_path, baseline_path, profile, args.mode, args.changed_path, deviations_path)
    except GateToolError as exc:
        report = tool_error_report(profile, args.mode, exc)
        try:
            write_report(out, report)
        except Exception:
            pass
        print("PROJECT_DIRECTORY_GATE=TOOL_ERROR")
        print(f"REPORT={out}")
        return 2
    except Exception as exc:  # fail-closed defensive boundary
        wrapped = GateToolError("UNEXPECTED_TOOL_ERROR", str(exc))
        report = tool_error_report(profile, args.mode, wrapped)
        try:
            write_report(out, report)
        except Exception:
            pass
        print("PROJECT_DIRECTORY_GATE=TOOL_ERROR")
        print(f"REPORT={out}")
        return 2

    write_report(out, report)
    print(f"PROJECT_DIRECTORY_GATE={report['status']}")
    print(f"PROFILE={profile}")
    print(f"MODE={report['scanMode']}")
    print(f"TRANSITION_FINDINGS={report['summary']['transitionFindingCount']}")
    print(f"NEW_FINDINGS={report['summary']['newFindingCount']}")
    print(f"REPORT={out}")
    if args.check and report["summary"]["newFindingCount"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
