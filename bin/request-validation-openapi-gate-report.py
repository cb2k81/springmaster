#!/usr/bin/env python3
"""Springmaster request-validation/OpenAPI gate report MVP.

The report is intentionally source-based and report-only. It captures the
current CatalogItem candidate reference for Bean Validation, request DTO
boundaries and OpenAPI-required field evidence without promoting strict gate
failure semantics.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

SCHEMA_VERSION = "springmaster.request-validation-openapi-gate-report.v1"
MODE = "report-only"
PROJECT = "springmaster"
DEFAULT_OUT = "reports/api/request-validation-openapi-gate-report.json"

CATALOG_CONTROLLER = Path("src/main/java/de/cocondo/platform/demo/catalog/api/CatalogItemController.java")
CATALOG_CREATE_DTO = Path("src/main/java/de/cocondo/platform/demo/catalog/CatalogItemCreateDTO.java")
CATALOG_UPDATE_DTO = Path("src/main/java/de/cocondo/platform/demo/catalog/CatalogItemUpdateDTO.java")
CATALOG_ENTITY = Path("src/main/java/de/cocondo/platform/demo/catalog/CatalogItem.java")
CATALOG_CONTROLLER_TEST = Path("src/test/java/de/cocondo/platform/demo/catalog/api/CatalogItemControllerTest.java")
CATALOG_OPENAPI_VALIDATION_TEST = Path("src/test/java/de/cocondo/platform/demo/catalog/api/CatalogItemOpenApiRequestValidationContractTest.java")
VALIDATION_STANDARD_DOC = Path("PROJECT_DOCS/STANDARDS/API/API_REQUEST_VALIDATION_STANDARD.md")
DTO_STANDARD_DOC = Path("PROJECT_DOCS/STANDARDS/API/DTO_BOUNDARY_AND_VALIDATION_STANDARD.md")
CORE_ERROR_DOC = Path("PROJECT_DOCS/CORE/CORE_GLOBAL_API_ERROR_CONTRACT.md")
REPORT_DOC = Path("PROJECT_DOCS/STANDARDS/API/REQUEST_VALIDATION_OPENAPI_GATE.md")


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


def full_operation(http_method: str, base: str, suffix: str) -> str:
    if not suffix:
        return f"{http_method} {base}"
    return f"{http_method} {base.rstrip('/')}/{suffix.strip('/')}"


def field_block(dto_text: str, field_name: str) -> str:
    field_idx = dto_text.find(f" {field_name};")
    if field_idx < 0:
        return ""
    previous_field = max(dto_text.rfind("private ", 0, field_idx - 1), dto_text.rfind("public ", 0, field_idx - 1))
    # Prefer the previous blank line after a method/field. This source-based MVP is intentionally compact.
    start = dto_text.rfind("\n\n", 0, field_idx)
    if start < 0:
        start = previous_field if previous_field >= 0 else 0
    return dto_text[start:field_idx + len(field_name) + 2]


def required_fields(dto_text: str) -> list[str]:
    fields: list[str] = []
    pattern = re.compile(r"((?:\s*@(?:NotBlank|NotNull|NotEmpty)[^\n]*\n|\s*@Size[^\n]*\n|\s*@Valid[^\n]*\n)*)\s*private\s+[^;]+\s+(\w+)\s*;", re.MULTILINE)
    for match in pattern.finditer(dto_text):
        annotations = match.group(1)
        field = match.group(2)
        if any(token in annotations for token in ("@NotBlank", "@NotNull", "@NotEmpty")):
            fields.append(field)
    return sorted(fields)


def size_limits(dto_text: str) -> dict[str, int]:
    limits: dict[str, int] = {}
    pattern = re.compile(r"((?:\s*@[^\n]+\n)+)\s*private\s+String\s+(\w+)\s*;", re.MULTILINE)
    for match in pattern.finditer(dto_text):
        annotations = match.group(1)
        field = match.group(2)
        size = re.search(r"@Size\s*\([^)]*max\s*=\s*(\d+)", annotations)
        if size:
            limits[field] = int(size.group(1))
    return dict(sorted(limits.items()))


def request_body_type(block: str) -> str:
    match = re.search(r"@RequestBody\s+([A-Za-z0-9_<>]+)\s+\w+", block)
    if match:
        return match.group(1)
    match = re.search(r"@Valid\s+@RequestBody\s+([A-Za-z0-9_<>]+)\s+\w+", block)
    return match.group(1) if match else ""


def required_file_findings(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    for path in [
        CATALOG_CONTROLLER,
        CATALOG_CREATE_DTO,
        CATALOG_UPDATE_DTO,
        CATALOG_ENTITY,
        CATALOG_CONTROLLER_TEST,
        CATALOG_OPENAPI_VALIDATION_TEST,
        VALIDATION_STANDARD_DOC,
        DTO_STANDARD_DOC,
        CORE_ERROR_DOC,
        REPORT_DOC,
    ]:
        if not (root / path).is_file():
            findings.append(Finding(
                id="VAL-GATE-001",
                severity="error",
                resource="CatalogItem",
                operation="source-preflight",
                message=f"Required request-validation/OpenAPI gate report input is missing: {path}",
                standard="REQUEST_VALIDATION_OPENAPI_GATE.md",
                evidence={"file": str(path)},
            ))
    return findings


def classify_catalog(root: Path) -> tuple[dict[str, object], list[Finding]]:
    findings = required_file_findings(root)
    if findings:
        return {"resource": "CatalogItem", "status": "incomplete-input", "operations": []}, findings

    controller = read_text(root, CATALOG_CONTROLLER)
    create_dto = read_text(root, CATALOG_CREATE_DTO)
    update_dto = read_text(root, CATALOG_UPDATE_DTO)
    entity = read_text(root, CATALOG_ENTITY)
    controller_test = read_text(root, CATALOG_CONTROLLER_TEST)
    openapi_test = read_text(root, CATALOG_OPENAPI_VALIDATION_TEST)
    base = request_mapping_base(controller)

    create_block = method_block(controller, "PostMapping", "create")
    update_block = method_block(controller, "PutMapping", "update")
    create_operation = full_operation("POST", base, mapping_path(create_block))
    update_operation = full_operation("PUT", base, mapping_path(update_block))

    if "@Valid @RequestBody CatalogItemCreateDTO" not in create_block:
        findings.append(Finding(
            "VAL-BOUNDARY-001",
            "error",
            "CatalogItem",
            create_operation,
            "Create endpoint must use @Valid @RequestBody CatalogItemCreateDTO.",
            "REQUEST_VALIDATION_OPENAPI_GATE.md",
            {"file": str(CATALOG_CONTROLLER), "symbol": "create"},
        ))
    if "@Valid @RequestBody CatalogItemUpdateDTO" not in update_block:
        findings.append(Finding(
            "VAL-BOUNDARY-002",
            "error",
            "CatalogItem",
            update_operation,
            "Update endpoint must use @Valid @RequestBody CatalogItemUpdateDTO.",
            "REQUEST_VALIDATION_OPENAPI_GATE.md",
            {"file": str(CATALOG_CONTROLLER), "symbol": "update"},
        ))
    if "@RequestBody CatalogItem " in controller or "@RequestBody DomainEntity" in controller:
        findings.append(Finding(
            "VAL-BOUNDARY-003",
            "error",
            "CatalogItem",
            "request-body-boundary",
            "Controller must not expose a domain entity as request body.",
            "DTO_BOUNDARY_AND_VALIDATION_STANDARD.md",
            {"file": str(CATALOG_CONTROLLER)},
        ))

    create_required = required_fields(create_dto)
    update_required = required_fields(update_dto)
    if create_required != ["name", "sku"]:
        findings.append(Finding(
            "VAL-REQUIRED-001",
            "error",
            "CatalogItem",
            "CatalogItemCreateDTO",
            "CreateDTO Bean Validation required fields must be exactly name and sku.",
            "API_REQUEST_VALIDATION_STANDARD.md",
            {"actual": ",".join(create_required)},
        ))
    if update_required != ["name"]:
        findings.append(Finding(
            "VAL-REQUIRED-001",
            "error",
            "CatalogItem",
            "CatalogItemUpdateDTO",
            "UpdateDTO Bean Validation required fields must be exactly name.",
            "API_REQUEST_VALIDATION_STANDARD.md",
            {"actual": ",".join(update_required)},
        ))
    if "extends DomainEntity" not in entity:
        findings.append(Finding(
            "VAL-BOUNDARY-003",
            "warning",
            "CatalogItem",
            "entity-reference",
            "CatalogItem entity marker could not be confirmed; DTO-boundary check may be incomplete.",
            "DTO_BOUNDARY_AND_VALIDATION_STANDARD.md",
            {"file": str(CATALOG_ENTITY)},
        ))
    if "returnsBadRequestForInvalidPayloadWithViolations" not in controller_test or "returnsBadRequestForInvalidUpdatePayload" not in controller_test:
        findings.append(Finding(
            "VAL-RUNTIME-001",
            "error",
            "CatalogItem",
            "runtime-validation",
            "MockMvc runtime evidence for create/update VALIDATION_FAILED responses is missing.",
            "CORE_GLOBAL_API_ERROR_CONTRACT.md",
            {"file": str(CATALOG_CONTROLLER_TEST)},
        ))
    for token in [
        "CatalogItemCreateDTO",
        "CatalogItemUpdateDTO",
        "assertRequiredFields",
        "assertMaxLength",
        "assertRequestBodySchemaName",
    ]:
        if token not in openapi_test:
            findings.append(Finding(
                "VAL-OPENAPI-001",
                "error",
                "CatalogItem",
                "openapi-validation",
                "OpenAPI request-validation evidence test is missing required-field or boundary assertions.",
                "REQUEST_VALIDATION_OPENAPI_GATE.md",
                {"file": str(CATALOG_OPENAPI_VALIDATION_TEST), "token": token},
            ))

    resource = {
        "resource": "CatalogItem",
        "status": "aligned" if not findings else "findings-present",
        "operations": [create_operation, update_operation],
        "requestBodies": [
            {
                "operation": create_operation,
                "requestDto": request_body_type(create_block),
                "validAnnotation": "present" if "@Valid @RequestBody" in create_block else "missing",
                "requiredFields": create_required,
                "stringSizeLimits": size_limits(create_dto),
                "openApiRequiredEvidence": "CatalogItemOpenApiRequestValidationContractTest",
            },
            {
                "operation": update_operation,
                "requestDto": request_body_type(update_block),
                "validAnnotation": "present" if "@Valid @RequestBody" in update_block else "missing",
                "requiredFields": update_required,
                "stringSizeLimits": size_limits(update_dto),
                "openApiRequiredEvidence": "CatalogItemOpenApiRequestValidationContractTest",
            },
        ],
        "boundary": {
            "domainEntityRequestBody": "absent",
            "createDtoImplementsDataTransferObject": "DataTransferObject" in create_dto,
            "updateDtoImplementsDataTransferObject": "DataTransferObject" in update_dto,
        },
        "runtimeErrorContract": {
            "status": 400,
            "errorType": "VALIDATION_FAILED",
            "messageKey": "springmaster.validation.failed",
            "mockMvcEvidence": "CatalogItemControllerTest",
        },
    }
    return resource, findings


def generate_report(root: Path, generated_at: str) -> dict[str, object]:
    resource, findings = classify_catalog(root)
    return {
        "schemaVersion": SCHEMA_VERSION,
        "generatedAt": generated_at,
        "mode": MODE,
        "project": PROJECT,
        "summary": {
            "resources": 1,
            "findings": len(findings),
            "errors": sum(1 for finding in findings if finding.severity == "error"),
            "warnings": sum(1 for finding in findings if finding.severity == "warning"),
        },
        "resources": [resource],
        "findings": [finding.to_json() for finding in findings],
        "standards": [
            str(VALIDATION_STANDARD_DOC),
            str(DTO_STANDARD_DOC),
            str(CORE_ERROR_DOC),
            str(REPORT_DOC),
        ],
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate Springmaster request-validation/OpenAPI gate report.")
    parser.add_argument("--out", default=DEFAULT_OUT, help="Output JSON path")
    parser.add_argument("--generated-at", default=None, help="Fixed generatedAt timestamp for tests")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    generated_at = args.generated_at or datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    root = repo_root()
    report = generate_report(root, generated_at)
    out = root / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    print(f"Request Validation/OpenAPI gate report written: {out}")
    print(f"Findings: {report['summary']['findings']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
