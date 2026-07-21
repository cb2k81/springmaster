#!/usr/bin/env python3
from __future__ import annotations
import argparse
import json
import re
import sys
from pathlib import Path

SCHEMA = "springmaster.core-persistence-newness-contract.v1"
ALLOWED = {"decided", "implemented"}

def add(findings, identifier, message):
    findings.append({"id": identifier, "severity": "error", "message": message})

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("project_root", nargs="?", default=".")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--report")
    args = parser.parse_args()
    root = Path(args.project_root).resolve()
    contract = json.loads((root / "contracts/core/persistence-newness-contract.json").read_text(encoding="utf-8"))
    source = (root / "src/main/java/de/cocondo/system/entity/DomainEntity.java").read_text(encoding="utf-8")
    tests = (root / "src/test/java/de/cocondo/system/entity/DomainEntityPersistenceMappingTest.java").read_text(encoding="utf-8")
    findings = []
    status = contract.get("status")
    if contract.get("schemaVersion") != SCHEMA:
        add(findings, "SCHEMA", f"Expected {SCHEMA}.")
    if status not in ALLOWED:
        add(findings, "STATUS", f"Unsupported contract status: {status!r}")
    if "Persistable" in source:
        add(findings, "PERSISTABLE_COUPLING", "DomainEntity must not implement Spring Data Persistable.")
    target = contract.get("targetRuntime") or {}
    if target.get("transientVersion", "missing") is not None or target.get("firstPersistedVersion") != 0 or target.get("firstUpdatedVersion") != 1:
        add(findings, "TARGET_LIFECYCLE", "Target lifecycle must be null -> 0 -> 1.")
    eager = bool(re.search(r"private Long persistenceVersion\s*=\s*0L;", source))
    nullable = bool(re.search(r"private Long persistenceVersion;", source)) and not eager
    legacy_test = "assertEquals(0L, entity.getPersistenceVersion())" in tests
    nullable_test = "assertNull(entity.getPersistenceVersion())" in tests
    if status == "decided":
        if not eager or not legacy_test:
            add(findings, "PARTIAL_TRANSITION", "Decision phase must preserve the eager-zero in-memory compatibility baseline.")
        if (contract.get("implementationBoundary") or {}).get("status") != "deferred-atomic-candidate-slice":
            add(findings, "IMPLEMENTATION_BOUNDARY", "Decision phase must defer runtime change to the atomic candidate slice.")
    elif status == "implemented":
        if not nullable or not nullable_test:
            add(findings, "IMPLEMENTATION", "Implemented phase requires nullable DomainEntity version and transient-null test evidence.")
        evidence = root / "PROJECT_DOCS/DEMO/CATALOGITEM_PERSISTENT_CANDIDATE_SLICE.md"
        persistence_test = root / "src/test/java/de/cocondo/platform/demo/catalog/CatalogItemPersistenceContractTest.java"
        if not evidence.is_file() or not persistence_test.is_file():
            add(findings, "PERSISTENT_EVIDENCE", "Implemented phase requires persistent candidate documentation and Java evidence.")
        else:
            text = persistence_test.read_text(encoding="utf-8")
            if "created.getPersistenceVersion()).isZero()" not in text or "reloadedAfterUpdate.getPersistenceVersion()).isEqualTo(1L)" not in text:
                add(findings, "VERSION_LIFECYCLE_EVIDENCE", "Persistent evidence must prove insert version 0 and update version 1.")
    report = {"schemaVersion": SCHEMA, "status": "pass" if not findings else "fail", "contractStatus": status, "findings": findings}
    report_path = Path(args.report).resolve() if args.report else root / "target/core-persistence-newness-contract-report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"CORE_PERSISTENCE_NEWNESS_CONTRACT={'PASS' if not findings else 'FAIL'}")
    print(f"CONTRACT_STATUS={status}")
    print(f"REPORT={report_path}")
    return 1 if args.check and findings else 0

if __name__ == "__main__":
    sys.exit(main())
