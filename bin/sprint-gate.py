#!/usr/bin/env python3
"""Read-only report-only Sprint Contract gate."""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any

EXPECTED_SPRINT_SCHEMA = "springmaster.sprint-contract.v1"
EXPECTED_DRIFT_SCHEMA = "springmaster.sprint-drift-contract.v1"
REPORT_SCHEMA = "springmaster.sprint-gate-report.v1"


class GateToolError(RuntimeError):
    def __init__(self, code: str, message: str, path: str | None = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.path = path


def parse_scalar(raw: str) -> Any:
    value = raw.strip()
    lowered = value.lower()
    if lowered == "null":
        return None
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    if value == "[]":
        return []
    if value == "{}":
        return {}
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    return value


def front_matter(path: Path) -> dict[str, Any]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except Exception as exc:
        raise GateToolError("DOCUMENT_READ_ERROR", f"Cannot read Markdown document: {exc}", str(path)) from exc
    if not lines or lines[0] != "---":
        return {}
    result: dict[str, Any] = {}
    current_list: str | None = None
    for line in lines[1:]:
        if line == "---":
            return result
        if line.startswith("  - ") and current_list is not None:
            result[current_list].append(parse_scalar(line[4:]))
            continue
        current_list = None
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            raise GateToolError("FRONT_MATTER_PARSE_ERROR", f"Unsupported front matter line: {line!r}", str(path))
        key, raw = line.split(":", 1)
        key = key.strip()
        if not key:
            raise GateToolError("FRONT_MATTER_PARSE_ERROR", "Empty front matter key", str(path))
        if raw.strip() == "":
            result[key] = []
            current_list = key
        else:
            result[key] = parse_scalar(raw)
    raise GateToolError("FRONT_MATTER_UNTERMINATED", "Front matter is not terminated", str(path))


def read_json_object(path: Path, schema: str) -> dict[str, Any]:
    if not path.is_file():
        raise GateToolError("CONTRACT_MISSING", f"Required contract is missing: {path}", str(path))
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise GateToolError("CONTRACT_PARSE_ERROR", f"Cannot parse contract {path}: {exc}", str(path)) from exc
    if not isinstance(value, dict):
        raise GateToolError("CONTRACT_INVALID_SHAPE", f"Contract must contain an object: {path}", str(path))
    if value.get("schemaVersion") != schema:
        raise GateToolError("CONTRACT_SCHEMA_MISMATCH", f"Expected schema {schema}, got {value.get('schemaVersion')!r}", str(path))
    return value


def valid_iso_date(value: Any) -> bool:
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        return False
    try:
        date.fromisoformat(value)
        return True
    except ValueError:
        return False


def rel(root: Path, path: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return str(path)


def finding(rule_id: str, code: str, path: str, message: str, **details: Any) -> dict[str, Any]:
    item: dict[str, Any] = {"ruleId": rule_id, "code": code, "path": path, "message": message}
    if details:
        item["details"] = details
    return item


def headings(path: Path) -> list[str]:
    result: list[str] = []
    in_fence = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        match = re.match(r"^#{2,6}\s+(.+?)\s*$", line)
        if match:
            result.append(match.group(1).strip())
    return result


def section_lines(path: Path, heading: str) -> list[str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    start: int | None = None
    level = 0
    in_fence = False
    for index, line in enumerate(lines):
        if line.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        match = re.match(r"^(#{2,6})\s+(.+?)\s*$", line)
        if not match:
            continue
        if start is None and match.group(2).strip() == heading:
            start = index + 1
            level = len(match.group(1))
            continue
        if start is not None and len(match.group(1)) <= level:
            return lines[start:index]
    return lines[start:] if start is not None else []


def parse_table(path: Path, heading: str) -> tuple[list[str], list[dict[str, str]]]:
    lines = section_lines(path, heading)
    table_start: int | None = None
    for index, line in enumerate(lines):
        if line.strip().startswith("|"):
            table_start = index
            break
    if table_start is None or table_start + 1 >= len(lines):
        return [], []
    header = [part.strip() for part in lines[table_start].strip().strip("|").split("|")]
    separator = lines[table_start + 1].strip()
    if not separator.startswith("|") or not all(re.fullmatch(r":?-{3,}:?", part.strip()) for part in separator.strip("|").split("|")):
        return [], []
    rows: list[dict[str, str]] = []
    for line in lines[table_start + 2:]:
        if not line.strip().startswith("|"):
            break
        values = [part.strip() for part in line.strip().strip("|").split("|")]
        if len(values) != len(header):
            continue
        rows.append(dict(zip(header, values)))
    return header, rows


def complete_amendments(brief: Path, drift: dict[str, Any]) -> tuple[int, list[str]]:
    text = brief.read_text(encoding="utf-8")
    pattern = re.compile(r"^###\s+(AMEND-[0-9]{3})\s*$", re.MULTILINE)
    matches = list(pattern.finditer(text))
    missing: list[str] = []
    required = drift.get("amendmentRequiredFields", [])
    for idx, match in enumerate(matches):
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        block = text[match.end():end]
        for field in required:
            if not re.search(rf"^-\s+{re.escape(field)}:\s*\S", block, re.MULTILINE):
                missing.append(f"{match.group(1)}:{field}")
    return len(matches), missing


def validate_contract_shape(contract: dict[str, Any], drift: dict[str, Any], root: Path) -> None:
    if contract.get("status") != "report-only" or drift.get("status") != "report-only":
        raise GateToolError("CONTRACT_ENFORCEMENT_INVALID", "Sprint contracts must remain report-only in v1")
    for key in ("active", "archive"):
        if not isinstance(contract.get("roots", {}).get(key), str):
            raise GateToolError("CONTRACT_INVALID_SHAPE", f"roots.{key} must be a string")
    try:
        re.compile(contract.get("sprintIdPattern", ""))
        re.compile(drift.get("amendmentHeadingPattern", ""))
    except re.error as exc:
        raise GateToolError("CONTRACT_PATTERN_INVALID", f"Invalid contract pattern: {exc}") from exc
    for document in contract.get("activeDocuments", []):
        template = document.get("template")
        if not isinstance(template, str) or not (root / template).is_file():
            raise GateToolError("TEMPLATE_MISSING", f"Sprint template is missing: {template}", template)


def validate_document(root: Path, sprint_id: str, path: Path, spec: dict[str, Any], findings: list[dict[str, Any]]) -> dict[str, Any]:
    relative = rel(root, path)
    metadata = front_matter(path)
    expected_suffix = None
    if isinstance(spec.get("file"), str):
        expected_suffix = spec.get("documentIdSuffix")
    required = ["documentId", "documentType", "status", "authority", "temporary", "sprintId"] + list(spec.get("requiredMetadata", []))
    missing = [field for field in required if field not in metadata]
    if missing:
        findings.append(finding("SPR-DOC-001", "SPRINT_METADATA_MISSING", relative, "Required sprint metadata is missing.", missing=missing))
    if metadata.get("sprintId") != sprint_id:
        findings.append(finding("SPR-CONTRACT-001", "SPRINT_ID_MISMATCH", relative, "Document sprintId does not match its directory.", expected=sprint_id, actual=metadata.get("sprintId")))
    if metadata.get("documentType") != spec.get("documentType"):
        findings.append(finding("SPR-DOC-001", "SPRINT_DOCUMENT_TYPE_INVALID", relative, "Document type does not match the Sprint Contract.", expected=spec.get("documentType"), actual=metadata.get("documentType")))
    if metadata.get("authority") != spec.get("authority"):
        findings.append(finding("SPR-DOC-001", "SPRINT_DOCUMENT_AUTHORITY_INVALID", relative, "Document authority does not match the Sprint Contract.", expected=spec.get("authority"), actual=metadata.get("authority")))
    if metadata.get("temporary") is not spec.get("temporary"):
        findings.append(finding("SPR-DOC-001", "SPRINT_DOCUMENT_TEMPORARY_INVALID", relative, "Document temporary flag does not match the Sprint Contract.", expected=spec.get("temporary"), actual=metadata.get("temporary")))
    if metadata.get("status") not in spec.get("allowedStatuses", []):
        findings.append(finding("SPR-DOC-001", "SPRINT_DOCUMENT_STATUS_INVALID", relative, "Document status is not allowed for this Sprint Contract role.", allowed=spec.get("allowedStatuses", []), actual=metadata.get("status")))
    if spec.get("temporary") and not metadata.get("reviewBy"):
        findings.append(finding("SPR-DOC-001", "SPRINT_TEMPORARY_REVIEW_MISSING", relative, "Temporary sprint documents require reviewBy."))
    return metadata


def validate_headings(root: Path, path: Path, required: list[str], findings: list[dict[str, Any]]) -> None:
    current = headings(path)
    missing = [item for item in required if item not in current]
    if missing:
        findings.append(finding("SPR-DOC-001", "SPRINT_REQUIRED_HEADING_MISSING", rel(root, path), "Required sprint document headings are missing.", missing=missing))


def indexed(index_text: str, relative: str) -> bool:
    return f"`{relative}`" in index_text or relative in index_text


def validate_active_sprint(root: Path, sprint_dir: Path, contract: dict[str, Any], drift: dict[str, Any], index_text: str, findings: list[dict[str, Any]]) -> None:
    sprint_id = sprint_dir.name
    sprint_rel = rel(root, sprint_dir)
    if not re.fullmatch(contract["sprintIdPattern"], sprint_id):
        findings.append(finding("SPR-CONTRACT-001", "SPRINT_ID_INVALID", sprint_rel, "Sprint directory name does not match the configured Sprint ID pattern.", pattern=contract["sprintIdPattern"]))
    specs = {item["file"]: dict(item) for item in contract["activeDocuments"]}
    for filename, suffix in contract.get("documentIdSuffixes", {}).items():
        if filename in specs:
            specs[filename]["documentIdSuffix"] = suffix
    metadata_by_file: dict[str, dict[str, Any]] = {}
    for filename, spec in specs.items():
        path = sprint_dir / filename
        if not path.is_file():
            findings.append(finding("SPR-DOC-001", "SPRINT_REQUIRED_DOCUMENT_MISSING", rel(root, path), "Required active sprint document is missing.", file=filename))
            continue
        metadata = validate_document(root, sprint_id, path, spec, findings)
        metadata_by_file[filename] = metadata
        expected_id = sprint_id + contract.get("documentIdSuffixes", {}).get(filename, "")
        if metadata.get("documentId") != expected_id:
            findings.append(finding("SPR-CONTRACT-001", "SPRINT_DOCUMENT_ID_INVALID", rel(root, path), "Sprint documentId must derive from the Sprint ID and role.", expected=expected_id, actual=metadata.get("documentId")))
        validate_headings(root, path, contract.get("requiredHeadings", {}).get(filename, []), findings)
        if not indexed(index_text, rel(root, path)):
            findings.append(finding("SPR-INDEX-001", "SPRINT_DOCUMENT_NOT_INDEXED", rel(root, path), "Sprint document is not discoverable from PROJECT_DOCS/index.md."))

    status_docs: list[Path] = []
    for path in sprint_dir.rglob("*.md"):
        try:
            if front_matter(path).get("documentType") == "sprint-status":
                status_docs.append(path)
        except GateToolError:
            raise
    if len(status_docs) != 1:
        findings.append(finding("SPR-STATUS-001", "SPRINT_STATUS_SOURCE_COUNT_INVALID", sprint_rel, "An active sprint must contain exactly one sprint-status document.", count=len(status_docs), paths=[rel(root, p) for p in status_docs]))

    brief = sprint_dir / "SPRINT_BRIEF.md"
    milestone_ids: list[str] = []
    if brief.is_file():
        brief_headings = headings(brief)
        for pattern in contract.get("forbiddenBriefHeadingPatterns", []):
            rx = re.compile(pattern)
            bad = [heading for heading in brief_headings if rx.search(heading)]
            if bad:
                findings.append(finding("SPR-SEPARATION-001", "SOLUTION_CONTENT_IN_SPRINT_BRIEF", rel(root, brief), "Sprint Brief contains solution-space headings.", headings=bad))
        for heading_name, rule_id, code in (("Definition of Ready", "SPR-DOR-001", "SPRINT_DOR_INCOMPLETE"), ("Definition of Done", "SPR-DOD-001", "SPRINT_DOD_INCOMPLETE")):
            lines = section_lines(brief, heading_name)
            if not any(re.match(r"^\s*- \[[ xX]\]\s+\S", line) for line in lines):
                findings.append(finding(rule_id, code, rel(root, brief), f"{heading_name} must contain at least one checklist criterion."))
        table_contract = contract["milestoneTable"]
        header, rows = parse_table(brief, table_contract["heading"])
        missing_columns = [column for column in table_contract["requiredColumns"] if column not in header]
        if missing_columns or not rows:
            findings.append(finding("SPR-MILESTONE-001", "SPRINT_MILESTONE_TABLE_INVALID", rel(root, brief), "Milestone table is missing required columns or data rows.", missingColumns=missing_columns, rowCount=len(rows)))
        seen: set[str] = set()
        for row in rows:
            milestone_id = row.get("ID", "")
            if not re.fullmatch(table_contract["idPattern"], milestone_id):
                findings.append(finding("SPR-MILESTONE-001", "SPRINT_MILESTONE_ID_INVALID", rel(root, brief), "Milestone ID is invalid.", actual=milestone_id))
            elif milestone_id in seen:
                findings.append(finding("SPR-MILESTONE-001", "SPRINT_MILESTONE_ID_DUPLICATE", rel(root, brief), "Milestone ID is duplicated.", actual=milestone_id))
            else:
                seen.add(milestone_id)
                milestone_ids.append(milestone_id)
            if row.get("Status") not in contract["milestoneStatuses"]:
                findings.append(finding("SPR-MILESTONE-001", "SPRINT_MILESTONE_STATUS_INVALID", rel(root, brief), "Milestone status is invalid.", allowed=contract["milestoneStatuses"], actual=row.get("Status")))
        meta = metadata_by_file.get("SPRINT_BRIEF.md", {})
        start, target = meta.get("sprintStart"), meta.get("targetCompletion")
        if not valid_iso_date(start) or not valid_iso_date(target):
            findings.append(finding("SPR-CONTRACT-001", "SPRINT_PERIOD_INVALID", rel(root, brief), "sprintStart and targetCompletion must be ISO dates.", sprintStart=start, targetCompletion=target))
        elif start > target:
            findings.append(finding("SPR-CONTRACT-001", "SPRINT_PERIOD_ORDER_INVALID", rel(root, brief), "sprintStart must not be after targetCompletion."))

    status = sprint_dir / "STATUS.md"
    if status.is_file():
        meta = metadata_by_file.get("STATUS.md", {})
        checks = [
            ("sprintPhase", contract["phases"], "SPRINT_PHASE_INVALID"),
            ("overallStatus", contract["overallStatuses"], "SPRINT_OVERALL_STATUS_INVALID"),
            ("lastDriftResult", drift["results"], "SPRINT_DRIFT_RESULT_INVALID"),
            ("expectedVersionImpact", contract["versionImpacts"], "SPRINT_VERSION_IMPACT_INVALID"),
        ]
        for field, allowed, code in checks:
            if meta.get(field) not in allowed:
                findings.append(finding("SPR-STATUS-001" if field != "lastDriftResult" else "SPR-DRIFT-001", code, rel(root, status), f"{field} is not a controlled value.", allowed=allowed, actual=meta.get(field)))
        if not valid_iso_date(meta.get("lastDriftAt")):
            findings.append(finding("SPR-DRIFT-001", "SPRINT_DRIFT_DATE_INVALID", rel(root, status), "lastDriftAt must be an ISO date."))
        brief_meta = metadata_by_file.get("SPRINT_BRIEF.md", {})
        target = brief_meta.get("targetCompletion")
        if valid_iso_date(target) and target < date.today().isoformat() and valid_iso_date(meta.get("lastDriftAt")) and meta["lastDriftAt"] < target:
            findings.append(finding("SPR-DRIFT-002", "SPRINT_DRIFT_REVIEW_STALE", rel(root, status), "A crossed target completion requires a drift review on or after targetCompletion.", targetCompletion=target, lastDriftAt=meta.get("lastDriftAt")))
        _, status_rows = parse_table(status, "Teilziele")
        status_map = {row.get("ID", ""): row.get("Status", "") for row in status_rows}
        if milestone_ids and set(status_map) != set(milestone_ids):
            findings.append(finding("SPR-MILESTONE-001", "SPRINT_STATUS_MILESTONES_MISMATCH", rel(root, status), "STATUS.md must cover exactly the milestones from SPRINT_BRIEF.md.", expected=milestone_ids, actual=sorted(status_map)))
        for milestone_id, value in status_map.items():
            if value not in contract["milestoneStatuses"]:
                findings.append(finding("SPR-MILESTONE-001", "SPRINT_STATUS_MILESTONE_STATUS_INVALID", rel(root, status), "STATUS.md contains an invalid milestone status.", milestoneId=milestone_id, actual=value))
        amendment_count, amendment_missing = complete_amendments(brief, drift) if brief.is_file() else (0, [])
        if meta.get("lastDriftResult") == "accepted" and amendment_count == 0:
            findings.append(finding("SPR-AMEND-001", "SPRINT_ACCEPTED_DRIFT_WITHOUT_AMENDMENT", rel(root, status), "Accepted drift requires at least one amendment in SPRINT_BRIEF.md."))
        if amendment_missing:
            findings.append(finding("SPR-AMEND-001", "SPRINT_AMENDMENT_INCOMPLETE", rel(root, brief), "Sprint amendment is missing required fields.", missing=amendment_missing))

    work_root = sprint_dir / contract["workDocuments"]["root"]
    if work_root.exists():
        allowed = set(contract["workDocuments"]["allowedDirectories"])
        for child in work_root.iterdir():
            if child.name not in allowed:
                findings.append(finding("SPR-DOC-001", "SPRINT_WORK_PATH_INVALID", rel(root, child), "WORK content must use a registered sprint work directory.", allowed=sorted(allowed)))
        for path in work_root.rglob("*.md"):
            meta = front_matter(path)
            missing = [field for field in contract["workDocuments"]["requiredMetadata"] if not meta.get(field)]
            if meta.get("temporary") is not True or meta.get("sprintId") != sprint_id or missing:
                findings.append(finding("SPR-DOC-001", "SPRINT_WORK_METADATA_INVALID", rel(root, path), "Sprint WORK documents must be temporary and carry matching sprintId and reviewBy.", missing=missing, sprintId=meta.get("sprintId"), temporary=meta.get("temporary")))

    completion = sprint_dir / "COMPLETION_REPORT.md"
    if completion.is_file():
        meta = metadata_by_file.get("COMPLETION_REPORT.md", {})
        if meta.get("qualificationStatus") not in contract["qualificationStatuses"]:
            findings.append(finding("SPR-CLOSURE-001", "SPRINT_QUALIFICATION_STATUS_INVALID", rel(root, completion), "qualificationStatus is invalid.", allowed=contract["qualificationStatuses"], actual=meta.get("qualificationStatus")))
        if meta.get("closureStatus") not in contract["closureStatuses"]:
            findings.append(finding("SPR-CLOSURE-001", "SPRINT_CLOSURE_STATUS_INVALID", rel(root, completion), "closureStatus is invalid.", allowed=contract["closureStatuses"], actual=meta.get("closureStatus")))
        if meta.get("closureStatus") in {"completed", "cancelled"}:
            if meta.get("status") not in {"final", "corrected"} or not valid_iso_date(meta.get("closedAt")):
                findings.append(finding("SPR-CLOSURE-001", "SPRINT_CLOSURE_METADATA_INCOMPLETE", rel(root, completion), "Closed sprint reports require final/corrected status and closedAt."))
            header, rows = parse_table(completion, "Temporäre Dokumente")
            decisions = {row.get("Pfad", ""): row.get("Entscheidung", "") for row in rows}
            required_paths = {"SOLUTION_PLAN.md", "STATUS.md"}
            if work_root.exists():
                required_paths.update(rel(sprint_dir, p) for p in work_root.rglob("*.md"))
            allowed_decisions = {"promote", "aggregate", "archive", "discard"}
            missing_paths = sorted(path for path in required_paths if path not in decisions)
            invalid_decisions = {path: value for path, value in decisions.items() if value not in allowed_decisions}
            if "Pfad" not in header or "Entscheidung" not in header or missing_paths or invalid_decisions:
                findings.append(finding("SPR-CLOSURE-001", "SPRINT_TEMPORARY_DISPOSITION_INVALID", rel(root, completion), "Closed sprint must decide every temporary document.", missingPaths=missing_paths, invalidDecisions=invalid_decisions))
            text = completion.read_text(encoding="utf-8")
            missing_milestones = [item for item in milestone_ids if item not in text]
            if missing_milestones:
                findings.append(finding("SPR-CLOSURE-001", "SPRINT_COMPLETION_MILESTONES_MISSING", rel(root, completion), "Completion report must address every milestone.", missing=missing_milestones))


def validate_archived_sprint(root: Path, year_dir: Path, sprint_dir: Path, contract: dict[str, Any], index_text: str, findings: list[dict[str, Any]]) -> None:
    year = year_dir.name
    sprint_id = sprint_dir.name
    sprint_rel = rel(root, sprint_dir)
    if not re.fullmatch(r"[0-9]{4}", year):
        findings.append(finding("SPR-CLOSURE-001", "SPRINT_ARCHIVE_YEAR_INVALID", rel(root, year_dir), "Archive year directory must use YYYY."))
    if not re.fullmatch(contract["sprintIdPattern"], sprint_id):
        findings.append(finding("SPR-CONTRACT-001", "SPRINT_ID_INVALID", sprint_rel, "Archived sprint directory name is invalid."))
    for forbidden in contract["forbiddenArchiveEntries"]:
        if (sprint_dir / forbidden).exists():
            findings.append(finding("SPR-CLOSURE-001", "SPRINT_ARCHIVE_TEMPORARY_CONTENT_PRESENT", rel(root, sprint_dir / forbidden), "Archived sprint contains temporary control content."))
    allowed_names = {item["file"] for item in contract["archiveDocuments"]} | set(contract.get("optionalArchiveFiles", []))
    for child in sprint_dir.iterdir():
        if child.name not in allowed_names:
            findings.append(finding("SPR-CLOSURE-001", "SPRINT_ARCHIVE_ENTRY_UNREGISTERED", rel(root, child), "Archived sprint contains an unregistered entry.", allowed=sorted(allowed_names)))
    metadata_by_file: dict[str, dict[str, Any]] = {}
    for spec in contract["archiveDocuments"]:
        path = sprint_dir / spec["file"]
        if not path.is_file():
            findings.append(finding("SPR-CLOSURE-001", "SPRINT_ARCHIVE_DOCUMENT_MISSING", rel(root, path), "Required archived sprint document is missing."))
            continue
        metadata_by_file[spec["file"]] = validate_document(root, sprint_id, path, spec, findings)
        validate_headings(root, path, contract.get("requiredHeadings", {}).get(spec["file"], []), findings)
        if not indexed(index_text, rel(root, path)):
            findings.append(finding("SPR-INDEX-001", "SPRINT_DOCUMENT_NOT_INDEXED", rel(root, path), "Archived sprint document is not discoverable from PROJECT_DOCS/index.md."))
    completion = sprint_dir / "COMPLETION_REPORT.md"
    meta = metadata_by_file.get("COMPLETION_REPORT.md", {})
    if completion.is_file():
        if meta.get("closureStatus") not in {"completed", "cancelled"}:
            findings.append(finding("SPR-CLOSURE-001", "SPRINT_ARCHIVE_NOT_CLOSED", rel(root, completion), "Archived sprint must be completed or cancelled."))
        if meta.get("qualificationStatus") not in {"qualified", "qualified-with-deferrals", "cancelled"}:
            findings.append(finding("SPR-CLOSURE-001", "SPRINT_ARCHIVE_QUALIFICATION_INVALID", rel(root, completion), "Archived sprint qualification is not closure-compatible.", actual=meta.get("qualificationStatus")))
        closed_at = meta.get("closedAt")
        if not valid_iso_date(closed_at) or closed_at[:4] != year:
            findings.append(finding("SPR-CLOSURE-001", "SPRINT_ARCHIVE_YEAR_MISMATCH", rel(root, completion), "closedAt must be an ISO date in the archive year.", archiveYear=year, closedAt=closed_at))


def collect_sprints(root: Path, contract: dict[str, Any], mode: str, changed_paths: list[str]) -> tuple[list[Path], list[tuple[Path, Path]], bool]:
    active_root = root / contract["roots"]["active"]
    archive_root = root / contract["roots"]["archive"]
    expand_paths = {
        "PROJECT_DOCS/index.md",
        "PROJECT_DOCS/GOVERNANCE/SPRINT_GOVERNANCE.md",
        "contracts/governance/sprint/sprint-contract.json",
        "contracts/governance/sprint/sprint-drift-contract.json",
        "bin/sprint-gate.py",
    }
    expand_paths.update(item.get("template") for item in contract.get("activeDocuments", []) if isinstance(item.get("template"), str))
    expanded = mode != "changed" or any(path in expand_paths for path in changed_paths)
    def has_repository_content(path: Path) -> bool:
        return path.is_dir() and any(item.is_file() or item.is_symlink() for item in path.rglob("*"))

    active: list[Path] = []
    archived: list[tuple[Path, Path]] = []
    if expanded:
        if active_root.is_dir():
            active = sorted(path for path in active_root.iterdir() if has_repository_content(path))
        if archive_root.is_dir():
            for year_dir in sorted(path for path in archive_root.iterdir() if path.is_dir()):
                archived.extend((year_dir, path) for path in sorted(item for item in year_dir.iterdir() if item.is_dir()))
        return active, archived, mode == "changed"
    active_seen: set[Path] = set()
    archive_seen: set[tuple[Path, Path]] = set()
    active_prefix = Path(contract["roots"]["active"])
    archive_prefix = Path(contract["roots"]["archive"])
    for raw in changed_paths:
        path = Path(raw)
        parts = path.parts
        ap = active_prefix.parts
        ar = archive_prefix.parts
        if parts[:len(ap)] == ap and len(parts) > len(ap):
            active_seen.add(root / Path(*parts[:len(ap)+1]))
        if parts[:len(ar)] == ar and len(parts) > len(ar) + 1:
            year_dir = root / Path(*parts[:len(ar)+1])
            sprint_dir = root / Path(*parts[:len(ar)+2])
            archive_seen.add((year_dir, sprint_dir))
    return sorted(path for path in active_seen if has_repository_content(path)), sorted(archive_seen, key=lambda pair: str(pair[1])), False


def run(args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    root = args.root.resolve()
    contract_path = (root / args.contract).resolve()
    drift_path = (root / args.drift_contract).resolve()
    findings: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    tool_errors: list[dict[str, Any]] = []
    try:
        contract = read_json_object(contract_path, EXPECTED_SPRINT_SCHEMA)
        drift = read_json_object(drift_path, EXPECTED_DRIFT_SCHEMA)
        validate_contract_shape(contract, drift, root)
        index_path = root / contract["indexPath"]
        if not index_path.is_file():
            raise GateToolError("INDEX_MISSING", f"Documentation index is missing: {index_path}", str(index_path))
        index_text = index_path.read_text(encoding="utf-8")
        requested_mode = args.mode
        scan_mode = "all" if args.mode == "report" else args.mode
        active, archived, expanded = collect_sprints(root, contract, scan_mode, args.changed_path)
        for sprint_dir in active:
            validate_active_sprint(root, sprint_dir, contract, drift, index_text, findings)
        for year_dir, sprint_dir in archived:
            validate_archived_sprint(root, year_dir, sprint_dir, contract, index_text, findings)
        status = "PASS" if not findings else "FINDINGS"
        report = {
            "schemaVersion": REPORT_SCHEMA,
            "status": status,
            "result": "pass" if not findings else "findings",
            "enforcement": "report-only",
            "requestedMode": requested_mode,
            "scanMode": scan_mode,
            "expandedToAll": expanded,
            "contract": {
                "path": rel(root, contract_path),
                "schemaVersion": contract["schemaVersion"],
                "contractVersion": contract.get("contractVersion"),
                "status": contract.get("status"),
            },
            "driftContract": {
                "path": rel(root, drift_path),
                "schemaVersion": drift["schemaVersion"],
                "contractVersion": drift.get("contractVersion"),
                "status": drift.get("status"),
            },
            "summary": {
                "activeSprintCount": len(active),
                "archivedSprintCount": len(archived),
                "newFindingCount": len(findings),
                "warningFindingCount": len(warnings),
                "toolErrorCount": 0,
            },
            "changedPaths": args.changed_path,
            "newFindings": findings,
            "warnings": warnings,
            "toolErrors": [],
        }
        exit_code = 1 if args.check and findings else 0
        return report, exit_code
    except GateToolError as exc:
        tool_errors.append({"code": exc.code, "path": exc.path, "message": exc.message})
        report = {
            "schemaVersion": REPORT_SCHEMA,
            "status": "TOOL_ERROR",
            "result": "tool-error",
            "enforcement": "report-only",
            "requestedMode": args.mode,
            "scanMode": args.mode,
            "expandedToAll": False,
            "summary": {
                "activeSprintCount": 0,
                "archivedSprintCount": 0,
                "newFindingCount": 0,
                "warningFindingCount": 0,
                "toolErrorCount": len(tool_errors),
            },
            "changedPaths": args.changed_path,
            "newFindings": [],
            "warnings": [],
            "toolErrors": tool_errors,
        }
        return report, 2


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate Sprint Contract compliance without mutating the project.")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--contract", default="contracts/governance/sprint/sprint-contract.json")
    parser.add_argument("--drift-contract", default="contracts/governance/sprint/sprint-drift-contract.json")
    parser.add_argument("--mode", choices=["all", "changed", "report"], default="all")
    parser.add_argument("--changed-path", action="append", default=[])
    parser.add_argument("--out", type=Path)
    parser.add_argument("--check", action="store_true", help="Return exit 1 when findings exist; report-only remains the default.")
    args = parser.parse_args()
    report, exit_code = run(args)
    rendered = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
