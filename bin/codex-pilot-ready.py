#!/usr/bin/env python3
"""Strict read-only project readiness gate for the Springmaster Codex pilot."""
from __future__ import annotations

import argparse
import json
import os
import re
import stat
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPORT_SCHEMA = "springmaster.codex-pilot-readiness-report.v1"
EXPECTED_PROJECT_ID = "springmaster"
EXPECTED_TOOLKIT_VERSION = "1.1.1"
REQUIRED_RULE_IDS = {
    "AIA-PROJECT-001",
    "AIA-PATCH-001",
    "AIA-HARNESS-001",
    "AIA-CONCEPT-001",
    "AIA-CUTOVER-001",
    "AIA-HYGIENE-001",
    "AIA-INVENTORY-001",
    "AIA-EXECUTION-001",
    "AIA-TASK-SEMANTICS-001",
}
REQUIRED_TEST_PATHS = {"bin/agent-task-it.sh", "bin/codex-pilot-ready-it.sh"}
REQUIRED_FIXTURE_ID = "codex-pilot-readiness-v1"
REQUIRED_FILES = {
    "PROJECT_DOCS/ADR/ADR-0015-controlled-ai-assisted-development-pilot.md",
    "PROJECT_DOCS/GOVERNANCE/AI_AGENT_DEVELOPMENT_GOVERNANCE.md",
    "PROJECT_DOCS/DEMO/BUSINESS_PARTNER_CODEX_PILOT_FACHKONZEPT.md",
    "PROJECT_DOCS/TOOLING/CODEX_PILOT_OPERATIONS.md",
    "PROJECT_DOCS/TOOLING/OPERATOR_COMMAND_EFFECT_CONTRACT.md",
    "contracts/governance/agent/codex-pilot-contract.json",
    "contracts/governance/agent/agent-task-contract.schema.json",
    "contracts/governance/agent/operator-command-effect.schema.json",
    "contracts/governance/agent/codex-invocation-record.schema.json",
    "contracts/pilots/codex/business-partner-pilot-acceptance.json",
    "bin/agent-task.py",
    "bin/agent-task.sh",
    "bin/agent-task-it.sh",
    "bin/codex-pilot-ready.py",
    "bin/codex-pilot-ready.sh",
    "bin/codex-pilot-ready-it.sh",
    "src/test/resources/tooling/codex-pilot-readiness-v1/expected-cases.json",
}


class GateToolError(RuntimeError):
    def __init__(self, code: str, message: str, **details: object) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def run(argv: list[str], *, cwd: Path, timeout: int | None = None) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            argv,
            cwd=cwd,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            check=False,
        )
    except FileNotFoundError as exc:
        raise GateToolError("COMMAND_NOT_FOUND", f"Command not found: {argv[0]}", argv=argv) from exc
    except subprocess.TimeoutExpired as exc:
        raise GateToolError("COMMAND_TIMEOUT", "Command timed out", argv=argv, timeoutSeconds=timeout) from exc


def discover_root(explicit: str | None) -> Path:
    start = Path(explicit).expanduser() if explicit else Path.cwd()
    result = run(["git", "rev-parse", "--show-toplevel"], cwd=start)
    if result.returncode != 0 or not result.stdout.strip():
        raise GateToolError("PROJECT_ROOT_NOT_FOUND", "No Git project root could be resolved", start=str(start))
    return Path(result.stdout.strip()).resolve()


def git(root: Path, *args: str) -> str:
    result = run(["git", *args], cwd=root)
    if result.returncode != 0:
        raise GateToolError("GIT_COMMAND_FAILED", "Git command failed", argv=["git", *args], stderr=result.stderr[-2000:])
    return result.stdout.strip()


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise GateToolError("JSON_MISSING", "JSON file is missing", path=str(path)) from exc
    except json.JSONDecodeError as exc:
        raise GateToolError("JSON_INVALID", "JSON file is invalid", path=str(path), line=exc.lineno, column=exc.colno) from exc
    if not isinstance(value, dict):
        raise GateToolError("JSON_ROOT_INVALID", "JSON root must be an object", path=str(path))
    return value


