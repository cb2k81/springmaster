#!/usr/bin/env python3
"""Validate and package the accepted Cocondo backend operation contracts."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import zipfile
from pathlib import Path
from typing import Any


KINDS = {"QUERY", "COMMAND", "PRECHECK", "CAPABILITY_EVALUATION"}
ROLES = {
    "ENTITY_LIST", "ENTITY_DETAIL", "ENTITY_CREATE", "ENTITY_UPDATE", "ENTITY_DELETE",
    "REFERENCE_LOOKUP", "RELATION_LIST", "CANDIDATE_LIST", "OVERVIEW_LIST", "HISTORY_LIST",
    "PROJECTION_READ", "TEMPORAL_READ", "BULK_COMMAND", "BULK_STATUS", "EXPORT",
    "AGGREGATION", "DELTA_READ",
}
PRECONDITIONS = {"NONE", "EXPECTED_VERSION", "EXPECTED_VERSION_SET", "SNAPSHOT_TOKEN", "ETAG"}
HISTORY_MODELS = {"NONE", "ROOT_VERSION", "PLAN_SNAPSHOT", "APPEND_ONLY", "TEMPORAL_RELATION"}
TRANSACTION_SCOPES = {"SINGLE_AGGREGATE", "AGGREGATE_GRAPH", "MULTI_AGGREGATE"}
CONSISTENCY_STRATEGIES = {"OPTIMISTIC", "PESSIMISTIC", "MIXED"}
SCHEMA_NAMES = (
    "backend-operation-profile.schema.v1.json",
    "backend-resource-semantics.schema.v1.json",
    "backend-precondition-profile.schema.v1.json",
    "backend-bulk-operation-profile.schema.v1.json",
    "backend-implementation-evidence.schema.v1.json",
    "operation-catalog.schema.v1.json",
    "contract-manifest.schema.v1.json",
)


class ContractError(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ContractError("BACKEND_CONTRACT_INVALID_JSON", f"Cannot read JSON {path}: {error}") from error


def repository_root() -> Path:
    return Path(__file__).resolve().parent.parent


def resolve_index(path_text: str) -> tuple[Path, dict[str, Any]]:
    path = Path(path_text).resolve()
    value = read_json(path)
    if not isinstance(value, dict) or not isinstance(value.get("fixtures"), list):
        raise ContractError("BACKEND_CONTRACT_INVALID_FIXTURE_INDEX", "Fixture index must contain fixtures[]")
    ids: set[str] = set()
    for entry in value["fixtures"]:
        fixture_id = entry.get("fixtureId") if isinstance(entry, dict) else None
        if not fixture_id or fixture_id in ids:
            raise ContractError("BACKEND_CONTRACT_INVALID_FIXTURE_INDEX", "Fixture IDs must be non-empty and unique")
        ids.add(fixture_id)
        expected = entry.get("expectedResult")
        diagnostic = entry.get("expectedDiagnosticCode")
        if expected not in {"PASS", "FAIL"} or (expected == "PASS" and diagnostic is not None) or (expected == "FAIL" and not diagnostic):
            raise ContractError("BACKEND_CONTRACT_INVALID_FIXTURE_INDEX", f"Invalid expectation for {fixture_id}")
        for field in ("capabilityIds", "requirementIds"):
            if not isinstance(entry.get(field), list) or not entry[field]:
                raise ContractError("BACKEND_CONTRACT_INVALID_FIXTURE_INDEX", f"Missing {field} for {fixture_id}")
        if entry.get("sourceKind") not in {"IMMUTABLE_REFERENCE", "SYNTHETIC_CONTRACT"}:
            raise ContractError("BACKEND_CONTRACT_INVALID_FIXTURE_INDEX", f"Invalid sourceKind for {fixture_id}")
    return path, value


def fixture_path(entry: dict[str, Any]) -> Path:
    root = repository_root()
    relative = Path(entry["path"])
    path = (root / relative).resolve()
    try:
        path.relative_to(root)
    except ValueError as error:
        raise ContractError("BACKEND_CONTRACT_FIXTURE_PATH_FORBIDDEN", str(relative)) from error
    if not path.is_file():
        raise ContractError("BACKEND_CONTRACT_FIXTURE_MISSING", str(relative))
    return path


def require_operation_shape(operation: Any) -> None:
    if not isinstance(operation, dict):
        raise ContractError("BACKEND_CONTRACT_INVALID_OPERATION", "Operation must be an object")
    required = ("operationKey", "operationId", "method", "path", "operationKind", "operationRoles", "security", "effects")
    if any(field not in operation for field in required):
        raise ContractError("BACKEND_CONTRACT_INVALID_OPERATION", f"Incomplete operation {operation.get('operationKey')}")
    if not all(isinstance(operation.get(field), str) and operation[field] for field in ("operationKey", "operationId", "method", "path")):
        raise ContractError("BACKEND_CONTRACT_INVALID_OPERATION", "Operation identity fields must be non-empty strings")
    if not operation["path"].startswith("/api/"):
        raise ContractError("BACKEND_CONTRACT_INVALID_OPERATION", f"Non-API path {operation['path']}")


def validate_document(document: Any) -> None:
    if not isinstance(document, dict):
        raise ContractError("BACKEND_CONTRACT_INVALID_DOCUMENT", "Fixture must be an object")
    operations = document.get("operations", [])
    resources = document.get("resources", [])
    if not isinstance(operations, list) or not isinstance(resources, list):
        raise ContractError("BACKEND_CONTRACT_INVALID_DOCUMENT", "operations and resources must be arrays")

    keys: set[str] = set()
    technical: set[tuple[str, str, str]] = set()
    resource_by_key: dict[str, dict[str, Any]] = {}
    for resource in resources:
        if not isinstance(resource, dict) or not resource.get("resourceKey"):
            raise ContractError("BACKEND_CONTRACT_INVALID_RESOURCE", "Resource semantics require resourceKey")
        if resource.get("historyModel") not in HISTORY_MODELS:
            raise ContractError("BACKEND_CONTRACT_UNKNOWN_HISTORY_MODEL", str(resource.get("historyModel")))
        resource_by_key[resource["resourceKey"]] = resource

    for operation in operations:
        require_operation_shape(operation)
        key = operation["operationKey"]
        identity = (operation["method"].upper(), operation["path"], operation["operationId"])
        if key in keys:
            raise ContractError("BACKEND_CONTRACT_DUPLICATE_OPERATION_KEY", key)
        if identity in technical:
            raise ContractError("BACKEND_CONTRACT_DUPLICATE_TECHNICAL_IDENTITY", "|".join(identity))
        keys.add(key)
        technical.add(identity)

        roles = operation.get("operationRoles")
        if isinstance(roles, list) and "WORKSPACE" in roles:
            raise ContractError("BACKEND_CONTRACT_WORKSPACE_OPERATION_FORBIDDEN", key)
        if operation.get("operationKind") not in KINDS:
            raise ContractError("BACKEND_CONTRACT_UNKNOWN_OPERATION_KIND", str(operation.get("operationKind")))
        if not isinstance(roles, list) or any(role not in ROLES for role in roles):
            raise ContractError("BACKEND_CONTRACT_UNKNOWN_OPERATION_ROLE", str(roles))

        effects = operation.get("effects")
        if not isinstance(effects, dict) or "affectedResourceKeys" not in effects:
            raise ContractError("BACKEND_CONTRACT_EFFECTS_REQUIRED", key)
        forbidden_effects = {"reloadGraph", "refresh", "workspace", "dirtyState", "staleResponse"}.intersection(effects)
        if forbidden_effects:
            raise ContractError("BACKEND_CONTRACT_UI_RELOAD_GRAPH_FORBIDDEN", key)
        if set(effects) != {"affectedResourceKeys"} or not isinstance(effects["affectedResourceKeys"], list):
            raise ContractError("BACKEND_CONTRACT_UI_RELOAD_GRAPH_FORBIDDEN", key)

        security = operation.get("security")
        if not isinstance(security, dict) or not {"classification", "permissions", "targetAuthorization"}.issubset(security):
            raise ContractError("BACKEND_CONTRACT_SECURITY_PROFILE_REQUIRED", key)
        if security.get("classification") not in {"PUBLIC", "AUTHENTICATED", "MANAGEMENT", "TECHNICAL", "SYSTEM"}:
            raise ContractError("BACKEND_CONTRACT_SECURITY_PROFILE_REQUIRED", key)
        if not isinstance(security.get("permissions"), list) or (security.get("classification") == "MANAGEMENT" and not security["permissions"]):
            raise ContractError("BACKEND_CONTRACT_SECURITY_PROFILE_REQUIRED", key)
        if security.get("targetAuthorization") not in {"NONE", "REQUEST_CONTEXT", "EACH_TARGET"}:
            raise ContractError("BACKEND_CONTRACT_SECURITY_PROFILE_REQUIRED", key)
        if ("CANDIDATE_LIST" in roles or security.get("targetAuthorization") == "REQUEST_CONTEXT") and not operation.get("targetContextRequired"):
            raise ContractError("BACKEND_CONTRACT_TARGET_CONTEXT_REQUIRED", key)
        if "TEMPORAL_READ" in roles and not operation.get("temporalContext"):
            raise ContractError("BACKEND_CONTRACT_TEMPORAL_CONTEXT_REQUIRED", key)
        if "PROJECTION_READ" in roles and not operation.get("projectionResponseSchema"):
            raise ContractError("BACKEND_CONTRACT_PROJECTION_RESPONSE_REQUIRED", key)

        precondition = operation.get("precondition")
        if precondition is not None:
            if not isinstance(precondition, dict) or precondition.get("type") not in PRECONDITIONS:
                raise ContractError("BACKEND_CONTRACT_UNKNOWN_PRECONDITION", key)
            if precondition.get("type") == "SNAPSHOT_TOKEN" and not precondition.get("producerOperationKey"):
                raise ContractError("BACKEND_CONTRACT_SNAPSHOT_TOKEN_PRODUCER_REQUIRED", key)
            if precondition.get("type") in {"EXPECTED_VERSION", "EXPECTED_VERSION_SET", "SNAPSHOT_TOKEN"} and (precondition.get("binding") != "BODY" or precondition.get("conflictStatus") != 409):
                raise ContractError("BACKEND_CONTRACT_PRECONDITION_BINDING_INVALID", key)
            if precondition.get("type") == "ETAG" and (precondition.get("binding") != "HEADER" or precondition.get("conflictStatus") != 412 or (precondition.get("required") and precondition.get("missingStatus") != 428)):
                raise ContractError("BACKEND_CONTRACT_PRECONDITION_BINDING_INVALID", key)
            if precondition.get("type") == "NONE" and (precondition.get("required") or precondition.get("binding") != "NONE"):
                raise ContractError("BACKEND_CONTRACT_PRECONDITION_BINDING_INVALID", key)

        resource = resource_by_key.get(operation.get("resourceKey"))
        if resource and resource.get("historyModel") == "APPEND_ONLY" and ({"ENTITY_UPDATE", "ENTITY_DELETE"}.intersection(roles) or operation["method"] in {"PUT", "PATCH", "DELETE"}):
            raise ContractError("BACKEND_CONTRACT_APPEND_ONLY_MUTATION_FORBIDDEN", key)

        if "BULK_COMMAND" in roles:
            bulk = operation.get("bulkProfile")
            if not isinstance(bulk, dict) or not bulk.get("atomicity"):
                raise ContractError("BACKEND_CONTRACT_BULK_ATOMICITY_REQUIRED", key)
            if not bulk.get("nonDisclosure"):
                raise ContractError("BACKEND_CONTRACT_NON_DISCLOSURE_REQUIRED", key)
            selection = bulk.get("selection", {})
            if selection.get("mode") == "QUERY_SNAPSHOT" and selection.get("frozenBeforeExecution") is not True:
                raise ContractError("BACKEND_CONTRACT_QUERY_SELECTION_FREEZE_REQUIRED", key)
            delivery = bulk.get("resultDelivery", {})
            if bulk.get("execution") == "ASYNCHRONOUS" and (delivery.get("mode") != "STATUS_RESOURCE" or not delivery.get("statusOperationKey") or not delivery.get("resultOperationKey")):
                raise ContractError("BACKEND_CONTRACT_ASYNC_RESULT_CONTRACT_REQUIRED", key)
            bulk_required = {"selection", "atomicity", "execution", "targetAuthorization", "nonDisclosure", "idempotency", "limits", "outcomes", "resultDelivery"}
            if not bulk_required.issubset(bulk) or bulk.get("targetAuthorization") != "EACH_TARGET_AT_EXECUTION" or security.get("targetAuthorization") != "EACH_TARGET":
                raise ContractError("BACKEND_CONTRACT_BULK_PROFILE_INCOMPLETE", key)

    for operation in operations:
        precondition = operation.get("precondition") or {}
        if precondition.get("type") == "SNAPSHOT_TOKEN" and precondition.get("producerOperationKey") not in keys:
            raise ContractError("BACKEND_CONTRACT_SNAPSHOT_TOKEN_PRODUCER_REQUIRED", operation["operationKey"])

    consistency = document.get("consistency")
    if consistency is not None:
        if consistency.get("strategy") not in CONSISTENCY_STRATEGIES or consistency.get("transactionScope") not in TRANSACTION_SCOPES:
            raise ContractError("BACKEND_CONTRACT_UNKNOWN_CONSISTENCY", "Invalid consistency classification")
        if consistency.get("strategy") in {"PESSIMISTIC", "MIXED"}:
            mutations = [op for op in operations if op.get("operationKind") == "COMMAND"]
            if mutations and any(not op.get("precondition") or op["precondition"].get("type") == "NONE" for op in mutations):
                raise ContractError("BACKEND_CONTRACT_VERSION_TOKEN_REQUIRED", mutations[0]["operationKey"])

    ui_spec = document.get("uiSpec")
    if ui_spec is not None:
        if not isinstance(ui_spec, dict):
            raise ContractError("BACKEND_CONTRACT_INVALID_UI_SPEC", "uiSpec must be an object")
        if ui_spec.get("version") == "1.1" and "operationKey" in ui_spec:
            raise ContractError("BACKEND_CONTRACT_GWC_V11_COMPATIBILITY_REQUIRED", "v1.1 cannot require operationKey")
        if ui_spec.get("version") == "1.2" and ui_spec.get("pattern") != "WORKSPACE":
            binding = ui_spec.get("binding", {})
            if not all(binding.get(field) for field in ("operationKey", "method", "path", "operationId")):
                raise ContractError("BACKEND_CONTRACT_GWC_BINDING_REQUIRED", "Incomplete v1.2 binding")

    competing_authorities = {key for key in document if key.startswith("x-cocondo-") and key != "x-cocondo-operation-profile"}
    if competing_authorities or document.get("generatedApplicationNormative") is True:
        raise ContractError("BACKEND_CONTRACT_AMBIGUOUS_AUTHORITY", "Competing semantic authority")


def validate_suite(index: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    results: list[dict[str, Any]] = []
    positive_documents: list[dict[str, Any]] = []
    for entry in index["fixtures"]:
        observed = "PASS"
        diagnostic = None
        document: dict[str, Any] | None = None
        try:
            value = read_json(fixture_path(entry))
            validate_document(value)
            document = value
        except ContractError as error:
            observed = "FAIL"
            diagnostic = error.code
        qualified = observed == entry["expectedResult"] and diagnostic == entry.get("expectedDiagnosticCode")
        results.append({
            "fixtureId": entry["fixtureId"],
            "expectedResult": entry["expectedResult"],
            "observedResult": observed,
            "diagnosticCode": diagnostic,
            "status": "PASS" if qualified else "FAIL",
        })
        if qualified and observed == "PASS" and document is not None:
            positive_documents.append(document)
    return results, positive_documents


def build_catalog(documents: list[dict[str, Any]]) -> dict[str, Any]:
    by_key: dict[str, dict[str, Any]] = {}
    technical: dict[tuple[str, str, str], str] = {}
    for document in documents:
        for operation in document.get("operations", []):
            normalized = json.loads(canonical_bytes(operation))
            key = normalized["operationKey"]
            identity = (normalized["method"].upper(), normalized["path"], normalized["operationId"])
            previous = by_key.get(key)
            if previous is not None and previous != normalized:
                raise ContractError("BACKEND_CONTRACT_DUPLICATE_OPERATION_KEY", key)
            previous_key = technical.get(identity)
            if previous_key is not None and previous_key != key:
                raise ContractError("BACKEND_CONTRACT_DUPLICATE_TECHNICAL_IDENTITY", "|".join(identity))
            by_key[key] = normalized
            technical[identity] = key
    operations = sorted(by_key.values(), key=lambda item: item["operationKey"])
    return {"schemaVersion": "cocondo.operation-catalog.v1", "operations": operations, "aliases": []}


def qualification(index: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    results, documents = validate_suite(index)
    failures = [item for item in results if item["status"] != "PASS"]
    if failures:
        first = failures[0]
        raise ContractError("BACKEND_CONTRACT_FIXTURE_EXPECTATION_MISMATCH", first["fixtureId"])
    return results, build_catalog(documents)


def emit(payload: dict[str, Any], success: bool = True) -> int:
    sys.stdout.buffer.write(canonical_bytes(payload))
    return 0 if success else 1


def write_catalog(path: Path, catalog: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_bytes(catalog))


def export_bundle(index_path: Path, index: dict[str, Any], output: Path, catalog: dict[str, Any]) -> str:
    root = repository_root()
    catalog_data = canonical_bytes(catalog)
    index_data = canonical_bytes(index)
    files: list[tuple[str, bytes]] = [("operation-catalog.v1.json", catalog_data), ("fixture-index.v1.json", index_data)]
    for name in SCHEMA_NAMES:
        schema_path = root / "contracts" / "api" / "schemas" / name
        files.append((f"schemas/{name}", canonical_bytes(read_json(schema_path))))
    provenance = [{key: entry.get(key) for key in ("fixtureId", "sourceKind", "sourceProject", "sourceSha256")} for entry in index["fixtures"]]
    manifest = {
        "schemaVersion": "cocondo.contract-manifest.v1",
        "catalogSha256": sha256(catalog_data),
        "fixtureIndexSha256": sha256(index_data),
        "files": [{"path": name, "sha256": sha256(data)} for name, data in sorted(files)],
        "provenance": sorted(provenance, key=lambda item: item["fixtureId"]),
    }
    files.append(("contract-manifest.v1.json", canonical_bytes(manifest)))
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, data in sorted(files):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    return sha256(output.read_bytes())


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    subparsers = root.add_subparsers(dest="command", required=True)
    for command in ("validate", "catalog", "verify", "export"):
        sub = subparsers.add_parser(command)
        sub.add_argument("--fixture-index", required=True)
        sub.add_argument("--format", choices=["json"], default="json")
        if command in {"catalog", "export"}:
            sub.add_argument("--output", required=True)
        if command == "verify":
            sub.add_argument("--catalog", required=True)
    return root


def main() -> int:
    args = parser().parse_args()
    try:
        index_path, index = resolve_index(args.fixture_index)
        results, catalog = qualification(index)
        if args.command == "validate":
            return emit({"command": "validate", "diagnosticCode": None, "fixtureCount": len(results), "status": "PASS", "results": results})
        if args.command == "catalog":
            output = Path(args.output).resolve()
            write_catalog(output, catalog)
            return emit({"command": "catalog", "diagnosticCode": None, "operationCount": len(catalog["operations"]), "output": str(output), "sha256": sha256(output.read_bytes()), "status": "PASS"})
        if args.command == "verify":
            catalog_path = Path(args.catalog).resolve()
            actual = catalog_path.read_bytes() if catalog_path.is_file() else b""
            expected = canonical_bytes(catalog)
            if actual != expected:
                raise ContractError("BACKEND_CONTRACT_CATALOG_DRIFT", str(catalog_path))
            return emit({"command": "verify", "diagnosticCode": None, "operationCount": len(catalog["operations"]), "status": "PASS", "sha256": sha256(actual)})
        output = Path(args.output).resolve()
        bundle_hash = export_bundle(index_path, index, output, catalog)
        return emit({"command": "export", "diagnosticCode": None, "output": str(output), "status": "PASS", "sha256": bundle_hash})
    except ContractError as error:
        return emit({"command": getattr(args, "command", None), "diagnosticCode": error.code, "message": error.message, "status": "FAIL"}, success=False)
    except OSError as error:
        return emit({"command": getattr(args, "command", None), "diagnosticCode": "BACKEND_CONTRACT_IO_ERROR", "message": str(error), "status": "FAIL"}, success=False)


if __name__ == "__main__":
    raise SystemExit(main())
