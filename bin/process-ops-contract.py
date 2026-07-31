#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path
from typing import Any

FORBIDDEN = (
    re.compile(r"/mnt/data"),
    re.compile(r"/opt/cocondo"),
    re.compile(r"/home/[^/\s]+"),
)
FORBIDDEN_PROCESS_WORDS = (re.compile(r"\bnohup\b"), re.compile(r"\bsetsid\b"))


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def parse_env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        key, separator, value = line.partition("=")
        if not separator:
            raise ValueError(f"Invalid env line: {line}")
        values[key.strip()] = value.strip()
    return values


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root")
    parser.add_argument("--contract", default="contracts/governance/tooling/process-operations-contract.json")
    parser.add_argument("--out", default="target/process-operations-contract-report.json")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    root = Path(args.root).resolve() if args.root else Path(__file__).resolve().parents[1]
    findings: list[dict[str, Any]] = []

    contract_path = root / args.contract
    try:
        contract = read_json(contract_path)
    except Exception as exc:
        findings.append({"code": "PROCESS_CONTRACT_INVALID", "detail": str(exc)})
        contract = {}

    if contract.get("schemaVersion") != "cocondo.process-operations-contract.v1":
        findings.append({"code": "PROCESS_CONTRACT_SCHEMA_MISMATCH", "actual": contract.get("schemaVersion")})
    if contract.get("projectNeutral") is not True:
        findings.append({"code": "PROCESS_CONTRACT_NOT_PROJECT_NEUTRAL"})

    background = contract.get("backgroundPolicy") if isinstance(contract.get("backgroundPolicy"), dict) else {}
    singleton_expected = {
        "singletonStartSupported": True,
        "singletonLockDirectory": "CPROCESS_STATE_DIRECTORY/locks",
        "singletonPointerDirectory": "CPROCESS_STATE_DIRECTORY/pointers",
        "duplicateActiveStart": "REUSE_EXISTING_RUN",
        "terminalRestartRequiresExplicitFlag": True,
    }
    for key, expected in singleton_expected.items():
        if background.get(key) != expected:
            findings.append({
                "code": "PROCESS_SINGLETON_POLICY_MISMATCH",
                "key": key,
                "expected": expected,
                "actual": background.get(key),
            })

    workspace = contract.get("operatorWorkspacePolicy") if isinstance(contract.get("operatorWorkspacePolicy"), dict) else {}
    workspace_expected = {
        "scope": "one-current-writer-workflow",
        "pathMustBeProjectRelative": True,
        "rootMustAlreadyExist": True,
        "implicitRootCreation": "forbidden",
        "cleanupTrigger": "before-each-writer",
        "observerMutationForbidden": True,
        "activeWorkflowCleanup": "block",
        "unresolvedWorkflowCleanup": "block",
        "trackedContent": "block",
        "symlinkContent": "block",
        "nestedRepositoryContent": "block",
        "specialFileContent": "block",
        "mountPointContent": "block",
        "workspaceRootPreserved": True,
        "workspaceRecordSchema": "cocondo.operator-workspace.v2",
        "diagnosticHandoffCommand": "diagnostic-handoff",
        "diagnosticArchiveCount": 1,
        "agentWritePolicy": "forbidden",
    }
    for key, expected in workspace_expected.items():
        if workspace.get(key) != expected:
            findings.append({
                "code": "PROCESS_WORKSPACE_POLICY_MISMATCH",
                "key": key,
                "expected": expected,
                "actual": workspace.get(key),
            })


    writers = workspace.get("writers") if isinstance(workspace.get("writers"), list) else []
    expected_writers = {
        "workspace-start", "patch-dry-run", "patch-accept", "diagnose",
        "incident", "diagnostic-handoff", "delivery-prepare",
    }
    if set(writers) != expected_writers:
        findings.append({"code": "PROCESS_WORKSPACE_WRITER_SET_MISMATCH", "expected": sorted(expected_writers), "actual": sorted(writers)})

    chaining = contract.get("commandChainingPolicy") if isinstance(contract.get("commandChainingPolicy"), dict) else {}
    if chaining.get("allowedChain") != ["preflight", "writer-start", "lightweight-observation", "terminal-result"] or chaining.get("allTransitionsRequireExitZero") is not True or chaining.get("stageEvidenceRequired") is not True or chaining.get("stopOnFirstFailure") is not True:
        findings.append({"code": "PROCESS_COMMAND_CHAINING_POLICY_MISMATCH"})
    if chaining.get("automaticDryRunToAccept") != "forbidden" or chaining.get("automaticDiagnosisToRepair") != "forbidden" or chaining.get("automaticFailedRunRetry") != "forbidden":
        findings.append({"code": "PROCESS_COMMAND_CHAINING_BOUNDARY_MISMATCH"})

    console = contract.get("consoleOutputPolicy") if isinstance(contract.get("consoleOutputPolicy"), dict) else {}
    if console.get("fullJsonInventoryDefault") != "forbidden" or console.get("continuousLogStreamingDefault") != "forbidden" or console.get("boundedFailureTail") is not True:
        findings.append({"code": "PROCESS_CONSOLE_OUTPUT_POLICY_MISMATCH"})

    recovery = contract.get("failureRecoveryPolicy") if isinstance(contract.get("failureRecoveryPolicy"), dict) else {}
    if recovery.get("blindRetry") != "forbidden" or recovery.get("canonicalStateInspectionRequired") is not True or recovery.get("diagnoseUnknownTargetStateBeforeRemediation") is not True or recovery.get("preserveEvidenceBeforeCleanup") is not True:
        findings.append({"code": "PROCESS_FAILURE_RECOVERY_POLICY_MISMATCH"})

    diagnostic = contract.get("diagnosticHandoffPolicy") if isinstance(contract.get("diagnosticHandoffPolicy"), dict) else {}
    if diagnostic.get("onlineChatPath") != "patches/work/diagnostic-<operation-id>.zip" or diagnostic.get("onlineChatArchiveCount") != 1 or diagnostic.get("codexUsesOperatorWorkspace") is not False or diagnostic.get("cleanupTrigger") != "before-each-writer-not-observer":
        findings.append({"code": "PROCESS_DIAGNOSTIC_HANDOFF_POLICY_MISMATCH"})

    ingress = contract.get("artifactIngressPolicy") if isinstance(contract.get("artifactIngressPolicy"), dict) else {}
    if ingress.get("selectionKey") != "expected-sha256" or ingress.get("multipleIdenticalHashMatches") != "deterministic-sorted-selection" or ingress.get("conflictingHashes") != "block" or ingress.get("regularFileModeBinding") != "git-executable-bit" or ingress.get("hostModeNormalizationAfterHashCheck") is not True:
        findings.append({"code": "PROCESS_ARTIFACT_INGRESS_POLICY_MISMATCH"})

    writer_policy = contract.get("writerPolicy") if isinstance(contract.get("writerPolicy"), dict) else {}
    if set(writer_policy.get("commands", [])) != expected_writers:
        findings.append({"code": "PROCESS_WRITER_POLICY_MISMATCH"})
    if writer_policy.get("centralFacade") != "bin/process-ops.sh" or writer_policy.get("workspaceStartRequired") is not True:
        findings.append({"code": "PROCESS_WRITER_FACADE_MISMATCH"})
    if writer_policy.get("freeChatOrchestration") != "forbidden" or writer_policy.get("workerStartBeforePreflight") != "forbidden":
        findings.append({"code": "PROCESS_WRITER_BOUNDARY_MISMATCH"})

    artifact_policy = contract.get("artifactRootAuthorizationPolicy") if isinstance(contract.get("artifactRootAuthorizationPolicy"), dict) else {}
    artifact_expected = {
        "configurationIsAuthorization": False,
        "configurationAmbiguity": "BLOCKING_TOOL_ERROR",
        "rootMustAlreadyExist": True,
        "implicitRootCreation": "forbidden",
        "canonicalPathRequired": True,
        "authorizationRecord": "CPROCESS_ARTIFACT_AUTHORIZATION_RECORD",
        "recordSchema": "cocondo.artifact-root-authorization.v1",
        "unauthorizedWorkerStart": "block",
        "remediationStateRoot": "CPROCESS_DELIVERY_DIRECTORY",
    }
    for key, expected in artifact_expected.items():
        if artifact_policy.get(key) != expected:
            findings.append({"code": "PROCESS_ARTIFACT_AUTHORIZATION_POLICY_MISMATCH", "key": key, "expected": expected, "actual": artifact_policy.get(key)})
    required_bindings = {"projectId", "configuredPath", "canonicalPath", "device", "inode"}
    if set(artifact_policy.get("recordBinding", [])) != required_bindings:
        findings.append({"code": "PROCESS_ARTIFACT_AUTHORIZATION_BINDING_MISMATCH"})

    inventory_policy = contract.get("deliveryInventoryPolicy") if isinstance(contract.get("deliveryInventoryPolicy"), dict) else {}
    expected_entry_policies = {
        "deliveryDirectory": "RESERVE",
        "knownHistoricalMetadata": "IGNORE_AND_COUNT",
        "genericRunRecord": "IGNORE_AND_COUNT",
        "patchRunRecord": "RESERVE",
        "legacyNumericPatchRunRecord": "RESERVE",
        "acceptedPatchRecord": "RESERVE",
        "historicalFailedRunUnderAcceptedOwner": "IGNORE_AND_COUNT",
        "currentDelivery": "CURRENT_DELIVERY_EXCEPTION",
        "unknownRegularFile": "BLOCKING_TOOL_ERROR",
        "symlink": "BLOCKING_TOOL_ERROR",
        "specialFile": "BLOCKING_TOOL_ERROR",
        "unreadableOrInconsistentJson": "BLOCKING_TOOL_ERROR",
        "identityConflict": "BLOCKING_TOOL_ERROR",
    }
    if inventory_policy.get("entryPolicies") != expected_entry_policies:
        findings.append({"code": "PROCESS_DELIVERY_INVENTORY_POLICY_MISMATCH"})
    patterns = inventory_policy.get("knownMetadataPatterns")
    if not isinstance(patterns, list) or "*-accept-discovery.env" not in patterns:
        findings.append({"code": "PROCESS_DELIVERY_METADATA_POLICY_MISSING"})
    if inventory_policy.get("freeTextNumbersReserveIdentity") is not False or inventory_policy.get("currentDeliveryMatchCount") != 1:
        findings.append({"code": "PROCESS_DELIVERY_ID_POLICY_MISMATCH"})
    legacy_expected = {
        "policy": "RESERVE",
        "recordSchema": "cocondo.run-record.v1",
        "commands": ["patch-dry-run", "patch-accept"],
        "numericPatchIdPattern": "^[0-9]{6}$",
        "canonicalPatchIdSource": "metadata.artifactFile",
        "artifactFilePattern": "^[A-Za-z0-9._-]+__(?P<patchId>[0-9]{6}_[A-Za-z0-9][A-Za-z0-9._-]*)__+(?P<artifactToken>[0-9a-fA-F]{8})\\.zip$",
        "artifactIdPattern": "^urn:uuid:(?P<artifactToken>[0-9a-fA-F]{8})-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$",
        "requirePatchNumberMatch": True,
        "requireArtifactTokenMatch": True,
        "unverifiedOrConflicting": "BLOCKING_TOOL_ERROR",
    }
    if inventory_policy.get("legacyNumericPatchRunCompatibility") != legacy_expected:
        findings.append({"code": "PROCESS_DELIVERY_LEGACY_NUMERIC_POLICY_MISMATCH"})
    accepted_expected = {
        "policy": "RESERVE",
        "recordSchema": "cocondo.patch-acceptance.v2",
        "artifactIdPattern": "^urn:uuid:(?P<artifactUuid>[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})$",
        "numericPatchIdPattern": "^[0-9]{6}$",
        "numericResolutionCommand": "patch-accept",
        "numericResolutionStatus": "SUCCEEDED",
        "historicalFailedStatuses": ["ABORTED", "FAILED", "INCONSISTENT", "ORPHANED"],
        "differentDeliveryOrNonFailedRun": "BLOCKING_TOOL_ERROR",
        "multipleAcceptedOwners": "BLOCKING_TOOL_ERROR",
    }
    if inventory_policy.get("acceptedPatchAuthority") != accepted_expected:
        findings.append({"code": "PROCESS_DELIVERY_ACCEPTED_AUTHORITY_POLICY_MISMATCH"})

    operator_logs = contract.get("operatorLogPolicy") if isinstance(contract.get("operatorLogPolicy"), dict) else {}
    if operator_logs.get("canonicalRunStateRemainsInGitCommonDirectory") is not True:
        findings.append({"code": "PROCESS_OPERATOR_LOG_TRUTH_MISMATCH"})
    if operator_logs.get("commitPolicy") != "forbidden" or operator_logs.get("exportPolicy") != "excluded":
        findings.append({"code": "PROCESS_OPERATOR_LOG_LIFECYCLE_MISMATCH"})
    operator_log_expected = {
        "historicalTrackedSiblings": "allow",
        "currentRunDirectoryTrackedContent": "block",
        "currentRunDirectoryIgnored": "required",
        "runDirectoryPattern": "<operator-log-root>/<patch-id>/<run-id>",
        "pathPreparation": "fail-closed-current-run-directory",
    }
    for key, expected in operator_log_expected.items():
        if operator_logs.get(key) != expected:
            findings.append({
                "code": "PROCESS_OPERATOR_LOG_POLICY_MISMATCH",
                "key": key,
                "expected": expected,
                "actual": operator_logs.get(key),
            })

    implementation = contract.get("implementation") if isinstance(contract.get("implementation"), dict) else {}
    required = {
        "entrypoint": "bin/process-ops.sh",
        "python": "bin/process-ops.py",
        "config": ".cocondo/process.env",
        "integrationTest": "bin/process-ops-it.sh",
        "guide": "PROJECT_DOCS/TOOLING/PROCESS_OPERATIONS.md",
        "knownErrors": "PROJECT_DOCS/TOOLING/PROCESS_KNOWN_ERRORS.md",
        "decision": "PROJECT_DOCS/ADR/ADR-0014-process-execution-observation-and-recovery.md",
    }
    for key, expected in required.items():
        if implementation.get(key) != expected:
            findings.append({"code": "PROCESS_IMPLEMENTATION_PATH_MISMATCH", "key": key, "expected": expected, "actual": implementation.get(key)})
        path = root / expected
        if not path.is_file():
            findings.append({"code": "PROCESS_IMPLEMENTATION_FILE_MISSING", "path": expected})

    for relative in ("bin/process-ops.sh", "bin/process-ops.py", "bin/process-ops-it.sh"):
        path = root / relative
        if path.is_file() and not os.access(path, os.X_OK):
            findings.append({"code": "PROCESS_TOOL_NOT_EXECUTABLE", "path": relative})

    env_path = root / ".cocondo/process.env"
    try:
        env = parse_env(env_path)
    except Exception as exc:
        findings.append({"code": "PROCESS_CONFIG_INVALID", "detail": str(exc)})
        env = {}
    expected_env = {
        "CPROCESS_CONFIG_VERSION": "3",
        "CPROCESS_STATE_DIRECTORY": ".git/cocondo-process",
        "CPROCESS_INCIDENT_DIRECTORY": ".git/cocondo-process/incidents",
        "CPROCESS_DELIVERY_DIRECTORY": ".git/cocondo-process/deliveries",
        "CPROCESS_ARTIFACT_AUTHORIZATION_RECORD": ".git/cocondo-process/authorizations/artifact-root.json",
        "CPROCESS_OPERATOR_LOG_DIRECTORY": "patches/logs/validation",
        "CPROCESS_WORK_DIRECTORY": "patches/work",
    }
    for key, expected in expected_env.items():
        if env.get(key) != expected:
            findings.append({"code": "PROCESS_CONFIG_MISMATCH", "key": key, "expected": expected, "actual": env.get(key)})

    runtime_dirs = contract.get("runtimeDirectories") if isinstance(contract.get("runtimeDirectories"), dict) else {}
    runtime_expected = {
        "processDeliveries": "CPROCESS_DELIVERY_DIRECTORY",
        "artifactRootAuthorization": "CPROCESS_ARTIFACT_AUTHORIZATION_RECORD",
        "operatorWorkspace": "CPROCESS_WORK_DIRECTORY",
    }
    for key, expected in runtime_expected.items():
        if runtime_dirs.get(key) != expected:
            findings.append({"code": "PROCESS_RUNTIME_DIRECTORY_MISMATCH", "key": key, "expected": expected, "actual": runtime_dirs.get(key)})

    process_source = root / "bin/process-ops.py"
    if process_source.is_file():
        source_text = process_source.read_text(encoding="utf-8")
        for command_name in sorted(expected_writers | {"artifact-root-authorize", "artifact-root-status", "delivery-inventory", "delivery-next-id"}):
            if f'add_parser("{command_name}")' not in source_text:
                findings.append({"code": "PROCESS_COMMAND_MISSING", "command": command_name})

    scanned = [
        "AGENTS.md",
        "PROJECT_DOCS/TOOLING/PATCH_SYSTEM.md",
        "bin/process-ops.sh",
        "bin/process-ops.py",
        "PROJECT_DOCS/ADR/ADR-0014-process-execution-observation-and-recovery.md",
        "PROJECT_DOCS/TOOLING/PROCESS_OPERATIONS.md",
        "PROJECT_DOCS/TOOLING/PATCH_COMMAND_GENERATION_CONTRACT.md",
    ]
    for relative in scanned:
        path = root / relative
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        for pattern in FORBIDDEN:
            if pattern.search(text):
                findings.append({"code": "PROCESS_STATIC_PATH_FORBIDDEN", "path": relative, "pattern": pattern.pattern})
        if relative in {"bin/process-ops.sh", "bin/process-ops.py"}:
            for pattern in FORBIDDEN_PROCESS_WORDS:
                if pattern.search(text):
                    findings.append({"code": "PROCESS_NESTED_DETACHMENT_FORBIDDEN", "path": relative, "pattern": pattern.pattern})

    gitignore_path = root / ".gitignore"
    if not gitignore_path.is_file() or "patches/work/" not in gitignore_path.read_text(encoding="utf-8").splitlines():
        findings.append({"code": "PROCESS_WORKSPACE_GITIGNORE_MISSING"})

    try:
        export_config = read_json(root / "export.config.json")
    except Exception as exc:
        findings.append({"code": "PROCESS_EXPORT_CONFIG_INVALID", "detail": str(exc)})
        export_config = {}
    global_exclude = export_config.get("globalExclude") if isinstance(export_config.get("globalExclude"), list) else []
    if "patches/work/**" not in global_exclude:
        findings.append({"code": "PROCESS_WORKSPACE_EXPORT_EXCLUDE_MISSING"})

    try:
        directory_contract = read_json(root / "contracts/governance/project-structure/project-directory-contract.json")
    except Exception as exc:
        findings.append({"code": "PROCESS_DIRECTORY_CONTRACT_INVALID", "detail": str(exc)})
        directory_contract = {}
    areas = directory_contract.get("areas") if isinstance(directory_contract.get("areas"), list) else []
    workspace_areas = [item for item in areas if isinstance(item, dict) and item.get("id") == "patch-workspace"]
    if len(workspace_areas) != 1 or workspace_areas[0].get("patterns") != ["patches/work/**"]:
        findings.append({"code": "PROCESS_WORKSPACE_DIRECTORY_AREA_MISSING"})
    elif workspace_areas[0].get("commitPolicy") != "forbidden" or workspace_areas[0].get("pathClass") != "temporary":
        findings.append({"code": "PROCESS_WORKSPACE_DIRECTORY_POLICY_MISMATCH"})

    try:
        codex_contract = read_json(root / "contracts/governance/agent/codex-pilot-contract.json")
    except Exception as exc:
        findings.append({"code": "PROCESS_CODEX_CONTRACT_INVALID", "detail": str(exc)})
        codex_contract = {}
    codex_paths = codex_contract.get("paths") if isinstance(codex_contract.get("paths"), dict) else {}
    if "patches/work/**" not in codex_paths.get("alwaysForbidden", []):
        findings.append({"code": "PROCESS_WORKSPACE_CODEX_DENY_MISSING"})

    activation_path = root / "contracts/governance/tooling/patch-toolkit-activation-contract.json"
    try:
        activation = read_json(activation_path)
    except Exception as exc:
        findings.append({"code": "ACTIVATION_CONTRACT_INVALID", "detail": str(exc)})
        activation = {}
    process_ops = activation.get("processOperations") if isinstance(activation.get("processOperations"), dict) else {}
    if process_ops.get("contract") != args.contract:
        findings.append({"code": "ACTIVATION_PROCESS_CONTRACT_MISSING"})
    if process_ops.get("managedProjectRollout") != "BLOCKED_PENDING_SPRINGMASTER_PILOT":
        findings.append({"code": "PROCESS_ROLLOUT_GATE_NOT_BLOCKED", "actual": process_ops.get("managedProjectRollout")})

    report = {
        "schemaVersion": "cocondo.process-operations-contract-report.v1",
        "status": "PASS" if not findings else "FAIL",
        "findingCount": len(findings),
        "findings": sorted(findings, key=lambda item: (str(item.get("code")), json.dumps(item, sort_keys=True))),
    }
    out = Path(args.out)
    if not out.is_absolute():
        out = root / out
    out.parent.mkdir(parents=True, exist_ok=True)
    temporary = out.with_suffix(out.suffix + ".tmp")
    temporary.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, out)
    print(f"PROCESS_OPERATIONS_CONTRACT={report['status']}")
    print(f"REPORT={out}")
    return 1 if args.check and findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
