#!/usr/bin/env python3
"""Springmaster write API contract gate report MVP.

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

SCHEMA_VERSION = "springmaster.write-api-contract-gate-report.v1"
MODE = "report-only"
PROJECT = "springmaster"
DEFAULT_OUT = "reports/api/write-api-contract-gate-report.json"

CATALOG_CONTROLLER = Path("src/main/java/de/cocondo/platform/demo/catalog/api/CatalogItemController.java")
CATALOG_SERVICE = Path("src/main/java/de/cocondo/platform/demo/catalog/CatalogItemService.java")
CATALOG_CONTROLLER_TEST = Path("src/test/java/de/cocondo/platform/demo/catalog/api/CatalogItemControllerTest.java")
CATALOG_OPENAPI_WRITE_TEST = Path("src/test/java/de/cocondo/platform/demo/catalog/api/CatalogItemOpenApiWriteContractTest.java")
ENDPOINT_STANDARD_DOC = Path("PROJECT_DOCS/STANDARDS/API/API_ENDPOINT_CONTRACT_STANDARD.md")
COMMAND_HTTP_DOC = Path("PROJECT_DOCS/STANDARDS/API/COMMAND_HTTP_STANDARD.md")
ERROR_CONTRACT_DOC = Path("PROJECT_DOCS/STANDARDS/API/API_ERROR_CONTRACT_STANDARD.md")
CORE_ERROR_DOC = Path("PROJECT_DOCS/CORE/CORE_GLOBAL_API_ERROR_CONTRACT.md")
WRITE_REPORT_DOC = Path("PROJECT_DOCS/STANDARDS/API/WRITE_API_CONTRACT_REPORT.md")


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


def full_operation(http_method: str, base: str, suffix: str) -> str:
    if not suffix:
        return f"{http_method} {base}"
    return f"{http_method} {base.rstrip('/')}/{suffix.strip('/')}"


def required_file_findings(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    for path in [
        CATALOG_CONTROLLER,
        CATALOG_SERVICE,
        CATALOG_CONTROLLER_TEST,
        CATALOG_OPENAPI_WRITE_TEST,
        ENDPOINT_STANDARD_DOC,
        COMMAND_HTTP_DOC,
        ERROR_CONTRACT_DOC,
        CORE_ERROR_DOC,
        WRITE_REPORT_DOC,
    ]:
        if not (root / path).is_file():
            findings.append(Finding(
                id="WRT-GATE-001",
                severity="error",
                resource="CatalogItem",
                operation="source-preflight",
                message=f"Required write-api-contract report input is missing: {path}",
                standard="WRITE_API_CONTRACT_REPORT.md",
                evidence={"file": str(path)},
            ))
    return findings


def classify_catalog(root: Path) -> tuple[dict[str, object], list[Finding]]:
    findings = required_file_findings(root)
    if findings:
        return {"resource": "CatalogItem", "status": "incomplete-input", "operations": []}, findings

    controller = read_text(root, CATALOG_CONTROLLER)
    service = read_text(root, CATALOG_SERVICE)
    controller_test = read_text(root, CATALOG_CONTROLLER_TEST)
    openapi_test = read_text(root, CATALOG_OPENAPI_WRITE_TEST)
    base = request_mapping_base(controller)

    create_block = method_block(controller, "PostMapping", "create")
    update_block = method_block(controller, "PutMapping", "update")
    delete_block = method_block(controller, "DeleteMapping", "delete")

    create_operation = full_operation("POST", base, mapping_path(create_block))
    update_path = mapping_path(update_block)
    delete_path = mapping_path(delete_block)
    update_operation = full_operation("PUT", base, update_path)
    delete_operation = full_operation("DELETE", base, delete_path)
    update_vars = path_variables(update_block)
    delete_vars = path_variables(delete_block)

    if mapping_path(create_block) != "":
        findings.append(Finding(
            "WRT-CREATE-001",
            "error",
            "CatalogItem",
            create_operation,
            "Create endpoint must use the collection root POST mapping.",
            "API_ENDPOINT_CONTRACT_STANDARD.md",
            {"file": str(CATALOG_CONTROLLER), "path": mapping_path(create_block)},
        ))
    if "@Valid @RequestBody CatalogItemCreateDTO" not in create_block:
        findings.append(Finding(
            "WRT-CREATE-002",
            "error",
            "CatalogItem",
            create_operation,
            "Create endpoint must use a validated CatalogItemCreateDTO request body.",
            "DTO_BOUNDARY_AND_VALIDATION_STANDARD.md",
            {"file": str(CATALOG_CONTROLLER), "symbol": "create"},
        ))
    if "ResponseEntity<CatalogItemDTO>" not in create_block or "ResponseEntity.created(location).body(created)" not in create_block:
        findings.append(Finding(
            "WRT-CREATE-003",
            "error",
            "CatalogItem",
            create_operation,
            "Create endpoint must return 201 Created with Location and CatalogItemDTO body evidence.",
            "API_ERROR_IDENTITY_STATUSCODE_CONSISTENCY_STANDARD.md",
            {"file": str(CATALOG_CONTROLLER), "symbol": "create"},
        ))
    if "/api/demo/catalog/items/" not in create_block or "UriUtils.encodePathSegment" not in create_block:
        findings.append(Finding(
            "WRT-CREATE-004",
            "warning",
            "CatalogItem",
            create_operation,
            "Create Location should point to the opaque-id detail endpoint and encode the id path segment.",
            "API_ENDPOINT_CONTRACT_STANDARD.md",
            {"file": str(CATALOG_CONTROLLER), "symbol": "location"},
        ))

    if update_path != "/{id}" or "id" not in update_vars:
        findings.append(Finding(
            "WRT-UPDATE-001",
            "error",
            "CatalogItem",
            update_operation,
            "Update endpoint must be PUT /{id} with path variable id.",
            "API_ENDPOINT_CONTRACT_STANDARD.md",
            {"file": str(CATALOG_CONTROLLER), "path": update_path or "missing", "pathVariables": ",".join(update_vars)},
        ))
    if "@Valid @RequestBody CatalogItemUpdateDTO" not in update_block:
        findings.append(Finding(
            "WRT-UPDATE-002",
            "error",
            "CatalogItem",
            update_operation,
            "Update endpoint must use a validated CatalogItemUpdateDTO request body.",
            "DTO_BOUNDARY_AND_VALIDATION_STANDARD.md",
            {"file": str(CATALOG_CONTROLLER), "symbol": "update"},
        ))
    if "CatalogItemDTO update" not in update_block or "service.update(id, request)" not in update_block:
        findings.append(Finding(
            "WRT-UPDATE-003",
            "warning",
            "CatalogItem",
            update_operation,
            "Update endpoint should return the updated CatalogItemDTO using 200 OK default semantics.",
            "API_ERROR_IDENTITY_STATUSCODE_CONSISTENCY_STANDARD.md",
            {"file": str(CATALOG_CONTROLLER), "symbol": "update"},
        ))

    if delete_path != "/{id}" or "id" not in delete_vars:
        findings.append(Finding(
            "WRT-DELETE-001",
            "error",
            "CatalogItem",
            delete_operation,
            "Delete endpoint must be DELETE /{id} with path variable id.",
            "API_ENDPOINT_CONTRACT_STANDARD.md",
            {"file": str(CATALOG_CONTROLLER), "path": delete_path or "missing", "pathVariables": ",".join(delete_vars)},
        ))
    if "@RequestBody" in delete_block:
        findings.append(Finding(
            "WRT-DELETE-002",
            "error",
            "CatalogItem",
            delete_operation,
            "Single-resource delete must be bodyless.",
            "COMMAND_HTTP_STANDARD.md",
            {"file": str(CATALOG_CONTROLLER), "symbol": "delete"},
        ))
    if "ResponseEntity<Void>" not in delete_block or "ResponseEntity.noContent().build()" not in delete_block:
        findings.append(Finding(
            "WRT-DELETE-003",
            "error",
            "CatalogItem",
            delete_operation,
            "Delete endpoint must return 204 No Content with no response body evidence.",
            "API_ERROR_IDENTITY_STATUSCODE_CONSISTENCY_STANDARD.md",
            {"file": str(CATALOG_CONTROLLER), "symbol": "delete"},
        ))

    if "EntityAlreadyExistsException" not in service or "catalog.item.conflict" not in service:
        findings.append(Finding(
            "WRT-CONFLICT-001",
            "error",
            "CatalogItem",
            create_operation,
            "Duplicate business key create must use the global CONFLICT contract with the CatalogItem conflict message key.",
            "CORE_GLOBAL_API_ERROR_CONTRACT.md",
            {"file": str(CATALOG_SERVICE), "symbol": "EntityAlreadyExistsException"},
        ))
    shared_not_found = (
            "private CatalogItem requireById(String id)" in service
            and service.count("CatalogItem item = requireById(id);") >= 2
            and "catalog.item.not-found" in service
    )
    if "ResourceNotFoundException" not in service or not shared_not_found:
        findings.append(Finding(
            "WRT-NOTFOUND-001",
            "error",
            "CatalogItem",
            "update/delete missing resource",
            "Unknown update/delete ids must use the global RESOURCE_NOT_FOUND contract with the CatalogItem not-found message key.",
            "CORE_GLOBAL_API_ERROR_CONTRACT.md",
            {"file": str(CATALOG_SERVICE), "symbol": "ResourceNotFoundException"},
        ))

    test_markers = {
        "createsCatalogItemWithOpaqueIdLocation": "create 201 Location MockMvc evidence",
        "updatesCatalogItemByOpaqueId": "update 200 MockMvc evidence",
        "deletesCatalogItemByOpaqueIdBodylessly": "delete 204 bodyless MockMvc evidence",
        "returnsBadRequestForInvalidPayloadWithViolations": "create 400 validation evidence",
        "returnsBadRequestForInvalidUpdatePayload": "update 400 validation evidence",
        "returnsConflictForDuplicateSkuWithStandardErrorBody": "create duplicate 409 evidence",
        "createLocationCanBeUsedForDetailLookup": "create Location to detail follow-up evidence",
    }
    for marker, label in test_markers.items():
        if marker not in controller_test:
            findings.append(Finding(
                "WRT-TEST-001",
                "warning",
                "CatalogItem",
                label,
                "CatalogItem MockMvc write evidence marker is missing.",
                "WRITE_API_CONTRACT_REPORT.md",
                {"file": str(CATALOG_CONTROLLER_TEST), "marker": marker},
            ))
    if "CatalogItemOpenApiWriteContractTest" not in openapi_test or "assertNoDeleteRequestBody" not in openapi_test:
        findings.append(Finding(
            "WRT-OPENAPI-001",
            "warning",
            "CatalogItem",
            "OpenAPI write evidence",
            "OpenAPI write contract evidence test is missing required markers.",
            "WRITE_API_CONTRACT_REPORT.md",
            {"file": str(CATALOG_OPENAPI_WRITE_TEST)},
        ))

    if "CatalogItem" in create_block and "CatalogItemDTO" not in create_block + update_block:
        findings.append(Finding(
            "WRT-DTO-001",
            "error",
            "CatalogItem",
            "write DTO boundary",
            "Write endpoints must not expose persistence entities as public request/response body types.",
            "DTO_BOUNDARY_AND_VALIDATION_STANDARD.md",
            {"file": str(CATALOG_CONTROLLER)},
        ))

    status = "pass" if not findings else "review"
    resource = {
        "resource": "CatalogItem",
        "status": status,
        "sourceType": "springmaster-candidate-reference-slice",
        "operations": [
            {
                "kind": "create",
                "operation": create_operation,
                "requestBody": "CatalogItemCreateDTO",
                "validation": "@Valid",
                "success": {
                    "status": 201,
                    "location": "/api/demo/catalog/items/{id}",
                    "response": "CatalogItemDTO",
                },
                "conflict": {
                    "status": 409,
                    "errorType": "CONFLICT",
                    "messageKey": "catalog.item.conflict",
                },
                "validationError": {
                    "status": 400,
                    "errorType": "VALIDATION_FAILED",
                    "messageKey": "springmaster.validation.failed",
                },
            },
            {
                "kind": "update",
                "operation": update_operation,
                "pathVariables": update_vars,
                "requestBody": "CatalogItemUpdateDTO",
                "validation": "@Valid",
                "success": {
                    "status": 200,
                    "response": "CatalogItemDTO",
                },
                "notFound": {
                    "status": 404,
                    "errorType": "RESOURCE_NOT_FOUND",
                    "messageKey": "catalog.item.not-found",
                },
                "validationError": {
                    "status": 400,
                    "errorType": "VALIDATION_FAILED",
                    "messageKey": "springmaster.validation.failed",
                },
            },
            {
                "kind": "delete",
                "operation": delete_operation,
                "pathVariables": delete_vars,
                "requestBody": "absent",
                "success": {
                    "status": 204,
                    "responseBody": "absent",
                },
                "notFound": {
                    "status": 404,
                    "errorType": "RESOURCE_NOT_FOUND",
                    "messageKey": "catalog.item.not-found",
                },
            },
        ],
        "serviceEvidence": {
            "create": "present",
            "update": "present",
            "delete": "present",
            "duplicateBusinessKeyConflict": "EntityAlreadyExistsException",
            "missingResource": "ResourceNotFoundException",
        },
        "globalErrorContract": "present",
        "mockMvcEvidence": "present",
        "openApiEvidence": "present",
        "deleteRequestBody": "absent",
        "createLocationDetailConsistency": "present",
        "publicVocabulary": {
            "bodyBearingDelete": "absent",
            "bulkCommandCoverage": "deferred",
            "stateCommandCoverage": "deferred",
            "relationshipCommandCoverage": "deferred",
        },
    }
    return resource, findings


def build_report(root: Path, generated_at: str) -> dict[str, object]:
    resource, findings = classify_catalog(root)
    finding_objects = [finding.to_json() for finding in findings]
    return {
        "schemaVersion": SCHEMA_VERSION,
        "generatedAt": generated_at,
        "project": PROJECT,
        "mode": MODE,
        "source": {
            "javaSources": "src/main/java",
            "tests": "src/test/java",
            "standards": "PROJECT_DOCS/STANDARDS/API",
        },
        "summary": {
            "resources": 1,
            "findings": len(finding_objects),
            "errors": sum(1 for finding in findings if finding.severity == "error"),
            "warnings": sum(1 for finding in findings if finding.severity == "warning"),
            "info": sum(1 for finding in findings if finding.severity == "info"),
        },
        "resources": [resource],
        "findings": finding_objects,
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate Springmaster write API contract report.")
    parser.add_argument("--root", default=None, help="Project root. Defaults to the repository root derived from this script.")
    parser.add_argument("--out", default=DEFAULT_OUT, help=f"Output file. Defaults to {DEFAULT_OUT}.")
    parser.add_argument("--generated-at", default=None, help="Stable generatedAt timestamp for tests/fixtures.")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    root = Path(args.root).resolve() if args.root else repo_root()
    generated_at = args.generated_at or datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    report = build_report(root, generated_at)
    out = Path(args.out)
    if not out.is_absolute():
        out = root / out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Write API contract report written: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
