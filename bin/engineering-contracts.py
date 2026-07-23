#!/usr/bin/env python3
"""Validate Springmaster engineering classification, profile, evidence and completion contracts."""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
from pathlib import Path
from typing import Any

REPORT_SCHEMA = "springmaster.engineering-contract-validation-report.v1"
CONTRACT_FILES = {
    "classification": ("change-classification-contract.json", "springmaster.change-classification-contract.v1"),
    "profiles": ("engineering-profile-contract.json", "springmaster.engineering-profile-contract.v1"),
    "evidence": ("engineering-evidence-contract.json", "springmaster.engineering-evidence-contract.v1"),
    "completion": ("engineering-completion-contract.json", "springmaster.engineering-completion-contract.v1"),
}


class ToolError(RuntimeError):
    def __init__(self, code: str, message: str, path: str | None = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.path = path


def load_json(path: Path, *, tool_error_code: str = "JSON_READ_ERROR") -> Any:
    if not path.is_file():
        raise ToolError("FILE_MISSING", f"Required JSON file is missing: {path}", str(path))
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ToolError(tool_error_code, f"Cannot parse JSON file {path}: {exc}", str(path)) from exc


def load_contracts(contract_root: Path) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for key, (filename, schema) in CONTRACT_FILES.items():
        path = contract_root / filename
        value = load_json(path, tool_error_code="CONTRACT_PARSE_ERROR")
        if not isinstance(value, dict):
            raise ToolError("CONTRACT_INVALID_SHAPE", f"Contract must contain a JSON object: {path}", str(path))
        if value.get("schemaVersion") != schema:
            raise ToolError(
                "CONTRACT_SCHEMA_MISMATCH",
                f"Expected schema {schema}, got {value.get('schemaVersion')!r}",
                str(path),
            )
        result[key] = value
    return result


def issue(code: str, path: str, message: str, **details: Any) -> dict[str, Any]:
    item: dict[str, Any] = {"code": code, "path": path, "message": message}
    if details:
        item["details"] = details
    return item


def duplicate_values(values: list[Any]) -> list[Any]:
    seen: set[Any] = set()
    duplicates: list[Any] = []
    for value in values:
        if value in seen and value not in duplicates:
            duplicates.append(value)
        seen.add(value)
    return duplicates


def ids(items: Any, field: str = "id") -> list[str]:
    if not isinstance(items, list):
        return []
    return [item.get(field) for item in items if isinstance(item, dict) and isinstance(item.get(field), str)]


def semantic_contract_findings(contracts: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    classification = contracts["classification"]
    profiles = contracts["profiles"]
    evidence = contracts["evidence"]
    completion = contracts["completion"]

    risk_levels = classification.get("riskLevels")
    risk_ids = ids(risk_levels)
    if not isinstance(risk_levels, list) or not risk_levels:
        findings.append(issue("RISK_LEVELS_MISSING", "change-classification-contract.json", "riskLevels must be a non-empty list"))
    for value in duplicate_values(risk_ids):
        findings.append(issue("DUPLICATE_RISK_LEVEL", "change-classification-contract.json", f"Duplicate risk level: {value}"))
    orders = [item.get("order") for item in risk_levels or [] if isinstance(item, dict)]
    if len(orders) != len(risk_ids) or any(not isinstance(value, int) for value in orders):
        findings.append(issue("RISK_ORDER_INVALID", "change-classification-contract.json", "Each risk level needs an integer order"))
    elif len(set(orders)) != len(orders):
        findings.append(issue("RISK_ORDER_DUPLICATE", "change-classification-contract.json", "Risk level orders must be unique"))

    class_ids = ids(classification.get("changeClasses"))
    if not class_ids:
        findings.append(issue("CHANGE_CLASSES_MISSING", "change-classification-contract.json", "changeClasses must be non-empty"))
    for value in duplicate_values(class_ids):
        findings.append(issue("DUPLICATE_CHANGE_CLASS", "change-classification-contract.json", f"Duplicate change class: {value}"))

    indicator_ids = ids(classification.get("riskIndicators"))
    for value in duplicate_values(indicator_ids):
        findings.append(issue("DUPLICATE_RISK_INDICATOR", "change-classification-contract.json", f"Duplicate risk indicator: {value}"))
    for item in classification.get("riskIndicators", []):
        if isinstance(item, dict) and item.get("minimumRisk") not in risk_ids:
            findings.append(issue("UNKNOWN_INDICATOR_RISK", "change-classification-contract.json", f"Unknown minimumRisk for indicator {item.get('id')!r}"))

    flag_ids = classification.get("flags")
    if not isinstance(flag_ids, list) or any(not isinstance(value, str) for value in flag_ids):
        findings.append(issue("FLAGS_INVALID", "change-classification-contract.json", "flags must be a string list"))
        flag_ids = []
    for value in duplicate_values(flag_ids):
        findings.append(issue("DUPLICATE_FLAG", "change-classification-contract.json", f"Duplicate flag: {value}"))

    profile_items = profiles.get("profiles")
    profile_ids = ids(profile_items)
    if not profile_ids:
        findings.append(issue("PROFILES_MISSING", "engineering-profile-contract.json", "profiles must be non-empty"))
    for value in duplicate_values(profile_ids):
        findings.append(issue("DUPLICATE_PROFILE", "engineering-profile-contract.json", f"Duplicate profile: {value}"))
    for item in profile_items or []:
        if not isinstance(item, dict):
            findings.append(issue("PROFILE_INVALID", "engineering-profile-contract.json", "Every profile must be an object"))
            continue
        if not isinstance(item.get("checkClasses"), list) or not item.get("checkClasses"):
            findings.append(issue("PROFILE_CHECK_CLASSES_MISSING", "engineering-profile-contract.json", f"Profile {item.get('id')!r} needs checkClasses"))

    selection_rule_ids = ids(profiles.get("selectionRules"))
    for value in duplicate_values(selection_rule_ids):
        findings.append(issue("DUPLICATE_SELECTION_RULE", "engineering-profile-contract.json", f"Duplicate selection rule: {value}"))
    for rule in profiles.get("selectionRules", []):
        if not isinstance(rule, dict):
            findings.append(issue("SELECTION_RULE_INVALID", "engineering-profile-contract.json", "Selection rule must be an object"))
            continue
        for profile_id in rule.get("requiredProfiles", []):
            if profile_id not in profile_ids:
                findings.append(issue("UNKNOWN_PROFILE_REFERENCE", "engineering-profile-contract.json", f"Selection rule {rule.get('id')!r} references unknown profile {profile_id!r}"))
        when = rule.get("when")
        if not isinstance(when, dict):
            findings.append(issue("SELECTION_CONDITION_INVALID", "engineering-profile-contract.json", f"Selection rule {rule.get('id')!r} needs an object condition"))
            continue
        for class_id in when.get("anyClass", []):
            if class_id not in class_ids:
                findings.append(issue("UNKNOWN_CLASS_REFERENCE", "engineering-profile-contract.json", f"Selection rule {rule.get('id')!r} references unknown class {class_id!r}"))
        for flag_id in when.get("anyFlag", []):
            if flag_id not in flag_ids:
                findings.append(issue("UNKNOWN_FLAG_REFERENCE", "engineering-profile-contract.json", f"Selection rule {rule.get('id')!r} references unknown flag {flag_id!r}"))

    for profile_id in profiles.get("optionalProfiles", []):
        if profile_id not in profile_ids:
            findings.append(issue("UNKNOWN_OPTIONAL_PROFILE", "engineering-profile-contract.json", f"Unknown optional profile: {profile_id!r}"))
    for item in profiles.get("substitution", []):
        if not isinstance(item, dict) or item.get("profile") not in profile_ids:
            findings.append(issue("SUBSTITUTION_PROFILE_INVALID", "engineering-profile-contract.json", "Substitution profile is unknown"))
            continue
        for covered in item.get("covers", []):
            if covered not in profile_ids:
                findings.append(issue("SUBSTITUTION_COVER_UNKNOWN", "engineering-profile-contract.json", f"Unknown covered profile: {covered!r}"))

    if evidence.get("technicalStatuses") != completion.get("statuses"):
        findings.append(issue("STATUS_ENUM_MISMATCH", "engineering-evidence-contract.json", "Evidence and completion status enums must match"))
    criterion_ids = ids(completion.get("criteria"))
    if len(criterion_ids) != 14:
        findings.append(issue("COMPLETION_CRITERIA_COUNT", "engineering-completion-contract.json", "Exactly 14 completion criteria are required", actual=len(criterion_ids)))
    for value in duplicate_values(criterion_ids):
        findings.append(issue("DUPLICATE_COMPLETION_CRITERION", "engineering-completion-contract.json", f"Duplicate completion criterion: {value}"))

    return findings


def risk_maps(classification_contract: dict[str, Any]) -> tuple[dict[str, int], dict[str, str]]:
    order = {item["id"]: item["order"] for item in classification_contract["riskLevels"]}
    indicator_risk = {item["id"]: item["minimumRisk"] for item in classification_contract["riskIndicators"]}
    return order, indicator_risk


def validate_classification(value: Any, contracts: dict[str, dict[str, Any]], path: str = "classification") -> tuple[list[dict[str, Any]], dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    contract = contracts["classification"]
    profiles = contracts["profiles"]
    if not isinstance(value, dict):
        return [issue("CLASSIFICATION_INVALID_SHAPE", path, "Classification must be a JSON object")], {}
    for field in contract.get("requiredFields", []):
        if field not in value:
            findings.append(issue("CLASSIFICATION_FIELD_MISSING", path, f"Missing required field: {field}"))
    if value.get("schemaVersion") != contract.get("changeInputSchema"):
        findings.append(issue("CLASSIFICATION_SCHEMA_INVALID", path, f"Expected schema {contract.get('changeInputSchema')!r}"))
    change_id = value.get("changeId")
    if not isinstance(change_id, str) or not re.fullmatch(contract.get("changeIdPattern", r".+"), change_id):
        findings.append(issue("CHANGE_ID_INVALID", path, "changeId does not match the contract pattern"))

    known_classes = set(ids(contract.get("changeClasses")))
    classes = value.get("classes")
    if not isinstance(classes, list) or not classes or any(not isinstance(item, str) for item in classes):
        findings.append(issue("CHANGE_CLASSES_INVALID", path, "classes must be a non-empty string list"))
        classes = []
    for duplicate in duplicate_values(classes):
        findings.append(issue("CHANGE_CLASS_DUPLICATE", path, f"Duplicate class: {duplicate}"))
    for class_id in classes:
        if class_id not in known_classes:
            findings.append(issue("CHANGE_CLASS_UNKNOWN", path, f"Unknown change class: {class_id}"))

    order, indicator_risk = risk_maps(contract)
    declared_risk = value.get("declaredRiskLevel")
    if declared_risk not in order:
        findings.append(issue("RISK_LEVEL_UNKNOWN", path, f"Unknown declared risk level: {declared_risk!r}"))
    indicators = value.get("riskIndicators")
    if not isinstance(indicators, list) or any(not isinstance(item, str) for item in indicators):
        findings.append(issue("RISK_INDICATORS_INVALID", path, "riskIndicators must be a string list"))
        indicators = []
    for duplicate in duplicate_values(indicators):
        findings.append(issue("RISK_INDICATOR_DUPLICATE", path, f"Duplicate risk indicator: {duplicate}"))
    for indicator in indicators:
        if indicator not in indicator_risk:
            findings.append(issue("RISK_INDICATOR_UNKNOWN", path, f"Unknown risk indicator: {indicator}"))

    flags = value.get("flags")
    known_flags = set(contract.get("flags", []))
    if not isinstance(flags, dict):
        findings.append(issue("FLAGS_INVALID_SHAPE", path, "flags must be an object"))
        flags = {}
    for flag, enabled in flags.items():
        if flag not in known_flags:
            findings.append(issue("FLAG_UNKNOWN", path, f"Unknown flag: {flag}"))
        if not isinstance(enabled, bool):
            findings.append(issue("FLAG_VALUE_INVALID", path, f"Flag {flag!r} must be boolean"))

    effective_risk = declared_risk if declared_risk in order else None
    for indicator in indicators:
        minimum = indicator_risk.get(indicator)
        if minimum and (effective_risk is None or order[minimum] > order[effective_risk]):
            effective_risk = minimum
    if declared_risk in order and effective_risk in order and order[declared_risk] < order[effective_risk]:
        findings.append(issue("RISK_LEVEL_UNDERRATED", path, f"Declared risk {declared_risk!r} is below derived minimum {effective_risk!r}"))

    profile_order = ids(profiles.get("profiles"))
    selected: list[str] = []
    for rule in profiles.get("selectionRules", []):
        when = rule.get("when", {})
        matches = bool(when.get("always"))
        if when.get("anyClass"):
            matches = any(item in classes for item in when["anyClass"])
        if when.get("anyFlag"):
            matches = any(flags.get(item) is True for item in when["anyFlag"])
        if matches:
            for profile_id in rule.get("requiredProfiles", []):
                if profile_id not in selected:
                    selected.append(profile_id)
    selected.sort(key=lambda item: profile_order.index(item) if item in profile_order else len(profile_order))
    output = {
        "schemaVersion": profiles.get("selectionOutputSchema"),
        "changeId": change_id,
        "effectiveRiskLevel": effective_risk,
        "requiredProfiles": selected,
        "optionalProfiles": list(profiles.get("optionalProfiles", [])),
    }
    return findings, output


def require_fields(value: dict[str, Any], required: list[str], path: str, findings: list[dict[str, Any]]) -> None:
    for field in required:
        if field not in value:
            findings.append(issue("FIELD_MISSING", path, f"Missing required field: {field}"))


def validate_evidence(value: Any, contracts: dict[str, dict[str, Any]], path: str = "evidence") -> tuple[list[dict[str, Any]], dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    contract = contracts["evidence"]
    profile_contract = contracts["profiles"]
    if not isinstance(value, dict):
        return [issue("EVIDENCE_INVALID_SHAPE", path, "Evidence must be a JSON object")], {}
    require_fields(value, contract.get("requiredFields", []), path, findings)
    if value.get("schemaVersion") != contract.get("evidenceSchema"):
        findings.append(issue("EVIDENCE_SCHEMA_INVALID", path, f"Expected schema {contract.get('evidenceSchema')!r}"))
    evidence_id = value.get("evidenceId")
    if not isinstance(evidence_id, str) or not re.fullmatch(contract.get("evidenceIdPattern", r".+"), evidence_id):
        findings.append(issue("EVIDENCE_ID_INVALID", path, "evidenceId does not match the contract pattern"))

    baseline = value.get("baseline")
    if not isinstance(baseline, dict):
        findings.append(issue("BASELINE_INVALID", path, "baseline must be an object"))
    else:
        require_fields(baseline, contract.get("baselineRequiredFields", []), f"{path}.baseline", findings)
        if not isinstance(baseline.get("gitHead"), str) or not re.fullmatch(r"[0-9a-f]{40}", baseline.get("gitHead", "")):
            findings.append(issue("BASELINE_GIT_HEAD_INVALID", f"{path}.baseline", "gitHead must be a 40-character lowercase SHA-1"))
        if not isinstance(baseline.get("dirty"), bool):
            findings.append(issue("BASELINE_DIRTY_INVALID", f"{path}.baseline", "dirty must be boolean"))
        if not isinstance(baseline.get("sourceExportSha256"), str) or not re.fullmatch(r"[0-9a-f]{64}", baseline.get("sourceExportSha256", "")):
            findings.append(issue("BASELINE_EXPORT_HASH_INVALID", f"{path}.baseline", "sourceExportSha256 must be a 64-character lowercase SHA-256"))

    scope = value.get("acceptedScope")
    if not isinstance(scope, dict):
        findings.append(issue("SCOPE_INVALID", path, "acceptedScope must be an object"))
    else:
        require_fields(scope, contract.get("scopeRequiredFields", []), f"{path}.acceptedScope", findings)

    classification_findings, selection = validate_classification(value.get("classification"), contracts, f"{path}.classification")
    findings.extend(classification_findings)
    profile_selection = value.get("profileSelection")
    if not isinstance(profile_selection, dict):
        findings.append(issue("PROFILE_SELECTION_INVALID", path, "profileSelection must be an object"))
        profile_selection = {}
    if profile_selection.get("schemaVersion") != profile_contract.get("selectionOutputSchema"):
        findings.append(issue("PROFILE_SELECTION_SCHEMA_INVALID", path, "profileSelection schema is invalid"))
    if profile_selection.get("requiredProfiles") != selection.get("requiredProfiles"):
        findings.append(issue("PROFILE_SELECTION_MISMATCH", path, "requiredProfiles do not match deterministic selection", expected=selection.get("requiredProfiles"), actual=profile_selection.get("requiredProfiles")))

    if not isinstance(value.get("ruleSources"), list) or not value.get("ruleSources"):
        findings.append(issue("RULE_SOURCES_INVALID", path, "ruleSources must be a non-empty list"))

    known_profiles = set(ids(profile_contract.get("profiles")))
    execution_statuses = set(contract.get("executionStatuses", []))
    executions = value.get("executions")
    if not isinstance(executions, list):
        findings.append(issue("EXECUTIONS_INVALID", path, "executions must be a list"))
        executions = []
    execution_ids: list[str] = []
    for index, execution in enumerate(executions):
        epath = f"{path}.executions[{index}]"
        if not isinstance(execution, dict):
            findings.append(issue("EXECUTION_INVALID", epath, "Execution must be an object"))
            continue
        require_fields(execution, contract.get("executionRequiredFields", []), epath, findings)
        execution_id = execution.get("executionId")
        if isinstance(execution_id, str):
            execution_ids.append(execution_id)
        if execution.get("profileId") not in known_profiles:
            findings.append(issue("EXECUTION_PROFILE_UNKNOWN", epath, f"Unknown profile: {execution.get('profileId')!r}"))
        if execution.get("status") not in execution_statuses:
            findings.append(issue("EXECUTION_STATUS_UNKNOWN", epath, f"Unknown execution status: {execution.get('status')!r}"))
        if not isinstance(execution.get("reportRefs"), list):
            findings.append(issue("EXECUTION_REPORT_REFS_INVALID", epath, "reportRefs must be a list"))
    for duplicate in duplicate_values(execution_ids):
        findings.append(issue("EXECUTION_ID_DUPLICATE", path, f"Duplicate executionId: {duplicate}"))

    finding_items = value.get("findings")
    if not isinstance(finding_items, list):
        findings.append(issue("FINDINGS_INVALID", path, "findings must be a list"))
        finding_items = []
    finding_ids: list[str] = []
    for index, item in enumerate(finding_items):
        fpath = f"{path}.findings[{index}]"
        if not isinstance(item, dict):
            findings.append(issue("FINDING_INVALID", fpath, "Finding must be an object"))
            continue
        require_fields(item, contract.get("findingRequiredFields", []), fpath, findings)
        if isinstance(item.get("findingId"), str):
            finding_ids.append(item["findingId"])
        if item.get("severity") not in contract.get("findingSeverities", []):
            findings.append(issue("FINDING_SEVERITY_UNKNOWN", fpath, f"Unknown severity: {item.get('severity')!r}"))
        if item.get("status") not in contract.get("findingStatuses", []):
            findings.append(issue("FINDING_STATUS_UNKNOWN", fpath, f"Unknown finding status: {item.get('status')!r}"))
    for duplicate in duplicate_values(finding_ids):
        findings.append(issue("FINDING_ID_DUPLICATE", path, f"Duplicate findingId: {duplicate}"))

    for list_field in ("deferrals", "technicalDebt", "artifactFamilies"):
        if not isinstance(value.get(list_field), list):
            findings.append(issue("LIST_FIELD_INVALID", path, f"{list_field} must be a list"))
    impact = value.get("impact")
    if not isinstance(impact, dict):
        findings.append(issue("IMPACT_INVALID", path, "impact must be an object"))
    else:
        require_fields(impact, contract.get("impactRequiredFields", []), f"{path}.impact", findings)

    technical_status = value.get("technicalStatus")
    if technical_status not in contract.get("technicalStatuses", []):
        findings.append(issue("TECHNICAL_STATUS_UNKNOWN", path, f"Unknown technicalStatus: {technical_status!r}"))
    if technical_status in {"qualified", "qualified-with-findings"}:
        qualified_statuses = set(contract.get("qualifiedExecutionStatuses", []))
        for required_profile in selection.get("requiredProfiles", []):
            matching = [item for item in executions if isinstance(item, dict) and item.get("profileId") == required_profile]
            if not matching or not any(item.get("status") in qualified_statuses for item in matching):
                findings.append(issue("REQUIRED_PROFILE_NOT_QUALIFIED", path, f"Required profile {required_profile!r} has no qualified execution"))
        if any(isinstance(item, dict) and item.get("status") in {"blocked", "tool-error", "not-executed"} for item in executions):
            findings.append(issue("QUALIFIED_WITH_FAILED_EXECUTION", path, "Qualified evidence cannot contain blocked, tool-error or not-executed executions"))
        if not isinstance(value.get("completionRef"), str) or not value.get("completionRef"):
            findings.append(issue("COMPLETION_REF_REQUIRED", path, "Qualified evidence requires completionRef"))

    return findings, {"selection": selection, "evidenceId": evidence_id, "technicalStatus": technical_status}


def validate_completion(value: Any, evidence: Any, contracts: dict[str, dict[str, Any]], path: str = "completion") -> tuple[list[dict[str, Any]], dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    contract = contracts["completion"]
    evidence_findings, evidence_result = validate_evidence(evidence, contracts, "evidence")
    findings.extend(evidence_findings)
    if not isinstance(value, dict):
        return findings + [issue("COMPLETION_INVALID_SHAPE", path, "Completion must be a JSON object")], {}
    require_fields(value, contract.get("requiredFields", []), path, findings)
    if value.get("schemaVersion") != contract.get("completionSchema"):
        findings.append(issue("COMPLETION_SCHEMA_INVALID", path, f"Expected schema {contract.get('completionSchema')!r}"))
    completion_id = value.get("completionId")
    if not isinstance(completion_id, str) or not re.fullmatch(contract.get("completionIdPattern", r".+"), completion_id):
        findings.append(issue("COMPLETION_ID_INVALID", path, "completionId does not match the contract pattern"))
    if isinstance(evidence, dict):
        if value.get("evidenceRef") != evidence.get("evidenceId"):
            findings.append(issue("EVIDENCE_REF_MISMATCH", path, "evidenceRef does not match evidenceId"))
        if value.get("changeRef") != evidence.get("changeRef"):
            findings.append(issue("CHANGE_REF_MISMATCH", path, "changeRef does not match evidence changeRef"))

    status = value.get("status")
    if status not in contract.get("statuses", []):
        findings.append(issue("COMPLETION_STATUS_UNKNOWN", path, f"Unknown completion status: {status!r}"))
    if evidence_result.get("technicalStatus") and status != evidence_result.get("technicalStatus"):
        findings.append(issue("EVIDENCE_STATUS_MISMATCH", path, "Completion status must equal evidence technicalStatus"))

    criteria = value.get("criterionResults")
    if not isinstance(criteria, list):
        findings.append(issue("CRITERIA_INVALID", path, "criterionResults must be a list"))
        criteria = []
    expected_ids = ids(contract.get("criteria"))
    actual_ids: list[str] = []
    criterion_statuses: list[str] = []
    for index, item in enumerate(criteria):
        cpath = f"{path}.criterionResults[{index}]"
        if not isinstance(item, dict):
            findings.append(issue("CRITERION_INVALID", cpath, "Criterion result must be an object"))
            continue
        criterion_id = item.get("criterionId")
        criterion_status = item.get("status")
        if isinstance(criterion_id, str):
            actual_ids.append(criterion_id)
        criterion_statuses.append(criterion_status)
        if criterion_id not in expected_ids:
            findings.append(issue("CRITERION_UNKNOWN", cpath, f"Unknown criterionId: {criterion_id!r}"))
        if criterion_status not in contract.get("criterionStatuses", []):
            findings.append(issue("CRITERION_STATUS_UNKNOWN", cpath, f"Unknown criterion status: {criterion_status!r}"))
    for duplicate in duplicate_values(actual_ids):
        findings.append(issue("CRITERION_DUPLICATE", path, f"Duplicate criterionId: {duplicate}"))
    missing_ids = [criterion_id for criterion_id in expected_ids if criterion_id not in actual_ids]
    if missing_ids:
        findings.append(issue("CRITERIA_MISSING", path, "Completion criteria are missing", missing=missing_ids))

    blockers = value.get("openBlockingFindingIds")
    tools = value.get("openToolErrorIds")
    accepted = value.get("acceptedFindingIds")
    reviewers = value.get("reviewers")
    for field_name, field_value in (("openBlockingFindingIds", blockers), ("openToolErrorIds", tools), ("acceptedFindingIds", accepted), ("reviewers", reviewers)):
        if not isinstance(field_value, list):
            findings.append(issue("COMPLETION_LIST_INVALID", path, f"{field_name} must be a list"))
    blockers = blockers if isinstance(blockers, list) else []
    tools = tools if isinstance(tools, list) else []
    accepted = accepted if isinstance(accepted, list) else []
    reviewers = reviewers if isinstance(reviewers, list) else []

    qualified_criterion_statuses = set(contract.get("qualifiedCriterionStatuses", []))
    all_qualified = bool(criteria) and all(status_value in qualified_criterion_statuses for status_value in criterion_statuses)
    failed_or_pending = any(status_value in {"failed", "pending"} for status_value in criterion_statuses)
    if status == "qualified":
        if not all_qualified or blockers or tools or accepted:
            findings.append(issue("QUALIFIED_STATE_INVALID", path, "qualified requires all criteria satisfied and no open or accepted findings"))
        if not reviewers:
            findings.append(issue("QUALIFIED_REVIEWER_REQUIRED", path, "qualified requires at least one reviewer"))
    elif status == "qualified-with-findings":
        if not all_qualified or blockers or tools or not accepted:
            findings.append(issue("QUALIFIED_WITH_FINDINGS_STATE_INVALID", path, "qualified-with-findings requires satisfied criteria, accepted findings and no blocker or tool error"))
        if not reviewers:
            findings.append(issue("QUALIFIED_REVIEWER_REQUIRED", path, "qualified-with-findings requires at least one reviewer"))
    elif status == "blocked":
        if not (blockers or tools or any(item == "failed" for item in criterion_statuses)):
            findings.append(issue("BLOCKED_CAUSE_REQUIRED", path, "blocked requires a failed criterion, blocking finding or tool error"))
    elif status == "incomplete":
        if not (failed_or_pending or evidence_result.get("technicalStatus") == "incomplete"):
            findings.append(issue("INCOMPLETE_CAUSE_REQUIRED", path, "incomplete requires pending/failed criteria or incomplete evidence"))
    elif status == "cancelled":
        if not isinstance(value.get("cancellationReason"), str) or not value.get("cancellationReason").strip():
            findings.append(issue("CANCELLATION_REASON_REQUIRED", path, "cancelled requires cancellationReason"))

    if status in {"qualified", "qualified-with-findings"} and not isinstance(value.get("completedAt"), str):
        findings.append(issue("COMPLETED_AT_REQUIRED", path, "Qualified completion requires completedAt"))
    return findings, {"completionId": completion_id, "status": status}


def atomic_write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent), text=True)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_name, path)
    finally:
        if os.path.exists(tmp_name):
            os.unlink(tmp_name)


def build_report(operation: str, findings: list[dict[str, Any]], tool_errors: list[dict[str, Any]], details: dict[str, Any], contracts: dict[str, dict[str, Any]] | None) -> dict[str, Any]:
    status = "TOOL_ERROR" if tool_errors else ("FINDINGS" if findings else "PASS")
    versions = {}
    if contracts:
        versions = {key: value.get("contractVersion") for key, value in contracts.items()}
    return {
        "schemaVersion": REPORT_SCHEMA,
        "operation": operation,
        "status": status,
        "findingCount": len(findings),
        "toolErrorCount": len(tool_errors),
        "contractVersions": versions,
        "details": details,
        "findings": findings,
        "toolErrors": tool_errors,
    }


def parser() -> argparse.ArgumentParser:
    project_root = Path(__file__).resolve().parent.parent
    result = argparse.ArgumentParser(prog="engineering-contracts.py", description="Validate Springmaster engineering contracts and records.")
    result.add_argument("--contract-root", type=Path, default=project_root / "contracts/governance/engineering")
    result.add_argument("--out", type=Path, help="Write a deterministic JSON report")
    result.add_argument("--check", action="store_true", help="Return exit 1 when validation findings exist")
    sub = result.add_subparsers(dest="operation", required=True)
    sub.add_parser("contracts", help="Validate the four engineering contracts")
    profiles = sub.add_parser("profiles", help="Validate a change classification and select required profiles")
    profiles.add_argument("--input", type=Path, required=True)
    evidence = sub.add_parser("evidence", help="Validate an engineering evidence record")
    evidence.add_argument("--input", type=Path, required=True)
    completion = sub.add_parser("completion", help="Validate an engineering completion record against evidence")
    completion.add_argument("--input", type=Path, required=True)
    completion.add_argument("--evidence", type=Path, required=True)
    return result


def main() -> int:
    args = parser().parse_args()
    findings: list[dict[str, Any]] = []
    tool_errors: list[dict[str, Any]] = []
    details: dict[str, Any] = {}
    contracts: dict[str, dict[str, Any]] | None = None
    try:
        contracts = load_contracts(args.contract_root.resolve())
        findings.extend(semantic_contract_findings(contracts))
        if args.operation == "profiles":
            value = load_json(args.input.resolve())
            profile_findings, selection = validate_classification(value, contracts)
            findings.extend(profile_findings)
            details["profileSelection"] = selection
        elif args.operation == "evidence":
            value = load_json(args.input.resolve())
            evidence_findings, result = validate_evidence(value, contracts)
            findings.extend(evidence_findings)
            details["evidence"] = result
        elif args.operation == "completion":
            value = load_json(args.input.resolve())
            evidence = load_json(args.evidence.resolve())
            completion_findings, result = validate_completion(value, evidence, contracts)
            findings.extend(completion_findings)
            details["completion"] = result
    except ToolError as exc:
        item: dict[str, Any] = {"code": exc.code, "message": exc.message}
        if exc.path:
            item["path"] = exc.path
        tool_errors.append(item)
    report = build_report(args.operation, findings, tool_errors, details, contracts)
    if args.out:
        atomic_write_json(args.out.resolve(), report)
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    if tool_errors:
        return 2
    if findings and args.check:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
