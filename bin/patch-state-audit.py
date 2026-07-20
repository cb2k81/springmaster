#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA = "springmaster.patch-state-audit.v2"
RECONCILIATION_SCHEMA = "springmaster.patch-state-reconciliations.v1"
RECONCILIATION_PATH = Path("contracts/governance/patch-state-reconciliations.json")
ALLOWED_RESOLUTIONS = {"historical_joint_closure"}


def read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - surfaced as deterministic finding
        raise ValueError(f"cannot read JSON {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return data


def read_summary_status(path: Path) -> str | None:
    if not path.is_file():
        return None
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith("STATUS="):
            value = line.split("=", 1)[1].strip()
            return value or None
    return None


def git_dirty_paths(project_root: Path) -> list[str]:
    result = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=all"],
        cwd=project_root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        return [f"<git-status-error:{result.stderr.strip() or result.returncode}>"]
    paths: list[str] = []
    for raw in result.stdout.splitlines():
        if not raw.strip():
            continue
        path = raw[3:] if len(raw) >= 4 else raw
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        paths.append(path)
    return sorted(paths)


def load_reconciliations(project_root: Path, findings: list[dict[str, str]]) -> dict[str, dict[str, Any]]:
    path = project_root / RECONCILIATION_PATH
    if not path.is_file():
        return {}
    try:
        data = read_json(path)
    except Exception as exc:
        findings.append({
            "id": "RECONCILIATION_REGISTRY_INVALID",
            "severity": "error",
            "patchId": "-",
            "message": str(exc),
        })
        return {}
    if data.get("schemaVersion") != RECONCILIATION_SCHEMA or not isinstance(data.get("entries"), list):
        findings.append({
            "id": "RECONCILIATION_REGISTRY_INVALID",
            "severity": "error",
            "patchId": "-",
            "message": f"Expected {RECONCILIATION_SCHEMA} with an entries array.",
        })
        return {}
    result: dict[str, dict[str, Any]] = {}
    for index, raw in enumerate(data["entries"]):
        if not isinstance(raw, dict):
            findings.append({
                "id": "RECONCILIATION_ENTRY_INVALID",
                "severity": "error",
                "patchId": "-",
                "message": f"Entry {index} must be an object.",
            })
            continue
        patch_id = str(raw.get("patchId") or "").strip()
        if not patch_id or patch_id in result:
            findings.append({
                "id": "RECONCILIATION_ENTRY_INVALID",
                "severity": "error",
                "patchId": patch_id or "-",
                "message": "Reconciliation patchId must be non-empty and unique.",
            })
            continue
        if raw.get("resolution") not in ALLOWED_RESOLUTIONS:
            findings.append({
                "id": "RECONCILIATION_ENTRY_INVALID",
                "severity": "error",
                "patchId": patch_id,
                "message": "Unsupported reconciliation resolution.",
            })
            continue
        closure_ids = raw.get("closurePatchIds")
        evidence_paths = raw.get("evidencePaths")
        if not isinstance(closure_ids, list) or not closure_ids or not all(isinstance(v, str) and v for v in closure_ids):
            findings.append({
                "id": "RECONCILIATION_ENTRY_INVALID",
                "severity": "error",
                "patchId": patch_id,
                "message": "closurePatchIds must be a non-empty string array.",
            })
            continue
        if not isinstance(evidence_paths, list) or not evidence_paths or not all(isinstance(v, str) and v for v in evidence_paths):
            findings.append({
                "id": "RECONCILIATION_ENTRY_INVALID",
                "severity": "error",
                "patchId": patch_id,
                "message": "evidencePaths must be a non-empty string array.",
            })
            continue
        result[patch_id] = raw
    return result


def validate_reconciliation(
    project_root: Path,
    patch_id: str,
    archive_status: str,
    summary_status: str | None,
    reconciliation: dict[str, Any],
) -> str | None:
    if reconciliation.get("observedArchiveStatus") != archive_status:
        return "Reconciliation archive status does not match the observed archive state."
    if reconciliation.get("observedAcceptStatus") != summary_status:
        return "Reconciliation accept status does not match the observed acceptance summary."
    missing = [
        path for path in reconciliation.get("evidencePaths", [])
        if not (project_root / path).is_file()
    ]
    if missing:
        return "Reconciliation evidence is missing: " + ", ".join(sorted(missing))
    return None


def audit(project_root: Path, require_clean: bool, skip_git: bool) -> dict[str, Any]:
    archives_root = project_root / "patches" / "archives"
    accept_root = project_root / "patches" / "logs" / "accept"
    findings: list[dict[str, str]] = []
    patches: list[dict[str, Any]] = []
    reconciliations = load_reconciliations(project_root, findings)
    used_reconciliations: set[str] = set()

    archive_dirs = sorted(
        [path for path in archives_root.iterdir() if path.is_dir()],
        key=lambda path: path.name,
    ) if archives_root.is_dir() else []

    for archive_dir in archive_dirs:
        patch_id = archive_dir.name
        log_path = archive_dir / "patch-log.json"
        rollback_marker = (archive_dir / "ROLLBACK_DONE").is_file()
        try:
            patch_log = read_json(log_path)
            archive_status = str(patch_log.get("status") or "unknown")
        except Exception as exc:
            archive_status = "invalid"
            findings.append({
                "id": "PATCH_LOG_INVALID",
                "severity": "error",
                "patchId": patch_id,
                "message": str(exc),
            })

        summary_status = read_summary_status(accept_root / patch_id / "SUMMARY.txt")
        effective_status = "rolled_back" if rollback_marker else archive_status
        reconciliation_status = None

        if rollback_marker != (archive_status == "rolled_back"):
            findings.append({
                "id": "ROLLBACK_STATUS_MISMATCH",
                "severity": "error",
                "patchId": patch_id,
                "message": "ROLLBACK_DONE and patch-log status must agree.",
            })

        if effective_status == "applied" and summary_status == "FAILED":
            reconciliation = reconciliations.get(patch_id)
            if reconciliation is None:
                findings.append({
                    "id": "APPLIED_WITH_FAILED_ACCEPT",
                    "severity": "error",
                    "patchId": patch_id,
                    "message": "A patch with failed acceptance must be rolled back or explicitly reconciled by immutable closure evidence.",
                })
            else:
                error = validate_reconciliation(project_root, patch_id, archive_status, summary_status, reconciliation)
                used_reconciliations.add(patch_id)
                if error:
                    reconciliation_status = "invalid"
                    findings.append({
                        "id": "RECONCILIATION_INVALID",
                        "severity": "error",
                        "patchId": patch_id,
                        "message": error,
                    })
                else:
                    reconciliation_status = "accepted"
                    findings.append({
                        "id": "HISTORICAL_ACCEPT_RECONCILED",
                        "severity": "warning",
                        "patchId": patch_id,
                        "message": "Historical failed acceptance is retained and explicitly closed by later immutable evidence.",
                    })

        if effective_status == "rolled_back" and summary_status == "SUCCESS":
            findings.append({
                "id": "ROLLED_BACK_WITH_SUCCESS_SUMMARY",
                "severity": "warning",
                "patchId": patch_id,
                "message": "The patch was rolled back after a successful acceptance; review provenance.",
            })

        patches.append({
            "patchId": patch_id,
            "archiveStatus": archive_status,
            "effectiveStatus": effective_status,
            "acceptStatus": summary_status,
            "rollbackMarker": rollback_marker,
            "reconciliationStatus": reconciliation_status,
        })

    archive_patch_ids = {path.name for path in archive_dirs}
    unused_reconciliations = sorted(set(reconciliations) - used_reconciliations)
    for patch_id in unused_reconciliations:
        if patch_id in archive_patch_ids:
            findings.append({
                "id": "STALE_RECONCILIATION",
                "severity": "error",
                "patchId": patch_id,
                "message": "Reconciliation entry does not match the present patch runtime state.",
            })
        else:
            findings.append({
                "id": "RECONCILIATION_PATCH_UNAVAILABLE",
                "severity": "warning",
                "patchId": patch_id,
                "message": "The reconciled historical patch archive is not present in this checkout; declaration is retained but runtime verification is unavailable.",
            })

    dirty_paths: list[str] = []
    if not skip_git:
        dirty_paths = git_dirty_paths(project_root)
        if require_clean and dirty_paths:
            findings.append({
                "id": "GIT_WORKTREE_DIRTY",
                "severity": "error",
                "patchId": "-",
                "message": "A clean Working Tree is required: " + ", ".join(dirty_paths),
            })

    errors = sum(1 for finding in findings if finding["severity"] == "error")
    warnings = sum(1 for finding in findings if finding["severity"] == "warning")
    return {
        "schemaVersion": SCHEMA,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "projectRoot": str(project_root),
        "status": "pass" if errors == 0 else "fail",
        "summary": {
            "archives": len(archive_dirs),
            "errors": errors,
            "warnings": warnings,
            "dirtyPaths": len(dirty_paths),
            "reconciliations": len(reconciliations),
        },
        "patches": patches,
        "dirtyPaths": dirty_paths,
        "findings": findings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit patch archive, acceptance, reconciliation and Git state invariants.")
    parser.add_argument("project_root", nargs="?", default=".")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--require-clean", action="store_true")
    parser.add_argument("--skip-git", action="store_true")
    parser.add_argument("--report")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    report = audit(project_root, args.require_clean, args.skip_git)
    report_path = Path(args.report).resolve() if args.report else project_root / "target" / "patch-state-audit-report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(f"PATCH_STATE_AUDIT={'PASS' if report['status'] == 'pass' else 'FAIL'}")
    print(f"REPORT={report_path}")
    for finding in report["findings"]:
        print(f"{finding['severity'].upper()} {finding['id']} {finding['patchId']}: {finding['message']}")

    return 0 if report["status"] == "pass" or not args.check else 1


if __name__ == "__main__":
    sys.exit(main())
