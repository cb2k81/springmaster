#!/usr/bin/env python3
"""Springmaster detail/lookup contract gate report MVP.

The report is intentionally source-based and report-only. It proves the
machine-readable contract for the current Springmaster CatalogItem candidate
reference slice without promoting strict build-failure semantics.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

SCHEMA_VERSION = "springmaster.detail-lookup-contract-gate-report.v1"
MODE = "report-only"
PROJECT = "springmaster"
DEFAULT_OUT = "reports/api/detail-lookup-contract-gate-report.json"

CATALOG_CONTROLLER = Path("src/main/java/de/cocondo/platform/demo/catalog/api/CatalogItemController.java")
CATALOG_SERVICE = Path("src/main/java/de/cocondo/platform/demo/catalog/CatalogItemService.java")
CATALOG_REPOSITORY = Path("src/main/java/de/cocondo/platform/demo/catalog/CatalogItemRepository.java")
CATALOG_CONTROLLER_TEST = Path("src/test/java/de/cocondo/platform/demo/catalog/api/CatalogItemControllerTest.java")
CATALOG_OPENAPI_DETAIL_TEST = Path("src/test/java/de/cocondo/platform/demo/catalog/api/CatalogItemOpenApiDetailLookupContractTest.java")
ENDPOINT_STANDARD_DOC = Path("PROJECT_DOCS/STANDARDS/API/API_ENDPOINT_CONTRACT_STANDARD.md")
ERROR_CONTRACT_DOC = Path("PROJECT_DOCS/STANDARDS/API/API_ERROR_CONTRACT_STANDARD.md")
CORE_ERROR_DOC = Path("PROJECT_DOCS/CORE/CORE_GLOBAL_API_ERROR_CONTRACT.md")
DETAIL_REPORT_DOC = Path("PROJECT_DOCS/STANDARDS/API/DETAIL_LOOKUP_CONTRACT_REPORT.md")


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


def path_variables(block: str) -> list[str]:
    names: set[str] = set()
    for match in re.finditer(r"@PathVariable\s*\(([^)]*)\)", block, re.DOTALL):
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
    for path in [
        CATALOG_CONTROLLER,
        CATALOG_SERVICE,
        CATALOG_REPOSITORY,
        CATALOG_CONTROLLER_TEST,
        CATALOG_OPENAPI_DETAIL_TEST,
        ENDPOINT_STANDARD_DOC,
        ERROR_CONTRACT_DOC,
        CORE_ERROR_DOC,
        DETAIL_REPORT_DOC,
    ]:
        if not (root / path).is_file():
            findings.append(Finding(
                id="DTL-GATE-001",
                severity="error",
                resource="CatalogItem",
                operation="source-preflight",
                message=f"Required detail/lookup-contract report input is missing: {path}",
                standard="DETAIL_LOOKUP_CONTRACT_REPORT.md",
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
    repository = read_text(root, CATALOG_REPOSITORY)
    controller_test = read_text(root, CATALOG_CONTROLLER_TEST)
    openapi_test = read_text(root, CATALOG_OPENAPI_DETAIL_TEST)
    base = request_mapping_base(controller)

    detail_block = method_block(controller, "GetMapping", "findById")
    sku_block = method_block(controller, "GetMapping", "findBySku")

    detail_path = mapping_path(detail_block)
    sku_path = mapping_path(sku_block)
    detail_operation = full_operation(base, detail_path)
    sku_operation = full_operation(base, sku_path)
    detail_vars = path_variables(detail_block)
    sku_vars = path_variables(sku_block)

    if detail_path != "/{id}" or "id" not in detail_vars:
        findings.append(Finding(
            "DTL-DETAIL-001",
            "error",
            "CatalogItem",
            detail_operation,
            "Opaque-id detail endpoint must be GET /{id} with path variable id.",
            "API_ENDPOINT_CONTRACT_STANDARD.md",
            {"file": str(CATALOG_CONTROLLER), "path": detail_path or "missing", "pathVariables": ",".join(detail_vars)},
        ))
    if "ResponseEntity<CatalogItemDTO>" not in detail_block:
        findings.append(Finding(
            "DTL-DETAIL-002",
            "warning",
            "CatalogItem",
            detail_operation,
            "Detail endpoint should return CatalogItemDTO through ResponseEntity evidence.",
            "API_ENDPOINT_CONTRACT_STANDARD.md",
            {"file": str(CATALOG_CONTROLLER), "symbol": "findById"},
        ))
    if "ResourceNotFoundException" not in detail_block or "catalog.item.not-found" not in detail_block:
        findings.append(Finding(
            "DTL-NOTFOUND-001",
            "error",
            "CatalogItem",
            detail_operation,
            "Unknown detail id must use the global RESOURCE_NOT_FOUND contract with the CatalogItem not-found message key.",
            "CORE_GLOBAL_API_ERROR_CONTRACT.md",
            {"file": str(CATALOG_CONTROLLER), "symbol": "findById"},
        ))

    if sku_path != "/by-sku/{sku}" or "sku" not in sku_vars:
        findings.append(Finding(
            "DTL-LOOKUP-001",
            "error",
            "CatalogItem",
            sku_operation,
            "Alternate-key lookup endpoint must be GET /by-sku/{sku} with path variable sku.",
            "API_ENDPOINT_CONTRACT_STANDARD.md",
            {"file": str(CATALOG_CONTROLLER), "path": sku_path or "missing", "pathVariables": ",".join(sku_vars)},
        ))
    if "ResponseEntity<CatalogItemDTO>" not in sku_block:
        findings.append(Finding(
            "DTL-LOOKUP-002",
            "warning",
            "CatalogItem",
            sku_operation,
            "Alternate-key lookup should return CatalogItemDTO through ResponseEntity evidence.",
            "API_ENDPOINT_CONTRACT_STANDARD.md",
            {"file": str(CATALOG_CONTROLLER), "symbol": "findBySku"},
        ))
    if "ResourceNotFoundException" not in sku_block or "catalog.item.not-found" not in sku_block:
        findings.append(Finding(
            "DTL-NOTFOUND-001",
            "error",
            "CatalogItem",
            sku_operation,
            "Unknown alternate key must use the global RESOURCE_NOT_FOUND contract with the CatalogItem not-found message key.",
            "CORE_GLOBAL_API_ERROR_CONTRACT.md",
            {"file": str(CATALOG_CONTROLLER), "symbol": "findBySku"},
        ))

    if "Optional<CatalogItemDTO> findById(String id)" not in service:
        findings.append(Finding(
            "DTL-SERVICE-001",
            "error",
            "CatalogItem",
            "service findById",
            "Service detail lookup must expose Optional<CatalogItemDTO> findById(String id).",
            "API_ENDPOINT_CONTRACT_STANDARD.md",
            {"file": str(CATALOG_SERVICE), "symbol": "findById"},
        ))
    repository_lookup = "Optional<CatalogItem> findBySkuIgnoreCase(String sku)" in repository
    service_uses_repository_lookup = "repository.findBySkuIgnoreCase" in service
    if (
            "Optional<CatalogItemDTO> findBySku(String sku)" not in service
            or not repository_lookup
            or not service_uses_repository_lookup
    ):
        findings.append(Finding(
            "DTL-SERVICE-002",
            "error",
            "CatalogItem",
            "service findBySku",
            "Service alternate-key lookup must expose Optional<CatalogItemDTO> findBySku(String sku) backed by the case-insensitive repository lookup.",
            "API_ENDPOINT_CONTRACT_STANDARD.md",
            {"file": str(CATALOG_REPOSITORY), "symbol": "findBySkuIgnoreCase"},
        ))

    test_markers = {
        "findsCatalogItemByOpaqueId": "detail positive MockMvc evidence",
        "findsCatalogItemBySkuCaseInsensitivelyThroughBusinessKeyLookup": "alternate-key positive MockMvc evidence",
        "returnsNotFoundErrorBodyForUnknownId": "detail 404 global error evidence",
        "returnsNotFoundErrorBodyForUnknownSku": "alternate-key 404 global error evidence",
        "createLocationCanBeUsedForDetailLookup": "create Location to detail lookup evidence",
    }
    for marker, label in test_markers.items():
        if marker not in controller_test:
            findings.append(Finding(
                "DTL-MOCKMVC-001",
                "warning",
                "CatalogItem",
                "MockMvc evidence",
                f"Missing {label} test marker: {marker}.",
                "DETAIL_LOOKUP_CONTRACT_REPORT.md",
                {"file": str(CATALOG_CONTROLLER_TEST), "symbol": marker},
            ))

    if "DETAIL_PATH" not in openapi_test or "BY_SKU_PATH" not in openapi_test:
        findings.append(Finding(
            "DTL-OPENAPI-001",
            "warning",
            "CatalogItem",
            "OpenAPI evidence",
            "OpenAPI detail/lookup test must explicitly cover detail and by-sku paths.",
            "DETAIL_LOOKUP_CONTRACT_REPORT.md",
            {"file": str(CATALOG_OPENAPI_DETAIL_TEST)},
        ))

    status = "pass" if not findings else "review"
    resource = {
        "resource": "CatalogItem",
        "status": status,
        "sourceType": "springmaster-candidate-reference-slice",
        "operations": [
            {
                "kind": "detail",
                "operation": detail_operation,
                "pathVariables": detail_vars,
                "lookupSemantics": "opaque-external-id",
                "response": "CatalogItemDTO" if "CatalogItemDTO" in detail_block else "unknown",
                "notFound": {
                    "status": 404,
                    "errorType": "RESOURCE_NOT_FOUND",
                    "messageKey": "catalog.item.not-found",
                },
            },
            {
                "kind": "alternate-key-lookup",
                "operation": sku_operation,
                "pathVariables": sku_vars,
                "lookupSemantics": "unique-business-key",
                "businessKey": "sku",
                "response": "CatalogItemDTO" if "CatalogItemDTO" in sku_block else "unknown",
                "notFound": {
                    "status": 404,
                    "errorType": "RESOURCE_NOT_FOUND",
                    "messageKey": "catalog.item.not-found",
                },
            },
        ],
        "serviceEvidence": {
            "findById": "present" if "Optional<CatalogItemDTO> findById(String id)" in service else "missing",
            "findBySku": "present" if "Optional<CatalogItemDTO> findBySku(String sku)" in service else "missing",
            "alternateKeyUniquenessIndex": "repository.findBySkuIgnoreCase"
            if repository_lookup and service_uses_repository_lookup else "missing",
        },
        "globalErrorContract": "present" if "ResourceNotFoundException" in controller else "missing",
        "mockMvcEvidence": "present",
        "openApiEvidence": "present" if "DETAIL_PATH" in openapi_test and "BY_SKU_PATH" in openapi_test else "missing",
        "createLocationDetailConsistency": "present" if "createLocationCanBeUsedForDetailLookup" in controller_test else "missing",
        "publicVocabulary": {
            "forbiddenFindOneFindFirstFindAny": "absent" if not re.search(r"findOne|findFirst|findAny", controller) else "review",
            "controllerMethodNames": ["findById", "findBySku"],
        },
    }
    return resource, findings


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
    print("Springmaster detail/lookup contract report: SUCCESS")
    print(f"  Schema:   {report['schemaVersion']}")
    print(f"  Mode:     {report['mode']}")
    print(f"  Resources:{report['summary']['resources']}")
    print(f"  Findings: {report['summary']['findings']}")
    print(f"  Report:   {args.out}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Springmaster detail/lookup contract gate report MVP")
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
