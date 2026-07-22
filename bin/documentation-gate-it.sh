#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
RUN_DIR="${PROJECT_ROOT}/build/documentation-gate-it/$(date +%Y%m%d_%H%M%S)_$$"
mkdir -p "${RUN_DIR}"

python3 - "${PROJECT_ROOT}" "${RUN_DIR}" <<'PY'
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

project_root = Path(sys.argv[1])
run_dir = Path(sys.argv[2])
expectations = json.loads((project_root / "src/test/resources/tooling/documentation-gate-v2/expected-cases.json").read_text(encoding="utf-8"))


def canonical_hash(paths, technical):
    raw = json.dumps({"paths": sorted(paths), "technicalArtifactPaths": sorted(technical)}, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def metadata(document_id, title, document_type, status, authority):
    return f"""---
documentId: {document_id}
title: {title}
documentType: {document_type}
status: {status}
authority: {authority}
scopeLevel: ecosystem
scopePaths:
  - springmaster/documentation
appliesTo:
  - springmaster
owner: springmaster-maintainers
createdAt: 2026-07-22
validFrom: {'2026-07-22' if status in {'active','accepted','final'} else 'null'}
lastReviewedAt: 2026-07-22
reviewBy: 2099-01-01
supersedes: []
supersededBy: null
temporary: false
sprintId: null
---
"""


def prepare(case_id):
    root = run_dir / case_id
    (root / "bin").mkdir(parents=True)
    shutil.copy2(project_root / "bin/documentation-gate.py", root / "bin/documentation-gate.py")
    shutil.copytree(project_root / "contracts/governance/documentation", root / "contracts/governance/documentation")
    shutil.copytree(project_root / "PROJECT_DOCS/_TEMPLATES", root / "PROJECT_DOCS/_TEMPLATES")
    (root / "PROJECT_DOCS/TOOLING").mkdir(parents=True)
    (root / "PROJECT_DOCS/GOVERNANCE").mkdir(parents=True)
    (root / "PROJECT_DOCS/STANDARDS").mkdir(parents=True)

    governance = metadata("DOC-GOV-TEST-001", "Fixture Governance", "governance", "active", "normative") + "\n# Fixture Governance\n"
    standard = metadata("DOC-STD-TEST-001", "Fixture Standard", "standard", "draft", "normative") + "\n# Fixture Standard\n"
    (root / "PROJECT_DOCS/GOVERNANCE/FIXTURE_GOVERNANCE.md").write_text(governance, encoding="utf-8")
    (root / "PROJECT_DOCS/STANDARDS/FIXTURE_STANDARD.md").write_text(standard, encoding="utf-8")

    legacy_paths = []
    technical_paths = ["PROJECT_DOCS/TOOLING/documentation-transition-baseline.json"]

    if case_id == "unknown-document-type":
        p = root / "PROJECT_DOCS/STANDARDS/FIXTURE_STANDARD.md"
        p.write_text(p.read_text().replace("documentType: standard", "documentType: unknown-type"), encoding="utf-8")
    elif case_id == "missing-required-field":
        p = root / "PROJECT_DOCS/STANDARDS/FIXTURE_STANDARD.md"
        p.write_text(p.read_text().replace("owner: springmaster-maintainers\n", ""), encoding="utf-8")
    elif case_id == "invalid-status":
        p = root / "PROJECT_DOCS/STANDARDS/FIXTURE_STANDARD.md"
        p.write_text(p.read_text().replace("status: draft", "status: accepted"), encoding="utf-8")
    elif case_id == "duplicate-document-id":
        duplicate = metadata("DOC-STD-TEST-001", "Duplicate Standard", "standard", "draft", "normative") + "\n# Duplicate\n"
        (root / "PROJECT_DOCS/STANDARDS/DUPLICATE_STANDARD.md").write_text(duplicate, encoding="utf-8")
    elif case_id == "invalid-supersession":
        p = root / "PROJECT_DOCS/STANDARDS/FIXTURE_STANDARD.md"
        p.write_text(p.read_text().replace("supersedes: []", "supersedes:\n  - DOC-UNKNOWN-999"), encoding="utf-8")
    elif case_id == "new-technical-artifact":
        (root / "PROJECT_DOCS/TECH").mkdir()
        (root / "PROJECT_DOCS/TECH/new-contract.json").write_text("{}\n", encoding="utf-8")
    elif case_id in {"valid-legacy-baseline", "invalid-baseline-extension"}:
        (root / "PROJECT_DOCS/legacy.md").write_text("# Legacy\n", encoding="utf-8")
        legacy_paths.append("PROJECT_DOCS/legacy.md")

    baseline = {
        "schemaVersion": "springmaster.documentation-transition-baseline.v2",
        "establishedFromGitHead": "fixture",
        "establishedAt": "2026-07-22",
        "paths": legacy_paths,
        "technicalArtifactPaths": technical_paths,
    }
    baseline["pathSetSha256"] = canonical_hash(legacy_paths, technical_paths)
    (root / "PROJECT_DOCS/TOOLING/documentation-transition-baseline.json").write_text(json.dumps(baseline, indent=2) + "\n", encoding="utf-8")

    metadata_contract_path = root / "contracts/governance/documentation/document-metadata-contract.json"
    metadata_contract = json.loads(metadata_contract_path.read_text(encoding="utf-8"))
    if case_id != "invalid-baseline-extension":
        metadata_contract["transitionBaseline"]["pathSetSha256"] = baseline["pathSetSha256"]
    metadata_contract_path.write_text(json.dumps(metadata_contract, indent=2) + "\n", encoding="utf-8")

    index_meta = metadata("DOC-IDX-TEST-001", "Fixture Index", "documentation-index", "active", "informative")
    md_paths = sorted(p.relative_to(root).as_posix() for p in (root / "PROJECT_DOCS").rglob("*.md") if p.name != "index.md")
    index = index_meta + "\n# Index\n\n" + "\n".join(f"- `{path}`" for path in md_paths) + "\n"
    (root / "PROJECT_DOCS/index.md").write_text(index, encoding="utf-8")

    if case_id == "tool-error-missing-contract":
        (root / "contracts/governance/documentation/document-types.json").unlink()
    return root


for case in expectations["cases"]:
    case_id = case["id"]
    fixture = prepare(case_id)
    report = run_dir / f"{case_id}.json"
    completed = subprocess.run(
        [sys.executable, str(fixture / "bin/documentation-gate.py"), "--root", str(fixture), "--out", str(report), "--check-all"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if completed.returncode != case["expectedExit"]:
        raise SystemExit(f"{case_id}: expected exit {case['expectedExit']}, got {completed.returncode}: {completed.stdout}")
    payload = json.loads(report.read_text(encoding="utf-8"))
    if payload.get("status") != case["expectedStatus"]:
        raise SystemExit(f"{case_id}: expected status {case['expectedStatus']}, got {payload.get('status')}")
    codes = {item.get("code") for item in payload.get("blockingFindings", [])}
    transition_codes = {item.get("code") for item in payload.get("transitionFindings", [])}
    tool_codes = {item.get("code") for item in payload.get("toolErrors", [])}
    if case.get("expectedCode") not in (None, *codes):
        raise SystemExit(f"{case_id}: expected blocking code {case.get('expectedCode')}, got {sorted(codes)}")
    if case.get("expectedTransitionCode") not in (None, *transition_codes):
        raise SystemExit(f"{case_id}: expected transition code {case.get('expectedTransitionCode')}, got {sorted(transition_codes)}")
    if case.get("expectedToolErrorCode") not in (None, *tool_codes):
        raise SystemExit(f"{case_id}: expected tool error code {case.get('expectedToolErrorCode')}, got {sorted(tool_codes)}")

print(f"DOCUMENTATION_GATE_IT=PASS")
print(f"CASES={len(expectations['cases'])}")
print(f"REPORT_DIR={run_dir}")
PY
