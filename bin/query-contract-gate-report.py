#!/usr/bin/env python3
"""Springmaster query contract gate report MVP.

The report is intentionally source-based and report-only. It proves the
machine-readable contract introduced by `QUERY_CONTRACT_GATE_REPORT.md` for the
current Springmaster CatalogItem candidate slice without promoting strict build
failure semantics.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

SCHEMA_VERSION = "springmaster.query-contract-gate-report.v1"
MODE = "report-only"
PROJECT = "springmaster"
DEFAULT_OUT = "reports/api/query-contract-gate-report.json"

CATALOG_CONTROLLER = Path("src/main/java/de/cocondo/platform/demo/catalog/api/CatalogItemController.java")
CATALOG_SERVICE = Path("src/main/java/de/cocondo/platform/demo/catalog/CatalogItemService.java")
CATALOG_PAGED_QUERY = Path("src/main/java/de/cocondo/platform/demo/catalog/CatalogItemPagedQuery.java")
CATALOG_ALL_QUERY = Path("src/main/java/de/cocondo/platform/demo/catalog/CatalogItemAllQuery.java")
CATALOG_COUNT_QUERY = Path("src/main/java/de/cocondo/platform/demo/catalog/CatalogItemCountQuery.java")
CATALOG_COUNT_DOC = Path("PROJECT_DOCS/DEMO/CATALOGITEM_COUNT_REFERENCE_SLICE.md")
QUERY_GATE_DOC = Path("PROJECT_DOCS/STANDARDS/API/QUERY_CONTRACT_GATE_REPORT.md")
COUNT_CONTRACT_DOC = Path("PROJECT_DOCS/STANDARDS/API/API_COUNT_RESPONSE_CONTRACT_CANDIDATE.md")
JPA_COUNT_DOC = Path("PROJECT_DOCS/STANDARDS/API/JPA_COUNT_QUERY_EFFICIENCY_REFERENCE.md")

LIST_REQUIRED = {"page", "size", "sortBy", "sortDir"}
CATALOG_FILTERS = {"sku", "name"}
ALL_FORBIDDEN = {"page", "size"}
COUNT_FORBIDDEN = {"page", "size", "sortBy", "sortDir"}
COUNT_ALLOWED = CATALOG_FILTERS


@dataclass(frozen=True)
class Finding:
    id: str
    severity: str
    resource: str
    operation: str
    message: str
    standard: str
    evidence: dict[str, str]

    def to_json(self) -> dict[str, object]:
        return asdict(self)


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def read_text(root: Path, path: Path) -> str:
    return (root / path).read_text(encoding="utf-8", errors="replace")


def request_mapping_base(text: str) -> str:
    match = re.search(r"@RequestMapping\s*\(\s*\"([^\"]+)\"\s*\)", text)
    return match.group(1) if match else ""


def method_block(text: str, annotation: str, method_name: str) -> str:
    marker = f"@{annotation}"
    method_idx = text.find(method_name + "(")
    if method_idx < 0:
        return ""
    annotation_idx = text.rfind(marker, 0, method_idx)
    if annotation_idx < 0:
        return ""
    next_mapping = len(text)
    for candidate in ("@GetMapping", "@PostMapping", "@PutMapping", "@DeleteMapping", "@PatchMapping", "@ExceptionHandler"):
        idx = text.find(candidate, method_idx + len(method_name))
        if idx >= 0:
            next_mapping = min(next_mapping, idx)
    return text[annotation_idx:next_mapping]


def mapping_path(block: str) -> str:
    match = re.search(
        r"@(?:GetMapping|PostMapping|PutMapping|DeleteMapping|PatchMapping)\s*(?:\((.*?)\))?",
        block,
        re.DOTALL,
    )
    if not match:
        return ""
    args = match.group(1) or ""
    named = re.search(r"(?:path|value)\s*=\s*\{?\s*\"([^\"]*)\"", args, re.DOTALL)
    if named:
        return named.group(1) or ""
    literal = re.search(r"\"([^\"]*)\"", args)
    return literal.group(1) if literal else ""


def request_params(block: str) -> list[str]:
    names: set[str] = set()
    for match in re.finditer(r"@RequestParam\s*\(([^)]*)\)", block, re.DOTALL):
        args = match.group(1)
        for named in re.findall(r"(?:name|value)\s*=\s*\"([^\"]+)\"", args):
            names.add(named)
        if not names:
            literal = re.search(r"\"([^\"]+)\"", args)
            if literal:
                names.add(literal.group(1))
    return sorted(names)


def full_operation(base: str, suffix: str) -> str:
    if not suffix:
        return f"GET {base}"
    return f"GET {base.rstrip('/')}/{suffix.strip('/')}"


def required_file_findings(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    for path in [CATALOG_CONTROLLER, CATALOG_SERVICE, CATALOG_PAGED_QUERY, CATALOG_ALL_QUERY, CATALOG_COUNT_QUERY, QUERY_GATE_DOC, COUNT_CONTRACT_DOC, JPA_COUNT_DOC]:
        if not (root / path).is_file():
            findings.append(Finding(
                id="QRY-GATE-001",
                severity="error",
                resource="CatalogItem",
                operation="source-preflight",
                message=f"Required query-contract report input is missing: {path}",
                standard="QUERY_CONTRACT_GATE_REPORT.md",
                evidence={"file": str(path)},
            ))
    return findings


def classify_catalog(root: Path) -> tuple[dict[str, object], list[Finding]]:
    findings = required_file_findings(root)
    if findings:
        return {
            "resource": "CatalogItem",
            "status": "incomplete-input",
            "operations": [],
        }, findings

    controller = read_text(root, CATALOG_CONTROLLER)
    service = read_text(root, CATALOG_SERVICE)
    base = request_mapping_base(controller)

    list_block = method_block(controller, "GetMapping", "list")
    all_block = method_block(controller, "GetMapping", "listAll")
    count_block = method_block(controller, "GetMapping", "count")

    list_params = set(request_params(list_block))
    all_params = set(request_params(all_block))
    count_params = set(request_params(count_block))

    list_operation = full_operation(base, mapping_path(list_block))
    all_operation = full_operation(base, mapping_path(all_block))
    count_operation = full_operation(base, mapping_path(count_block))

    if not list_block:
        findings.append(Finding("QRY-LIST-001", "error", "CatalogItem", "GET /api/demo/catalog/items", "Paged list operation is missing.", "LIST_FILTER_QUERY_STANDARD.md", {"file": str(CATALOG_CONTROLLER), "symbol": "list"}))
    missing_list = sorted(LIST_REQUIRED - list_params)
    if missing_list:
        findings.append(Finding("QRY-LIST-001", "error", "CatalogItem", list_operation, "Paged list operation misses canonical paging/sorting parameters.", "LIST_FILTER_QUERY_STANDARD.md", {"file": str(CATALOG_CONTROLLER), "missing": ",".join(missing_list)}))
    if "PagedResponseDTO" not in list_block:
        findings.append(Finding("QRY-LIST-003", "warning", "CatalogItem", list_operation, "Paged list response does not show PagedResponseDTO metadata evidence.", "LIST_FILTER_QUERY_STANDARD.md", {"file": str(CATALOG_CONTROLLER), "symbol": "list"}))

    if not all_block:
        findings.append(Finding("QRY-ALL-003", "info", "CatalogItem", "GET /api/demo/catalog/items/all", "Complete-result-set operation is missing.", "API_RESULT_SET_EXPORT_ALL_STANDARD.md", {"file": str(CATALOG_CONTROLLER), "symbol": "listAll"}))
    forbidden_all = sorted(ALL_FORBIDDEN & all_params)
    if forbidden_all:
        findings.append(Finding("QRY-ALL-001", "warning", "CatalogItem", all_operation, "/all operation exposes paging parameters.", "API_RESULT_SET_EXPORT_ALL_STANDARD.md", {"file": str(CATALOG_CONTROLLER), "forbidden": ",".join(forbidden_all)}))

    if not count_block:
        findings.append(Finding("QRY-COUNT-002", "warning", "CatalogItem", "GET /api/demo/catalog/items/count", "Count operation is missing.", "API_COUNT_RESPONSE_CONTRACT_CANDIDATE.md", {"file": str(CATALOG_CONTROLLER), "symbol": "count"}))
    if "CountResponseDTO" not in count_block:
        findings.append(Finding("QRY-COUNT-002", "warning", "CatalogItem", count_operation, "Count operation does not expose CountResponseDTO evidence.", "API_COUNT_RESPONSE_CONTRACT_CANDIDATE.md", {"file": str(CATALOG_CONTROLLER), "symbol": "count"}))
    forbidden_count = sorted(COUNT_FORBIDDEN & count_params)
    if forbidden_count:
        findings.append(Finding("QRY-COUNT-003", "warning", "CatalogItem", count_operation, "Count endpoint exposes paging or sorting parameters.", "API_COUNT_RESPONSE_CONTRACT_CANDIDATE.md", {"file": str(CATALOG_CONTROLLER), "forbidden": ",".join(forbidden_count)}))
    if "COUNT_QUERY_PARAMETERS = Set.of(\"sku\", \"name\")" not in controller or "validateCountQueryParameters(request)" not in count_block:
        findings.append(Finding("QRY-COUNT-003", "warning", "CatalogItem", count_operation, "Count endpoint does not show strict unsupported-parameter validation evidence.", "API_COUNT_RESPONSE_CONTRACT_CANDIDATE.md", {"file": str(CATALOG_CONTROLLER), "symbol": "COUNT_QUERY_PARAMETERS"}))

    list_filters = list_params - LIST_REQUIRED
    all_filters = all_params - {"sortBy", "sortDir"}
    count_filters = count_params
    if list_filters != all_filters or count_filters != COUNT_ALLOWED or list_filters != COUNT_ALLOWED:
        findings.append(Finding(
            "QRY-FILTER-001",
            "warning",
            "CatalogItem",
            "list/all/count",
            "List, /all and /count do not expose the same business filter family.",
            "LIST_FILTER_QUERY_STANDARD.md",
            {"list": ",".join(sorted(list_filters)), "all": ",".join(sorted(all_filters)), "count": ",".join(sorted(count_filters))},
        ))

    if "SORT_COMPARATORS" not in service or '"sku"' not in service or '"name"' not in service:
        findings.append(Finding("QRY-SORT-001", "warning", "CatalogItem", "service sort", "Sort allowlist evidence is missing.", "LIST_FILTER_QUERY_STANDARD.md", {"file": str(CATALOG_SERVICE), "symbol": "SORT_COMPARATORS"}))
    if "TIE_BREAKER_COMPARATOR" not in service or "stableComparator" not in service:
        findings.append(Finding("QRY-SORT-002", "info", "CatalogItem", "service sort", "Stable tie-breaker evidence is missing.", "LIST_FILTER_QUERY_STANDARD.md", {"file": str(CATALOG_SERVICE), "symbol": "stableComparator"}))
    if "implements ResultSetQueryOperations" not in service:
        findings.append(Finding("QRY-OPS-001", "info", "CatalogItem", "service contract", "Service does not implement ResultSetQueryOperations.", "CORE_QUERY_OPERATIONS_INTERFACE_CONTRACT.md", {"file": str(CATALOG_SERVICE), "symbol": "CatalogItemService"}))
    count_method = method_body_like(service, "count", "CatalogItemCountQuery")
    if re.search(r"listAll\s*\([^)]*\)\.size\s*\(|findAll\s*\([^)]*\)\.size\s*\(|\.map\s*\(\s*mapper::", count_method):
        findings.append(Finding("QRY-COUNT-004", "warning", "CatalogItem", "service count", "Count implementation appears to materialize data or DTOs before counting.", "JPA_COUNT_QUERY_EFFICIENCY_REFERENCE.md", {"file": str(CATALOG_SERVICE), "symbol": "count"}))

    status = "pass" if not findings else "review"
    resource = {
        "resource": "CatalogItem",
        "status": status,
        "sourceType": "springmaster-candidate-reference-slice",
        "persistence": "in-memory",
        "jpaEfficiency": "not-applicable-in-memory",
        "operations": [
            {"kind": "paged-list", "operation": list_operation, "parameters": sorted(list_params), "requiredParametersPresent": sorted(LIST_REQUIRED <= list_params and LIST_REQUIRED or [])},
            {"kind": "complete-result-set", "operation": all_operation, "parameters": sorted(all_params), "forbiddenPagingParametersPresent": forbidden_all},
            {"kind": "count", "operation": count_operation, "parameters": sorted(count_params), "forbiddenPagingSortParametersPresent": forbidden_count, "response": "CountResponseDTO" if "CountResponseDTO" in count_block else "unknown"},
        ],
        "filterFamily": sorted(CATALOG_FILTERS),
        "sortAllowlist": ["name", "sku"] if "SORT_COMPARATORS" in service else [],
        "stableTieBreakerEvidence": "present" if "TIE_BREAKER_COMPARATOR" in service and "stableComparator" in service else "missing",
        "queryOperationsInterface": "present" if "implements ResultSetQueryOperations" in service else "missing",
    }
    return resource, findings


def method_body_like(text: str, method_name: str, parameter_type: str) -> str:
    sig = re.search(rf"\b{re.escape(method_name)}\s*\(\s*{re.escape(parameter_type)}\b", text)
    if not sig:
        return ""
    start = text.find("{", sig.end())
    if start < 0:
        return ""
    depth = 0
    for idx in range(start, len(text)):
        if text[idx] == "{":
            depth += 1
        elif text[idx] == "}":
            depth -= 1
            if depth == 0:
                return text[start:idx + 1]
    return text[start:]


def severity_summary(findings: Iterable[Finding]) -> dict[str, int]:
    rows = list(findings)
    return {
        "errors": sum(1 for row in rows if row.severity == "error"),
        "warnings": sum(1 for row in rows if row.severity == "warning"),
        "info": sum(1 for row in rows if row.severity == "info"),
    }


def write_report(path: Path, report: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False, sort_keys=False) + "\n", encoding="utf-8")


def build_report(root: Path, generated_at: str | None = None) -> dict[str, object]:
    resource, findings = classify_catalog(root)
    counts = severity_summary(findings)
    generated = generated_at or datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    return {
        "schemaVersion": SCHEMA_VERSION,
        "generatedAt": generated,
        "project": PROJECT,
        "mode": MODE,
        "source": {
            "javaSources": "src/main/java",
            "tests": "src/test/java",
            "standards": "PROJECT_DOCS/STANDARDS/API",
        },
        "summary": {
            "resources": 1,
            "findings": len(findings),
            **counts,
        },
        "resources": [resource],
        "findings": [finding.to_json() for finding in findings],
    }


def command_report(args: argparse.Namespace) -> int:
    root = repo_root()
    report = build_report(root, generated_at=args.generated_at)
    out = root / args.out
    write_report(out, report)
    print("Springmaster query contract report: SUCCESS")
    print(f"  Schema:   {report['schemaVersion']}")
    print(f"  Mode:     {report['mode']}")
    print(f"  Resources:{report['summary']['resources']}")
    print(f"  Findings: {report['summary']['findings']}")
    print(f"  Report:   {args.out}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Springmaster query contract gate report MVP")
    parser.add_argument("--out", default=DEFAULT_OUT, help="output JSON path relative to repository root")
    parser.add_argument("--generated-at", help="deterministic timestamp override for tests")
    parser.set_defaults(func=command_report)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
