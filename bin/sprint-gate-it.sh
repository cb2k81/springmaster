#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
RUN_DIR="${PROJECT_ROOT}/build/sprint-gate-it/$(date +%Y%m%d_%H%M%S)_$$"
mkdir -p "${RUN_DIR}"

python3 - "${PROJECT_ROOT}" "${RUN_DIR}" <<'PY'
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

project_root = Path(sys.argv[1])
run_dir = Path(sys.argv[2])
expectations = json.loads((project_root / "src/test/resources/tooling/sprint-gate-v1/expected-cases.json").read_text(encoding="utf-8"))

SPRINT_ID = "TEST-SPRINT-001"


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def metadata(document_id: str, title: str, document_type: str, status: str, authority: str, temporary: bool, extra: dict[str, str | None] | None = None) -> str:
    values = {
        "documentId": document_id,
        "title": title,
        "documentType": document_type,
        "status": status,
        "authority": authority,
        "scope": "repository",
        "scopeLevel": "project",
        "scopePaths": ["springmaster/sprints"],
        "appliesTo": ["springmaster"],
        "owner": "test-owner",
        "createdAt": "2099-01-01",
        "validFrom": None,
        "lastReviewedAt": None,
        "reviewBy": "2099-12-31" if temporary else None,
        "supersedes": [],
        "supersededBy": None,
        "temporary": temporary,
        "sprintId": SPRINT_ID,
    }
    if extra:
        values.update(extra)
    lines = ["---"]
    for key, value in values.items():
        if isinstance(value, list):
            if not value:
                lines.append(f"{key}: []")
            else:
                lines.append(f"{key}:")
                lines.extend(f"  - {item}" for item in value)
        elif value is None:
            lines.append(f"{key}: null")
        elif isinstance(value, bool):
            lines.append(f"{key}: {'true' if value else 'false'}")
        else:
            lines.append(f"{key}: {value}")
    lines.extend(["---", ""])
    return "\n".join(lines)


def brief(status: str = "planned", sprint_id: str = SPRINT_ID, target: str = "2099-03-31") -> str:
    text = metadata(
        f"{sprint_id}-BRIEF",
        "Test Sprint Brief",
        "sprint-brief",
        status,
        "directive",
        False,
        {"sprintId": sprint_id, "sprintStart": "2099-01-01", "targetCompletion": target},
    )
    return text + """# Test Sprint Brief

## Sprintziel

Nachweisbares Ergebnis.

## Strategischer Bezug

Strategisches Ziel.

## Ausgangslage und Baseline

Baseline.

## Problemstellung und Stakeholder

Problem.

## Anforderungen

REQ-001.

## Qualitätsanforderungen

Qualität.

## In Scope

Scope.

## Out of Scope

Keine Features.

## Constraints und Abhängigkeiten

Constraint.

## Risiken

Risiko.

## Definition of Ready

- [x] Auftrag und Scope bestätigt.

## Definition of Done

- [ ] Ergebnis und Evidence bewertet.

## Messbare Teilziele

| ID | Ergebnis | Anforderungen | Acceptance | Evidence | Owner | Status |
|---|---|---|---|---|---|---|
| M-001 | Ergebnis | REQ-001 | Kriterium | Report | test-owner | planned |

## SemVer-Auswirkung

none

## Stop- und Abbruchkriterien

Stop bei unzuverlässiger Baseline.

## Amendments

Keine.

## Lifecycle

| Datum | Vorher | Nachher | Grund |
|---|---|---|---|
| 2099-01-01 | - | planned | Sprint angelegt |
"""


def solution() -> str:
    return metadata(f"{SPRINT_ID}-PLAN", "Test Solution Plan", "plan", "draft", "directive", True) + """# Test Solution Plan

## Lösungsoptionen und Auswahl

Option A.

## Architektur- und Contract-Auswirkungen

Keine.

## Slices und Reihenfolge

Slice 1.

## Teststrategie und Zwischenverifikationen

Gate.

## Messkriterien

M-001.

## Migration und Rollback

Rollback.

## Tool- und Gate-Einsatz

Sprint Gate.

## Dokumentations- und Registerauswirkungen

Keine.

## Versionswirkung

none

## Patch- oder Commitsequenz

Patch 1.

## Unsicherheiten und Entscheidungszeitpunkte

Keine.

## Lifecycle

| Datum | Vorher | Nachher | Grund |
|---|---|---|---|
| 2099-01-01 | - | draft | Plan angelegt |
"""


