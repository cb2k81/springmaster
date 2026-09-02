#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
RUN_DIR="${PROJECT_ROOT}/build/engineering-contracts-it/$(date +%Y%m%d_%H%M%S)_$$"
mkdir -p "${RUN_DIR}"

python3 - "${PROJECT_ROOT}" "${RUN_DIR}" <<'PY'
from __future__ import annotations

import copy
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

project_root = Path(sys.argv[1])
run_dir = Path(sys.argv[2])
expectation_file = project_root / "src/test/resources/tooling/engineering-contracts-v1/expected-cases.json"
expectations = json.loads(expectation_file.read_text(encoding="utf-8"))["cases"]
tool = project_root / "bin/engineering-contracts.py"
source_contract_root = project_root / "contracts/governance/engineering"


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def tree_hash(path: Path) -> str:
    digest = hashlib.sha256()
    for item in sorted(candidate for candidate in path.rglob("*") if candidate.is_file()):
        digest.update(item.relative_to(path).as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(item.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def classification(change_id: str = "SPRINGMASTER-S01", classes: list[str] | None = None, risk: str = "low", indicators: list[str] | None = None, flags: dict[str, bool] | None = None) -> dict:
    return {
        "schemaVersion": "springmaster.engineering-change-classification.v1",
        "changeId": change_id,
        "classes": classes if classes is not None else ["documentation"],
        "declaredRiskLevel": risk,
        "riskIndicators": indicators if indicators is not None else [],
        "flags": flags if flags is not None else {
            "governanceMigration": False,
            "strictPromotion": False,
            "periodicAudit": False,
            "releaseCandidate": False,
        },
    }


def selection(required: list[str]) -> dict:
    return {
        "schemaVersion": "springmaster.engineering-profile-selection.v1",
        "requiredProfiles": required,
        "optionalProfiles": ["fast"],
    }


def base_evidence(status: str = "incomplete", required_profiles: list[str] | None = None) -> dict:
    required = required_profiles if required_profiles is not None else ["qualification"]
    executions = [
        {
            "executionId": f"EXEC-{profile.upper()}",
            "profileId": profile,
            "checkId": f"CHECK-{profile.upper()}",
            "status": "passed" if status in {"qualified", "qualified-with-findings"} else "not-executed",
            "command": f"./bin/example.sh {profile}",
            "reportRefs": [f"build/example/{profile}.json"] if status in {"qualified", "qualified-with-findings"} else [],
        }
        for profile in required
    ]
    return {
        "schemaVersion": "springmaster.engineering-evidence.v1",
        "evidenceId": "ENG-EVID-SPRINGMASTER-S01",
        "changeRef": "SPRINGMASTER-S01",
        "sprintRef": "SPRINGMASTER-SPRINT-001",
        "baseline": {
            "gitHead": "f23b994412569f8e95e6f9f82285f6ec1d18916d",
            "dirty": False,
            "sourceExportSha256": "a" * 64,
        },
        "acceptedScope": {
            "desiredResult": "Materialize engineering contracts",
            "requirements": ["EQP-REQ-001", "EQP-REQ-002"],
            "paths": ["contracts/governance/engineering/**"],
            "outOfScope": ["strict promotion"],
        },
        "classification": classification(),
        "profileSelection": selection(required),
        "ruleSources": ["PROJECT_DOCS/GOVERNANCE/ENGINEERING_GOVERNANCE.md"],
        "executions": executions,
        "findings": [],
        "deferrals": [],
        "technicalDebt": [],
        "impact": {
            "version": "minor",
            "projectNew": "not-assessed-in-s01",
            "managedProjects": "none",
            "dependencies": "none",
            "documentation": "engineering-governance-and-sprint-status",
        },
        "artifactFamilies": ["engineering-contracts", "contract-fixtures"],
        "technicalStatus": status,
        "completionRef": "ENG-COMP-SPRINGMASTER-S01" if status in {"qualified", "qualified-with-findings"} else None,
    }


def base_completion(status: str = "qualified", criterion_status: str = "passed") -> dict:
    return {
        "schemaVersion": "springmaster.engineering-completion.v1",
        "completionId": "ENG-COMP-SPRINGMASTER-S01",
        "changeRef": "SPRINGMASTER-S01",
        "evidenceRef": "ENG-EVID-SPRINGMASTER-S01",
        "status": status,
        "criterionResults": [
            {"criterionId": f"ENG-COMP-{index:03d}", "status": criterion_status}
            for index in range(1, 15)
        ],
        "openBlockingFindingIds": [],
        "openToolErrorIds": [],
        "acceptedFindingIds": [],
        "reviewers": ["springmaster-maintainers"] if status in {"qualified", "qualified-with-findings"} else [],
        "completedAt": "2026-07-23" if status in {"qualified", "qualified-with-findings"} else None,
        "cancellationReason": None,
    }


def recovery_record(integration_hash: str) -> dict:
    return {
        "schemaVersion": "springmaster.maintenance-recovery.v1",
        "recordId": "MAINT-REC-DEFECTIVE-GATE",
        "authority": "PROJECT_DOCS/ADR/ADR-0020-enabling-governance-and-recoverable-tooling.md",
        "classification": classification(
            change_id="SPRINGMASTER-S006-M001",
            classes=["contract", "test", "tooling"],
            risk="critical",
            indicators=["public-or-reusable-contract", "central-security-or-integrity-boundary"],
        ),
        "defect": {
            "component": "copied-contract-gate",
            "entrypoint": "bin/defective-gate.sh",
            "reasonCode": "INTENTIONAL_FIXTURE_DEFECT",
            "category": "TOOLING",
            "message": "Copied gate exits before validating its input",
        },
        "baseline": {
            "gitHead": "4a28f2de2d4cf33f2b772e96745f2bcbf317a28d",
            "integrationRef": "main",
            "integrationTreeSha256": integration_hash,
        },
        "isolatedWorktree": {
            "path": "fixture/isolated-repair",
            "baseCommit": "4a28f2de2d4cf33f2b772e96745f2bcbf317a28d",
            "detached": True,
            "integrationWorktree": False,
        },
        "authorizedRepairPaths": ["bin/defective-gate.sh"],
        "actualRepairPaths": ["bin/defective-gate.sh"],
        "authorizedCapabilities": [
            "read-source",
            "edit-authorized-paths",
            "run-unaffected-bootstrap",
            "run-targeted-qualification",
            "run-final-qualification",
            "prepare-integration-disposition",
        ],
        "usedCapabilities": [
            "read-source",
            "edit-authorized-paths",
            "run-unaffected-bootstrap",
            "run-targeted-qualification",
            "run-final-qualification",
            "prepare-integration-disposition",
        ],
        "forbiddenOperations": ["direct-main-mutation", "push", "cross-project-mutation"],
        "observedForbiddenOperations": [],
        "unaffectedBootstrapCommands": ["python3 fixture/unaffected-bootstrap.py"],
        "targetedQualification": {
            "profileId": "fast",
            "command": "bash bin/defective-gate.sh",
            "status": "passed",
            "exitCode": 0,
            "reportRefs": ["fixture/targeted.txt"],
        },
        "finalQualification": {
            "profileId": "qualification",
            "command": "bash bin/full-boundary.sh",
            "status": "passed",
            "exitCode": 0,
            "reportRefs": ["fixture/full-boundary.txt"],
        },
        "disposition": {
            "integration": "requires-human-integration",
            "delivery": "not-requested",
        },
        "recoverability": {
            "recoverable": True,
            "maintenanceAllowed": True,
            "safeNextAction": "Review the isolated diff before the separately authorized integration boundary.",
        },
    }


failures: list[str] = []
results: list[dict] = []
for expected in expectations:
    case_id = expected["id"]
    case_dir = run_dir / case_id
    contract_root = case_dir / "contracts"
    shutil.copytree(source_contract_root, contract_root)
    input_path = case_dir / "input.json"
    evidence_path = case_dir / "evidence.json"
    out_path = case_dir / "report.json"
    operation = expected["operation"]

    command = [sys.executable, str(tool), "--contract-root", str(contract_root), "--out", str(out_path), "--check"]
    if case_id == "contracts-duplicate-class":
        path = contract_root / "change-classification-contract.json"
        value = json.loads(path.read_text(encoding="utf-8"))
        value["changeClasses"].append(copy.deepcopy(value["changeClasses"][0]))
        write_json(path, value)
    elif case_id == "contracts-unknown-profile-reference":
        path = contract_root / "engineering-profile-contract.json"
        value = json.loads(path.read_text(encoding="utf-8"))
        value["selectionRules"][0]["requiredProfiles"].append("unknown-profile")
        write_json(path, value)
    elif case_id == "tool-error-missing-contract-root":
        shutil.rmtree(contract_root)
    elif case_id.startswith("recovery-"):
        value = recovery_record("a" * 64)
        if case_id == "recovery-positive-self-repair":
            integration_root = case_dir / "integration-main"
            isolated_root = case_dir / "isolated-repair"
            gate = integration_root / "bin/defective-gate.sh"
            full_boundary = integration_root / "bin/full-boundary.sh"
            gate.parent.mkdir(parents=True)
            gate.write_text("#!/usr/bin/env bash\nset -euo pipefail\nexit 17\n", encoding="utf-8")
            full_boundary.write_text(
                "#!/usr/bin/env bash\nset -euo pipefail\nSCRIPT_DIR=\"$(cd \"$(dirname \"${BASH_SOURCE[0]}\")\" && pwd)\"\nbash \"${SCRIPT_DIR}/defective-gate.sh\"\n",
                encoding="utf-8",
            )
            unrelated = integration_root / "UNRELATED.txt"
            unrelated.write_bytes(b"byte-identical sentinel\n")
            before_hash = tree_hash(integration_root)
            unrelated_before = unrelated.read_bytes()
            shutil.copytree(integration_root, isolated_root)

            defective = subprocess.run(
                ["bash", str(isolated_root / "bin/defective-gate.sh")],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            if defective.returncode != 17:
                failures.append(f"{case_id}: copied gate was not intentionally defective")
            bootstrap = subprocess.run(
                [sys.executable, "-c", "from pathlib import Path; p=Path(__import__('sys').argv[1]); assert p.is_file() and p.read_bytes()", str(isolated_root / "bin/defective-gate.sh")],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            if bootstrap.returncode != 0:
                failures.append(f"{case_id}: unaffected bootstrap failed: {bootstrap.stderr!r}")
            (isolated_root / "bin/defective-gate.sh").write_text(
                "#!/usr/bin/env bash\nset -euo pipefail\nprintf '%s\\n' 'COPIED_GATE=PASS'\n",
                encoding="utf-8",
            )
            targeted = subprocess.run(["bash", str(isolated_root / "bin/defective-gate.sh")], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            full = subprocess.run(["bash", str(isolated_root / "bin/full-boundary.sh")], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            changed = sorted(
                item.relative_to(isolated_root).as_posix()
                for item in isolated_root.rglob("*")
                if item.is_file() and item.read_bytes() != (integration_root / item.relative_to(isolated_root)).read_bytes()
            )
            if targeted.returncode != 0 or full.returncode != 0:
                failures.append(f"{case_id}: repaired gate did not pass targeted/full qualification")
            if tree_hash(integration_root) != before_hash or unrelated.read_bytes() != unrelated_before:
                failures.append(f"{case_id}: integration main or unrelated sentinel changed")
            if changed != ["bin/defective-gate.sh"]:
                failures.append(f"{case_id}: isolated repair changed unexpected paths: {changed!r}")
            value = recovery_record(before_hash)
            value["targetedQualification"]["exitCode"] = targeted.returncode
            value["finalQualification"]["exitCode"] = full.returncode
        elif case_id == "recovery-path-expansion":
            value["actualRepairPaths"].append("bin/unrelated.sh")
        elif case_id == "recovery-capability-expansion":
            value["usedCapabilities"].append("cross-project-mutation")
        elif case_id == "recovery-direct-main-mutation":
            value["observedForbiddenOperations"].append("direct-main-mutation")
        elif case_id == "recovery-push":
            value["observedForbiddenOperations"].append("push")
        elif case_id == "recovery-false-pass":
            value["targetedQualification"]["exitCode"] = 17
        elif case_id == "recovery-missing-final-qualification":
            value["finalQualification"]["status"] = "not-executed"
            value["finalQualification"]["exitCode"] = 0
            value["finalQualification"]["reportRefs"] = []
        write_json(input_path, value)
        command.extend(["maintenance-recovery", "--input", str(input_path)])
    elif case_id.startswith("profiles-"):
        value = classification()
        if case_id == "profiles-high-contract":
            value = classification(classes=["contract", "tooling"], risk="high", indicators=["public-or-reusable-contract"])
        elif case_id == "profiles-release":
            value = classification(classes=["release", "build"], risk="high", flags={
                "governanceMigration": False,
                "strictPromotion": False,
                "periodicAudit": False,
                "releaseCandidate": True,
            })
        elif case_id == "profiles-unknown-class":
            value["classes"] = ["unknown-class"]
        write_json(input_path, value)
        command.extend(["profiles", "--input", str(input_path)])
    elif case_id.startswith("evidence-"):
        status = "qualified" if case_id != "evidence-incomplete-valid" else "incomplete"
        value = base_evidence(status=status)
        if case_id == "evidence-profile-selection-mismatch":
            value["profileSelection"]["requiredProfiles"] = ["fast"]
        elif case_id == "evidence-qualified-with-tool-error":
            value["executions"][0]["status"] = "tool-error"
        elif case_id == "evidence-duplicate-execution":
            value["executions"].append(copy.deepcopy(value["executions"][0]))
        write_json(input_path, value)
        command.extend(["evidence", "--input", str(input_path)])
    elif case_id.startswith("completion-"):
        if case_id == "completion-qualified-with-findings-valid":
            evidence = base_evidence(status="qualified-with-findings")
            evidence["findings"] = [{"findingId": "F-001", "severity": "WARNING", "status": "accepted", "message": "Accepted non-blocking finding"}]
            completion = base_completion(status="qualified-with-findings")
            completion["acceptedFindingIds"] = ["F-001"]
        elif case_id == "completion-qualified-open-blocker":
            evidence = base_evidence(status="qualified")
            completion = base_completion(status="qualified")
            completion["openBlockingFindingIds"] = ["F-BLOCK"]
        elif case_id == "completion-blocked-without-cause":
            evidence = base_evidence(status="blocked")
            completion = base_completion(status="blocked")
        elif case_id == "completion-incomplete-valid":
            evidence = base_evidence(status="incomplete")
            completion = base_completion(status="incomplete", criterion_status="pending")
        else:
            evidence = base_evidence(status="qualified")
            completion = base_completion(status="qualified")
        write_json(evidence_path, evidence)
        write_json(input_path, completion)
        command.extend(["completion", "--input", str(input_path), "--evidence", str(evidence_path)])
    if operation == "contracts":
        command.append("contracts")

    completed = subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    report = json.loads(out_path.read_text(encoding="utf-8")) if out_path.is_file() else {}
    actual_status = report.get("status")
    ok = completed.returncode == expected["expectedExit"] and actual_status == expected["expectedStatus"]
    expected_finding_code = expected.get("expectedFindingCode")
    if expected_finding_code and expected_finding_code not in {finding.get("code") for finding in report.get("findings", [])}:
        ok = False

    if case_id == "profiles-low-documentation" and report.get("details", {}).get("profileSelection", {}).get("requiredProfiles") != ["qualification"]:
        ok = False
    if case_id == "profiles-high-contract":
        selected = report.get("details", {}).get("profileSelection", {})
        if selected.get("effectiveRiskLevel") != "high" or selected.get("requiredProfiles") != ["qualification"]:
            ok = False
    if case_id == "profiles-release" and report.get("details", {}).get("profileSelection", {}).get("requiredProfiles") != ["qualification", "audit", "release"]:
        ok = False

    results.append({
        "id": case_id,
        "expectedExit": expected["expectedExit"],
        "actualExit": completed.returncode,
        "expectedStatus": expected["expectedStatus"],
        "actualStatus": actual_status,
        "passed": ok,
    })
    if not ok:
        failures.append(
            f"{case_id}: expected exit/status {expected['expectedExit']}/{expected['expectedStatus']}, "
            f"got {completed.returncode}/{actual_status}; stdout={completed.stdout!r}; stderr={completed.stderr!r}"
        )

summary = {
    "schemaVersion": "springmaster.engineering-contracts-it-report.v1",
    "status": "PASS" if not failures else "FAIL",
    "caseCount": len(results),
    "passedCount": sum(1 for result in results if result["passed"]),
    "failedCount": len(failures),
    "results": results,
    "failures": failures,
}
write_json(run_dir / "REPORT.json", summary)
if failures:
    print("ENGINEERING_CONTRACTS_IT=FAIL")
    for failure in failures:
        print(failure, file=sys.stderr)
    raise SystemExit(1)
print("ENGINEERING_CONTRACTS_IT=PASS")
print(f"CASES={len(results)}")
print(f"REPORT={run_dir / 'REPORT.json'}")
PY
