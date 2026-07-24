#!/usr/bin/env python3
import argparse
import hashlib
import json
import re
from pathlib import Path

HEX_SHA256 = re.compile(r"^[0-9a-f]{64}$")


def parse_env(path: Path) -> tuple[dict[str, str], list[dict[str, object]]]:
    values: dict[str, str] = {}
    findings: list[dict[str, object]] = []
    for number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            findings.append({"code": "ENV_LINE_INVALID", "path": path.as_posix(), "line": number})
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if key in values:
            findings.append({"code": "ENV_KEY_DUPLICATE", "path": path.as_posix(), "key": key})
        values[key] = value.strip()
    return values, findings


def read_json(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def add_mismatch(findings: list[dict[str, object]], code: str, expected: object, actual: object, **extra: object) -> None:
    finding: dict[str, object] = {"code": code, "expected": expected, "actual": actual}
    finding.update(extra)
    findings.append(finding)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root")
    parser.add_argument(
        "--contract",
        default="contracts/governance/tooling/patch-toolkit-activation-contract.json",
    )
    parser.add_argument("--out", default="target/patch-toolkit-activation-report.json")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    root = Path(args.root).resolve() if args.root else Path(__file__).resolve().parents[1]
    contract_path = root / args.contract
    findings: list[dict[str, object]] = []

    if not contract_path.is_file():
        findings.append({"code": "ACTIVATION_CONTRACT_MISSING", "path": args.contract})
        contract: dict[str, object] = {}
    else:
        try:
            contract = read_json(contract_path)
        except Exception as exc:
            findings.append({"code": "ACTIVATION_CONTRACT_INVALID", "detail": str(exc)})
            contract = {}

    if contract.get("schemaVersion") != "springmaster.patch-toolkit-activation-contract.v1":
        add_mismatch(
            findings,
            "ACTIVATION_CONTRACT_SCHEMA_MISMATCH",
            "springmaster.patch-toolkit-activation-contract.v1",
            contract.get("schemaVersion"),
        )

    expected_toolkit = contract.get("toolkitVersion")
    expected_runtime = contract.get("runtimeSha256")
    if not isinstance(expected_runtime, str) or not HEX_SHA256.fullmatch(expected_runtime):
        findings.append({"code": "RUNTIME_SHA256_INVALID", "actual": expected_runtime})

    project_env_path = root / ".cocondo/tooling/project.env"
    if project_env_path.is_file():
        project_env, env_findings = parse_env(project_env_path)
        findings.extend(env_findings)
        expected_project_values = {
            "CPATCH_PROJECT_ID": contract.get("projectId"),
            "CPATCH_TOOLKIT_VERSION": expected_toolkit,
            "CPATCH_REQUIRE_CLEAN_TREE": str(contract.get("requireCleanTree", False)).lower(),
            "CPATCH_COMMIT_ON_ACCEPT": str(contract.get("commitOnAccept", False)).lower(),
            "CPATCH_REQUIRE_WORKTREE": str(contract.get("requireWorktree", False)).lower(),
            "CPATCH_REQUIRE_WORKSPACE_FOR_CREATE": str(contract.get("requireWorkspaceForCreate", False)).lower(),
            "CPATCH_INTEGRATION_BRANCH": contract.get("integrationBranch"),
        }
        for key, expected in expected_project_values.items():
            actual = project_env.get(key)
            if actual != expected:
                add_mismatch(findings, "PROJECT_ENV_MISMATCH", expected, actual, key=key)
    else:
        findings.append({"code": "PROJECT_ENV_MISSING", "path": project_env_path.relative_to(root).as_posix()})

    lock_path = root / ".cocondo/tooling/tooling.lock.json"
    if lock_path.is_file():
        try:
            lock = read_json(lock_path)
        except Exception as exc:
            findings.append({"code": "TOOLING_LOCK_INVALID", "detail": str(exc)})
            lock = {}
        if lock.get("toolkitVersion") != expected_toolkit:
            add_mismatch(findings, "TOOLING_LOCK_VERSION_MISMATCH", expected_toolkit, lock.get("toolkitVersion"))
        if lock.get("sha256") != expected_runtime:
            add_mismatch(findings, "TOOLING_LOCK_SHA256_MISMATCH", expected_runtime, lock.get("sha256"))
    else:
        findings.append({"code": "TOOLING_LOCK_MISSING", "path": lock_path.relative_to(root).as_posix()})

    runtime_path = root / ".cocondo/tooling/cocondo-toolkit.pyz"
    if runtime_path.is_file():
        actual_runtime = sha256(runtime_path)
        if actual_runtime != expected_runtime:
            add_mismatch(findings, "RUNTIME_FILE_SHA256_MISMATCH", expected_runtime, actual_runtime)
    else:
        findings.append({"code": "RUNTIME_FILE_MISSING", "path": runtime_path.relative_to(root).as_posix()})

    sidecar_path = root / ".cocondo/tooling/cocondo-toolkit.pyz.sha256"
    if sidecar_path.is_file():
        sidecar_value = sidecar_path.read_text(encoding="utf-8").split()[0]
        if sidecar_value != expected_runtime:
            add_mismatch(findings, "RUNTIME_SIDECAR_MISMATCH", expected_runtime, sidecar_value)
    else:
        findings.append({"code": "RUNTIME_SIDECAR_MISSING", "path": sidecar_path.relative_to(root).as_posix()})

    closure = contract.get("versionClosure") if isinstance(contract.get("versionClosure"), dict) else {}
    platform_path = root / "platform/versions/platform.env"
    if platform_path.is_file():
        platform_env, env_findings = parse_env(platform_path)
        findings.extend(env_findings)
        closure_mapping = {
            "PLATFORM_VERSION": closure.get("platformVersion"),
            "PLATFORM_TOOLING_VERSION": closure.get("toolingVersion"),
            "PLATFORM_STATE_PATCH": closure.get("statePatch"),
        }
        for key, expected in closure_mapping.items():
            actual = platform_env.get(key)
            if actual != expected:
                add_mismatch(findings, "PLATFORM_VERSION_MISMATCH", expected, actual, key=key)
    else:
        findings.append({"code": "PLATFORM_ENV_MISSING", "path": platform_path.relative_to(root).as_posix()})

    pom_path = root / "pom.xml"
    if pom_path.is_file():
        pom = pom_path.read_text(encoding="utf-8")
        expected_pom_version = f"<version>{closure.get('mavenVersion')}</version>"
        if expected_pom_version not in pom:
            findings.append({"code": "MAVEN_VERSION_MISMATCH", "expected": closure.get("mavenVersion")})
    else:
        findings.append({"code": "POM_MISSING", "path": "pom.xml"})

    canonical_entrypoint = contract.get("canonicalMutatingEntrypoint")
    if not isinstance(canonical_entrypoint, str) or not (root / canonical_entrypoint).is_file():
        findings.append({"code": "CANONICAL_ENTRYPOINT_MISSING", "path": canonical_entrypoint})
    elif canonical_entrypoint == "bin/cpatch":
        cpatch_text = (root / canonical_entrypoint).read_text(encoding="utf-8")
        if '"workspace"' not in cpatch_text:
            findings.append({"code": "CPATCH_WORKSPACE_ROUTING_MISSING"})

    for legacy_path in contract.get("legacyEntrypoints", []):
        if not isinstance(legacy_path, str) or not (root / legacy_path).is_file():
            findings.append({"code": "LEGACY_ENTRYPOINT_MISSING", "path": legacy_path})

    evidence_rel = contract.get("evidenceFile")
    if isinstance(evidence_rel, str) and (root / evidence_rel).is_file():
        try:
            evidence = read_json(root / evidence_rel)
        except Exception as exc:
            findings.append({"code": "ACTIVATION_EVIDENCE_INVALID", "detail": str(exc)})
            evidence = {}
        if evidence.get("schemaVersion") != "springmaster.patch-toolkit-activation-evidence.v1":
            add_mismatch(
                findings,
                "ACTIVATION_EVIDENCE_SCHEMA_MISMATCH",
                "springmaster.patch-toolkit-activation-evidence.v1",
                evidence.get("schemaVersion"),
            )
        for key, expected in (
            ("projectId", contract.get("projectId")),
            ("toolkitVersion", expected_toolkit),
            ("runtimeSha256", expected_runtime),
            ("legacyMutationPolicy", contract.get("legacyMutationPolicy")),
            ("canonicalMutatingEntrypoint", canonical_entrypoint),
        ):
            actual = evidence.get(key)
            if actual != expected:
                add_mismatch(findings, "ACTIVATION_EVIDENCE_MISMATCH", expected, actual, key=key)
        qualification = evidence.get("installationQualification")
        if not isinstance(qualification, dict) or qualification.get("status") != "PASS":
            findings.append({"code": "INSTALLATION_QUALIFICATION_NOT_PASS"})
        process_evidence = evidence.get("processOperations")
        if not isinstance(process_evidence, dict):
            findings.append({"code": "PROCESS_OPERATIONS_EVIDENCE_MISSING"})
        else:
            expected_process_evidence = {
                "contractStatus": "PASS",
                "integrationFixture": "PASS",
                "realSpringmasterPilot": "PENDING",
                "managedProjectRollout": "BLOCKED_PENDING_SPRINGMASTER_PILOT",
            }
            for key, expected in expected_process_evidence.items():
                actual = process_evidence.get(key)
                if actual != expected:
                    add_mismatch(findings, "PROCESS_OPERATIONS_EVIDENCE_MISMATCH", expected, actual, key=key)
        export = evidence.get("qualifiedExport")
        if not isinstance(export, dict) or export.get("status") != "COMPLETE" or not HEX_SHA256.fullmatch(str(export.get("sha256", ""))):
            findings.append({"code": "QUALIFIED_EXPORT_EVIDENCE_INVALID"})
    else:
        findings.append({"code": "ACTIVATION_EVIDENCE_MISSING", "path": evidence_rel})

    report_rel = contract.get("activationReport")
    if not isinstance(report_rel, str) or not (root / report_rel).is_file():
        findings.append({"code": "ACTIVATION_REPORT_MISSING", "path": report_rel})

    process_operations = contract.get("processOperations") if isinstance(contract.get("processOperations"), dict) else {}
    expected_process_values = {
        "contract": "contracts/governance/tooling/process-operations-contract.json",
        "config": ".cocondo/process.env",
        "entrypoint": "bin/process-ops.sh",
        "integrationTest": "bin/process-ops-it.sh",
        "managedProjectRollout": "BLOCKED_PENDING_SPRINGMASTER_PILOT",
        "nestedDetachment": "forbidden",
        "pathResolution": "git-runtime",
        "terminalOutput": "compact-default",
    }
    for key, expected in expected_process_values.items():
        actual = process_operations.get(key)
        if actual != expected:
            add_mismatch(findings, "PROCESS_OPERATIONS_ACTIVATION_MISMATCH", expected, actual, key=key)
    for key in ("contract", "config", "entrypoint", "integrationTest"):
        relative = process_operations.get(key)
        if not isinstance(relative, str) or not (root / relative).is_file():
            findings.append({"code": "PROCESS_OPERATIONS_FILE_MISSING", "key": key, "path": relative})

    agents_path = root / "AGENTS.md"
    if agents_path.is_file():
        agents = agents_path.read_text(encoding="utf-8")
        for marker in (
            "./bin/cpatch workspace init",
            "./bin/cpatch create",
            "./bin/cpatch accept",
            "LEGACY_PATCH_MUTATION_DISABLED",
        ):
            if marker not in agents:
                findings.append({"code": "AGENTS_ACTIVATION_MARKER_MISSING", "marker": marker})
    else:
        findings.append({"code": "AGENTS_MISSING", "path": "AGENTS.md"})

    report = {
        "schemaVersion": "springmaster.patch-toolkit-activation-report.v1",
        "status": "PASS" if not findings else "FAIL",
        "toolkitVersion": expected_toolkit,
        "runtimeSha256": expected_runtime,
        "findingCount": len(findings),
        "findings": sorted(findings, key=lambda item: (str(item.get("code")), json.dumps(item, sort_keys=True))),
    }

    out = Path(args.out)
    if not out.is_absolute():
        out = root / out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(f"PATCH_TOOLKIT_ACTIVATION={report['status']}")
    print(f"REPORT={out}")
    return 1 if args.check and findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