def status(last_drift: str = "none", drift_at: str = "2099-01-01", phase: str = "problem-framing", milestone_id: str = "M-001") -> str:
    return metadata(
        f"{SPRINT_ID}-STATUS",
        "Test Sprint Status",
        "sprint-status",
        "planned",
        "evidence",
        True,
        {
            "sprintPhase": phase,
            "overallStatus": "planned",
            "lastDriftResult": last_drift,
            "lastDriftAt": drift_at,
            "expectedVersionImpact": "none",
        },
    ) + f"""# Test Sprint Status

## Aktueller Stand

Geplant.

## Teilziele

| ID | Status | Evidence oder Blocker |
|---|---|---|
| {milestone_id} | planned | offen |

## Blocker und Erkenntnisse

Keine.

## Drift-Bewertung

{last_drift}

## Risiken und technische Schulden

Keine.

## Versionswirkung

none

## Nächster kontrollierter Schritt

Problem Framing abschließen.

## Lifecycle

| Datum | Vorher | Nachher | Grund |
|---|---|---|---|
| 2099-01-01 | - | planned | Status angelegt |
"""


def completion(status_value: str = "draft", qualification: str = "pending", closure: str = "open", closed_at: str | None = None, disposition: bool = True) -> str:
    extra = {"qualificationStatus": qualification, "closureStatus": closure, "closedAt": closed_at}
    text = metadata(f"{SPRINT_ID}-COMPLETION", "Test Completion Report", "sprint-completion-report", status_value, "evidence", False, extra)
    disposition_rows = "| SOLUTION_PLAN.md | aggregate | Report |\n| STATUS.md | discard | Endstand im Report |" if disposition else "| STATUS.md | discard | Endstand im Report |"
    return text + f"""# Test Completion Report

## Ergebnisübersicht

Noch offen.

## Anforderungen und Teilziele

M-001 ist bewertet.

## Definition of Done und Qualification

{qualification}

## Akzeptierte Änderungen

Keine.

## Dauerhafte Promotionen

Keine.

## Offene Findings, Risiken und Schulden

Keine.

## Temporäre Dokumente

| Pfad | Entscheidung | Ziel oder Begründung |
|---|---|---|
{disposition_rows}

## SemVer- und Releasebewertung

none

## Nicht erreichte Ziele und Folgebedarf

Keine.

## Lifecycle

| Datum | Vorher | Nachher | Grund |
|---|---|---|---|
| 2099-01-01 | - | {status_value} | Report angelegt |
"""


def base_root(case_id: str) -> Path:
    root = run_dir / case_id
    root.mkdir(parents=True)
    for relative in [
        "bin/sprint-gate.py",
        "contracts/governance/sprint/sprint-contract.json",
        "contracts/governance/sprint/sprint-drift-contract.json",
        "PROJECT_DOCS/_TEMPLATES/SPRINT_BRIEF_TEMPLATE.md",
        "PROJECT_DOCS/_TEMPLATES/SPRINT_SOLUTION_PLAN_TEMPLATE.md",
        "PROJECT_DOCS/_TEMPLATES/SPRINT_STATUS_TEMPLATE.md",
        "PROJECT_DOCS/_TEMPLATES/SPRINT_COMPLETION_REPORT_TEMPLATE.md",
    ]:
        source = project_root / relative
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    write(root / "PROJECT_DOCS/index.md", "# Index\n")
    return root


def create_active(root: Path, sprint_id: str = SPRINT_ID) -> Path:
    sprint = root / "PROJECT_DOCS/SPRINTS/ACTIVE" / sprint_id
    sprint.mkdir(parents=True)
    write(sprint / "SPRINT_BRIEF.md", brief(sprint_id=sprint_id))
    write(sprint / "SOLUTION_PLAN.md", solution().replace(SPRINT_ID, sprint_id))
    write(sprint / "STATUS.md", status().replace(SPRINT_ID, sprint_id))
    write(sprint / "COMPLETION_REPORT.md", completion().replace(SPRINT_ID, sprint_id))
    index = "# Index\n" + "\n".join(f"- `{path.relative_to(root).as_posix()}`" for path in sorted(sprint.glob("*.md"))) + "\n"
    write(root / "PROJECT_DOCS/index.md", index)
    return sprint


def create_archive(root: Path) -> Path:
    sprint = root / "PROJECT_DOCS/SPRINTS/ARCHIVE/2099" / SPRINT_ID
    sprint.mkdir(parents=True)
    write(sprint / "SPRINT_BRIEF.md", brief(status="archived"))
    write(sprint / "COMPLETION_REPORT.md", completion("final", "qualified", "completed", "2099-03-31"))
    index = "# Index\n" + "\n".join(f"- `{path.relative_to(root).as_posix()}`" for path in sorted(sprint.glob("*.md"))) + "\n"
    write(root / "PROJECT_DOCS/index.md", index)
    return sprint


