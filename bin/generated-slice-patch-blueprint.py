#!/usr/bin/env python3
"""Create a deterministic, non-mutating patch blueprint from Generated Slice IR.

The tool consumes only the canonical JSON IR from patch 000125. It does not
read Slice-Spec YAML, render Java sources, inspect Demo implementations, create
a patch archive or mutate a target repository.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

BLUEPRINT_SCHEMA_VERSION = "springmaster.generated-service-slice-patch-blueprint.v1"
SUPPORTED_IR_SCHEMA = "springmaster.generated-service-slice-ir.v1"
DEFAULT_IR = "src/test/resources/tooling/generated-slice-ir.business-partner.golden.json"
DEFAULT_OUT = "reports/tooling/generated-slice-patch-blueprint.business-partner.json"
IR_TOOL = "bin/generated-slice-ir.py"
BLUEPRINT_CONTRACT = "PROJECT_DOCS/TOOLING/GENERATED_SLICE_PATCH_BLUEPRINT_DRY_RUN.md"
EXPECTED_IR_SECTIONS = [
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
REQUIRED_REPORTS = [
    ("queryContract", "query-contract-gate-report"),
    ("detailLookupContract", "detail-lookup-contract-gate-report"),
    ("writeApiContract", "write-api-contract-gate-report"),
    ("requestValidationOpenApiGate", "request-validation-openapi-gate-report"),
]


class BlueprintError(ValueError):
    """Raised when the IR cannot be projected into a safe dry-run blueprint."""


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


def load_ir_tool(root: Path) -> ModuleType:
    tool_path = root / IR_TOOL
    spec = importlib.util.spec_from_file_location("springmaster_generated_slice_ir", tool_path)
    if spec is None or spec.loader is None:
        raise BlueprintError(f"cannot load Generated Slice IR validator: {tool_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def lower_camel_to_kebab(value: str) -> str:
    if not re.fullmatch(r"[A-Za-z][A-Za-z0-9]*", value):
        raise BlueprintError(f"resource name cannot be converted to a stable slug: {value!r}")
    first = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1-\2", value)
    second = re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", first)
    return second.lower()


def validate_ir(ir: Any, ir_tool: ModuleType) -> dict[str, Any]:
    if not isinstance(ir, dict):
        raise BlueprintError("IR root must be a JSON object")
    if list(ir.keys()) != EXPECTED_IR_SECTIONS:
        raise BlueprintError(
            "IR top-level sections are incomplete or out of canonical order: "
            f"expected={EXPECTED_IR_SECTIONS!r} actual={list(ir.keys())!r}"
        )
    if ir.get("schemaVersion") != SUPPORTED_IR_SCHEMA:
        raise BlueprintError(
            f"unsupported IR schema: expected={SUPPORTED_IR_SCHEMA} actual={ir.get('schemaVersion')!r}"
        )
    try:
        ir_tool.validate_ir(ir)
    except Exception as exc:  # preserve fail-closed diagnostics from the canonical IR validator
        raise BlueprintError(f"IR validation failed: {exc}") from exc

    packages = ir.get("packages", {})
    base_package = packages.get("base")
    module_package = packages.get("module")
    if not isinstance(base_package, str) or not isinstance(module_package, str):
        raise BlueprintError("IR packages.base and packages.module must be strings")
    prefix = base_package + "."
    if not module_package.startswith(prefix):
        raise BlueprintError(
            "IR module package must be below the IR base package so that a target-neutral suffix can be derived"
        )
    module_suffix = module_package[len(prefix):]
    if not module_suffix or any(not part for part in module_suffix.split(".")):
        raise BlueprintError("IR module package suffix is invalid")

    reports = ir.get("reports", {})
    for key, _ in REQUIRED_REPORTS:
        if reports.get(key) != "required":
            raise BlueprintError(f"IR report contract must remain required: reports.{key}")

    delivery = ir.get("delivery", {})
    expected_delivery = {
        "outputMode": "patch-zip",
        "targetApply": "forbidden-in-springmaster",
        "targetPatchDryRun": "required-before-apply",
        "targetMavenTest": "required-after-apply",
        "targetFullExport": "required-after-apply",
    }
    for key, expected in expected_delivery.items():
        if delivery.get(key) != expected:
            raise BlueprintError(
                f"IR delivery contract mismatch: delivery.{key} expected={expected!r} actual={delivery.get(key)!r}"
            )
    return ir


def artifact(path_template: str, artifact_type: str, role: str, required: bool = True) -> dict[str, Any]:
    return {
        "pathTemplate": path_template,
        "type": artifact_type,
        "role": role,
        "required": required,
        "state": "planned-not-rendered",
    }


def operation_plan(ir: dict[str, Any]) -> list[dict[str, Any]]:
    operations: list[dict[str, Any]] = []
    ordered: list[tuple[str, dict[str, Any]]] = []
    for item in ir["query"]["operations"]:
        ordered.append(("query", item))
    ordered.append(("detail", ir["detail"]["byId"]))
    for item in ir["detail"]["alternateLookups"]:
        ordered.append(("alternate-lookup", item))
    ordered.extend(("write", ir["write"][key]) for key in ("create", "update", "delete"))

    for family, item in ordered:
        entry: dict[str, Any] = {
            "key": item["key"],
            "family": family,
            "method": item["method"],
            "path": item["absolutePath"],
            "responseShape": item["responseShape"],
            "expectedSuccessStatus": item.get("successStatus", 200),
        }
        if "requestDto" in item:
            entry["requestDto"] = item["requestDto"]
        if "requestBody" in item:
            entry["requestBody"] = item["requestBody"]
        if "inherits" in item:
            entry["inherits"] = item["inherits"]
        if "businessKey" in item:
            entry["businessKey"] = item["businessKey"]
        operations.append(entry)
    return operations


def build_blueprint(ir: dict[str, Any], ir_path: str, ir_sha256: str) -> dict[str, Any]:
    packages = ir["packages"]
    resource = ir["resource"]
    model = ir["model"]
    dto = model["dto"]
    entity = model["entity"]
    module_suffix = packages["module"][len(packages["base"]) + 1:]
    module_suffix_path = module_suffix.replace(".", "/")
    target_module_package = "${targetBasePackage}." + module_suffix
    target_module_path = "${targetBasePackagePath}/" + module_suffix_path
    slice_slug = lower_camel_to_kebab(resource["name"])
    main_root = "src/main/java/" + target_module_path
    test_root = "src/test/java/" + target_module_path

    artifacts = [
        artifact(f"{main_root}/api/{entity}Controller.java", "java-source", "rest-controller"),
        artifact(f"{main_root}/application/{entity}Service.java", "java-source", "application-service"),
        artifact(f"{main_root}/domain/{entity}.java", "java-source", "domain-model"),
        artifact(f"{main_root}/dto/{dto['read']}.java", "java-source", "read-dto"),
        artifact(f"{main_root}/dto/{dto['listItem']}.java", "java-source", "list-item-dto"),
        artifact(f"{main_root}/dto/{dto['create']}.java", "java-source", "create-dto"),
        artifact(f"{main_root}/dto/{dto['update']}.java", "java-source", "update-dto"),
        artifact(f"{main_root}/mapper/{entity}Mapper.java", "java-source", "mapper"),
        artifact(f"{main_root}/validation/{entity}Validator.java", "java-source", "service-boundary-validator"),
        artifact(f"{test_root}/api/{entity}ControllerTest.java", "java-test", "controller-contract-test"),
        artifact(f"{test_root}/application/{entity}ServiceTest.java", "java-test", "service-contract-test"),
        artifact(f"{test_root}/mapper/{entity}MapperTest.java", "java-test", "mapper-contract-test"),
        artifact(f"{test_root}/validation/{entity}ValidatorTest.java", "java-test", "validator-contract-test"),
        artifact(
            f"PROJECT_DOCS/GENERATED_SLICES/{slice_slug}/GENERATED_SLICE_EVIDENCE.json",
            "json-evidence",
            "generated-slice-evidence",
        ),
        artifact(
            "patches/logs/root/CHANGELOG-${targetPatchId}.md",
            "markdown-changelog",
            "target-patch-changelog",
        ),
    ]

    reports = [
        {
            "key": key,
            "tool": tool,
            "required": True,
            "expectedResult": "findings=0",
        }
        for key, tool in REQUIRED_REPORTS
    ]

    source_tests = [
        {
            "pathTemplate": f"{test_root}/api/{entity}ControllerTest.java",
            "covers": ["query", "detail", "alternate-lookup", "write", "global-error-contract"],
        },
        {
            "pathTemplate": f"{test_root}/application/{entity}ServiceTest.java",
            "covers": ["create", "update", "delete", "not-found", "business-key-conflict"],
        },
        {
            "pathTemplate": f"{test_root}/mapper/{entity}MapperTest.java",
            "covers": [dto["read"], dto["listItem"], dto["create"], dto["update"]],
        },
        {
            "pathTemplate": f"{test_root}/validation/{entity}ValidatorTest.java",
            "covers": ["create-required-fields", "update-required-fields", "bean-validation-openapi-alignment"],
        },
    ]

    blueprint: dict[str, Any] = {
        "schemaVersion": BLUEPRINT_SCHEMA_VERSION,
        "source": {
            "irContract": ir["source"]["irContract"],
            "blueprintContract": BLUEPRINT_CONTRACT,
            "irPath": ir_path,
            "irSha256": ir_sha256,
            "irSchemaVersion": ir["schemaVersion"],
            "specSha256": ir["source"]["specSha256"],
            "sliceId": ir["source"]["sliceId"],
        },
        "projection": {
            "mode": "target-neutral-template",
            "sliceSlug": slice_slug,
            "sourceModulePackage": packages["module"],
            "modulePackageSuffix": module_suffix,
            "modulePathSuffix": module_suffix_path,
            "targetModulePackageTemplate": target_module_package,
            "targetModulePathTemplate": target_module_path,
            "requiredBindings": [
                "targetProjectKey",
                "targetBasePackage",
                "targetBasePackagePath",
                "targetPatchId",
                "targetBaselineHead",
                "targetBaselineSha256ByPath",
            ],
        },
        "patch": {
            "scope": "root",
            "patchIdTemplate": "${targetPatchId}",
            "archiveNameTemplate": "${targetPatchId}.zip",
            "manifestRequired": True,
            "baselinePolicy": "target-live-raw-repository-bytes",
            "archiveEntries": [
                "manifest.json",
                "files/**",
                "logs/CHANGELOG-${targetPatchId}.md",
            ],
            "mutationMode": "dry-run-only",
        },
        "artifacts": artifacts,
        "apiOperations": operation_plan(ir),
        "tests": {
            "sourceTests": source_tests,
            "reportGates": reports,
            "deliveryGates": [
                "target-patch-artifact-preflight",
                "target-patch-dry-run",
                "target-patch-apply-after-explicit-authorization",
                "target-targeted-tests",
                "target-full-maven-test",
                "target-git-diff-check",
                "target-full-export",
                "target-export-integrity-check",
            ],
        },
        "reports": reports,
        "delivery": {
            "output": "blueprint-json-only",
            "targetMutation": "forbidden",
            "sourceRendering": "forbidden-in-000126",
            "patchArchiveGeneration": "forbidden-in-000126",
            "targetApply": ir["delivery"]["targetApply"],
            "targetPatchDryRun": ir["delivery"]["targetPatchDryRun"],
            "targetMavenTest": ir["delivery"]["targetMavenTest"],
            "targetFullExport": ir["delivery"]["targetFullExport"],
            "nextPhase": "000127_springmaster_zbm_generated_slice_pilot_plan",
        },
        "blockers": [
            {
                "id": "target-baseline-binding",
                "status": "unresolved",
                "resolution": "current target Full-Export and clean committed HEAD required",
            },
            {
                "id": "target-package-binding",
                "status": "unresolved",
                "resolution": "target project base package required",
            },
            {
                "id": "persistence-contract",
                "status": "not-represented-in-ir-v1",
                "resolution": "pilot must explicitly choose candidate store or durable persistence before rendering",
            },
            {
                "id": "security-contract",
                "status": "not-represented-in-ir-v1",
                "resolution": "pilot must explicitly document deferred or implemented security before rendering",
            },
            {
                "id": "target-apply-authorization",
                "status": "blocked",
                "resolution": "explicit user approval required after target dry-run and tests",
            },
        ],
        "summary": {
            "plannedArtifacts": len(artifacts),
            "plannedJavaSources": sum(1 for item in artifacts if item["type"] == "java-source"),
            "plannedJavaTests": sum(1 for item in artifacts if item["type"] == "java-test"),
            "apiOperations": len(operation_plan(ir)),
            "reportGates": len(reports),
            "unresolvedBlockers": 5,
            "targetFilesWritten": 0,
            "patchArchivesWritten": 0,
        },
    }
    validate_blueprint(blueprint)
    return blueprint


def validate_blueprint(blueprint: dict[str, Any]) -> None:
    expected_sections = [
        "schemaVersion",
        "source",
        "projection",
        "patch",
        "artifacts",
        "apiOperations",
        "tests",
        "reports",
        "delivery",
        "blockers",
        "summary",
    ]
    if list(blueprint.keys()) != expected_sections:
        raise BlueprintError("blueprint sections are incomplete or out of canonical order")
    if blueprint["schemaVersion"] != BLUEPRINT_SCHEMA_VERSION:
        raise BlueprintError("blueprint schema mismatch")
    if blueprint["patch"]["scope"] != "root":
        raise BlueprintError("generated slice candidate blueprint must use the cross-cutting root scope")
    if blueprint["patch"]["mutationMode"] != "dry-run-only":
        raise BlueprintError("blueprint patch plan must remain dry-run-only")
    if blueprint["delivery"]["targetMutation"] != "forbidden":
        raise BlueprintError("blueprint must forbid target mutation")
    if blueprint["delivery"]["sourceRendering"] != "forbidden-in-000126":
        raise BlueprintError("source rendering must remain outside patch 000126")
    if blueprint["delivery"]["patchArchiveGeneration"] != "forbidden-in-000126":
        raise BlueprintError("patch archive generation must remain outside patch 000126")

    paths = [item["pathTemplate"] for item in blueprint["artifacts"]]
    if len(paths) != len(set(paths)):
        raise BlueprintError("planned artifact paths must be unique")
    if any(path.startswith(("/", "~")) or ".." in Path(path).parts for path in paths):
        raise BlueprintError("planned artifact paths must be safe repository-relative templates")
    if any("de/cocondo/platform/demo" in path.lower() or "catalogitem" in path.lower() for path in paths):
        raise BlueprintError("planned target artifacts must not contain Demo or CatalogItem paths")
    if any(item.get("state") != "planned-not-rendered" for item in blueprint["artifacts"]):
        raise BlueprintError("all blueprint artifacts must remain planned-not-rendered")

    operation_pairs = [(item["method"], item["path"]) for item in blueprint["apiOperations"]]
    if len(operation_pairs) != len(set(operation_pairs)):
        raise BlueprintError("blueprint API operations must be unique")
    if len(blueprint["reports"]) != 4 or any(item["required"] is not True for item in blueprint["reports"]):
        raise BlueprintError("all four report gates must remain required")
    if blueprint["summary"]["targetFilesWritten"] != 0 or blueprint["summary"]["patchArchivesWritten"] != 0:
        raise BlueprintError("dry-run blueprint must report zero target mutations and zero patch archives")


def canonical_json(blueprint: dict[str, Any]) -> bytes:
    return (json.dumps(blueprint, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a non-mutating Generated Slice patch blueprint dry-run.")
    parser.add_argument("--ir", default=DEFAULT_IR, help=f"Canonical IR JSON path (default: {DEFAULT_IR})")
    parser.add_argument("--out", default=DEFAULT_OUT, help=f"Blueprint JSON path (default: {DEFAULT_OUT})")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    root = repo_root()
    ir_path = resolve_input(root, args.ir)
    out_path = resolve_input(root, args.out)

    if not ir_path.is_file():
        print(f"Generated Slice Patch Blueprint: FAIL\nIR file is missing: {display_path(root, ir_path)}", file=sys.stderr)
        return 1
    ir_bytes = ir_path.read_bytes()
    try:
        ir = json.loads(ir_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        print(f"Generated Slice Patch Blueprint: FAIL\nIR JSON parsing failed: {exc}", file=sys.stderr)
        return 1

    try:
        ir_tool = load_ir_tool(root)
        validated_ir = validate_ir(ir, ir_tool)
        blueprint = build_blueprint(validated_ir, display_path(root, ir_path), hashlib.sha256(ir_bytes).hexdigest())
    except (KeyError, TypeError, BlueprintError) as exc:
        print(f"Generated Slice Patch Blueprint: FAIL\nBlueprint planning failed: {exc}", file=sys.stderr)
        return 1

    payload = canonical_json(blueprint)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(payload)
    print("Generated Slice Patch Blueprint: PASS")
    print(f"IR:         {blueprint['source']['irPath']}")
    print(f"Slice:      {blueprint['source']['sliceId']}")
    print(f"Schema:     {blueprint['schemaVersion']}")
    print(f"Artifacts:  {blueprint['summary']['plannedArtifacts']}")
    print(f"Operations: {blueprint['summary']['apiOperations']}")
    print(f"Mutations:  {blueprint['summary']['targetFilesWritten']}")
    print(f"ZIPs:       {blueprint['summary']['patchArchivesWritten']}")
    print(f"SHA-256:    {hashlib.sha256(payload).hexdigest()}")
    print(f"Output:     {display_path(root, out_path)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
