#!/usr/bin/env python3
"""Evaluate Springmaster engineering qualification evidence without mutating the repository."""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any

REPORT_SCHEMA = "springmaster.engineering-qualification-gate-report.v1"
GATE_CONTRACT_SCHEMA = "springmaster.engineering-qualification-gate-contract.v1"
QUALITY_CATALOG_SCHEMA = "springmaster.quality-rule-catalog.v1"
GATE_REGISTRY_SCHEMA = "springmaster.gate-registry.v1"
TEST_SUITE_SCHEMA = "springmaster.test-suite-contract.v1"


class ToolError(RuntimeError):
    def __init__(self, code: str, message: str, path: str | None = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.path = path


def load_json(path: Path, code: str = "JSON_READ_ERROR") -> Any:
    if not path.is_file():
        raise ToolError("FILE_MISSING", f"Required JSON file is missing: {path}", str(path))
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ToolError(code, f"Cannot parse JSON file {path}: {exc}", str(path)) from exc


def load_object(path: Path, schema: str, code: str = "CONTRACT_PARSE_ERROR") -> dict[str, Any]:
    value = load_json(path, code)
    if not isinstance(value, dict):
        raise ToolError("INVALID_JSON_SHAPE", f"JSON file must contain an object: {path}", str(path))
    if value.get("schemaVersion") != schema:
        raise ToolError(
            "SCHEMA_MISMATCH",
            f"Expected schema {schema}, got {value.get('schemaVersion')!r}",
            str(path),
        )
    return value


def load_engineering_module(project_root: Path):
    path = project_root / "bin/engineering-contracts.py"
    if not path.is_file():
        raise ToolError("ENGINEERING_VALIDATOR_MISSING", f"Engineering contract validator is missing: {path}", str(path))
    spec = importlib.util.spec_from_file_location("springmaster_engineering_contracts", path)
    if spec is None or spec.loader is None:
        raise ToolError("ENGINEERING_VALIDATOR_LOAD_ERROR", f"Cannot create module specification for {path}", str(path))
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception as exc:
        raise ToolError("ENGINEERING_VALIDATOR_LOAD_ERROR", f"Cannot load {path}: {exc}", str(path)) from exc
    return module


def issue(code: str, path: str, message: str, **details: Any) -> dict[str, Any]:
    result: dict[str, Any] = {"code": code, "path": path, "message": message}
    if details:
        result["details"] = details
    return result


def duplicates(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value in seen and value not in result:
            result.append(value)
        seen.add(value)
    return result


def atomic_write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent), text=True)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def policy_map(contract: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        item.get("profileId"): item
        for item in contract.get("profilePolicies", [])
        if isinstance(item, dict) and isinstance(item.get("profileId"), str)
    }


