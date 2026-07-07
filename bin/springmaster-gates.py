#!/usr/bin/env python3
"""Springmaster report-only gate seed.

This tool is intentionally small and deterministic. It implements the first
report-only diagnostic seed defined by the Springmaster ADR and tooling docs.
It does not scan target projects, does not run strict gates and does not change
source files.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

SEED_ID = "springmaster.report-only-gate-seed.v1"
REPORT_SCHEMA_VERSION = "springmaster.report-only-report.v1"
REQUIRED_REPORT_FILES = ["summary.txt", "summary.json", "findings.jsonl", "rule-sources.json", "input-manifest.json"]
SUPPORTED_MODE = "report-only"
SUPPORTED_SCOPE = "springmaster-reference-only"

REQUIRED_RULE_SOURCES = [
    "PROJECT_DOCS/ADR/ADR-0002-api-boundary-and-endpoint-contract.md",
    "PROJECT_DOCS/ADR/ADR-0003-application-layer-and-transaction-boundary.md",
    "PROJECT_DOCS/ADR/ADR-0004-persistence-identity-and-domainentity-strategy.md",
    "PROJECT_DOCS/ADR/ADR-0005-security-and-permission-boundary.md",
    "PROJECT_DOCS/ADR/ADR-0006-verification-and-gate-strategy.md",
    "PROJECT_DOCS/ADR/ADR-0007-catalog-demo-canonicalization-strategy.md",
]

OPTIONAL_RULE_SOURCES = [
    "PROJECT_DOCS/STANDARDS/API/API_ENDPOINT_CONTRACT_STANDARD.md",
    "PROJECT_DOCS/STANDARDS/API/API_QUERY_REFERENCE_DATA_CONSISTENCY_STANDARD.md",
    "PROJECT_DOCS/STANDARDS/API/API_ERROR_CONTRACT_STANDARD.md",
    "PROJECT_DOCS/STANDARDS/API/API_ERROR_IDENTITY_STATUSCODE_CONSISTENCY_STANDARD.md",
    "PROJECT_DOCS/STANDARDS/CONTROLLER_SERVICE_USECASE_TRANSACTION_STANDARD.md",
    "PROJECT_DOCS/STANDARDS/DOMAIN_ENTITY_PERSISTENCE_STANDARD.md",
    "PROJECT_DOCS/STANDARDS/SECURITY_PERMISSION_BOUNDARY_STANDARD.md",
    "PROJECT_DOCS/DEMO/CATALOG_DEMO_READINESS_PLAN.md",
    "PROJECT_DOCS/TOOLING/REPORT_ONLY_GATE_SEED_PLAN.md",
]

SEVERITIES = ["BLOCKER", "ERROR", "WARNING", "INFO", "MANUAL_REVIEW"]
CATALOG_CANDIDATE_EVIDENCE_JSON = "PROJECT_DOCS/DEMO/CATALOGITEM_CANDIDATE_SLICE_EVIDENCE.json"
CATALOG_CANDIDATE_EVIDENCE_MD = "PROJECT_DOCS/DEMO/CATALOGITEM_CANDIDATE_SLICE_EVIDENCE.md"
CATALOG_READINESS_PLAN = "PROJECT_DOCS/DEMO/CATALOG_DEMO_READINESS_PLAN.md"



@dataclass(frozen=True)
class Finding:
    gateId: str
    ruleId: str
    layer: str
    mode: str
    severity: str
    ruleSource: str
    subject: str
    message: str
    remediation: str | None = None
    path: str | None = None
    method: str | None = None
    className: str | None = None
    memberName: str | None = None
    expected: str | None = None
    actual: str | None = None

    def to_json(self) -> dict[str, str]:
        return {key: value for key, value in asdict(self).items() if value is not None}


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def utc_run_id() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ-report-only")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def read_json_object(path: Path) -> dict[str, object]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def catalog_candidate_evidence(root: Path) -> dict[str, object]:
    json_path = root / CATALOG_CANDIDATE_EVIDENCE_JSON
    md_path = root / CATALOG_CANDIDATE_EVIDENCE_MD
    readiness_path = root / CATALOG_READINESS_PLAN
    evidence: dict[str, object] = {
        "schema": "springmaster.catalog-demo.candidate-evidence.v1",
        "subject": "Catalog-demo",
        "slice": "CatalogItem",
        "sliceState": "unknown",
        "canonicalState": "unknown",
        "securityMode": "unknown",
        "source": "none",
        "jsonEvidencePresent": json_path.exists(),
        "markdownEvidencePresent": md_path.exists(),
        "readinessPlanPresent": readiness_path.exists(),
    }

    if json_path.exists():
        data = read_json_object(json_path)
        if data:
            evidence.update({
                "schema": data.get("schema", evidence["schema"]),
                "subject": data.get("subject", evidence["subject"]),
                "slice": data.get("slice", evidence["slice"]),
                "sliceState": data.get("sliceState", evidence["sliceState"]),
                "canonicalState": data.get("canonicalState", evidence["canonicalState"]),
                "securityMode": data.get("securityMode", evidence["securityMode"]),
                "source": CATALOG_CANDIDATE_EVIDENCE_JSON,
                "implementedOperations": data.get("implementedOperations", []),
                "deferredCanonicalEvidence": data.get("deferredCanonicalEvidence", []),
                "targetComparison": data.get("targetComparison", "blocked"),
                "targetDelivery": data.get("targetDelivery", "blocked"),
            })
            return evidence

    markdown = read_text(md_path) if md_path.exists() else ""
    readiness = read_text(readiness_path) if readiness_path.exists() else ""
    combined = markdown + "\n" + readiness
    if "candidate-reference-slice" in markdown:
        evidence["sliceState"] = "candidate-reference-slice"
        evidence["source"] = CATALOG_CANDIDATE_EVIDENCE_MD
    elif "legacy-demo-seed" in readiness:
        evidence["sliceState"] = "legacy-demo-seed"
        evidence["source"] = CATALOG_READINESS_PLAN
    if "not canonical" in combined or "not-canonical" in combined:
        evidence["canonicalState"] = "not-canonical"
    if "documented-deferred-security" in combined:
        evidence["securityMode"] = "documented-deferred-security"
    return evidence


def iter_java_sources(root: Path) -> Iterable[Path]:
    base = root / "src" / "main" / "java"
    if not base.exists():
        return []
    return sorted(base.rglob("*.java"))


def rel(root: Path, path: Path) -> str:
    return str(path.relative_to(root)).replace("\\", "/")


def java_class_name(path: Path) -> str:
    text = read_text(path)
    package = re.search(r"^\s*package\s+([A-Za-z0-9_.]+)\s*;", text, re.MULTILINE)
    name = path.stem
    return f"{package.group(1)}.{name}" if package else name


def request_mapping_literals(text: str) -> list[tuple[str, str]]:
    result: list[tuple[str, str]] = []
    annotation_pattern = re.compile(
        r"@(GetMapping|PostMapping|PutMapping|PatchMapping|DeleteMapping|RequestMapping)\s*(?:\(([^)]*)\))?",
        re.MULTILINE | re.DOTALL,
    )
    string_pattern = re.compile(r'"([^"]*)"')
    for match in annotation_pattern.finditer(text):
        annotation = match.group(1)
        args = match.group(2) or ""
        strings = string_pattern.findall(args)
        if not strings and annotation in {"GetMapping", "PostMapping", "PutMapping", "PatchMapping", "DeleteMapping"}:
            strings = [""]
        for literal in strings:
            result.append((annotation, literal))
    return result


def request_param_literals(text: str) -> list[str]:
    result: list[str] = []
    for match in re.finditer(r"@RequestParam\s*(?:\(([^)]*)\))?", text, re.DOTALL):
        args = match.group(1) or ""
        strings = re.findall(r'"([^"]+)"', args)
        result.extend(strings)
        named = re.findall(r"(?:name|value)\s*=\s*\"([^\"]+)\"", args)
        result.extend(named)
    return sorted(set(result))


def add_rule_source_findings(root: Path, mode: str) -> list[Finding]:
    findings: list[Finding] = []
    for source in REQUIRED_RULE_SOURCES:
        findings.append(Finding(
            gateId="SM-G0-RULE-SOURCE-COVERAGE",
            ruleId="SM-G0-RULE-SOURCE-001",
            layer="G0",
            mode=mode,
            severity="INFO",
            ruleSource="PROJECT_DOCS/ADR/ADR-0006-verification-and-gate-strategy.md",
            subject=source,
            message="Required ADR rule source is present and can be referenced by report-only findings.",
            expected="present",
            actual="present" if (root / source).exists() else "missing",
        ))
    return findings


def add_http_vocabulary_findings(root: Path, mode: str) -> list[Finding]:
    findings: list[Finding] = []
    for path in iter_java_sources(root):
        if not path.name.endswith("Controller.java"):
            continue
        text = read_text(path)
        class_name = java_class_name(path)
        for annotation, literal in request_mapping_literals(text):
            subject = f"{class_name} {annotation} {literal or '<empty>'}"
            normalized = f"/{literal.strip('/')}" if literal else ""
            if re.search(r"/(all)(/|$)", normalized):
                findings.append(Finding(
                    gateId="SM-G1-HTTP-VOCABULARY",
                    ruleId="SM-API-ALL-ENDPOINT-001",
                    layer="G1",
                    mode=mode,
                    severity="WARNING",
                    ruleSource="PROJECT_DOCS/ADR/ADR-0002-api-boundary-and-endpoint-contract.md",
                    subject=subject,
                    message="Non-canonical `/all` path vocabulary appears in a controller mapping.",
                    remediation="Use the collection resource for pageable lists or `/options` only for bounded selector data.",
                    path=normalized,
                    className=class_name,
                ))
            if re.search(r"/(findOne|findFirst|findLast)(/|$)", normalized, flags=re.IGNORECASE):
                findings.append(Finding(
                    gateId="SM-G1-HTTP-VOCABULARY",
                    ruleId="SM-API-FIND-VOCAB-001",
                    layer="G1",
                    mode=mode,
                    severity="WARNING",
                    ruleSource="PROJECT_DOCS/ADR/ADR-0002-api-boundary-and-endpoint-contract.md",
                    subject=subject,
                    message="Public path vocabulary exposes repository-style findOne/findFirst/findLast semantics.",
                    remediation="Translate repository vocabulary into explicit domain semantics such as current, latest, primary or by-<key>.",
                    path=normalized,
                    className=class_name,
                ))
            if re.search(r"/options(/|$)", normalized):
                findings.append(Finding(
                    gateId="SM-G1-HTTP-VOCABULARY",
                    ruleId="SM-API-OPTIONS-001",
                    layer="G1",
                    mode=mode,
                    severity="INFO",
                    ruleSource="PROJECT_DOCS/ADR/ADR-0002-api-boundary-and-endpoint-contract.md",
                    subject=subject,
                    message="`/options` path vocabulary is present and should remain bounded selector evidence.",
                    path=normalized,
                    className=class_name,
                ))
        if re.search(r"\bfind(?:One|First|Last)\s*\(", text):
            findings.append(Finding(
                gateId="SM-G1-HTTP-VOCABULARY",
                ruleId="SM-API-FIND-VOCAB-001",
                layer="G1",
                mode=mode,
                severity="WARNING",
                ruleSource="PROJECT_DOCS/ADR/ADR-0002-api-boundary-and-endpoint-contract.md",
                subject=class_name,
                message="Controller method names expose findOne/findFirst/findLast vocabulary that should not become public API semantics.",
                remediation="Use domain-oriented method names at API boundary or keep repository vocabulary below the application boundary.",
                className=class_name,
            ))
    return findings


def add_query_findings(root: Path, mode: str) -> list[Finding]:
    findings: list[Finding] = []
    for path in iter_java_sources(root):
        if not path.name.endswith("Controller.java"):
            continue
        text = read_text(path)
        class_name = java_class_name(path)
        params = request_param_literals(text)
        if "sort" in params:
            findings.append(Finding(
                gateId="SM-G1-QUERY-PARAMETERS",
                ruleId="SM-API-SORTBY-001",
                layer="G1",
                mode=mode,
                severity="WARNING",
                ruleSource="PROJECT_DOCS/ADR/ADR-0002-api-boundary-and-endpoint-contract.md",
                subject=class_name,
                message="Controller exposes legacy `sort` query vocabulary where `sortBy` is canonical for new reference APIs.",
                remediation="Use `sortBy` for canonical reference APIs; keep `sort` only for legacy/target comparison tolerance.",
                className=class_name,
                expected="sortBy",
                actual="sort",
            ))
        if path.name == "CatalogItemController.java" and "sortBy" not in params:
            findings.append(Finding(
                gateId="SM-G1-QUERY-PARAMETERS",
                ruleId="SM-API-SORTBY-001",
                layer="G1",
                mode=mode,
                severity="WARNING",
                ruleSource="PROJECT_DOCS/ADR/ADR-0002-api-boundary-and-endpoint-contract.md",
                subject=class_name,
                message="CatalogItemController does not yet expose canonical pageable query vocabulary including `sortBy`.",
                remediation="Keep this as legacy-demo-seed evidence until the candidate reference slice introduces page, size, sortBy and sortDir.",
                className=class_name,
                expected="page,size,sortBy,sortDir",
                actual=",".join(params) if params else "no @RequestParam evidence",
            ))
    return findings


def add_status_error_findings(root: Path, mode: str) -> list[Finding]:
    findings: list[Finding] = []
    for path in iter_java_sources(root):
        if not path.name.endswith("Controller.java"):
            continue
        text = read_text(path)
        class_name = java_class_name(path)
        if "Map<String, Object>" in text and "@ExceptionHandler" in text:
            findings.append(Finding(
                gateId="SM-G1-STATUS-ERROR-CONTRACT",
                ruleId="SM-API-ERROR-001",
                layer="G1",
                mode=mode,
                severity="INFO",
                ruleSource="PROJECT_DOCS/ADR/ADR-0002-api-boundary-and-endpoint-contract.md",
                subject=class_name,
                message="Controller uses ad-hoc Map<String,Object> exception response; this is legacy-demo-seed evidence, not canonical error contract behavior.",
                remediation="Introduce the canonical API error response DTO when Catalog-demo becomes a candidate reference slice.",
                className=class_name,
                expected="errorId,errorType,message,path,method",
                actual="Map<String,Object>",
            ))
        if "ResponseEntity.created" in text:
            findings.append(Finding(
                gateId="SM-G1-STATUS-ERROR-CONTRACT",
                ruleId="SM-API-STATUS-001",
                layer="G1",
                mode=mode,
                severity="INFO",
                ruleSource="PROJECT_DOCS/ADR/ADR-0002-api-boundary-and-endpoint-contract.md",
                subject=class_name,
                message="Create endpoint appears to return 201 Created evidence.",
                className=class_name,
                expected="201 Created",
                actual="ResponseEntity.created",
            ))
        if "@DeleteMapping" not in text and path.name == "CatalogItemController.java":
            findings.append(Finding(
                gateId="SM-G1-STATUS-ERROR-CONTRACT",
                ruleId="SM-API-STATUS-001",
                layer="G1",
                mode=mode,
                severity="INFO",
                ruleSource="PROJECT_DOCS/ADR/ADR-0002-api-boundary-and-endpoint-contract.md",
                subject=class_name,
                message="CatalogItemController does not yet provide delete status-code evidence.",
                remediation="Candidate reference slice should demonstrate bodyless DELETE with 204 and 404 behavior.",
                className=class_name,
                expected="DELETE 204/404 evidence",
                actual="no @DeleteMapping evidence",
            ))
    return findings


def add_application_boundary_findings(root: Path, mode: str) -> list[Finding]:
    findings: list[Finding] = []
    for path in iter_java_sources(root):
        text = read_text(path)
        class_name = java_class_name(path)
        if path.name.endswith("Controller.java"):
            if re.search(r"\b(EntityManager|[A-Za-z0-9_]*Repository)\b", text):
                findings.append(Finding(
                    gateId="SM-G3-APPLICATION-BOUNDARY-HINTS",
                    ruleId="SM-JAVA-CONTROLLER-REPO-001",
                    layer="G3",
                    mode=mode,
                    severity="WARNING",
                    ruleSource="PROJECT_DOCS/ADR/ADR-0003-application-layer-and-transaction-boundary.md",
                    subject=class_name,
                    message="Controller appears to access repository or EntityManager boundary.",
                    remediation="Route persistence access through application services or use-case handlers.",
                    className=class_name,
                ))
            if "@Transactional" in text:
                findings.append(Finding(
                    gateId="SM-G3-APPLICATION-BOUNDARY-HINTS",
                    ruleId="SM-JAVA-CONTROLLER-TX-001",
                    layer="G3",
                    mode=mode,
                    severity="WARNING",
                    ruleSource="PROJECT_DOCS/ADR/ADR-0003-application-layer-and-transaction-boundary.md",
                    subject=class_name,
                    message="Controller appears to own a transaction boundary.",
                    remediation="Move transaction ownership to service or use-case boundary.",
                    className=class_name,
                ))
        if path.name.endswith("Mapper.java"):
            if re.search(r"\b(Repository|EntityManager|SecurityContext|Authentication|@Transactional)\b", text):
                findings.append(Finding(
                    gateId="SM-G3-APPLICATION-BOUNDARY-HINTS",
                    ruleId="SM-JAVA-MAPPER-DEPENDENCY-001",
                    layer="G3",
                    mode=mode,
                    severity="WARNING",
                    ruleSource="PROJECT_DOCS/ADR/ADR-0003-application-layer-and-transaction-boundary.md",
                    subject=class_name,
                    message="Mapper appears to depend on repository, security or transaction concepts.",
                    remediation="Keep mappers deterministic and free of repository/security/transaction dependencies.",
                    className=class_name,
                ))
    return findings


def add_persistence_identity_findings(root: Path, mode: str) -> list[Finding]:
    findings: list[Finding] = []
    for path in iter_java_sources(root):
        if not path.name.endswith("DTO.java"):
            continue
        text = read_text(path)
        class_name = java_class_name(path)
        if re.search(r"\b(?:Long|Integer|long|int)\s+id\s*;", text):
            findings.append(Finding(
                gateId="SM-G3-PERSISTENCE-IDENTITY-HINTS",
                ruleId="SM-JAVA-ID-LEAK-001",
                layer="G3",
                mode=mode,
                severity="WARNING",
                ruleSource="PROJECT_DOCS/ADR/ADR-0004-persistence-identity-and-domainentity-strategy.md",
                subject=class_name,
                message="Public DTO appears to expose numeric `id`, which may leak internal surrogate identity.",
                remediation="Use opaque string public IDs unless a documented exception exists.",
                className=class_name,
                expected="String id",
                actual="numeric id field",
            ))
    return findings


def add_security_findings(root: Path, mode: str) -> list[Finding]:
    findings: list[Finding] = []
    evidence = catalog_candidate_evidence(root)
    security_mode = str(evidence.get("securityMode") or "unknown")
    documented_deferred = security_mode == "documented-deferred-security"
    for path in iter_java_sources(root):
        if not path.name.endswith("Controller.java"):
            continue
        class_name = java_class_name(path)
        text = read_text(path)
        if "de.cocondo.platform.demo.catalog" in class_name and not re.search(r"@PreAuthorize|SecurityRequirement|@Secured", text):
            findings.append(Finding(
                gateId="SM-G4-SECURITY-CLASSIFICATION",
                ruleId="SM-SEC-CLASSIFICATION-001",
                layer="G4",
                mode=mode,
                severity="WARNING",
                ruleSource="PROJECT_DOCS/ADR/ADR-0005-security-and-permission-boundary.md",
                subject=class_name,
                message="Catalog-demo controller has no implemented security annotation evidence; classification must remain explicit while security is deferred.",
                remediation="Keep documented-deferred-security evidence current or implement management security before canonical reference status.",
                className=class_name,
                expected="documented-deferred-security or implemented-management-security",
                actual="documented-deferred-security" if documented_deferred else "no source-level security evidence",
            ))
    return findings


def add_catalog_readiness_findings(root: Path, mode: str) -> list[Finding]:
    evidence = catalog_candidate_evidence(root)
    readiness_plan_present = bool(evidence.get("readinessPlanPresent"))
    if not readiness_plan_present:
        return [Finding(
            gateId="SM-G5-CATALOG-READINESS-EVIDENCE",
            ruleId="SM-DEMO-EVIDENCE-001",
            layer="G5",
            mode=mode,
            severity="MANUAL_REVIEW",
            ruleSource="PROJECT_DOCS/ADR/ADR-0007-catalog-demo-canonicalization-strategy.md",
            subject="Catalog-demo",
            message="Catalog-demo readiness plan is missing.",
            remediation="Restore the readiness plan before declaring Catalog-demo candidate or canonical.",
            expected="readiness plan present",
            actual="missing",
        )]

    slice_state = str(evidence.get("sliceState") or "unknown")
    canonical_state = str(evidence.get("canonicalState") or "unknown")
    source = str(evidence.get("source") or "unknown")

    if slice_state == "candidate-reference-slice" and canonical_state in {"not-canonical", "not canonical"}:
        return []

    if slice_state == "legacy-demo-seed":
        return [Finding(
            gateId="SM-G5-CATALOG-READINESS-EVIDENCE",
            ruleId="SM-DEMO-EVIDENCE-001",
            layer="G5",
            mode=mode,
            severity="MANUAL_REVIEW",
            ruleSource="PROJECT_DOCS/ADR/ADR-0007-catalog-demo-canonicalization-strategy.md",
            subject="Catalog-demo",
            message="Catalog-demo is explicitly still legacy-demo-seed; candidate evidence is not complete yet.",
            remediation="Implement or restore candidate-reference-slice evidence with endpoint, DTO, validation, error, application-layer, persistence, mapping, security and gate evidence.",
            expected="candidate-reference-slice or canonical-reference-slice evidence",
            actual="legacy-demo-seed",
        )]

    return [Finding(
        gateId="SM-G5-CATALOG-READINESS-EVIDENCE",
        ruleId="SM-DEMO-EVIDENCE-001",
        layer="G5",
        mode=mode,
        severity="MANUAL_REVIEW",
        ruleSource="PROJECT_DOCS/ADR/ADR-0007-catalog-demo-canonicalization-strategy.md",
        subject="Catalog-demo",
        message="Catalog-demo readiness evidence exists, but the slice state could not be classified deterministically.",
        remediation="Record machine-readable candidate or canonical evidence before changing readiness status.",
        expected="candidate-reference-slice or canonical-reference-slice evidence",
        actual=f"{slice_state} from {source}",
    )]


def collect_findings(root: Path, mode: str) -> list[Finding]:
    findings: list[Finding] = []
    findings.extend(add_rule_source_findings(root, mode))
    findings.extend(add_http_vocabulary_findings(root, mode))
    findings.extend(add_query_findings(root, mode))
    findings.extend(add_status_error_findings(root, mode))
    findings.extend(add_application_boundary_findings(root, mode))
    findings.extend(add_persistence_identity_findings(root, mode))
    findings.extend(add_security_findings(root, mode))
    findings.extend(add_catalog_readiness_findings(root, mode))
    return findings


def build_rule_source_registry(root: Path) -> list[dict[str, str | bool]]:
    registry = []
    for source in REQUIRED_RULE_SOURCES:
        registry.append({"path": source, "required": True, "present": (root / source).exists()})
    for source in OPTIONAL_RULE_SOURCES:
        registry.append({"path": source, "required": False, "present": (root / source).exists()})
    return registry


def write_json(path: Path, data: object) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: Iterable[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def severity_counts(findings: list[Finding]) -> dict[str, int]:
    return {severity: sum(1 for finding in findings if finding.severity == severity) for severity in SEVERITIES}


def gate_counts(findings: list[Finding]) -> dict[str, int]:
    result: dict[str, int] = {}
    for finding in findings:
        result[finding.gateId] = result.get(finding.gateId, 0) + 1
    return dict(sorted(result.items()))


def layer_counts(findings: list[Finding]) -> dict[str, int]:
    result: dict[str, int] = {}
    for finding in findings:
        result[finding.layer] = result.get(finding.layer, 0) + 1
    return dict(sorted(result.items()))


def write_summary_txt(path: Path, summary: dict[str, object]) -> None:
    lines = [
        "Springmaster report-only gate seed",
        "==================================",
        "",
        f"Seed:        {summary['seedId']}",
        f"Run ID:      {summary['runId']}",
        f"Mode:        {summary['mode']}",
        f"Scope:       {summary['scope']}",
        f"Status:      {summary['status']}",
        f"Findings:    {summary['findingCount']}",
        "",
        "Severity counts:",
    ]
    for severity, count in summary["severityCounts"].items():
        lines.append(f"  {severity:<13} {count}")
    lines.append("")
    lines.append("Gate counts:")
    for gate, count in summary["gateCounts"].items():
        lines.append(f"  {gate:<38} {count}")
    lines.append("")
    lines.append("Report-only findings do not fail execution. Tool setup/runtime errors do fail execution.")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def input_manifest(root: Path) -> dict[str, object]:
    java_files = list(iter_java_sources(root))
    openapi_candidates = sorted(
        str(path.relative_to(root)).replace("\\", "/")
        for pattern in ("**/*openapi*.json", "**/*openapi*.yaml", "**/*openapi*.yml")
        for path in root.glob(pattern)
        if "target/" not in str(path.relative_to(root)).replace("\\", "/")
    )
    return {
        "reportSchemaVersion": REPORT_SCHEMA_VERSION,
        "seedId": SEED_ID,
        "scope": SUPPORTED_SCOPE,
        "includedInputs": [
            {"type": "java-source", "path": "src/main/java", "fileCount": len(java_files)},
            {"type": "documentation", "path": "PROJECT_DOCS/ADR", "fileCount": len(list((root / "PROJECT_DOCS" / "ADR").glob("*.md")))},
            {"type": "documentation", "path": "PROJECT_DOCS/STANDARDS", "fileCount": len(list((root / "PROJECT_DOCS" / "STANDARDS").rglob("*.md")))},
            {"type": "documentation", "path": "PROJECT_DOCS/DEMO", "fileCount": len(list((root / "PROJECT_DOCS" / "DEMO").rglob("*.md")))},
        ],
        "availableOpenApiFiles": openapi_candidates,
        "catalogDemoEvidence": catalog_candidate_evidence(root),
        "unavailableInputs": [
            {"type": "compiled-classes", "reason": "not required for first source-based report-only seed"},
            {"type": "target-projects", "reason": "explicitly excluded by scope springmaster-reference-only"},
        ],
        "excludedTargets": ["/opt/cocondo/idm", "/opt/cocondo/personnel", "/opt/cocondo/contacts", "/opt/cocondo/orders"],
    }


def ensure_required_sources(root: Path) -> None:
    missing = [source for source in REQUIRED_RULE_SOURCES if not (root / source).is_file()]
    if missing:
        raise SystemExit("Missing required rule sources: " + ", ".join(missing))


def command_report(args: argparse.Namespace) -> int:
    if args.mode != SUPPORTED_MODE:
        raise SystemExit(f"Unsupported mode {args.mode!r}; only {SUPPORTED_MODE!r} is implemented.")
    if args.scope != SUPPORTED_SCOPE:
        raise SystemExit(f"Unsupported scope {args.scope!r}; only {SUPPORTED_SCOPE!r} is implemented.")
    if args.target:
        raise SystemExit("Target-project input is not supported by the first report-only gate seed.")

    root = repo_root()
    ensure_required_sources(root)

    run_id = args.run_id or utc_run_id()
    out_base = (root / args.out_dir).resolve() if args.out_dir else root / "target" / "springmaster-gates"
    report_dir = out_base / run_id
    if report_dir.exists():
        if args.clean:
            shutil.rmtree(report_dir)
        else:
            raise SystemExit(f"Report directory already exists: {report_dir}. Use --clean or a different --run-id.")
    report_dir.mkdir(parents=True, exist_ok=False)

    rule_sources = build_rule_source_registry(root)
    findings = collect_findings(root, args.mode)
    now = datetime.now(timezone.utc).isoformat()
    summary = {
        "reportSchemaVersion": REPORT_SCHEMA_VERSION,
        "seedId": SEED_ID,
        "runId": run_id,
        "generatedAt": now,
        "mode": args.mode,
        "scope": args.scope,
        "status": "SUCCESS",
        "findingCount": len(findings),
        "severityCounts": severity_counts(findings),
        "gateCounts": gate_counts(findings),
        "layerCounts": layer_counts(findings),
        "reportDirectory": str(report_dir.relative_to(root)).replace("\\", "/"),
    }

    write_json(report_dir / "rule-sources.json", {"reportSchemaVersion": REPORT_SCHEMA_VERSION, "seedId": SEED_ID, "generatedAt": now, "ruleSources": rule_sources})
    write_json(report_dir / "input-manifest.json", input_manifest(root))
    write_jsonl(report_dir / "findings.jsonl", [finding.to_json() for finding in findings])
    write_json(report_dir / "summary.json", summary)
    write_summary_txt(report_dir / "summary.txt", summary)

    print(f"Springmaster gates: {summary['status']}")
    print(f"  Seed:     {SEED_ID}")
    print(f"  Mode:     {args.mode}")
    print(f"  Scope:    {args.scope}")
    print(f"  Run ID:   {run_id}")
    print(f"  Findings: {len(findings)}")
    print(f"  Schema:   {REPORT_SCHEMA_VERSION}")
    print(f"  Report:   {summary['reportDirectory']}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Springmaster report-only gate seed")
    subparsers = parser.add_subparsers(dest="command", required=True)
    report = subparsers.add_parser("report", help="run report-only diagnostics")
    report.add_argument("--mode", default=SUPPORTED_MODE)
    report.add_argument("--scope", default=SUPPORTED_SCOPE)
    report.add_argument("--run-id")
    report.add_argument("--out-dir", default="target/springmaster-gates")
    report.add_argument("--clean", action="store_true")
    report.add_argument("--target", action="append", help="unsupported placeholder to fail on accidental target input")
    report.set_defaults(func=command_report)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())