def parse_env(path: Path) -> dict[str, str]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError as exc:
        raise GateToolError("PROJECT_ENV_MISSING", "Project environment is missing", path=str(path)) from exc
    values: dict[str, str] = {}
    for number, raw in enumerate(lines, start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            raise GateToolError("PROJECT_ENV_INVALID", "Invalid project environment line", path=str(path), line=number)
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    return values


def frontmatter_value(path: Path, key: str) -> str | None:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---\n", 4)
    if end < 0:
        return None
    for raw in text[4:end].splitlines():
        if raw.startswith(f"{key}:"):
            return raw.split(":", 1)[1].strip()
    return None


def path_contains(parent: Path, child: Path) -> bool:
    try:
        child.relative_to(parent)
        return True
    except ValueError:
        return False


def symlink_component(path: Path) -> Path | None:
    current = Path(path.anchor)
    for part in path.parts[1:]:
        current = current / part
        if current.exists() and stat.S_ISLNK(current.lstat().st_mode):
            return current
    return None


def finding(findings: list[dict[str, Any]], rule_id: str, code: str, message: str, **details: object) -> None:
    item: dict[str, Any] = {"ruleId": rule_id, "code": code, "message": message}
    if details:
        item["details"] = details
    findings.append(item)


def check_external_roots(root: Path, common: Path, findings: list[dict[str, Any]]) -> dict[str, str]:
    result: dict[str, str] = {}
    for variable in ("COCONDO_WORKTREE_ROOT", "COCONDO_AGENT_RUN_ROOT", "COCONDO_ARTIFACT_ROOT"):
        raw = os.environ.get(variable)
        if not raw:
            finding(findings, "AIA-HYGIENE-001", "EXTERNAL_ROOT_UNSET", f"{variable} is not set", variable=variable)
            continue
        path = Path(raw).expanduser()
        if not path.is_absolute():
            finding(findings, "AIA-HYGIENE-001", "EXTERNAL_ROOT_NOT_ABSOLUTE", f"{variable} is not absolute", value=raw)
            continue
        if not path.exists() or not path.is_dir():
            finding(findings, "AIA-HYGIENE-001", "EXTERNAL_ROOT_MISSING", f"{variable} must exist and be a directory", value=raw)
            continue
        if not os.access(path, os.W_OK | os.X_OK):
            finding(findings, "AIA-HYGIENE-001", "EXTERNAL_ROOT_NOT_WRITABLE", f"{variable} must be writable and searchable", value=raw)
            continue
        linked = symlink_component(path)
        if linked is not None:
            finding(findings, "AIA-HYGIENE-001", "EXTERNAL_ROOT_SYMLINK", f"{variable} contains a symlink component", component=str(linked))
            continue
        resolved = path.resolve()
        if path_contains(root, resolved) or path_contains(resolved, root):
            finding(findings, "AIA-HYGIENE-001", "EXTERNAL_ROOT_PROJECT_OVERLAP", f"{variable} overlaps Springmaster", value=str(resolved))
        if path_contains(common, resolved) or path_contains(resolved, common):
            finding(findings, "AIA-HYGIENE-001", "EXTERNAL_ROOT_GIT_OVERLAP", f"{variable} overlaps the Git common directory", value=str(resolved))
        result[variable] = str(resolved)
    values = list(result.values())
    if len(values) != len(set(values)):
        finding(findings, "AIA-HYGIENE-001", "EXTERNAL_ROOTS_NOT_DISTINCT", "External roots must be pairwise distinct", roots=result)
    return result


def run_self_test(root: Path, path: str, findings: list[dict[str, Any]]) -> None:
    completed = run([str(root / path)], cwd=root, timeout=180)
    if completed.returncode != 0:
        finding(
            findings,
            "AIA-HARNESS-001",
            "SELF_TEST_FAILED",
            f"Pilot self-test failed: {path}",
            exitCode=completed.returncode,
            stdout=completed.stdout[-2000:],
            stderr=completed.stderr[-2000:],
        )


def evaluate(root: Path, mode: str, skip_self_tests: bool) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    details: dict[str, Any] = {"mode": mode, "projectRoot": str(root)}
    common = Path(git(root, "rev-parse", "--path-format=absolute", "--git-common-dir")).resolve()
    details["gitCommonDir"] = str(common)

    for relative in sorted(REQUIRED_FILES):
        path = root / relative
        if not path.is_file():
            finding(findings, "AIA-PROJECT-001", "REQUIRED_FILE_MISSING", "Required pilot file is missing", path=relative)

    if not findings or all(item["code"] != "REQUIRED_FILE_MISSING" for item in findings):
        expected_statuses = {
            "PROJECT_DOCS/ADR/ADR-0015-controlled-ai-assisted-development-pilot.md": "accepted",
            "PROJECT_DOCS/GOVERNANCE/AI_AGENT_DEVELOPMENT_GOVERNANCE.md": "active",
            "PROJECT_DOCS/DEMO/BUSINESS_PARTNER_CODEX_PILOT_FACHKONZEPT.md": "active",
            "PROJECT_DOCS/TOOLING/CODEX_PILOT_OPERATIONS.md": "active",
            "PROJECT_DOCS/TOOLING/OPERATOR_COMMAND_EFFECT_CONTRACT.md": "active",
        }
        for relative, expected in expected_statuses.items():
            actual = frontmatter_value(root / relative, "status")
            if actual != expected:
                finding(findings, "AIA-PROJECT-001", "DOCUMENT_STATUS_INVALID", "Pilot document has the wrong status", path=relative, expected=expected, actual=actual)

    pilot = load_json(root / "contracts/governance/agent/codex-pilot-contract.json")
    task_schema = load_json(root / "contracts/governance/agent/agent-task-contract.schema.json")
    effect_schema = load_json(root / "contracts/governance/agent/operator-command-effect.schema.json")
    invocation_schema = load_json(root / "contracts/governance/agent/codex-invocation-record.schema.json")
    acceptance = load_json(root / "contracts/pilots/codex/business-partner-pilot-acceptance.json")
    if pilot.get("schemaVersion") != "springmaster.codex-pilot-contract.v1" or pilot.get("status") != "active":
        finding(findings, "AIA-PROJECT-001", "PILOT_CONTRACT_INVALID", "Pilot contract schema or status is invalid")
    pilot_state = pilot.get("pilot") if isinstance(pilot.get("pilot"), dict) else {}
    if pilot_state.get("repositoryId") != EXPECTED_PROJECT_ID or pilot_state.get("integrationBranch") != "main":
        finding(findings, "AIA-PROJECT-001", "PILOT_BOUNDARY_INVALID", "Pilot repository or branch boundary is invalid", pilot=pilot_state)
    if pilot_state.get("currentLifecycle") != "PROJECT_READY":
        finding(findings, "AIA-CUTOVER-001", "PILOT_LIFECYCLE_INVALID", "Committed pilot contract must stop at PROJECT_READY", actual=pilot_state.get("currentLifecycle"))
    if pilot_state.get("codexExecutionBeforeProjectReady") != "forbidden" or pilot_state.get("managedProjectMutation") != "forbidden":
        finding(findings, "AIA-CUTOVER-001", "PILOT_PROHIBITION_INVALID", "Pre-readiness Codex and managed-project mutation must remain forbidden")
    readiness = pilot.get("projectReadiness") if isinstance(pilot.get("projectReadiness"), dict) else {}
    if readiness.get("doesNotAuthorizeWritableCodex") is not True or readiness.get("nextAction") != "CODEX_CALIBRATION":
        finding(findings, "AIA-CUTOVER-001", "CUTOVER_SEMANTICS_INVALID", "PROJECT_READY must authorize calibration only", projectReadiness=readiness)
    if task_schema.get("$id") != "urn:springmaster:schema:agent-task:v2" or task_schema.get("additionalProperties") is not False:
        finding(findings, "AIA-HARNESS-001", "TASK_SCHEMA_INVALID", "Task schema identity or closed-object policy is invalid")
    required_task_fields = set(task_schema.get("required", []))
    if not {"allowedPaths", "forbiddenPaths", "capabilities", "qualificationCommands", "requiredEvidence"} <= required_task_fields:
        finding(findings, "AIA-HARNESS-001", "TASK_SCHEMA_INCOMPLETE", "Task schema misses required boundary fields")
    if effect_schema.get("$id") != "urn:springmaster:schema:operator-command-effect:v1" or effect_schema.get("additionalProperties") is not False:
        finding(findings, "AIA-EXECUTION-001", "OPERATOR_EFFECT_SCHEMA_INVALID", "Operator command effect schema identity or closed-object policy is invalid")
    if invocation_schema.get("$id") != "urn:springmaster:schema:codex-invocation-record:v1" or invocation_schema.get("additionalProperties") is not False:
        finding(findings, "AIA-EXECUTION-001", "INVOCATION_RECORD_SCHEMA_INVALID", "Codex invocation record schema identity or closed-object policy is invalid")
    invocation = pilot.get("invocation") if isinstance(pilot.get("invocation"), dict) else {}
    expected_mode_writes = {"analysis": [], "implementation": ["task-worktree"], "qualification": []}
    expected_mode_mutations = {"analysis": "none", "implementation": "task-worktree-only", "qualification": "none"}
    expected_sandboxes = {
        "analysis": {"cliValue": "read-only", "recordValue": "linux-bwrap-read-only"},
        "implementation": {"cliValue": "workspace-write", "recordValue": "linux-bwrap-workspace-write"},
        "qualification": {"cliValue": "read-only", "recordValue": "linux-bwrap-read-only"},
    }
    forbidden_flags = set(invocation.get("forbiddenFlags", []))
    required_flags = set(invocation.get("requiredBooleanFlags", []))
    hard_forbidden = {"--add-dir", "--dangerously-bypass-approvals-and-sandbox", "--yolo", "--full-auto", "--config", "-c", "--profile", "-p"}
    always_forbidden_writes = set(invocation.get("alwaysForbiddenAgentWriteScopes", []))
    expected_forbidden_writes = {
        "operator-home", "operator-downloads", "integration-worktree", "git-common-directory",
        "external-run-root", "external-artifact-root", "other-repositories", "temporary-directories",
    }
    invocation_valid = (
        invocation.get("recordOperation") == "agent-task record-invocation"
        and invocation.get("immutableAfterRecord") is True
        and invocation.get("requiredArgvPrefix") == ["codex", "exec"]
        and {"--ephemeral", "--ignore-user-config", "--ignore-rules", "--json"} <= required_flags
        and hard_forbidden <= forbidden_flags
        and invocation.get("requiredApprovalPolicy") == "never"
        and invocation.get("modeWriteScopes") == expected_mode_writes
        and invocation.get("modeRepositoryMutationPolicies") == expected_mode_mutations
        and invocation.get("modeSandboxPolicies") == expected_sandboxes
        and invocation.get("platformSandboxImplementation") == "linux-bwrap"
        and invocation.get("additionalWritableRoots") == []
        and invocation.get("agentWriteBoundary") == "task-worktree-only"
        and expected_forbidden_writes <= always_forbidden_writes
        and invocation.get("operatorHandoffPolicy") == "separate-trusted-operator-action"
        and invocation.get("agentHandoffCapability") == "forbidden"
    )
    if not invocation_valid:
        finding(findings, "AIA-EXECUTION-001", "INVOCATION_POLICY_INVALID", "Codex invocation recording policy is incomplete or unsafe", invocation=invocation)
    semantics = pilot.get("taskSemantics") if isinstance(pilot.get("taskSemantics"), dict) else {}
    if set(semantics.get("supportedModes", [])) != {"analysis", "implementation", "qualification"}:
        finding(findings, "AIA-TASK-SEMANTICS-001", "TASK_MODE_POLICY_INVALID", "Task mode policy is incomplete")
    mode_policies = semantics.get("modePolicies", {}) if isinstance(semantics.get("modePolicies"), dict) else {}
    if mode_policies.get("analysis", {}).get("changedPathPolicy") != "forbid" or mode_policies.get("qualification", {}).get("changedPathPolicy") != "forbid":
        finding(findings, "AIA-TASK-SEMANTICS-001", "NON_MUTATING_MODE_POLICY_INVALID", "Analysis and qualification modes must forbid changed paths")
    risk_policies = semantics.get("riskPolicies", {}) if isinstance(semantics.get("riskPolicies"), dict) else {}
    if set(risk_policies) != {"low", "medium", "high", "critical"} or "implementation" in risk_policies.get("critical", {}).get("allowedModes", []):
        finding(findings, "AIA-TASK-SEMANTICS-001", "RISK_POLICY_INVALID", "Risk policies are incomplete or allow critical implementation tasks")
    if acceptance.get("status") != "frozen-for-pilot" or acceptance.get("pilotId") != "springmaster-codex-pilot-v1":
        finding(findings, "AIA-CONCEPT-001", "ACCEPTANCE_CONTRACT_INVALID", "Business Partner acceptance contract is not frozen for the pilot")
    if acceptance.get("traceability", {}).get("requiredCoveragePercent") != 100:
        finding(findings, "AIA-CONCEPT-001", "TRACEABILITY_TARGET_INVALID", "Traceability target must be 100 percent")
    if acceptance.get("safetyTargets", {}).get("writesOutsideTaskWorktree") != 0:
        finding(findings, "AIA-CONCEPT-001", "SAFETY_TARGET_INVALID", "Writes outside the task worktree target must be zero")

    project_env = parse_env(root / ".cocondo/tooling/project.env")
    expected_env = {
        "CPATCH_PROJECT_ID": EXPECTED_PROJECT_ID,
        "CPATCH_TOOLKIT_VERSION": EXPECTED_TOOLKIT_VERSION,
        "CPATCH_REQUIRE_CLEAN_TREE": "true",
        "CPATCH_REQUIRE_WORKTREE": "true",
        "CPATCH_REQUIRE_WORKSPACE_FOR_CREATE": "true",
        "CPATCH_INTEGRATION_BRANCH": "main",
    }
    for key, expected in expected_env.items():
        if project_env.get(key) != expected:
            finding(findings, "AIA-PATCH-001", "CPATCH_CONFIG_INVALID", "Cocondo Patch Toolkit project configuration is invalid", key=key, expected=expected, actual=project_env.get(key))
    if not (root / "bin/cpatch").is_file():
        finding(findings, "AIA-PATCH-001", "CPATCH_ENTRYPOINT_MISSING", "Canonical cpatch entrypoint is missing")
    if mode == "live" and not (root / ".cocondo/tooling/cocondo-toolkit.pyz").is_file():
        finding(findings, "AIA-PATCH-001", "CPATCH_TOOLKIT_BINARY_MISSING", "Cocondo Patch Toolkit binary is missing in the live checkout")

    executable_paths = ["bin/agent-task.py", "bin/agent-task.sh", "bin/agent-task-it.sh", "bin/codex-pilot-ready.py", "bin/codex-pilot-ready.sh", "bin/codex-pilot-ready-it.sh"]
    for relative in executable_paths:
        path = root / relative
        if path.is_file() and not os.access(path, os.X_OK):
            finding(findings, "AIA-HARNESS-001", "ENTRYPOINT_NOT_EXECUTABLE", "Pilot entrypoint is not executable", path=relative)
    harness_source = (root / "bin/agent-task.py").read_text(encoding="utf-8") if (root / "bin/agent-task.py").is_file() else ""
    prohibited_markers = ["codex exec", "codex --", "git push", 'add_parser("integrate")', 'add_parser("merge")', 'add_parser("commit")']
    for marker in prohibited_markers:
        if marker in harness_source:
            finding(findings, "AIA-HARNESS-001", "HARNESS_OPERATION_FORBIDDEN", "Pre-cutover harness exposes a forbidden operation", marker=marker)
    required_harness_markers = [
        'add_parser("record-invocation")', "EXTERNAL_ROOT_MISSING", "TASK_MODE_WRITE_FORBIDDEN",
        "INVOCATION_FLAG_FORBIDDEN", "INVOCATION_ADDITIONAL_WRITE_ROOT_FORBIDDEN",
        "INVOCATION_HOST_WRITE_SCOPE_FORBIDDEN", "linux-bwrap",
    ]
    missing_harness_markers = [marker for marker in required_harness_markers if marker not in harness_source]
    if missing_harness_markers:
        finding(findings, "AIA-EXECUTION-001", "HARNESS_HARDENING_MISSING", "Agent harness misses invocation, explicit-root, sandbox or mode-enforcement hardening", missing=missing_harness_markers)

    agents = (root / "AGENTS.md").read_text(encoding="utf-8") if (root / "AGENTS.md").is_file() else ""
    if "## AI-Agent- und Codex-Pilot" not in agents or "PROJECT_READY" not in agents or "PILOT_WRITE_READY" not in agents:
        finding(findings, "AIA-PROJECT-001", "AGENTS_PILOT_RULES_MISSING", "AGENTS.md does not contain the pilot boundary section")
    evidence_policy = pilot.get("evidence", {}) if isinstance(pilot.get("evidence"), dict) else {}
    diagnostic_path = evidence_policy.get("diagnosticUploadPath")
    operator_log_path = evidence_policy.get("operatorLogPath")
    if diagnostic_path != "patches/work":
        finding(findings, "AIA-HYGIENE-001", "DIAGNOSTIC_PATH_INVALID", "Pilot upload diagnostics must use the single-current-workflow operator workspace", actual=diagnostic_path)
    if operator_log_path != "patches/logs/validation":
        finding(findings, "AIA-HYGIENE-001", "OPERATOR_LOG_PATH_INVALID", "Pilot operator logs must use the validation-log area", actual=operator_log_path)
    ignore = (root / ".gitignore").read_text(encoding="utf-8") if (root / ".gitignore").is_file() else ""
    ignore_lines = set(ignore.splitlines())
    for pattern in ("patches/logs/validation/", "patches/work/"):
        if pattern not in ignore_lines:
            finding(findings, "AIA-HYGIENE-001", "IGNORE_PATTERN_MISSING", "Pilot runtime path is not covered by Git ignore rules", pattern=pattern)
    export_config = load_json(root / "export.config.json")
    global_exclude = set(export_config.get("globalExclude", [])) if isinstance(export_config.get("globalExclude"), list) else set()
    if "patches/work/**" not in global_exclude:
        finding(findings, "AIA-HYGIENE-001", "EXPORT_EXCLUDE_MISSING", "Pilot diagnostic handoff workspace is not globally excluded from exports", pattern="patches/work/**")
    profiles = export_config.get("profiles", {}) if isinstance(export_config.get("profiles"), dict) else {}
    for profile_id in ("full", "patches"):
        profile = profiles.get(profile_id, {}) if isinstance(profiles.get(profile_id), dict) else {}
        excludes = set(profile.get("exclude", []))
        for pattern in ("patches/logs/validation/**", "patches/work/**"):
            if pattern not in excludes and pattern not in global_exclude:
                finding(findings, "AIA-HYGIENE-001", "EXPORT_EXCLUDE_MISSING", "Pilot runtime path is not excluded from the export profile", profile=profile_id, pattern=pattern)
    directory_contract = load_json(root / "contracts/governance/project-structure/project-directory-contract.json")
    areas = directory_contract.get("areas", [])
    area_patterns = {pattern for area in areas if isinstance(area, dict) for pattern in area.get("patterns", [])}
    for pattern in ("patches/logs/validation/**", "patches/work/**"):
        if pattern not in area_patterns:
            finding(findings, "AIA-HYGIENE-001", "DIRECTORY_AREA_MISSING", "Pilot runtime path is not covered by the directory contract", pattern=pattern)

    catalog = load_json(root / "contracts/governance/quality/quality-rule-catalog.json")
    rules = catalog.get("rules", [])
    rule_ids = {item.get("ruleId") for item in rules if isinstance(item, dict)}
    if not REQUIRED_RULE_IDS <= rule_ids:
        finding(findings, "AIA-INVENTORY-001", "QUALITY_RULES_MISSING", "Pilot quality rules are not fully registered", missing=sorted(REQUIRED_RULE_IDS - rule_ids))
    for item in rules:
        if isinstance(item, dict) and item.get("ruleId") in REQUIRED_RULE_IDS:
            if item.get("lifecycle") != "qualified-report-only" or "report-only" not in item.get("supportedEnforcementModes", []):
                finding(findings, "AIA-INVENTORY-001", "QUALITY_RULE_REGISTRATION_INVALID", "Pilot quality rule is not registered consistently with the current report-only registry", ruleId=item.get("ruleId"))
    gate_registry = load_json(root / "contracts/governance/quality/gate-registry.json")
    gates = gate_registry.get("gates", [])
    pilot_gates = [item for item in gates if isinstance(item, dict) and item.get("gateId") == "codex-pilot-readiness-v1"]
    if len(pilot_gates) != 1:
        finding(findings, "AIA-INVENTORY-001", "READINESS_GATE_REGISTRATION_INVALID", "Readiness gate must be registered exactly once", count=len(pilot_gates))
    else:
        gate = pilot_gates[0]
        if gate.get("lifecycle") != "qualified-report-only" or gate.get("defaultEnforcementMode") != "report-only" or gate.get("entrypoint") != "bin/codex-pilot-ready.sh":
            finding(findings, "AIA-INVENTORY-001", "READINESS_GATE_REGISTRATION_INVALID", "Readiness gate registration is inconsistent with the current registry or points to the wrong entrypoint", gate=gate)

    inventory = load_json(root / "contracts/governance/testing/test-inventory-baseline.json")
    test_paths = {item.get("path") for item in inventory.get("toolingTests", []) if isinstance(item, dict)}
    if not REQUIRED_TEST_PATHS <= test_paths:
        finding(findings, "AIA-INVENTORY-001", "PILOT_TESTS_MISSING", "Pilot test scripts are not fully inventoried", missing=sorted(REQUIRED_TEST_PATHS - test_paths))
    fixture_contract = load_json(root / "contracts/governance/testing/test-fixture-contract.json")
    fixture_paths = {item.get("path") for item in fixture_contract.get("fixtureEntries", []) if isinstance(item, dict)}
    if f"src/test/resources/tooling/{REQUIRED_FIXTURE_ID}/expected-cases.json" not in fixture_paths:
        finding(findings, "AIA-INVENTORY-001", "PILOT_FIXTURE_MISSING", "Pilot readiness fixture is not registered")

    if mode == "live":
        branch = git(root, "branch", "--show-current")
        status = git(root, "status", "--porcelain=v1", "--untracked-files=all")
        details["branch"] = branch
        details["head"] = git(root, "rev-parse", "HEAD")
        if branch != "main":
            finding(findings, "AIA-PROJECT-001", "LIVE_BRANCH_INVALID", "Live readiness requires main", actual=branch)
        if status:
            finding(findings, "AIA-PROJECT-001", "LIVE_TREE_DIRTY", "Live readiness requires a clean worktree", status=status)
        details["externalRoots"] = check_external_roots(root, common, findings)
    else:
        details["branch"] = git(root, "branch", "--show-current")
        details["head"] = git(root, "rev-parse", "HEAD")
        details["externalRoots"] = "NOT_REQUIRED_IN_CANDIDATE_MODE"

    if not skip_self_tests:
        for path in sorted(REQUIRED_TEST_PATHS):
            if (root / path).is_file() and os.access(root / path, os.X_OK):
                run_self_test(root, path, findings)

    status = "PROJECT_READY" if not findings else "FINDINGS"
    return {
        "schemaVersion": REPORT_SCHEMA,
        "generatedAt": utc_now(),
        "status": status,
        "nextAction": "CODEX_CALIBRATION" if status == "PROJECT_READY" else "REMAIN_PRE_CUTOVER",
        "writableCodexAuthorized": False,
        "findingCount": len(findings),
        "findings": findings,
        "details": details,
    }


def render_text(report: dict[str, Any]) -> str:
    lines = [
        f"CODEX_PILOT_READINESS={report['status']}",
        f"NEXT_ACTION={report['nextAction']}",
        f"WRITABLE_CODEX_AUTHORIZED={'true' if report['writableCodexAuthorized'] else 'false'}",
        f"FINDING_COUNT={report['findingCount']}",
    ]
    for index, item in enumerate(report["findings"], start=1):
        lines.append(f"FINDING_{index}={item['ruleId']}:{item['code']}:{item['message']}")
    return "\n".join(lines) + "\n"


def write(path: Path | None, content: str) -> None:
    if path is None:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(content, encoding="utf-8")
    os.replace(temporary, path)


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("operation", choices=("project",))
    mode = result.add_mutually_exclusive_group(required=True)
    mode.add_argument("--candidate", action="store_true")
    mode.add_argument("--live", action="store_true")
    result.add_argument("--check", action="store_true")
    result.add_argument("--project-root")
    result.add_argument("--out-json", type=Path)
    result.add_argument("--out-text", type=Path)
    result.add_argument("--skip-self-tests", action="store_true", help=argparse.SUPPRESS)
    return result


def main() -> int:
    args = parser().parse_args()
    try:
        root = discover_root(args.project_root)
        report = evaluate(root, "live" if args.live else "candidate", args.skip_self_tests)
    except GateToolError as exc:
        report = {
            "schemaVersion": REPORT_SCHEMA,
            "generatedAt": utc_now(),
            "status": "TOOL_ERROR",
            "nextAction": "REMAIN_PRE_CUTOVER",
            "writableCodexAuthorized": False,
            "findingCount": 0,
            "findings": [],
            "toolError": {"code": exc.code, "message": exc.message, "details": exc.details},
        }
    json_text = json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    text = render_text(report)
    write(args.out_json, json_text)
    write(args.out_text, text)
    if args.out_json is None and args.out_text is None:
        sys.stdout.write(text)
    if report["status"] == "TOOL_ERROR":
        return 2
    if args.check and report["status"] != "PROJECT_READY":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