def validate_wiring(
    project_root: Path,
    gate_contract: dict[str, Any],
    engineering_contracts: dict[str, dict[str, Any]],
    catalog: dict[str, Any],
    registry: dict[str, Any],
    test_suites: dict[str, Any],
) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    profile_ids = {
        item.get("id")
        for item in engineering_contracts["profiles"].get("profiles", [])
        if isinstance(item, dict)
    }
    policies = gate_contract.get("profilePolicies")
    if not isinstance(policies, list):
        findings.append(issue("ENG_QUAL_PROFILE_POLICIES_INVALID", "engineering-qualification-gate-contract.json", "profilePolicies must be a list"))
        policies = []
    policy_ids = [item.get("profileId") for item in policies if isinstance(item, dict) and isinstance(item.get("profileId"), str)]
    for value in duplicates(policy_ids):
        findings.append(issue("ENG_QUAL_PROFILE_POLICY_DUPLICATE", "engineering-qualification-gate-contract.json", f"Duplicate profile policy: {value}"))
    for item in policies:
        if not isinstance(item, dict):
            findings.append(issue("ENG_QUAL_PROFILE_POLICY_INVALID", "engineering-qualification-gate-contract.json", "Every profile policy must be an object"))
            continue
        profile_id = item.get("profileId")
        if profile_id not in profile_ids:
            findings.append(issue("ENG_QUAL_PROFILE_UNKNOWN", "engineering-qualification-gate-contract.json", f"Unknown profile policy: {profile_id!r}"))
        checks = item.get("requiredCheckIds")
        if not isinstance(checks, list) or any(not isinstance(value, str) for value in checks):
            findings.append(issue("ENG_QUAL_REQUIRED_CHECKS_INVALID", "engineering-qualification-gate-contract.json", f"requiredCheckIds for {profile_id!r} must be a string list"))
            continue
        for value in duplicates(checks):
            findings.append(issue("ENG_QUAL_REQUIRED_CHECK_DUPLICATE", "engineering-qualification-gate-contract.json", f"Duplicate required check {value!r} for profile {profile_id!r}"))

    gate_items = {
        item.get("gateId"): item
        for item in registry.get("gates", [])
        if isinstance(item, dict) and isinstance(item.get("gateId"), str)
    }
    for item in policies:
        if not isinstance(item, dict):
            continue
        for check_id in item.get("requiredCheckIds", []):
            gate = gate_items.get(check_id)
            if gate is None:
                findings.append(issue("ENG_QUAL_REQUIRED_GATE_UNKNOWN", "engineering-qualification-gate-contract.json", f"Required check is not registered: {check_id}"))
                continue
            if gate.get("readOnly") is not True:
                findings.append(issue("ENG_QUAL_REQUIRED_GATE_MUTATING", "gate-registry.json", f"Required check is not read-only: {check_id}"))
            if gate.get("defaultEnforcementMode") != "report-only":
                findings.append(issue("ENG_QUAL_REQUIRED_GATE_NOT_REPORT_ONLY", "gate-registry.json", f"Required check is not report-only: {check_id}"))

    own_gate_id = gate_contract.get("gateId")
    own_gate = gate_items.get(own_gate_id)
    if own_gate is None:
        findings.append(issue("ENG_QUAL_GATE_DESCRIPTOR_MISSING", "gate-registry.json", f"Gate descriptor is missing: {own_gate_id!r}"))
    else:
        if own_gate.get("entrypoint") != "bin/engineering-qualification-gate.sh":
            findings.append(issue("ENG_QUAL_ENTRYPOINT_MISMATCH", "gate-registry.json", "Engineering qualification gate entrypoint is inconsistent"))
        if own_gate.get("reportSchema") != gate_contract.get("reportSchema"):
            findings.append(issue("ENG_QUAL_REPORT_SCHEMA_MISMATCH", "gate-registry.json", "Gate and contract report schemas differ"))
        expected_inputs = set(gate_contract.get("inputContracts", []))
        actual_inputs = set(own_gate.get("inputContracts", []))
        if expected_inputs != actual_inputs:
            findings.append(issue("ENG_QUAL_INPUT_CONTRACT_MISMATCH", "gate-registry.json", "Gate inputContracts differ from the gate contract", expected=sorted(expected_inputs), actual=sorted(actual_inputs)))

    rule_items = {
        item.get("ruleId"): item
        for item in catalog.get("rules", [])
        if isinstance(item, dict) and isinstance(item.get("ruleId"), str)
    }
    required_rule_ids = gate_contract.get("requiredGateRuleIds", [])
    if not isinstance(required_rule_ids, list):
        findings.append(issue("ENG_QUAL_RULE_IDS_INVALID", "engineering-qualification-gate-contract.json", "requiredGateRuleIds must be a list"))
        required_rule_ids = []
    for rule_id in required_rule_ids:
        rule = rule_items.get(rule_id)
        if rule is None:
            findings.append(issue("ENG_QUAL_RULE_UNKNOWN", "quality-rule-catalog.json", f"Required gate rule is missing: {rule_id}"))
        elif own_gate_id not in rule.get("gateIds", []):
            findings.append(issue("ENG_QUAL_RULE_GATE_REFERENCE_MISSING", "quality-rule-catalog.json", f"Rule {rule_id} does not reference {own_gate_id}"))
    if own_gate is not None:
        actual_rule_ids = set(own_gate.get("ruleIds", []))
        if set(required_rule_ids) != actual_rule_ids:
            findings.append(issue("ENG_QUAL_GATE_RULE_SET_MISMATCH", "gate-registry.json", "Gate ruleIds differ from the gate contract", expected=sorted(required_rule_ids), actual=sorted(actual_rule_ids)))

    suite_profiles = set(test_suites.get("allowedEngineeringProfiles", []))
    if profile_ids != suite_profiles:
        findings.append(issue("ENG_QUAL_TEST_PROFILE_SET_MISMATCH", "test-suite-contract.json", "Test and engineering profile sets differ", engineering=sorted(profile_ids), testing=sorted(suite_profiles)))

    accepted = set(gate_contract.get("acceptedExecutionStatuses", []))
    evidence_statuses = set(engineering_contracts["evidence"].get("executionStatuses", []))
    if not accepted or not accepted.issubset(evidence_statuses):
        findings.append(issue("ENG_QUAL_ACCEPTED_STATUS_INVALID", "engineering-qualification-gate-contract.json", "Accepted execution statuses are not a non-empty subset of the evidence contract"))
    blocking = set(gate_contract.get("blockingExecutionStatuses", []))
    if not blocking.issubset(evidence_statuses):
        findings.append(issue("ENG_QUAL_BLOCKING_STATUS_INVALID", "engineering-qualification-gate-contract.json", "Blocking execution statuses are not a subset of the evidence contract"))

    for relative in gate_contract.get("inputContracts", []):
        if not isinstance(relative, str) or not (project_root / relative).is_file():
            findings.append(issue("ENG_QUAL_INPUT_CONTRACT_MISSING", "engineering-qualification-gate-contract.json", f"Input contract is missing: {relative!r}"))
    return findings


