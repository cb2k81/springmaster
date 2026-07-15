#!/usr/bin/env python3
"""Build the deterministic, domain-neutral GeneratedServiceSlice IR.

The input must first satisfy the executable Slice-Spec contract from patch
000123. This tool reuses that strict parser and validator, then normalizes the
validated document into the generator-facing Intermediate Representation used
by later patch-blueprint phases.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

IR_SCHEMA_VERSION = "springmaster.generated-service-slice-ir.v1"
DEFAULT_SPEC = "PROJECT_DOCS/TOOLING/GENERATED_SLICE_SPEC_GOLDEN_BUSINESS_PARTNER.yaml"
DEFAULT_OUT = "reports/tooling/generated-slice-ir.business-partner.json"
SPEC_CONTRACT = "PROJECT_DOCS/TOOLING/GENERATED_SLICE_SPEC_CONTRACT.md"
IR_CONTRACT = "PROJECT_DOCS/TOOLING/GENERATED_SLICE_INTERMEDIATE_REPRESENTATION.md"
FIXTURE_GATE_TOOL = "bin/generated-slice-spec-fixture-gate-report.py"
REQUIRED_IR_SECTIONS = [
    "schemaVersion",
    "source",
    "metadata",
    "packages",
    "resource",
    "query",
    "detail",
    "write",
    "model",
    "validation",
    "errorContract",
    "reports",
    "delivery",
]


class IrError(ValueError):
    """Raised when a validated Slice-Spec cannot be represented safely."""


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


def load_fixture_gate(root: Path) -> ModuleType:
    tool_path = root / FIXTURE_GATE_TOOL
    module_name = "springmaster_generated_slice_fixture_gate"
    spec = importlib.util.spec_from_file_location(module_name, tool_path)
    if spec is None or spec.loader is None:
        raise IrError(f"cannot load Slice-Spec fixture gate: {tool_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def absolute_path(base_path: str, relative_path: str) -> str:
    if not base_path.startswith("/"):
        raise IrError(f"apiSurface.basePath must be absolute: {base_path!r}")
    if relative_path == "":
        return base_path
    if not relative_path.startswith("/"):
        raise IrError(f"operation path must be empty or absolute-relative: {relative_path!r}")
    return base_path.rstrip("/") + relative_path


def operation(
    *,
    key: str,
    method: str,
    relative_path: str,
    base_path: str,
    response_shape: str,
    request_dto: str | None = None,
    success_status: int | None = None,
    inherits: list[str] | None = None,
    location_header: str | None = None,
    request_body: str | None = None,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "key": key,
        "method": method,
        "relativePath": relative_path,
        "absolutePath": absolute_path(base_path, relative_path),
        "responseShape": response_shape,
    }
    if request_dto is not None:
        result["requestDto"] = request_dto
    if success_status is not None:
        result["successStatus"] = success_status
    if inherits:
        result["inherits"] = inherits
    if location_header is not None:
        result["locationHeader"] = location_header
    if request_body is not None:
        result["requestBody"] = request_body
    return result



def value_at(document: Any, path: str) -> Any:
    current = document
    for token in path.split("."):
        if not isinstance(current, dict) or token not in current:
            return None
        current = current[token]
    return current


def validate_input_contract(document: Any) -> list[str]:
    """Validate contract-v1 generically without locking the IR to the golden resource."""
    errors: list[str] = []

    def require(condition: bool, path: str, message: str) -> None:
        if not condition:
            errors.append(f"{path}: {message}")

    require(isinstance(document, dict), "$", "root must be a mapping")
    if not isinstance(document, dict):
        return errors
    expected_top_level = [
        "specVersion", "kind", "metadata", "packageModel", "resource",
        "apiSurface", "model", "validation", "errorContract", "reports", "delivery"
    ]
    require(
        set(document.keys()) == set(expected_top_level) and len(document) == len(expected_top_level),
        "$",
        "top-level sections must be complete and contain no unknown fields",
    )
    require(document.get("specVersion") == 1, "specVersion", "must be 1")
    require(document.get("kind") == "GeneratedServiceSlice", "kind", "must be GeneratedServiceSlice")

    metadata = document.get("metadata")
    require(isinstance(metadata, dict), "metadata", "must be a mapping")
    if isinstance(metadata, dict):
        for key in ["sliceId", "status", "owner", "sourceReference"]:
            require(isinstance(metadata.get(key), str) and bool(metadata.get(key)), f"metadata.{key}", "must be a non-empty string")

    packages = document.get("packageModel")
    require(isinstance(packages, dict), "packageModel", "must be a mapping")
    forbidden: list[str] = []
    if isinstance(packages, dict):
        for key in ["basePackage", "modulePackage", "corePackage"]:
            require(isinstance(packages.get(key), str) and bool(packages.get(key)), f"packageModel.{key}", "must be a non-empty string")
        raw_forbidden = packages.get("forbiddenPackagePrefixes")
        require(isinstance(raw_forbidden, list) and all(isinstance(v, str) and v for v in raw_forbidden or []), "packageModel.forbiddenPackagePrefixes", "must be a non-empty string sequence")
        if isinstance(raw_forbidden, list):
            forbidden = raw_forbidden
        require("de.cocondo.platform.demo" in forbidden, "packageModel.forbiddenPackagePrefixes", "must explicitly forbid de.cocondo.platform.demo")
        module_package = packages.get("modulePackage")
        if isinstance(module_package, str):
            require(not any(module_package == prefix or module_package.startswith(prefix + ".") for prefix in forbidden), "packageModel.modulePackage", "must not use a forbidden package prefix")

    resource = document.get("resource")
    require(isinstance(resource, dict), "resource", "must be a mapping")
    if isinstance(resource, dict):
        for key in ["domain", "resourceName", "collectionName", "displayField"]:
            require(isinstance(resource.get(key), str) and bool(resource.get(key)), f"resource.{key}", "must be a non-empty string")
        external_id = resource.get("externalId")
        require(isinstance(external_id, dict), "resource.externalId", "must be a mapping")
        if isinstance(external_id, dict):
            require(isinstance(external_id.get("field"), str) and bool(external_id.get("field")), "resource.externalId.field", "must be a non-empty string")
            require(isinstance(external_id.get("type"), str) and bool(external_id.get("type")), "resource.externalId.type", "must be a non-empty string")
        business_keys = resource.get("businessKeys")
        require(isinstance(business_keys, list), "resource.businessKeys", "must be a sequence")
        if isinstance(business_keys, list):
            for index, item in enumerate(business_keys):
                require(isinstance(item, dict), f"resource.businessKeys[{index}]", "must be a mapping")
                if isinstance(item, dict):
                    for key in ["name", "field", "lookupPath"]:
                        require(isinstance(item.get(key), str) and bool(item.get(key)), f"resource.businessKeys[{index}].{key}", "must be a non-empty string")
                    require(item.get("unique") is True, f"resource.businessKeys[{index}].unique", "must be true")

    api = document.get("apiSurface")
    require(isinstance(api, dict), "apiSurface", "must be a mapping")
    if isinstance(api, dict):
        base_path = api.get("basePath")
        require(isinstance(base_path, str) and base_path.startswith("/api/"), "apiSurface.basePath", "must be an absolute /api path")
        query = api.get("query")
        require(isinstance(query, dict), "apiSurface.query", "must be a mapping")
        if isinstance(query, dict):
            expected = {"list": ("GET", ""), "all": ("GET", "/all"), "count": ("GET", "/count")}
            for key, (method, path) in expected.items():
                item = query.get(key)
                require(isinstance(item, dict), f"apiSurface.query.{key}", "must be a mapping")
                if isinstance(item, dict):
                    require(item.get("enabled") is True, f"apiSurface.query.{key}.enabled", "must be true")
                    require(item.get("method") == method, f"apiSurface.query.{key}.method", f"must be {method}")
                    require(item.get("path") == path, f"apiSurface.query.{key}.path", f"must be {path!r}")
            list_item = query.get("list") if isinstance(query.get("list"), dict) else {}
            require(list_item.get("pagination") == "offset", "apiSurface.query.list.pagination", "must be offset")
            require(isinstance(list_item.get("filters"), list), "apiSurface.query.list.filters", "must be a sequence")
            sorting = list_item.get("sorting")
            require(isinstance(sorting, dict), "apiSurface.query.list.sorting", "must be a mapping")
            if isinstance(sorting, dict):
                allowlist = sorting.get("allowlist")
                require(isinstance(allowlist, list) and bool(allowlist), "apiSurface.query.list.sorting.allowlist", "must be a non-empty sequence")
                default = sorting.get("default")
                require(isinstance(default, dict), "apiSurface.query.list.sorting.default", "must be a mapping")
                if isinstance(default, dict) and isinstance(allowlist, list):
                    require(default.get("sortBy") in allowlist, "apiSurface.query.list.sorting.default.sortBy", "must be in allowlist")
                    require(default.get("sortDir") in ["asc", "desc"], "apiSurface.query.list.sorting.default.sortDir", "must be asc or desc")
        detail = api.get("detail")
        require(isinstance(detail, dict), "apiSurface.detail", "must be a mapping")
        if isinstance(detail, dict):
            require(detail.get("enabled") is True, "apiSurface.detail.enabled", "must be true")
            require(detail.get("method") == "GET", "apiSurface.detail.method", "must be GET")
            require(isinstance(detail.get("path"), str) and detail.get("path", "").startswith("/"), "apiSurface.detail.path", "must be an absolute-relative path")
        lookups = api.get("alternateLookups")
        require(isinstance(lookups, list), "apiSurface.alternateLookups", "must be a sequence")
        if isinstance(lookups, list):
            for index, item in enumerate(lookups):
                require(isinstance(item, dict), f"apiSurface.alternateLookups[{index}]", "must be a mapping")
                if isinstance(item, dict):
                    require(isinstance(item.get("name"), str) and bool(item.get("name")), f"apiSurface.alternateLookups[{index}].name", "must be a non-empty string")
                    require(item.get("method") == "GET", f"apiSurface.alternateLookups[{index}].method", "must be GET")
                    require(isinstance(item.get("path"), str) and item.get("path", "").startswith("/"), f"apiSurface.alternateLookups[{index}].path", "must be an absolute-relative path")
                    require(item.get("unique") is True, f"apiSurface.alternateLookups[{index}].unique", "must be true")
        write = api.get("write")
        require(isinstance(write, dict), "apiSurface.write", "must be a mapping")
        if isinstance(write, dict):
            expected = {
                "create": ("POST", "", 201),
                "update": ("PUT", None, 200),
                "delete": ("DELETE", None, 204),
            }
            for key, (method, exact_path, status) in expected.items():
                item = write.get(key)
                require(isinstance(item, dict), f"apiSurface.write.{key}", "must be a mapping")
                if isinstance(item, dict):
                    require(item.get("enabled") is True, f"apiSurface.write.{key}.enabled", "must be true")
                    require(item.get("method") == method, f"apiSurface.write.{key}.method", f"must be {method}")
                    if exact_path is None:
                        require(isinstance(item.get("path"), str) and item.get("path", "").startswith("/"), f"apiSurface.write.{key}.path", "must be an absolute-relative path")
                    else:
                        require(item.get("path") == exact_path, f"apiSurface.write.{key}.path", f"must be {exact_path!r}")
                    require(item.get("successStatus") == status, f"apiSurface.write.{key}.successStatus", f"must be {status}")
            if isinstance(write.get("create"), dict):
                require(write["create"].get("locationHeader") == "detail", "apiSurface.write.create.locationHeader", "must be detail")
            if isinstance(write.get("delete"), dict):
                require(write["delete"].get("requestBody") == "forbidden", "apiSurface.write.delete.requestBody", "must be forbidden")

    model = document.get("model")
    require(isinstance(model, dict), "model", "must be a mapping")
    if isinstance(model, dict):
        entity = model.get("entity")
        dto = model.get("dto")
        fields = model.get("fields")
        require(isinstance(entity, dict) and isinstance(entity.get("name"), str) and bool(entity.get("name")), "model.entity.name", "must be a non-empty string")
        require(isinstance(dto, dict), "model.dto", "must be a mapping")
        if isinstance(dto, dict):
            for key in ["read", "listItem", "create", "update"]:
                require(isinstance(dto.get(key), str) and bool(dto.get(key)), f"model.dto.{key}", "must be a non-empty string")
            require(dto.get("create") != dto.get("update"), "model.dto", "create and update DTOs must be distinct")
            if isinstance(entity, dict):
                require(dto.get("create") != entity.get("name") and dto.get("update") != entity.get("name"), "model.dto", "entity must not be an inbound request DTO")
        require(isinstance(fields, list) and bool(fields), "model.fields", "must be a non-empty sequence")
        if isinstance(fields, list):
            names: set[str] = set()
            for index, field in enumerate(fields):
                require(isinstance(field, dict), f"model.fields[{index}]", "must be a mapping")
                if not isinstance(field, dict):
                    continue
                name = field.get("name")
                require(isinstance(name, str) and bool(name), f"model.fields[{index}].name", "must be a non-empty string")
                if isinstance(name, str):
                    require(name not in names, f"model.fields[{index}].name", "must be unique")
                    names.add(name)
                require(isinstance(field.get("type"), str) and bool(field.get("type")), f"model.fields[{index}].type", "must be a non-empty string")
                for key in ["requiredOnCreate", "requiredOnUpdate", "filterable", "sortable"]:
                    require(isinstance(field.get(key), bool), f"model.fields[{index}].{key}", "must be boolean")
                if field.get("type") == "string":
                    require(isinstance(field.get("maxLength"), int) and field.get("maxLength") > 0, f"model.fields[{index}].maxLength", "must be a positive integer for strings")

    expected_validation = {
        "requestBodiesRequireValidAnnotation": True,
        "entitiesAsRequestBody": "forbidden",
        "beanValidationToOpenApiRequiredAlignment": "required",
        "invalidRequestErrorType": "VALIDATION_FAILED",
    }
    require(document.get("validation") == expected_validation, "validation", "must match the contract-v1 DTO boundary")

    error_contract = document.get("errorContract")
    require(isinstance(error_contract, dict), "errorContract", "must be a mapping")
    if isinstance(error_contract, dict):
        require(error_contract.get("handler") == "global-core", "errorContract.handler", "must be global-core")
        require(error_contract.get("responseType") == "ApiErrorResponse", "errorContract.responseType", "must be ApiErrorResponse")
        required_types = ["VALIDATION_FAILED", "INVALID_REQUEST", "RESOURCE_NOT_FOUND", "CONFLICT", "INTERNAL_ERROR"]
        require(error_contract.get("requiredErrorTypes") == required_types, "errorContract.requiredErrorTypes", "must match the canonical error family")
        mappings = error_contract.get("expectedStatusMappings")
        require(isinstance(mappings, list), "errorContract.expectedStatusMappings", "must be a sequence")
        if isinstance(mappings, list):
            normalized = {m.get("status"): m.get("errorTypes") for m in mappings if isinstance(m, dict)}
            require(normalized.get(400) == ["VALIDATION_FAILED", "INVALID_REQUEST"], "errorContract.expectedStatusMappings[400]", "must map validation and invalid request")
            require(normalized.get(404) == ["RESOURCE_NOT_FOUND"], "errorContract.expectedStatusMappings[404]", "must map resource not found")
            require(normalized.get(409) == ["CONFLICT"], "errorContract.expectedStatusMappings[409]", "must map conflict")

    expected_reports = {
        "queryContract": "required",
        "detailLookupContract": "required",
        "writeApiContract": "required",
        "requestValidationOpenApiGate": "required",
    }
    require(document.get("reports") == expected_reports, "reports", "must require all four evidence families")
    expected_delivery = {
        "outputMode": "patch-zip",
        "targetApply": "forbidden-in-springmaster",
        "targetPatchDryRun": "required-before-apply",
        "targetMavenTest": "required-after-apply",
        "targetFullExport": "required-after-apply",
    }
    require(document.get("delivery") == expected_delivery, "delivery", "must preserve patch-only target verification")
    return errors

def build_ir(document: dict[str, Any], spec_path: str, spec_sha256: str) -> dict[str, Any]:
    metadata = document["metadata"]
    package_model = document["packageModel"]
    resource = document["resource"]
    api_surface = document["apiSurface"]
    query = api_surface["query"]
    detail = api_surface["detail"]
    alternate_lookups = api_surface["alternateLookups"]
    write = api_surface["write"]
    model = document["model"]
    dto = model["dto"]
    list_config = query["list"]
    sorting = list_config["sorting"]
    base_path = api_surface["basePath"]

    fields: list[dict[str, Any]] = []
    for field in model["fields"]:
        constraints: dict[str, Any] = {}
        if "maxLength" in field:
            constraints["maxLength"] = field["maxLength"]
        fields.append(
            {
                "name": field["name"],
                "type": field["type"],
                "required": {
                    "create": field["requiredOnCreate"],
                    "update": field["requiredOnUpdate"],
                },
                "constraints": constraints,
                "capabilities": {
                    "filterable": field["filterable"],
                    "sortable": field["sortable"],
                    "businessKey": bool(field.get("businessKey", False)),
                },
            }
        )

    query_operations = [
        operation(
            key="list",
            method=query["list"]["method"],
            relative_path=query["list"]["path"],
            base_path=base_path,
            response_shape="paged-list-item",
            inherits=["filters", "sorting", "pagination"],
        ),
        operation(
            key="all",
            method=query["all"]["method"],
            relative_path=query["all"]["path"],
            base_path=base_path,
            response_shape="list-item-array",
            inherits=["filters", "sorting"],
        ),
        operation(
            key="count",
            method=query["count"]["method"],
            relative_path=query["count"]["path"],
            base_path=base_path,
            response_shape="count-response",
            inherits=["filters"],
        ),
    ]

    alternate_ir: list[dict[str, Any]] = []
    business_keys_by_path = {
        key["lookupPath"]: key for key in resource.get("businessKeys", [])
    }
    for lookup in alternate_lookups:
        business_key = business_keys_by_path.get(lookup["path"])
        alternate_ir.append(
            {
                **operation(
                    key=lookup["name"],
                    method=lookup["method"],
                    relative_path=lookup["path"],
                    base_path=base_path,
                    response_shape="read-dto",
                ),
                "unique": lookup["unique"],
                "businessKey": business_key["field"] if business_key else None,
            }
        )

    ir = {
        "schemaVersion": IR_SCHEMA_VERSION,
        "source": {
            "specContract": SPEC_CONTRACT,
            "irContract": IR_CONTRACT,
            "specPath": spec_path,
            "specSha256": spec_sha256,
            "specVersion": document["specVersion"],
            "kind": document["kind"],
            "sliceId": metadata["sliceId"],
        },
        "metadata": {
            "status": metadata["status"],
            "owner": metadata["owner"],
        },
        "packages": {
            "base": package_model["basePackage"],
            "module": package_model["modulePackage"],
            "core": package_model["corePackage"],
            "forbiddenPrefixes": package_model["forbiddenPackagePrefixes"],
            "demoPackageReuse": "forbidden",
        },
        "resource": {
            "domain": resource["domain"],
            "name": resource["resourceName"],
            "collection": resource["collectionName"],
            "displayField": resource["displayField"],
            "externalId": resource["externalId"],
            "businessKeys": resource["businessKeys"],
        },
        "query": {
            "filters": list_config["filters"],
            "sorting": {
                "allowlist": sorting["allowlist"],
                "default": {
                    "field": sorting["default"]["sortBy"],
                    "direction": sorting["default"]["sortDir"],
                },
            },
            "pagination": {"mode": list_config["pagination"]},
            "operations": query_operations,
        },
        "detail": {
            "byId": operation(
                key="byId",
                method=detail["method"],
                relative_path=detail["path"],
                base_path=base_path,
                response_shape="read-dto",
            ),
            "alternateLookups": alternate_ir,
        },
        "write": {
            "create": operation(
                key="create",
                method=write["create"]["method"],
                relative_path=write["create"]["path"],
                base_path=base_path,
                response_shape="read-dto",
                request_dto=dto["create"],
                success_status=write["create"]["successStatus"],
                location_header=write["create"]["locationHeader"],
            ),
            "update": operation(
                key="update",
                method=write["update"]["method"],
                relative_path=write["update"]["path"],
                base_path=base_path,
                response_shape="read-dto",
                request_dto=dto["update"],
                success_status=write["update"]["successStatus"],
            ),
            "delete": operation(
                key="delete",
                method=write["delete"]["method"],
                relative_path=write["delete"]["path"],
                base_path=base_path,
                response_shape="empty",
                success_status=write["delete"]["successStatus"],
                request_body=write["delete"]["requestBody"],
            ),
        },
        "model": {
            "entity": model["entity"]["name"],
            "dto": {
                "read": dto["read"],
                "listItem": dto["listItem"],
                "create": dto["create"],
                "update": dto["update"],
            },
            "fields": fields,
        },
        "validation": {
            "requestBodiesRequireValidAnnotation": document["validation"]["requestBodiesRequireValidAnnotation"],
            "entitiesAsRequestBody": document["validation"]["entitiesAsRequestBody"],
            "beanValidationToOpenApiRequiredAlignment": document["validation"]["beanValidationToOpenApiRequiredAlignment"],
            "invalidRequestErrorType": document["validation"]["invalidRequestErrorType"],
        },
        "errorContract": {
            "handler": document["errorContract"]["handler"],
            "responseType": document["errorContract"]["responseType"],
            "requiredErrorTypes": document["errorContract"]["requiredErrorTypes"],
            "statusMappings": [
                {
                    "status": mapping["status"],
                    "errorTypes": mapping["errorTypes"],
                }
                for mapping in sorted(
                    document["errorContract"]["expectedStatusMappings"],
                    key=lambda value: value["status"],
                )
            ],
        },
        "reports": {
            "queryContract": document["reports"]["queryContract"],
            "detailLookupContract": document["reports"]["detailLookupContract"],
            "writeApiContract": document["reports"]["writeApiContract"],
            "requestValidationOpenApiGate": document["reports"]["requestValidationOpenApiGate"],
        },
        "delivery": {
            "outputMode": document["delivery"]["outputMode"],
            "targetApply": document["delivery"]["targetApply"],
            "targetPatchDryRun": document["delivery"]["targetPatchDryRun"],
            "targetMavenTest": document["delivery"]["targetMavenTest"],
            "targetFullExport": document["delivery"]["targetFullExport"],
        },
    }
    validate_ir(ir)
    return ir


def validate_ir(ir: dict[str, Any]) -> None:
    if list(ir.keys()) != REQUIRED_IR_SECTIONS:
        raise IrError(
            "IR top-level sections are incomplete or out of canonical order: "
            f"expected={REQUIRED_IR_SECTIONS!r} actual={list(ir.keys())!r}"
        )

    packages = ir["packages"]
    active_packages = [packages["base"], packages["module"], packages["core"]]
    forbidden = packages["forbiddenPrefixes"]
    for package in active_packages:
        if any(package == prefix or package.startswith(prefix + ".") for prefix in forbidden):
            raise IrError(f"active package uses forbidden prefix: {package}")
    if packages["demoPackageReuse"] != "forbidden":
        raise IrError("IR must prohibit Demo package reuse")

    fields = {field["name"]: field for field in ir["model"]["fields"]}
    if len(fields) != len(ir["model"]["fields"]):
        raise IrError("model field names must be unique")
    for name in ir["query"]["filters"]:
        field = fields.get(name)
        if field is None or field["capabilities"]["filterable"] is not True:
            raise IrError(f"query filter is not backed by a filterable model field: {name}")
    for name in ir["query"]["sorting"]["allowlist"]:
        field = fields.get(name)
        if field is None or field["capabilities"]["sortable"] is not True:
            raise IrError(f"query sort key is not backed by a sortable model field: {name}")

    default_sort = ir["query"]["sorting"]["default"]["field"]
    if default_sort not in ir["query"]["sorting"]["allowlist"]:
        raise IrError("default sort field must be present in the sort allowlist")

    business_keys = {key["field"]: key for key in ir["resource"]["businessKeys"]}
    for field_name in business_keys:
        field = fields.get(field_name)
        if field is None or field["capabilities"]["businessKey"] is not True:
            raise IrError(f"business key is not backed by a business-key model field: {field_name}")
    for lookup in ir["detail"]["alternateLookups"]:
        field_name = lookup["businessKey"]
        if field_name not in business_keys:
            raise IrError(f"alternate lookup has no matching business key: {lookup['key']}")
        if lookup["relativePath"] != business_keys[field_name]["lookupPath"]:
            raise IrError(f"alternate lookup path differs from its business-key path: {lookup['key']}")

    dto = ir["model"]["dto"]
    entity = ir["model"]["entity"]
    if dto["create"] == dto["update"]:
        raise IrError("CreateDTO and UpdateDTO must remain distinct")
    if dto["create"] == entity or dto["update"] == entity:
        raise IrError("domain entity must not be used as an inbound request DTO")

    operation_pairs: set[tuple[str, str]] = set()
    operations = list(ir["query"]["operations"])
    operations.append(ir["detail"]["byId"])
    operations.extend(ir["detail"]["alternateLookups"])
    operations.extend(ir["write"].values())
    for item in operations:
        pair = (item["method"], item["absolutePath"])
        if pair in operation_pairs:
            raise IrError(f"duplicate HTTP operation in IR: {pair[0]} {pair[1]}")
        operation_pairs.add(pair)

    if ir["delivery"]["outputMode"] != "patch-zip":
        raise IrError("IR delivery output must remain patch-zip")
    if ir["delivery"]["targetApply"] != "forbidden-in-springmaster":
        raise IrError("IR must not authorize direct target-project mutation")


def canonical_json(ir: dict[str, Any]) -> bytes:
    return (json.dumps(ir, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the GeneratedServiceSlice Intermediate Representation.")
    parser.add_argument("--spec", default=DEFAULT_SPEC, help=f"Slice-Spec YAML path (default: {DEFAULT_SPEC})")
    parser.add_argument("--out", default=DEFAULT_OUT, help=f"IR JSON path (default: {DEFAULT_OUT})")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    root = repo_root()
    spec_path = resolve_input(root, args.spec)
    out_path = resolve_input(root, args.out)
    fixture_gate = load_fixture_gate(root)

    if not spec_path.is_file():
        print(f"Generated Slice IR: FAIL\nSpec file is missing: {display_path(root, spec_path)}", file=sys.stderr)
        return 1
    spec_bytes = spec_path.read_bytes()
    try:
        document = fixture_gate.StrictYamlSubsetParser(spec_bytes.decode("utf-8")).parse()
    except (UnicodeDecodeError, fixture_gate.YamlSubsetError) as exc:
        print(f"Generated Slice IR: FAIL\nSlice-Spec parsing failed: {exc}", file=sys.stderr)
        return 1

    contract_errors = validate_input_contract(document)
    if contract_errors:
        print("Generated Slice IR: FAIL", file=sys.stderr)
        print("Slice-Spec contract violations:", file=sys.stderr)
        for error in contract_errors:
            print(f"  - {error}", file=sys.stderr)
        return 1

    try:
        ir = build_ir(
            document,
            display_path(root, spec_path),
            hashlib.sha256(spec_bytes).hexdigest(),
        )
    except (KeyError, TypeError, IrError) as exc:
        print(f"Generated Slice IR: FAIL\nIR normalization failed: {exc}", file=sys.stderr)
        return 1

    payload = canonical_json(ir)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(payload)
    print("Generated Slice IR: PASS")
    print(f"Spec:     {ir['source']['specPath']}")
    print(f"Slice:    {ir['source']['sliceId']}")
    print(f"Schema:   {ir['schemaVersion']}")
    print(f"IR-SHA:   {hashlib.sha256(payload).hexdigest()}")
    print(f"Output:   {display_path(root, out_path)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
