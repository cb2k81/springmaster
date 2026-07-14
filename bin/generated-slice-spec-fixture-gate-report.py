#!/usr/bin/env python3
"""Validate the Springmaster GeneratedServiceSlice golden YAML fixture.

The tool intentionally uses only the Python standard library. It parses the
strict YAML subset documented by GENERATED_SLICE_SPEC_FIXTURE_GATE.md and
fails closed for unsupported YAML features. The gate is fixture-focused: it
proves the executable contract before an intermediate representation or
patch-blueprint generator is introduced.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "springmaster.generated-slice-spec-fixture-gate-report.v1"
MODE = "strict-fixture-gate"
PROJECT = "springmaster"
DEFAULT_SPEC = "PROJECT_DOCS/TOOLING/GENERATED_SLICE_SPEC_GOLDEN_BUSINESS_PARTNER.yaml"
DEFAULT_OUT = "reports/tooling/generated-slice-spec-fixture-gate-report.json"
CONTRACT_DOC = "PROJECT_DOCS/TOOLING/GENERATED_SLICE_SPEC_CONTRACT.md"

REQUIRED_TOP_LEVEL = [
    "specVersion",
    "kind",
    "metadata",
    "packageModel",
    "resource",
    "apiSurface",
    "model",
    "validation",
    "errorContract",
    "reports",
    "delivery",
]
REQUIRED_ERROR_TYPES = [
    "VALIDATION_FAILED",
    "INVALID_REQUEST",
    "RESOURCE_NOT_FOUND",
    "CONFLICT",
    "INTERNAL_ERROR",
]
REQUIRED_REPORTS = [
    "queryContract",
    "detailLookupContract",
    "writeApiContract",
    "requestValidationOpenApiGate",
]
EXPECTED_STATUS_MAPPINGS = {
    400: ["VALIDATION_FAILED", "INVALID_REQUEST"],
    404: ["RESOURCE_NOT_FOUND"],
    409: ["CONFLICT"],
}
CHECK_DEFINITIONS = [
    ("SPEC-PARSE", "Strict YAML subset parsing"),
    ("SPEC-TOPLEVEL", "Required top-level contract fields"),
    ("SPEC-METADATA", "Slice metadata"),
    ("SPEC-PACKAGE", "Neutral package boundary"),
    ("SPEC-RESOURCE", "Resource identity and business keys"),
    ("SPEC-QUERY", "List, all and count query surface"),
    ("SPEC-DETAIL", "Detail and alternate lookup surface"),
    ("SPEC-WRITE", "Create, update and delete surface"),
    ("SPEC-DTO", "DTO boundary and field validation metadata"),
    ("SPEC-ERROR", "Global error contract and status families"),
    ("SPEC-REPORTS", "Required evidence report families"),
    ("SPEC-DELIVERY", "Patch-only target delivery boundary"),
]


class YamlSubsetError(ValueError):
    """Raised for invalid or unsupported YAML subset input."""


@dataclass(frozen=True)
class YamlLine:
    number: int
    indent: int
    content: str


@dataclass(frozen=True)
class Finding:
    id: str
    checkId: str
    path: str
    message: str
    expected: Any
    actual: Any

    def to_json(self) -> dict[str, Any]:
        return asdict(self)


class StrictYamlSubsetParser:
    """Small deterministic parser for the documented Slice-Spec YAML subset.

    Supported constructs:
    * indentation-based mappings and sequences;
    * scalar strings, quoted strings, booleans, null and integers;
    * sequence items containing scalars or mappings.

    Unsupported constructs such as anchors, aliases, tags, flow collections,
    block scalars and tab indentation are rejected instead of guessed.
    """

    _KEY_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_-]*$")
    _INT_RE = re.compile(r"^-?(?:0|[1-9][0-9]*)$")

    def __init__(self, text: str):
        self.lines = self._tokenize(text)

    def parse(self) -> Any:
        if not self.lines:
            raise YamlSubsetError("YAML document is empty")
        if self.lines[0].indent != 0:
            raise YamlSubsetError(f"line {self.lines[0].number}: root indentation must be zero")
        value, index = self._parse_block(0, 0)
        if index != len(self.lines):
            line = self.lines[index]
            raise YamlSubsetError(f"line {line.number}: unexpected trailing content")
        return value

    def _tokenize(self, text: str) -> list[YamlLine]:
        result: list[YamlLine] = []
        for number, raw in enumerate(text.splitlines(), start=1):
            if "\t" in raw[: len(raw) - len(raw.lstrip(" \t"))]:
                raise YamlSubsetError(f"line {number}: tab indentation is not supported")
            stripped = raw.strip()
            if not stripped or stripped.startswith("#"):
                continue
            indent = len(raw) - len(raw.lstrip(" "))
            if indent % 2 != 0:
                raise YamlSubsetError(f"line {number}: indentation must use multiples of two spaces")
            content = raw[indent:].rstrip()
            if content.startswith(("---", "...", "&", "*", "!", "|", ">")):
                raise YamlSubsetError(f"line {number}: unsupported YAML feature")
            result.append(YamlLine(number, indent, content))
        return result

    def _parse_block(self, index: int, indent: int) -> tuple[Any, int]:
        if index >= len(self.lines):
            raise YamlSubsetError("unexpected end of document")
        line = self.lines[index]
        if line.indent != indent:
            raise YamlSubsetError(
                f"line {line.number}: expected indentation {indent}, got {line.indent}"
            )
        if line.content.startswith("- ") or line.content == "-":
            return self._parse_sequence(index, indent)
        return self._parse_mapping(index, indent)

    def _parse_mapping(self, index: int, indent: int) -> tuple[dict[str, Any], int]:
        result: dict[str, Any] = {}
        while index < len(self.lines):
            line = self.lines[index]
            if line.indent < indent:
                break
            if line.indent > indent:
                raise YamlSubsetError(f"line {line.number}: unexpected indentation")
            if line.content.startswith("- ") or line.content == "-":
                break
            key, tail = self._split_mapping_entry(line)
            if key in result:
                raise YamlSubsetError(f"line {line.number}: duplicate mapping key {key!r}")
            index += 1
            if tail == "":
                if index >= len(self.lines) or self.lines[index].indent <= indent:
                    raise YamlSubsetError(f"line {line.number}: key {key!r} requires a nested value")
                if self.lines[index].indent != indent + 2:
                    raise YamlSubsetError(
                        f"line {self.lines[index].number}: nested value for {key!r} must be indented by two spaces"
                    )
                value, index = self._parse_block(index, indent + 2)
            else:
                value = self._parse_scalar(tail, line.number)
            result[key] = value
        return result, index

    def _parse_sequence(self, index: int, indent: int) -> tuple[list[Any], int]:
        result: list[Any] = []
        while index < len(self.lines):
            line = self.lines[index]
            if line.indent < indent:
                break
            if line.indent != indent or not (line.content.startswith("- ") or line.content == "-"):
                break
            tail = line.content[1:].strip()
            index += 1
            if tail == "":
                if index >= len(self.lines) or self.lines[index].indent != indent + 2:
                    raise YamlSubsetError(f"line {line.number}: sequence item requires a nested value")
                value, index = self._parse_block(index, indent + 2)
                result.append(value)
                continue
            if self._looks_like_mapping_entry(tail):
                item: dict[str, Any] = {}
                key, value_tail = self._split_inline_mapping_entry(tail, line.number)
                if value_tail == "":
                    if index >= len(self.lines) or self.lines[index].indent != indent + 4:
                        raise YamlSubsetError(
                            f"line {line.number}: sequence mapping key {key!r} requires a nested value"
                        )
                    value, index = self._parse_block(index, indent + 4)
                else:
                    value = self._parse_scalar(value_tail, line.number)
                item[key] = value
                while index < len(self.lines) and self.lines[index].indent == indent + 2:
                    continuation = self.lines[index]
                    if continuation.content.startswith("- ") or continuation.content == "-":
                        break
                    continuation_key, continuation_tail = self._split_mapping_entry(continuation)
                    if continuation_key in item:
                        raise YamlSubsetError(
                            f"line {continuation.number}: duplicate mapping key {continuation_key!r}"
                        )
                    index += 1
                    if continuation_tail == "":
                        if index >= len(self.lines) or self.lines[index].indent != indent + 4:
                            raise YamlSubsetError(
                                f"line {continuation.number}: key {continuation_key!r} requires a nested value"
                            )
                        continuation_value, index = self._parse_block(index, indent + 4)
                    else:
                        continuation_value = self._parse_scalar(continuation_tail, continuation.number)
                    item[continuation_key] = continuation_value
                result.append(item)
            else:
                result.append(self._parse_scalar(tail, line.number))
        return result, index

    def _split_mapping_entry(self, line: YamlLine) -> tuple[str, str]:
        return self._split_inline_mapping_entry(line.content, line.number)

    def _split_inline_mapping_entry(self, content: str, line_number: int) -> tuple[str, str]:
        if ":" not in content:
            raise YamlSubsetError(f"line {line_number}: expected mapping entry")
        key, tail = content.split(":", 1)
        key = key.strip()
        if not self._KEY_RE.fullmatch(key):
            raise YamlSubsetError(f"line {line_number}: unsupported mapping key {key!r}")
        return key, tail.strip()

    def _looks_like_mapping_entry(self, content: str) -> bool:
        if ":" not in content:
            return False
        key = content.split(":", 1)[0].strip()
        return bool(self._KEY_RE.fullmatch(key))

    def _parse_scalar(self, token: str, line_number: int) -> Any:
        if token.startswith("[") or token.startswith("{"):
            raise YamlSubsetError(f"line {line_number}: flow collections are not supported")
        if token.startswith(("&", "*", "!", "|", ">")):
            raise YamlSubsetError(f"line {line_number}: unsupported YAML scalar feature")
        if token.startswith('"'):
            try:
                value = json.loads(token)
            except json.JSONDecodeError as exc:
                raise YamlSubsetError(f"line {line_number}: invalid double-quoted scalar") from exc
            if not isinstance(value, str):
                raise YamlSubsetError(f"line {line_number}: quoted scalar must be a string")
            return value
        if token.startswith("'"):
            if not token.endswith("'") or len(token) < 2:
                raise YamlSubsetError(f"line {line_number}: invalid single-quoted scalar")
            return token[1:-1].replace("''", "'")
        lowered = token.lower()
        if lowered == "true":
            return True
        if lowered == "false":
            return False
        if lowered in {"null", "~"}:
            return None
        if self._INT_RE.fullmatch(token):
            return int(token)
        if " #" in token:
            token = token.split(" #", 1)[0].rstrip()
        return token


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def display_path(root: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(root.resolve()))
    except ValueError:
        return str(path.resolve())


def resolve_input(root: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else root / path


def add_finding(
    findings: list[Finding],
    finding_id: str,
    check_id: str,
    path: str,
    message: str,
    expected: Any,
    actual: Any,
) -> None:
    findings.append(Finding(finding_id, check_id, path, message, expected, actual))


def value_at(document: Any, path: str) -> Any:
    current = document
    for token in path.split("."):
        if not isinstance(current, dict) or token not in current:
            return None
        current = current[token]
    return current


def expect_equal(
    document: dict[str, Any],
    findings: list[Finding],
    path: str,
    expected: Any,
    finding_id: str,
    check_id: str,
    message: str,
) -> None:
    actual = value_at(document, path)
    if actual != expected:
        add_finding(findings, finding_id, check_id, path, message, expected, actual)


def expect_mapping(
    document: dict[str, Any],
    findings: list[Finding],
    path: str,
    finding_id: str,
    check_id: str,
) -> dict[str, Any]:
    actual = value_at(document, path)
    if not isinstance(actual, dict):
        add_finding(findings, finding_id, check_id, path, "Expected a mapping.", "mapping", type(actual).__name__)
        return {}
    return actual


def expect_list(
    document: dict[str, Any],
    findings: list[Finding],
    path: str,
    finding_id: str,
    check_id: str,
) -> list[Any]:
    actual = value_at(document, path)
    if not isinstance(actual, list):
        add_finding(findings, finding_id, check_id, path, "Expected a sequence.", "sequence", type(actual).__name__)
        return []
    return actual


def validate(document: Any) -> tuple[list[Finding], dict[str, Any]]:
    findings: list[Finding] = []
    evidence: dict[str, Any] = {
        "sliceId": None,
        "modulePackage": None,
        "apiSurface": [],
        "dtoBoundary": {},
        "errorStatusFamilies": {},
        "reportFamilies": [],
        "delivery": {},
    }
    if not isinstance(document, dict):
        add_finding(findings, "SPEC-TOPLEVEL-001", "SPEC-TOPLEVEL", "$", "Root document must be a mapping.", "mapping", type(document).__name__)
        return findings, evidence

    missing = [key for key in REQUIRED_TOP_LEVEL if key not in document]
    unexpected = [key for key in document if key not in REQUIRED_TOP_LEVEL]
    if missing:
        add_finding(findings, "SPEC-TOPLEVEL-001", "SPEC-TOPLEVEL", "$", "Required top-level fields are missing.", REQUIRED_TOP_LEVEL, sorted(document.keys()))
    if unexpected:
        add_finding(findings, "SPEC-TOPLEVEL-002", "SPEC-TOPLEVEL", "$", "Unexpected top-level fields are not allowed by contract version 1.", [], sorted(unexpected))
    expect_equal(document, findings, "specVersion", 1, "SPEC-TOPLEVEL-003", "SPEC-TOPLEVEL", "specVersion must be 1.")
    expect_equal(document, findings, "kind", "GeneratedServiceSlice", "SPEC-TOPLEVEL-004", "SPEC-TOPLEVEL", "kind must identify a GeneratedServiceSlice.")

    metadata = expect_mapping(document, findings, "metadata", "SPEC-METADATA-001", "SPEC-METADATA")
    for key in ["sliceId", "status", "owner", "sourceReference"]:
        if not isinstance(metadata.get(key), str) or not metadata.get(key):
            add_finding(findings, "SPEC-METADATA-002", "SPEC-METADATA", f"metadata.{key}", "Metadata field must be a non-empty string.", "non-empty string", metadata.get(key))
    if metadata.get("status") != "candidate-reference-slice":
        add_finding(findings, "SPEC-METADATA-003", "SPEC-METADATA", "metadata.status", "Golden fixture must remain a candidate reference slice.", "candidate-reference-slice", metadata.get("status"))
    evidence["sliceId"] = metadata.get("sliceId")

    package_model = expect_mapping(document, findings, "packageModel", "SPEC-PACKAGE-001", "SPEC-PACKAGE")
    for key in ["basePackage", "modulePackage", "corePackage"]:
        if not isinstance(package_model.get(key), str) or not package_model.get(key):
            add_finding(findings, "SPEC-PACKAGE-002", "SPEC-PACKAGE", f"packageModel.{key}", "Package value must be a non-empty string.", "non-empty string", package_model.get(key))
    module_package = package_model.get("modulePackage")
    forbidden_prefixes = package_model.get("forbiddenPackagePrefixes")
    if not isinstance(forbidden_prefixes, list):
        add_finding(findings, "SPEC-PACKAGE-003", "SPEC-PACKAGE", "packageModel.forbiddenPackagePrefixes", "Forbidden package prefixes must be a sequence.", ["de.cocondo.platform.demo"], forbidden_prefixes)
        forbidden_prefixes = []
    if "de.cocondo.platform.demo" not in forbidden_prefixes:
        add_finding(findings, "SPEC-PACKAGE-004", "SPEC-PACKAGE", "packageModel.forbiddenPackagePrefixes", "Demo package reuse must be explicitly forbidden.", "contains de.cocondo.platform.demo", forbidden_prefixes)
    if isinstance(module_package, str) and any(module_package == prefix or module_package.startswith(prefix + ".") for prefix in forbidden_prefixes if isinstance(prefix, str)):
        add_finding(findings, "SPEC-PACKAGE-005", "SPEC-PACKAGE", "packageModel.modulePackage", "Module package must not use a forbidden or Demo package prefix.", "neutral non-Demo package", module_package)
    if isinstance(module_package, str) and ".demo." in module_package:
        add_finding(findings, "SPEC-PACKAGE-005", "SPEC-PACKAGE", "packageModel.modulePackage", "Module package must not use a Demo package.", "neutral non-Demo package", module_package)
    evidence["modulePackage"] = module_package

    resource = expect_mapping(document, findings, "resource", "SPEC-RESOURCE-001", "SPEC-RESOURCE")
    for key in ["domain", "resourceName", "collectionName", "displayField"]:
        if not isinstance(resource.get(key), str) or not resource.get(key):
            add_finding(findings, "SPEC-RESOURCE-002", "SPEC-RESOURCE", f"resource.{key}", "Resource field must be a non-empty string.", "non-empty string", resource.get(key))
    external_id = resource.get("externalId")
    if not isinstance(external_id, dict) or external_id.get("field") != "id" or external_id.get("type") != "string":
        add_finding(findings, "SPEC-RESOURCE-003", "SPEC-RESOURCE", "resource.externalId", "Golden fixture must use an opaque string id boundary.", {"field": "id", "type": "string"}, external_id)
    business_keys = resource.get("businessKeys")
    if not isinstance(business_keys, list) or not business_keys:
        add_finding(findings, "SPEC-RESOURCE-004", "SPEC-RESOURCE", "resource.businessKeys", "At least one unique business key is required for the golden alternate lookup.", "non-empty sequence", business_keys)
    else:
        for index, item in enumerate(business_keys):
            if not isinstance(item, dict) or item.get("unique") is not True or not item.get("lookupPath"):
                add_finding(findings, "SPEC-RESOURCE-005", "SPEC-RESOURCE", f"resource.businessKeys[{index}]", "Business keys used for lookup must be unique and declare lookupPath.", {"unique": True, "lookupPath": "non-empty"}, item)

    api_surface = expect_mapping(document, findings, "apiSurface", "SPEC-QUERY-001", "SPEC-QUERY")
    base_path = api_surface.get("basePath")
    expected_base_path = "/api/administration/business-partners"
    if base_path != expected_base_path:
        add_finding(findings, "SPEC-QUERY-002", "SPEC-QUERY", "apiSurface.basePath", "Golden fixture basePath is not canonical.", expected_base_path, base_path)
    query = api_surface.get("query")
    if not isinstance(query, dict):
        add_finding(findings, "SPEC-QUERY-003", "SPEC-QUERY", "apiSurface.query", "Query surface must be a mapping.", "mapping", query)
        query = {}
    operations: list[str] = []
    query_expectations = {
        "list": ("GET", ""),
        "all": ("GET", "/all"),
        "count": ("GET", "/count"),
    }
    for operation, (method, path) in query_expectations.items():
        config = query.get(operation)
        if not isinstance(config, dict):
            add_finding(findings, "SPEC-QUERY-004", "SPEC-QUERY", f"apiSurface.query.{operation}", "Required query operation is missing.", {"enabled": True, "method": method, "path": path}, config)
            continue
        if config.get("enabled") is not True or config.get("method") != method or config.get("path") != path:
            add_finding(findings, "SPEC-QUERY-005", "SPEC-QUERY", f"apiSurface.query.{operation}", "Query operation does not match the baseline surface.", {"enabled": True, "method": method, "path": path}, config)
        else:
            operations.append(f"{method} {base_path}{path}")
    list_config = query.get("list") if isinstance(query.get("list"), dict) else {}
    if list_config.get("pagination") != "offset":
        add_finding(findings, "SPEC-QUERY-006", "SPEC-QUERY", "apiSurface.query.list.pagination", "Golden list query must use offset pagination.", "offset", list_config.get("pagination"))
    sorting = list_config.get("sorting")
    if not isinstance(sorting, dict) or not isinstance(sorting.get("allowlist"), list) or not sorting.get("allowlist"):
        add_finding(findings, "SPEC-QUERY-007", "SPEC-QUERY", "apiSurface.query.list.sorting", "List query must declare a non-empty sort allowlist.", "non-empty allowlist", sorting)
    if not isinstance(list_config.get("filters"), list):
        add_finding(findings, "SPEC-QUERY-008", "SPEC-QUERY", "apiSurface.query.list.filters", "List query filters must be explicit.", "sequence", list_config.get("filters"))

    detail = api_surface.get("detail")
    if not isinstance(detail, dict) or detail.get("enabled") is not True or detail.get("method") != "GET" or detail.get("path") != "/{id}":
        add_finding(findings, "SPEC-DETAIL-001", "SPEC-DETAIL", "apiSurface.detail", "Detail lookup must be GET /{id}.", {"enabled": True, "method": "GET", "path": "/{id}"}, detail)
    else:
        operations.append(f"GET {base_path}/{{id}}")
    alternate_lookups = api_surface.get("alternateLookups")
    if not isinstance(alternate_lookups, list) or not alternate_lookups:
        add_finding(findings, "SPEC-DETAIL-002", "SPEC-DETAIL", "apiSurface.alternateLookups", "Golden fixture requires one unique alternate lookup.", "non-empty sequence", alternate_lookups)
    else:
        for index, lookup in enumerate(alternate_lookups):
            if not isinstance(lookup, dict) or lookup.get("method") != "GET" or lookup.get("unique") is not True or not lookup.get("path"):
                add_finding(findings, "SPEC-DETAIL-003", "SPEC-DETAIL", f"apiSurface.alternateLookups[{index}]", "Alternate lookups must be unique GET operations with explicit paths.", {"method": "GET", "unique": True, "path": "non-empty"}, lookup)
            else:
                operations.append(f"GET {base_path}{lookup.get('path')}")

    write = api_surface.get("write")
    if not isinstance(write, dict):
        add_finding(findings, "SPEC-WRITE-001", "SPEC-WRITE", "apiSurface.write", "Write surface must be a mapping.", "mapping", write)
        write = {}
    write_expectations = {
        "create": {"enabled": True, "method": "POST", "path": "", "successStatus": 201},
        "update": {"enabled": True, "method": "PUT", "path": "/{id}", "successStatus": 200},
        "delete": {"enabled": True, "method": "DELETE", "path": "/{id}", "successStatus": 204},
    }
    for operation, expected in write_expectations.items():
        config = write.get(operation)
        if not isinstance(config, dict) or any(config.get(key) != value for key, value in expected.items()):
            add_finding(findings, "SPEC-WRITE-002", "SPEC-WRITE", f"apiSurface.write.{operation}", "Write operation does not match the baseline surface.", expected, config)
        else:
            operations.append(f"{expected['method']} {base_path}{expected['path']}")
    create = write.get("create") if isinstance(write.get("create"), dict) else {}
    delete = write.get("delete") if isinstance(write.get("delete"), dict) else {}
    if create.get("locationHeader") != "detail":
        add_finding(findings, "SPEC-WRITE-003", "SPEC-WRITE", "apiSurface.write.create.locationHeader", "Create must link its Location header to detail.", "detail", create.get("locationHeader"))
    if delete.get("requestBody") != "forbidden":
        add_finding(findings, "SPEC-WRITE-004", "SPEC-WRITE", "apiSurface.write.delete.requestBody", "Single-resource delete request bodies are forbidden.", "forbidden", delete.get("requestBody"))
    evidence["apiSurface"] = operations

    model = expect_mapping(document, findings, "model", "SPEC-DTO-001", "SPEC-DTO")
    dto = model.get("dto") if isinstance(model.get("dto"), dict) else {}
    entity = model.get("entity") if isinstance(model.get("entity"), dict) else {}
    required_dto_keys = ["read", "listItem", "create", "update"]
    if any(not isinstance(dto.get(key), str) or not dto.get(key) for key in required_dto_keys):
        add_finding(findings, "SPEC-DTO-002", "SPEC-DTO", "model.dto", "Read, listItem, create and update DTOs must be explicit.", required_dto_keys, dto)
    if dto.get("create") == dto.get("update") or dto.get("create") == entity.get("name") or dto.get("update") == entity.get("name"):
        add_finding(findings, "SPEC-DTO-003", "SPEC-DTO", "model.dto", "CreateDTO and UpdateDTO must be distinct and must not be the entity type.", "distinct boundary DTOs", dto)
    if isinstance(dto.get("create"), str) and not dto["create"].endswith("CreateDTO"):
        add_finding(findings, "SPEC-DTO-004", "SPEC-DTO", "model.dto.create", "Create boundary type must be a CreateDTO.", "*CreateDTO", dto.get("create"))
    if isinstance(dto.get("update"), str) and not dto["update"].endswith("UpdateDTO"):
        add_finding(findings, "SPEC-DTO-005", "SPEC-DTO", "model.dto.update", "Update boundary type must be an UpdateDTO.", "*UpdateDTO", dto.get("update"))
    fields = model.get("fields")
    if not isinstance(fields, list) or not fields:
        add_finding(findings, "SPEC-DTO-006", "SPEC-DTO", "model.fields", "Field metadata must be a non-empty sequence.", "non-empty sequence", fields)
    else:
        for index, field in enumerate(fields):
            required_keys = ["name", "type", "requiredOnCreate", "requiredOnUpdate", "filterable", "sortable"]
            if not isinstance(field, dict) or any(key not in field for key in required_keys):
                add_finding(findings, "SPEC-DTO-007", "SPEC-DTO", f"model.fields[{index}]", "Field validation/filter/sort metadata is incomplete.", required_keys, field)
            else:
                boolean_keys = ["requiredOnCreate", "requiredOnUpdate", "filterable", "sortable"]
                if any(not isinstance(field.get(key), bool) for key in boolean_keys):
                    add_finding(findings, "SPEC-DTO-008", "SPEC-DTO", f"model.fields[{index}]", "Required/filter/sort field flags must be explicit booleans.", {key: "boolean" for key in boolean_keys}, field)
                if field.get("type") == "string" and not isinstance(field.get("maxLength"), int):
                    add_finding(findings, "SPEC-DTO-009", "SPEC-DTO", f"model.fields[{index}].maxLength", "String fields must declare maxLength.", "integer", field.get("maxLength"))
    validation = expect_mapping(document, findings, "validation", "SPEC-DTO-010", "SPEC-DTO")
    validation_expectations = {
        "requestBodiesRequireValidAnnotation": True,
        "entitiesAsRequestBody": "forbidden",
        "beanValidationToOpenApiRequiredAlignment": "required",
        "invalidRequestErrorType": "VALIDATION_FAILED",
    }
    if any(validation.get(key) != value for key, value in validation_expectations.items()):
        add_finding(findings, "SPEC-DTO-011", "SPEC-DTO", "validation", "Validation boundary does not match the generated-slice contract.", validation_expectations, validation)
    evidence["dtoBoundary"] = {
        "entity": entity.get("name"),
        "create": dto.get("create"),
        "update": dto.get("update"),
        "entitiesAsRequestBody": validation.get("entitiesAsRequestBody"),
    }

    error_contract = expect_mapping(document, findings, "errorContract", "SPEC-ERROR-001", "SPEC-ERROR")
    if error_contract.get("handler") != "global-core" or error_contract.get("responseType") != "ApiErrorResponse":
        add_finding(findings, "SPEC-ERROR-002", "SPEC-ERROR", "errorContract", "Generated slices must reference the global Core ApiErrorResponse contract.", {"handler": "global-core", "responseType": "ApiErrorResponse"}, error_contract)
    actual_error_types = error_contract.get("requiredErrorTypes")
    if actual_error_types != REQUIRED_ERROR_TYPES:
        add_finding(findings, "SPEC-ERROR-003", "SPEC-ERROR", "errorContract.requiredErrorTypes", "Required error types are incomplete or not canonical.", REQUIRED_ERROR_TYPES, actual_error_types)
    mappings = error_contract.get("expectedStatusMappings")
    normalized_mappings: dict[int, list[str]] = {}
    if not isinstance(mappings, list):
        add_finding(findings, "SPEC-ERROR-004", "SPEC-ERROR", "errorContract.expectedStatusMappings", "Expected HTTP status families must be explicit.", EXPECTED_STATUS_MAPPINGS, mappings)
    else:
        for index, mapping in enumerate(mappings):
            if not isinstance(mapping, dict) or not isinstance(mapping.get("status"), int) or not isinstance(mapping.get("errorTypes"), list):
                add_finding(findings, "SPEC-ERROR-005", "SPEC-ERROR", f"errorContract.expectedStatusMappings[{index}]", "Status mapping must contain integer status and errorTypes sequence.", {"status": "integer", "errorTypes": "sequence"}, mapping)
                continue
            status = mapping["status"]
            if status in normalized_mappings:
                add_finding(findings, "SPEC-ERROR-005", "SPEC-ERROR", f"errorContract.expectedStatusMappings[{index}]", "Duplicate status mappings are not allowed.", "unique status", status)
            normalized_mappings[status] = mapping["errorTypes"]
        for status, expected_types in EXPECTED_STATUS_MAPPINGS.items():
            if normalized_mappings.get(status) != expected_types:
                add_finding(findings, "SPEC-ERROR-006", "SPEC-ERROR", f"errorContract.expectedStatusMappings[{status}]", "Required 400/404/409 error family is missing or inconsistent.", expected_types, normalized_mappings.get(status))
    evidence["errorStatusFamilies"] = {str(status): normalized_mappings.get(status, []) for status in sorted(EXPECTED_STATUS_MAPPINGS)}

    reports = expect_mapping(document, findings, "reports", "SPEC-REPORTS-001", "SPEC-REPORTS")
    for report_name in REQUIRED_REPORTS:
        if reports.get(report_name) != "required":
            add_finding(findings, "SPEC-REPORTS-002", "SPEC-REPORTS", f"reports.{report_name}", "Evidence report family must be required.", "required", reports.get(report_name))
    evidence["reportFamilies"] = [name for name in REQUIRED_REPORTS if reports.get(name) == "required"]

    delivery = expect_mapping(document, findings, "delivery", "SPEC-DELIVERY-001", "SPEC-DELIVERY")
    delivery_expectations = {
        "outputMode": "patch-zip",
        "targetApply": "forbidden-in-springmaster",
        "targetPatchDryRun": "required-before-apply",
        "targetMavenTest": "required-after-apply",
        "targetFullExport": "required-after-apply",
    }
    if any(delivery.get(key) != value for key, value in delivery_expectations.items()):
        add_finding(findings, "SPEC-DELIVERY-002", "SPEC-DELIVERY", "delivery", "Target delivery must remain patch-only and verified in the target project.", delivery_expectations, delivery)
    evidence["delivery"] = {key: delivery.get(key) for key in delivery_expectations}

    return findings, evidence


def check_rows(findings: list[Finding], parse_ok: bool) -> list[dict[str, str]]:
    failed_checks = {finding.checkId for finding in findings}
    rows: list[dict[str, str]] = []
    for check_id, title in CHECK_DEFINITIONS:
        status = "passed"
        if check_id == "SPEC-PARSE" and not parse_ok:
            status = "failed"
        elif check_id in failed_checks:
            status = "failed"
        elif not parse_ok:
            status = "not-run"
        rows.append({"id": check_id, "title": title, "status": status})
    return rows


def generated_at(value: str | None) -> str:
    if value:
        return value
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def build_report(root: Path, spec_path: Path, generated: str) -> tuple[dict[str, Any], int]:
    findings: list[Finding] = []
    document: Any = None
    parse_ok = False
    evidence: dict[str, Any] = {
        "sliceId": None,
        "modulePackage": None,
        "apiSurface": [],
        "dtoBoundary": {},
        "errorStatusFamilies": {},
        "reportFamilies": [],
        "delivery": {},
    }
    spec_bytes = b""
    if not spec_path.is_file():
        add_finding(findings, "SPEC-PARSE-001", "SPEC-PARSE", display_path(root, spec_path), "Slice-Spec YAML file is missing.", "existing file", "missing")
    else:
        spec_bytes = spec_path.read_bytes()
        try:
            text = spec_bytes.decode("utf-8")
        except UnicodeDecodeError as exc:
            add_finding(findings, "SPEC-PARSE-002", "SPEC-PARSE", display_path(root, spec_path), "Slice-Spec YAML must be UTF-8.", "UTF-8", str(exc))
        else:
            try:
                document = StrictYamlSubsetParser(text).parse()
                parse_ok = True
            except YamlSubsetError as exc:
                add_finding(findings, "SPEC-PARSE-003", "SPEC-PARSE", display_path(root, spec_path), "Slice-Spec YAML is invalid or uses unsupported YAML features.", "strict documented YAML subset", str(exc))
    if parse_ok:
        validation_findings, evidence = validate(document)
        findings.extend(validation_findings)

    checks = check_rows(findings, parse_ok)
    passed = sum(1 for row in checks if row["status"] == "passed")
    failed = sum(1 for row in checks if row["status"] == "failed")
    not_run = sum(1 for row in checks if row["status"] == "not-run")
    report = {
        "schemaVersion": SCHEMA_VERSION,
        "generatedAt": generated,
        "mode": MODE,
        "project": PROJECT,
        "contract": {
            "document": CONTRACT_DOC,
            "specPath": display_path(root, spec_path),
            "specSha256": hashlib.sha256(spec_bytes).hexdigest() if spec_bytes else None,
            "specVersion": document.get("specVersion") if isinstance(document, dict) else None,
            "kind": document.get("kind") if isinstance(document, dict) else None,
        },
        "summary": {
            "checks": len(checks),
            "passed": passed,
            "failed": failed,
            "notRun": not_run,
            "findings": len(findings),
            "status": "PASS" if not findings else "FAIL",
        },
        "checks": checks,
        "evidence": evidence,
        "findings": [finding.to_json() for finding in findings],
    }
    return report, 0 if not findings else 1


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate the GeneratedServiceSlice golden YAML fixture.")
    parser.add_argument("--spec", default=DEFAULT_SPEC, help=f"Slice-Spec YAML path (default: {DEFAULT_SPEC})")
    parser.add_argument("--out", default=DEFAULT_OUT, help=f"JSON report path (default: {DEFAULT_OUT})")
    parser.add_argument("--generated-at", help="Deterministic generatedAt value for tests and fixtures")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    root = repo_root()
    spec_path = resolve_input(root, args.spec)
    out_path = resolve_input(root, args.out)
    report, exit_code = build_report(root, spec_path, generated_at(args.generated_at))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Generated Slice Spec Fixture Gate: {report['summary']['status']}")
    print(f"Spec:     {report['contract']['specPath']}")
    print(f"Findings: {report['summary']['findings']}")
    print(f"Report:   {display_path(root, out_path)}")
    return exit_code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