def validate_qualification(
    classification: Any,
    evidence: Any,
    completion: Any,
    gate_contract: dict[str, Any],
    engineering_contracts: dict[str, dict[str, Any]],
    engineering_module: Any,
    registry: dict[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    classification_findings, selection = engineering_module.validate_classification(classification, engineering_contracts, "classification")
    findings.extend(classification_findings)
    evidence_findings, evidence_result = engineering_module.validate_evidence(evidence, engineering_contracts, "evidence")
    findings.extend(evidence_findings)
    completion_findings, completion_result = engineering_module.validate_completion(completion, evidence, engineering_contracts, "completion")
    findings.extend(completion_findings)

    if isinstance(classification, dict) and isinstance(evidence, dict):
        if classification.get("changeId") != evidence.get("changeRef"):
            findings.append(issue("ENG_QUAL_CHANGE_ID_MISMATCH", "evidence", "classification.changeId must equal evidence.changeRef"))
        if evidence.get("classification") != classification:
            findings.append(issue("ENG_QUAL_CLASSIFICATION_MISMATCH", "evidence.classification", "Evidence classification must equal the supplied classification record"))
    if isinstance(evidence, dict) and isinstance(completion, dict):
        if completion.get("changeRef") != evidence.get("changeRef"):
            findings.append(issue("ENG_QUAL_COMPLETION_CHANGE_MISMATCH", "completion", "Completion changeRef must equal evidence changeRef"))
        if completion.get("evidenceRef") != evidence.get("evidenceId"):
            findings.append(issue("ENG_QUAL_COMPLETION_EVIDENCE_MISMATCH", "completion", "Completion evidenceRef must equal evidenceId"))

    policies = policy_map(gate_contract)
    gate_ids = {
        item.get("gateId")
        for item in registry.get("gates", [])
        if isinstance(item, dict) and isinstance(item.get("gateId"), str)
    }
    executions = evidence.get("executions", []) if isinstance(evidence, dict) and isinstance(evidence.get("executions"), list) else []
    accepted_statuses = set(gate_contract.get("acceptedExecutionStatuses", []))
    required_profiles = selection.get("requiredProfiles", [])
    required_checks: dict[str, list[str]] = {}
    execution_summary: list[dict[str, Any]] = []

    seen_pairs: list[str] = []
    for index, execution in enumerate(executions):
        if not isinstance(execution, dict):
            continue
        profile_id = execution.get("profileId")
        check_id = execution.get("checkId")
        if isinstance(profile_id, str) and isinstance(check_id, str):
            pair = f"{profile_id}:{check_id}"
            seen_pairs.append(pair)
            if check_id not in gate_ids:
                findings.append(issue("ENG_QUAL_CHECK_UNKNOWN", f"evidence.executions[{index}]", f"Execution checkId is not a registered gate: {check_id!r}"))
            status = execution.get("status")
            refs = execution.get("reportRefs")
            if status in {"passed", "passed-with-findings"} and (not isinstance(refs, list) or not refs):
                findings.append(issue("ENG_QUAL_REPORT_REF_REQUIRED", f"evidence.executions[{index}]", "Passed execution requires at least one reportRef"))
            execution_summary.append({"profileId": profile_id, "checkId": check_id, "status": status})
    for pair in duplicates(seen_pairs):
        findings.append(issue("ENG_QUAL_CHECK_DUPLICATE", "evidence.executions", f"Duplicate profile/check execution: {pair}"))

    for profile_id in required_profiles:
        policy = policies.get(profile_id)
        if policy is None:
            findings.append(issue("ENG_QUAL_PROFILE_POLICY_MISSING", "engineering-qualification-gate-contract.json", f"No policy exists for required profile {profile_id!r}"))
            continue
        if policy.get("supported") is not True:
            findings.append(issue("ENG_QUAL_PROFILE_UNSUPPORTED", "engineering-qualification-gate-contract.json", f"Required profile is not supported by this gate: {profile_id}"))
            continue
        checks = list(policy.get("requiredCheckIds", []))
        required_checks[profile_id] = checks
        for check_id in checks:
            matches = [
                item
                for item in executions
                if isinstance(item, dict) and item.get("profileId") == profile_id and item.get("checkId") == check_id
            ]
            if not matches:
                findings.append(issue("ENG_QUAL_REQUIRED_CHECK_MISSING", "evidence.executions", f"Required check {check_id!r} is missing for profile {profile_id!r}"))
                continue
            if not any(item.get("status") in accepted_statuses for item in matches):
                findings.append(issue("ENG_QUAL_REQUIRED_CHECK_NOT_QUALIFIED", "evidence.executions", f"Required check {check_id!r} is not qualified for profile {profile_id!r}"))

    technical_status = completion_result.get("status") or evidence_result.get("technicalStatus")
    if technical_status in gate_contract.get("qualifiedStatuses", []) and findings:
        pass
    details = {
        "changeId": classification.get("changeId") if isinstance(classification, dict) else None,
        "evidenceId": evidence_result.get("evidenceId"),
        "completionId": completion_result.get("completionId"),
        "effectiveRiskLevel": selection.get("effectiveRiskLevel"),
        "requiredProfiles": required_profiles,
        "requiredChecks": required_checks,
        "executions": execution_summary,
        "technicalStatus": technical_status,
    }
    return findings, details


def parser() -> argparse.ArgumentParser:
    project_root = Path(__file__).resolve().parent.parent
    result = argparse.ArgumentParser(
        prog="engineering-qualification-gate.py",
        description="Evaluate Springmaster engineering qualification records in report-only mode.",
    )
    result.add_argument("--project-root", type=Path, default=project_root)
    result.add_argument("--contract-root", type=Path)
    result.add_argument("--quality-root", type=Path)
    result.add_argument("--testing-root", type=Path)
    result.add_argument("--out", type=Path)
    result.add_argument("--check", action="store_true", help="Return exit 1 when findings exist")
    subparsers = result.add_subparsers(dest="operation", required=True)
    subparsers.add_parser("contracts", help="Validate gate wiring and registered contract references")
    qualification = subparsers.add_parser("qualification", help="Evaluate classification, evidence and completion records")
    qualification.add_argument("--classification", type=Path, required=True)
    qualification.add_argument("--evidence", type=Path, required=True)
    qualification.add_argument("--completion", type=Path, required=True)
    return result


def main() -> int:
    args = parser().parse_args()
    project_root = args.project_root.resolve()
    engineering_root = (args.contract_root or project_root / "contracts/governance/engineering").resolve()
    quality_root = (args.quality_root or project_root / "contracts/governance/quality").resolve()
    testing_root = (args.testing_root or project_root / "contracts/governance/testing").resolve()
    findings: list[dict[str, Any]] = []
    tool_errors: list[dict[str, Any]] = []
    details: dict[str, Any] = {}
    technical_status: str | None = None
    try:
        engineering_module = load_engineering_module(project_root)
        engineering_contracts = engineering_module.load_contracts(engineering_root)
        findings.extend(engineering_module.semantic_contract_findings(engineering_contracts))
        gate_contract = load_object(engineering_root / "engineering-qualification-gate-contract.json", GATE_CONTRACT_SCHEMA)
        catalog = load_object(quality_root / "quality-rule-catalog.json", QUALITY_CATALOG_SCHEMA)
        registry = load_object(quality_root / "gate-registry.json", GATE_REGISTRY_SCHEMA)
        test_suites = load_object(testing_root / "test-suite-contract.json", TEST_SUITE_SCHEMA)
        findings.extend(validate_wiring(project_root, gate_contract, engineering_contracts, catalog, registry, test_suites))
        details.update(
            {
                "gateId": gate_contract.get("gateId"),
                "gateContractVersion": gate_contract.get("contractVersion"),
                "qualityCatalogVersion": catalog.get("catalogVersion"),
                "gateRegistryVersion": registry.get("registryVersion"),
            }
        )
        if args.operation == "qualification":
            classification = load_json(args.classification.resolve())
            evidence = load_json(args.evidence.resolve())
            completion = load_json(args.completion.resolve())
            qualification_findings, qualification_details = validate_qualification(
                classification,
                evidence,
                completion,
                gate_contract,
                engineering_contracts,
                engineering_module,
                registry,
            )
            findings.extend(qualification_findings)
            details.update(qualification_details)
            technical_status = qualification_details.get("technicalStatus")
    except ToolError as exc:
        item: dict[str, Any] = {"code": exc.code, "message": exc.message}
        if exc.path:
            item["path"] = exc.path
        tool_errors.append(item)
    except Exception as exc:
        tool_errors.append({"code": "UNEXPECTED_TOOL_ERROR", "message": str(exc)})

    status = "TOOL_ERROR" if tool_errors else ("FINDINGS" if findings else "PASS")
    report = {
        "schemaVersion": REPORT_SCHEMA,
        "status": status,
        "operation": args.operation,
        "technicalStatus": technical_status,
        "findingCount": len(findings),
        "toolErrorCount": len(tool_errors),
        "details": details,
        "findings": findings,
        "toolErrors": tool_errors,
    }
    if args.out:
        atomic_write_json(args.out.resolve(), report)
    else:
        sys.stdout.write(json.dumps(report, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n")
    print(f"ENGINEERING_QUALIFICATION_GATE={status}", file=sys.stderr)
    if tool_errors:
        return 2
    if findings and args.check:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
