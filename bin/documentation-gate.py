#!/usr/bin/env python3
"""Validate Springmaster Documentation Governance V2 contracts.

The gate keeps the existing transition model: explicitly baselined Markdown
files may remain V1/legacy and are reported without blocking. Every new or
migrated Markdown document must satisfy the V2 metadata contracts immediately.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any

REPORT_SCHEMA = "springmaster.documentation-gate-report.v2"
EXPECTED_CONTRACT_SCHEMAS = {
    "metadata": "springmaster.documentation-metadata-contract.v2",
    "types": "springmaster.documentation-types.v2",
    "scopes": "springmaster.documentation-scope-registry.v1",
    "baseline": "springmaster.documentation-transition-baseline.v2",
}


class GateToolError(RuntimeError):
    def __init__(self, code: str, message: str, path: str | None = None):
        super().__init__(message)
        self.code = code
        self.path = path


def rel(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def canonical_path_set_hash(paths: list[str], technical_paths: list[str]) -> str:
    payload = {"paths": sorted(paths), "technicalArtifactPaths": sorted(technical_paths)}
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def read_json_object(path: Path, schema: str | None = None) -> dict[str, Any]:
    if not path.is_file():
        raise GateToolError("CONTRACT_MISSING", f"Required contract file is missing: {path}", str(path))
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise GateToolError("CONTRACT_INVALID_JSON", f"Cannot parse JSON contract {path}: {exc}", str(path)) from exc
    if not isinstance(data, dict):
        raise GateToolError("CONTRACT_INVALID_SHAPE", f"JSON contract must be an object: {path}", str(path))
    if schema is not None and data.get("schemaVersion") != schema:
        raise GateToolError(
            "CONTRACT_SCHEMA_UNSUPPORTED",
            f"Unsupported schema in {path}: expected {schema!r}, got {data.get('schemaVersion')!r}",
            str(path),
        )
    return data


def parse_scalar(value: str) -> Any:
    value = value.strip()
    if value == "":
        return ""
    lowered = value.lower()
    if lowered in {"null", "~"}:
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
        raise GateToolError("DOCUMENT_READ_ERROR", f"Cannot read Markdown document {path}: {exc}", str(path)) from exc
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
            raise GateToolError("FRONT_MATTER_PARSE_ERROR", f"Unsupported front matter line in {path}: {line!r}", str(path))
        key, raw = line.split(":", 1)
        key = key.strip()
        if not key:
            raise GateToolError("FRONT_MATTER_PARSE_ERROR", f"Empty front matter key in {path}", str(path))
        if raw.strip() == "":
            result[key] = []
            current_list = key
        else:
            result[key] = parse_scalar(raw)
    raise GateToolError("FRONT_MATTER_UNTERMINATED", f"Front matter is not terminated in {path}", str(path))


def valid_date(value: Any) -> bool:
    if value is None:
        return True
    if not isinstance(value, str):
        return False
    try:
        date.fromisoformat(value)
        return bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}", value))
    except ValueError:
        return False


def finding(rule_id: str, code: str, path: str, message: str, **details: Any) -> dict[str, Any]:
    item: dict[str, Any] = {"ruleId": rule_id, "code": code, "path": path, "message": message}
    if details:
        item["details"] = details
    return item


def validate_v2_document(
    path: str,
    metadata: dict[str, Any],
    metadata_contract: dict[str, Any],
    type_map: dict[str, dict[str, Any]],
    authorities: set[str],
    scope_levels: set[str],
    scope_map: dict[str, dict[str, Any]],
    applies_to_values: set[str],
) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    required = metadata_contract.get("requiredFields")
    if not isinstance(required, list) or not all(isinstance(item, str) for item in required):
        raise GateToolError("CONTRACT_INVALID_SHAPE", "metadata contract requiredFields must be a string list")
    missing = [key for key in required if key not in metadata]
    if missing:
        findings.append(finding("DOC-META-001", "DOCUMENT_METADATA_MISSING", path, "Required V2 front matter fields are missing.", missing=missing))
        return findings

    document_id = metadata.get("documentId")
    id_pattern = metadata_contract.get("documentIdPattern")
    if not isinstance(document_id, str) or not isinstance(id_pattern, str) or re.fullmatch(id_pattern, document_id) is None:
        findings.append(finding("DOC-ID-001", "DOCUMENT_ID_INVALID", path, "documentId does not match the registered pattern.", actual=document_id))

    if not isinstance(metadata.get("title"), str) or not metadata.get("title", "").strip():
        findings.append(finding("DOC-META-001", "DOCUMENT_TITLE_INVALID", path, "title must be a non-empty string."))

    document_type = metadata.get("documentType")
    type_rule = type_map.get(document_type) if isinstance(document_type, str) else None
    if type_rule is None:
        findings.append(finding("DOC-TYPE-001", "DOCUMENT_TYPE_UNKNOWN", path, "documentType is not registered.", actual=document_type))
    else:
        status = metadata.get("status")
        if status not in type_rule.get("allowedStatuses", []):
            findings.append(finding("DOC-TYPE-001", "DOCUMENT_STATUS_INVALID", path, "status is not allowed for documentType.", documentType=document_type, actual=status, allowed=type_rule.get("allowedStatuses", [])))
        authority = metadata.get("authority")
        if authority not in authorities or authority not in set(type_rule.get("allowedAuthorities", [])):
            findings.append(finding("DOC-TYPE-001", "DOCUMENT_AUTHORITY_INVALID", path, "authority is not allowed for documentType.", documentType=document_type, actual=authority, allowed=type_rule.get("allowedAuthorities", [])))

    scope_level = metadata.get("scopeLevel")
    if scope_level not in scope_levels:
        findings.append(finding("DOC-SCOPE-001", "DOCUMENT_SCOPE_LEVEL_INVALID", path, "scopeLevel is not registered.", actual=scope_level))
    scope_paths = metadata.get("scopePaths")
    if not isinstance(scope_paths, list) or not scope_paths or not all(isinstance(item, str) and item in scope_map for item in scope_paths):
        unknown = [] if not isinstance(scope_paths, list) else [item for item in scope_paths if not isinstance(item, str) or item not in scope_map]
        findings.append(finding("DOC-SCOPE-001", "DOCUMENT_SCOPE_PATH_INVALID", path, "scopePaths must be a non-empty list of registered scopes.", unknown=unknown))

    applies_to = metadata.get("appliesTo")
    if not isinstance(applies_to, list) or not applies_to or not all(isinstance(item, str) and item in applies_to_values for item in applies_to):
        unknown = [] if not isinstance(applies_to, list) else [item for item in applies_to if not isinstance(item, str) or item not in applies_to_values]
        findings.append(finding("DOC-SCOPE-001", "DOCUMENT_APPLIES_TO_INVALID", path, "appliesTo must be a non-empty list of registered values.", unknown=unknown))

    owner = metadata.get("owner")
    owner_pattern = metadata_contract.get("ownerPattern")
    if not isinstance(owner, str) or not isinstance(owner_pattern, str) or re.fullmatch(owner_pattern, owner) is None:
        findings.append(finding("DOC-META-001", "DOCUMENT_OWNER_INVALID", path, "owner does not match the registered pattern.", actual=owner))

    for field_name in metadata_contract.get("dateFields", []):
        if not valid_date(metadata.get(field_name)):
            findings.append(finding("DOC-META-001", "DOCUMENT_DATE_INVALID", path, f"{field_name} must be null or an ISO date.", field=field_name, actual=metadata.get(field_name)))

    if type_rule is not None:
        status = metadata.get("status")
        if status in type_rule.get("reviewRequiredStatuses", []):
            review_by = metadata.get("reviewBy")
            if review_by is None:
                findings.append(finding("DOC-REVIEW-001", "DOCUMENT_REVIEW_DATE_REQUIRED", path, "reviewBy is required for this type and status."))
            elif valid_date(review_by) and date.fromisoformat(review_by) < date.today():
                findings.append(finding("DOC-REVIEW-001", "DOCUMENT_REVIEW_OVERDUE", path, "reviewBy is in the past.", reviewBy=review_by))
        if status in set(type_rule.get("allowedStatuses", [])) and status in set(type_map.get(document_type, {}).get("allowedStatuses", [])):
            pass

    valid_from_required = set(metadata_contract.get("validFromRequiredStatuses", []))
    if metadata.get("status") in valid_from_required and metadata.get("validFrom") is None:
        findings.append(finding("DOC-META-001", "DOCUMENT_VALID_FROM_REQUIRED", path, "validFrom is required for the current status."))

    if not isinstance(metadata.get("supersedes"), list) or not all(isinstance(item, str) for item in metadata.get("supersedes", [])):
        findings.append(finding("DOC-SUPERSESSION-001", "DOCUMENT_SUPERSEDES_INVALID", path, "supersedes must be a list of document IDs."))
    if metadata.get("supersededBy") is not None and not isinstance(metadata.get("supersededBy"), str):
        findings.append(finding("DOC-SUPERSESSION-001", "DOCUMENT_SUPERSEDED_BY_INVALID", path, "supersededBy must be null or a document ID."))

    if not isinstance(metadata.get("temporary"), bool):
        findings.append(finding("DOC-META-001", "DOCUMENT_TEMPORARY_INVALID", path, "temporary must be a boolean."))
    elif metadata.get("temporary"):
        if not isinstance(metadata.get("sprintId"), str) or not metadata.get("sprintId", "").strip():
            findings.append(finding("DOC-META-001", "TEMPORARY_DOCUMENT_SPRINT_REQUIRED", path, "temporary documents require sprintId."))
        if metadata.get("reviewBy") is None:
            findings.append(finding("DOC-REVIEW-001", "TEMPORARY_DOCUMENT_REVIEW_REQUIRED", path, "temporary documents require reviewBy."))

    if document_type in {"sprint-brief", "sprint-status", "sprint-completion-report"} and not isinstance(metadata.get("sprintId"), str):
        findings.append(finding("DOC-META-001", "SPRINT_DOCUMENT_ID_REQUIRED", path, "Sprint documents require sprintId."))

    basename = Path(path).name
    for pattern in metadata_contract.get("forbiddenFilenamePatterns", []):
        if re.search(pattern, basename):
            findings.append(finding("DOC-NAME-001", "DOCUMENT_FILENAME_FORBIDDEN", path, "Filename contains a forbidden manual revision or backup marker.", pattern=pattern))
            break
    return findings


def run_gate(root: Path) -> dict[str, Any]:
    docs = root / "PROJECT_DOCS"
    contract_root = root / "contracts/governance/documentation"
    metadata_contract = read_json_object(contract_root / "document-metadata-contract.json", EXPECTED_CONTRACT_SCHEMAS["metadata"])
    types_contract = read_json_object(contract_root / "document-types.json", EXPECTED_CONTRACT_SCHEMAS["types"])
    scopes_contract = read_json_object(contract_root / "scope-registry.json", EXPECTED_CONTRACT_SCHEMAS["scopes"])

    baseline_rel = metadata_contract.get("transitionBaseline", {}).get("path")
    if not isinstance(baseline_rel, str):
        raise GateToolError("CONTRACT_INVALID_SHAPE", "metadata contract transitionBaseline.path must be a string")
    baseline = read_json_object(root / baseline_rel, EXPECTED_CONTRACT_SCHEMAS["baseline"])

    baseline_paths = baseline.get("paths")
    technical_baseline = baseline.get("technicalArtifactPaths")
    if not isinstance(baseline_paths, list) or not all(isinstance(item, str) for item in baseline_paths):
        raise GateToolError("CONTRACT_INVALID_SHAPE", "transition baseline paths must be a string list", baseline_rel)
    if not isinstance(technical_baseline, list) or not all(isinstance(item, str) for item in technical_baseline):
        raise GateToolError("CONTRACT_INVALID_SHAPE", "transition baseline technicalArtifactPaths must be a string list", baseline_rel)

    blocking: list[dict[str, Any]] = []
    transition: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []

    canonical_hash = canonical_path_set_hash(baseline_paths, technical_baseline)
    declared_hash = baseline.get("pathSetSha256")
    locked_hash = metadata_contract.get("transitionBaseline", {}).get("pathSetSha256")
    if canonical_hash != declared_hash or canonical_hash != locked_hash:
        blocking.append(finding("DOC-BASELINE-001", "TRANSITION_BASELINE_LOCK_MISMATCH", baseline_rel, "Transition baseline path set does not match the accepted contract lock.", calculated=canonical_hash, baselineDeclared=declared_hash, contractLocked=locked_hash))

    current_markdown = sorted(rel(root, path) for path in docs.rglob("*.md"))
    current_technical = sorted(rel(root, path) for path in docs.rglob("*") if path.is_file() and path.suffix.lower() != ".md")
    baseline_set = set(baseline_paths)
    technical_baseline_set = set(technical_baseline)

    for path in sorted(baseline_set - set(current_markdown)):
        blocking.append(finding("DOC-BASELINE-001", "TRANSITION_BASELINE_STALE_PATH", path, "Baselined Markdown path no longer exists and must be removed from the baseline."))
    for path in sorted(technical_baseline_set - set(current_technical)):
        blocking.append(finding("DOC-BASELINE-001", "TECHNICAL_BASELINE_STALE_PATH", path, "Baselined technical artifact no longer exists and must be removed from the baseline."))
    for path in sorted(set(current_technical) - technical_baseline_set):
        blocking.append(finding("DOC-TECH-001", "NEW_TECHNICAL_ARTIFACT_UNDER_PROJECT_DOCS", path, "New non-Markdown technical artifacts are not allowed under PROJECT_DOCS."))

    type_entries = types_contract.get("types")
    if not isinstance(type_entries, list):
        raise GateToolError("CONTRACT_INVALID_SHAPE", "document types contract types must be a list")
    type_map: dict[str, dict[str, Any]] = {}
    for item in type_entries:
        if not isinstance(item, dict) or not isinstance(item.get("id"), str):
            raise GateToolError("CONTRACT_INVALID_SHAPE", "Each document type entry must be an object with a string id")
        if item["id"] in type_map:
            raise GateToolError("CONTRACT_DUPLICATE_ENTRY", f"Duplicate document type entry: {item['id']}")
        type_map[item["id"]] = item

    authorities = set(types_contract.get("authorities", []))
    metadata_contract["validFromRequiredStatuses"] = types_contract.get("validFromRequiredStatuses", [])
    scope_levels = set(scopes_contract.get("scopeLevels", []))
    applies_to_values = set(scopes_contract.get("appliesToValues", []))
    scope_entries = scopes_contract.get("scopes")
    if not isinstance(scope_entries, list):
        raise GateToolError("CONTRACT_INVALID_SHAPE", "scope registry scopes must be a list")
    scope_map = {item.get("id"): item for item in scope_entries if isinstance(item, dict) and isinstance(item.get("id"), str)}
    if len(scope_map) != len(scope_entries):
        raise GateToolError("CONTRACT_DUPLICATE_ENTRY", "Scope registry contains invalid or duplicate scope IDs")

    v2_docs: dict[str, dict[str, Any]] = {}
    ids: dict[str, list[str]] = {}
    for path in current_markdown:
        metadata = front_matter(root / path)
        if path in baseline_set:
            if all(key in metadata for key in metadata_contract.get("requiredFields", [])):
                warnings.append(finding("DOC-BASELINE-001", "BASELINED_DOCUMENT_V2_READY", path, "Baselined document already contains V2 metadata and should be removed from the transition baseline."))
            else:
                transition.append(finding("DOC-META-001", "LEGACY_DOCUMENT_METADATA_PENDING", path, "Baselined legacy document has not yet migrated to V2 metadata."))
            continue
        doc_findings = validate_v2_document(path, metadata, metadata_contract, type_map, authorities, scope_levels, scope_map, applies_to_values)
        blocking.extend(doc_findings)
        if not doc_findings or isinstance(metadata.get("documentId"), str):
            v2_docs[path] = metadata
            if isinstance(metadata.get("documentId"), str):
                ids.setdefault(metadata["documentId"], []).append(path)

    for document_id, paths in sorted(ids.items()):
        if len(paths) > 1:
            for path in paths:
                blocking.append(finding("DOC-ID-001", "DOCUMENT_ID_DUPLICATE", path, "documentId is used by more than one V2 document.", documentId=document_id, paths=paths))

    id_to_path = {document_id: paths[0] for document_id, paths in ids.items() if len(paths) == 1}
    for path, metadata in sorted(v2_docs.items()):
        current_id = metadata.get("documentId")
        supersedes = metadata.get("supersedes") if isinstance(metadata.get("supersedes"), list) else []
        for target_id in supersedes:
            target_path = id_to_path.get(target_id)
            if target_path is None:
                blocking.append(finding("DOC-SUPERSESSION-001", "SUPERSESSION_TARGET_UNKNOWN", path, "supersedes references an unknown V2 document ID.", targetId=target_id))
            elif v2_docs[target_path].get("supersededBy") != current_id:
                blocking.append(finding("DOC-SUPERSESSION-001", "SUPERSESSION_NOT_RECIPROCAL", path, "supersession relation is not reciprocal.", targetId=target_id, targetPath=target_path))
        superseded_by = metadata.get("supersededBy")
        if isinstance(superseded_by, str):
            successor_path = id_to_path.get(superseded_by)
            if successor_path is None:
                blocking.append(finding("DOC-SUPERSESSION-001", "SUPERSEDED_BY_TARGET_UNKNOWN", path, "supersededBy references an unknown V2 document ID.", successorId=superseded_by))
            elif current_id not in (v2_docs[successor_path].get("supersedes") or []):
                blocking.append(finding("DOC-SUPERSESSION-001", "SUPERSESSION_NOT_RECIPROCAL", path, "supersededBy relation is not reciprocal.", successorId=superseded_by, successorPath=successor_path))

    index_rel = metadata_contract.get("indexPath")
    if not isinstance(index_rel, str):
        raise GateToolError("CONTRACT_INVALID_SHAPE", "metadata contract indexPath must be a string")
    index_path = root / index_rel
    if not index_path.is_file():
        blocking.append(finding("DOC-INDEX-001", "DOCUMENTATION_INDEX_MISSING", index_rel, "Documentation index is missing."))
        indexed: set[str] = set()
    else:
        try:
            indexed = set(re.findall(r"`(PROJECT_DOCS/[^`]+\.md)`", index_path.read_text(encoding="utf-8")))
        except Exception as exc:
            raise GateToolError("DOCUMENT_READ_ERROR", f"Cannot read documentation index: {exc}", index_rel) from exc
    expected_index = set(current_markdown) - {index_rel}
    for path in sorted(expected_index - indexed):
        blocking.append(finding("DOC-INDEX-001", "INDEX_ENTRY_MISSING", path, "Markdown document is missing from PROJECT_DOCS/index.md."))
    for path in sorted(indexed - expected_index):
        blocking.append(finding("DOC-INDEX-001", "INDEX_ENTRY_STALE", path, "Index references a Markdown document that does not exist."))

    for type_id, item in sorted(type_map.items()):
        template_path = item.get("templatePath")
        if not isinstance(template_path, str) or not (root / template_path).is_file():
            blocking.append(finding("DOC-TEMPLATE-001", "DOCUMENT_TEMPLATE_MISSING", str(template_path or "<missing>"), "Registered document type does not resolve to an existing template.", documentType=type_id))

    result = "passed" if not blocking else "blocked"
    status = "PASS" if not blocking else "FAIL"
    return {
        "schema": REPORT_SCHEMA,
        "status": status,
        "result": result,
        "mode": "transition-report-only-for-baselined-legacy",
        "documentCount": len(current_markdown),
        "v2DocumentCount": len(current_markdown) - len(baseline_set & set(current_markdown)),
        "baselineCount": len(baseline_paths),
        "technicalArtifactBaselineCount": len(technical_baseline),
        "legacyMetadataFindingCount": len(transition),
        "blockingFindingCount": len(blocking),
        "warningFindingCount": len(warnings),
        "toolErrorCount": 0,
        "blockingFindings": blocking,
        "transitionFindings": transition,
        "legacyFindings": transition,
        "warnings": warnings,
        "toolErrors": [],
    }


def write_report(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=None)
    parser.add_argument("--out", default="target/documentation-gate-report.json")
    parser.add_argument("--check", action="store_true", help="Backward-compatible alias for --check-all")
    parser.add_argument("--check-all", action="store_true", help="Fail when blocking findings exist")
    parser.add_argument("--report", action="store_true", help="Generate a report without failing for findings")
    args = parser.parse_args()

    root = Path(args.root).resolve() if args.root else Path(__file__).resolve().parents[1]
    out = Path(args.out)
    if not out.is_absolute():
        out = root / out
    fail_on_findings = args.check or args.check_all

    try:
        report = run_gate(root)
    except GateToolError as exc:
        report = {
            "schema": REPORT_SCHEMA,
            "status": "TOOL_ERROR",
            "result": "tool-error",
            "mode": "transition-report-only-for-baselined-legacy",
            "documentCount": 0,
            "v2DocumentCount": 0,
            "baselineCount": 0,
            "technicalArtifactBaselineCount": 0,
            "legacyMetadataFindingCount": 0,
            "blockingFindingCount": 0,
            "warningFindingCount": 0,
            "toolErrorCount": 1,
            "blockingFindings": [],
            "transitionFindings": [],
            "legacyFindings": [],
            "warnings": [],
            "toolErrors": [{"code": exc.code, "path": exc.path, "message": str(exc)}],
        }
        try:
            write_report(out, report)
        except Exception:
            pass
        print("DOCUMENTATION_GATE=TOOL_ERROR")
        print(f"REPORT={out}")
        return 2
    except Exception as exc:  # defensive fail-closed boundary
        report = {
            "schema": REPORT_SCHEMA,
            "status": "TOOL_ERROR",
            "result": "tool-error",
            "mode": "transition-report-only-for-baselined-legacy",
            "documentCount": 0,
            "v2DocumentCount": 0,
            "baselineCount": 0,
            "technicalArtifactBaselineCount": 0,
            "legacyMetadataFindingCount": 0,
            "blockingFindingCount": 0,
            "warningFindingCount": 0,
            "toolErrorCount": 1,
            "blockingFindings": [],
            "transitionFindings": [],
            "legacyFindings": [],
            "warnings": [],
            "toolErrors": [{"code": "UNEXPECTED_TOOL_ERROR", "path": None, "message": str(exc)}],
        }
        try:
            write_report(out, report)
        except Exception:
            pass
        print("DOCUMENTATION_GATE=TOOL_ERROR")
        print(f"REPORT={out}")
        return 2

    write_report(out, report)
    print(f"DOCUMENTATION_GATE={report['status']}")
    print(f"REPORT={out}")
    if fail_on_findings and report["blockingFindingCount"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