def prepare(case_id: str) -> tuple[Path, list[str]]:
    root = base_root(case_id)
    changed_paths: list[str] = []
    if case_id == "no-sprints" or case_id == "contract-change-expands-all":
        return root, changed_paths
    if case_id == "empty-active-directory":
        (root / "PROJECT_DOCS/SPRINTS/ACTIVE" / SPRINT_ID).mkdir(parents=True)
        return root, changed_paths
    if case_id in {"valid-archived-sprint", "archive-temporary-content"}:
        sprint = create_archive(root)
        if case_id == "archive-temporary-content":
            write(sprint / "STATUS.md", status())
        return root, changed_paths
    sprint_id = "bad-sprint" if case_id == "invalid-sprint-id" else SPRINT_ID
    sprint = create_active(root, sprint_id)
    if case_id == "missing-required-document":
        (sprint / "SOLUTION_PLAN.md").unlink()
    elif case_id == "document-id-mismatch":
        path = sprint / "SPRINT_BRIEF.md"
        write(path, path.read_text(encoding="utf-8").replace(f"documentId: {SPRINT_ID}-BRIEF", "documentId: WRONG-BRIEF"))
    elif case_id == "required-heading-missing":
        path = sprint / "SOLUTION_PLAN.md"
        write(path, path.read_text(encoding="utf-8").replace("## Migration und Rollback\n", ""))
    elif case_id == "solution-content-in-brief":
        path = sprint / "SPRINT_BRIEF.md"
        write(path, path.read_text(encoding="utf-8") + "\n## Lösungsoptionen und Auswahl\n\nNicht zulässig.\n")
    elif case_id == "dor-incomplete":
        path = sprint / "SPRINT_BRIEF.md"
        write(path, path.read_text(encoding="utf-8").replace("- [x] Auftrag und Scope bestätigt.", "Auftrag und Scope bestätigt."))
    elif case_id == "milestone-status-invalid":
        path = sprint / "SPRINT_BRIEF.md"
        write(path, path.read_text(encoding="utf-8").replace("| M-001 | Ergebnis | REQ-001 | Kriterium | Report | test-owner | planned |", "| M-001 | Ergebnis | REQ-001 | Kriterium | Report | test-owner | unknown |"))
    elif case_id == "duplicate-status-source":
        write(sprint / "WORK/ANALYSES/SECOND_STATUS.md", status())
    elif case_id == "phase-invalid":
        path = sprint / "STATUS.md"
        write(path, path.read_text(encoding="utf-8").replace("sprintPhase: problem-framing", "sprintPhase: impossible"))
    elif case_id == "status-milestone-mismatch":
        write(sprint / "STATUS.md", status(milestone_id="M-999"))
    elif case_id == "accepted-drift-without-amendment":
        write(sprint / "STATUS.md", status(last_drift="accepted"))
    elif case_id == "incomplete-amendment":
        path = sprint / "SPRINT_BRIEF.md"
        text = path.read_text(encoding="utf-8").replace("## Lifecycle", "### AMEND-001\n\n- Datum: 2099-01-02\n- Anlass: Drift\n\n## Lifecycle", 1)
        write(path, text)
    elif case_id == "stale-target-drift":
        write(sprint / "SPRINT_BRIEF.md", brief(target="2020-01-01"))
        write(sprint / "STATUS.md", status(drift_at="2019-12-31"))
    elif case_id == "work-metadata-invalid":
        write(sprint / "WORK/ANALYSES/NOTE.md", "# Note\n")
    elif case_id == "closed-without-disposition":
        write(sprint / "COMPLETION_REPORT.md", completion("final", "qualified", "completed", "2099-03-31", disposition=False))
    return root, changed_paths


for case in expectations["cases"]:
    case_id = case["id"]
    root, changed_paths = prepare(case_id)
    if case_id == "tool-error-missing-contract":
        (root / "contracts/governance/sprint/sprint-drift-contract.json").unlink()
    report = run_dir / f"{case_id}.json"
    command = [
        sys.executable,
        str(root / "bin/sprint-gate.py"),
        "--root", str(root),
        "--mode", case.get("mode", "all"),
        "--out", str(report),
        "--check",
    ]
    if case.get("changedPath"):
        command.extend(["--changed-path", case["changedPath"]])
    completed = subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    if completed.returncode != case["expectedExit"]:
        raise SystemExit(f"{case_id}: expected exit {case['expectedExit']}, got {completed.returncode}: {completed.stdout}")
    payload = json.loads(report.read_text(encoding="utf-8"))
    if payload.get("status") != case["expectedStatus"]:
        raise SystemExit(f"{case_id}: expected status {case['expectedStatus']}, got {payload.get('status')}")
    codes = {item.get("code") for item in payload.get("newFindings", [])}
    tool_codes = {item.get("code") for item in payload.get("toolErrors", [])}
    expected_code = case.get("expectedCode")
    if expected_code and expected_code not in codes:
        raise SystemExit(f"{case_id}: expected finding {expected_code}, got {sorted(codes)}")
    expected_tool = case.get("expectedToolErrorCode")
    if expected_tool and expected_tool not in tool_codes:
        raise SystemExit(f"{case_id}: expected tool error {expected_tool}, got {sorted(tool_codes)}")
    if "expectedExpandedToAll" in case and payload.get("expandedToAll") is not case["expectedExpandedToAll"]:
        raise SystemExit(f"{case_id}: expected expandedToAll={case['expectedExpandedToAll']}, got {payload.get('expandedToAll')}")

print("SPRINT_GATE_IT=PASS")
print(f"CASES={len(expectations['cases'])}")
print(f"REPORT_DIR={run_dir}")
PY
