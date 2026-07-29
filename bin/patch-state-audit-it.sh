#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AUDITOR="${SCRIPT_DIR}/patch-state-audit.py"
TMP_ROOT="$(mktemp -d)"
trap 'rm -rf "${TMP_ROOT}"' EXIT

make_patch() {
  local root="$1" patch_id="$2" archive_status="$3" accept_status="$4" rollback="$5"
  mkdir -p "${root}/patches/archives/${patch_id}" "${root}/patches/logs/accept/${patch_id}"
  printf '{"patchId":"%s","status":"%s"}\n' "${patch_id}" "${archive_status}" > "${root}/patches/archives/${patch_id}/patch-log.json"
  printf 'STATUS=%s\n' "${accept_status}" > "${root}/patches/logs/accept/${patch_id}/SUMMARY.txt"
  if [[ "${rollback}" == "yes" ]]; then
    : > "${root}/patches/archives/${patch_id}/ROLLBACK_DONE"
  fi
}

write_reconciliation() {
  local root="$1" patch_id="$2" evidence_path="$3" archive_status="${4:-applied}" accept_status="${5:-FAILED}"
  mkdir -p "${root}/contracts/governance" "${root}/$(dirname "${evidence_path}")"
  printf 'closure\n' > "${root}/${evidence_path}"
  cat > "${root}/contracts/governance/patch-state-reconciliations.json" <<EOF
{
  "schemaVersion": "springmaster.patch-state-reconciliations.v1",
  "entries": [{
    "patchId": "${patch_id}",
    "observedArchiveStatus": "${archive_status}",
    "observedAcceptStatus": "${accept_status}",
    "resolution": "historical_joint_closure",
    "closurePatchIds": ["000010_closure"],
    "evidencePaths": ["${evidence_path}"],
    "rationale": "fixture"
  }]
}
EOF
}

PASS_ROOT="${TMP_ROOT}/pass"
make_patch "${PASS_ROOT}" "000001_success" "applied" "SUCCESS" "no"
python3 "${AUDITOR}" "${PASS_ROOT}" --check --skip-git >/dev/null

FAILED_ROOT="${TMP_ROOT}/failed"
make_patch "${FAILED_ROOT}" "000002_failed" "applied" "FAILED" "no"
if python3 "${AUDITOR}" "${FAILED_ROOT}" --check --skip-git >/dev/null 2>&1; then
  echo "Expected APPLIED_WITH_FAILED_ACCEPT to fail." >&2
  exit 1
fi

RECOVERED_ROOT="${TMP_ROOT}/recovered"
make_patch "${RECOVERED_ROOT}" "000003_recovered" "rolled_back" "FAILED" "yes"
python3 "${AUDITOR}" "${RECOVERED_ROOT}" --check --skip-git >/dev/null

RECONCILED_ROOT="${TMP_ROOT}/reconciled"
make_patch "${RECONCILED_ROOT}" "000004_historical" "applied" "FAILED" "no"
write_reconciliation "${RECONCILED_ROOT}" "000004_historical" "PROJECT_DOCS/closure.md"
python3 "${AUDITOR}" "${RECONCILED_ROOT}" --check --skip-git > "${TMP_ROOT}/reconciled.log"
grep -q 'HISTORICAL_ACCEPT_RECONCILED' "${TMP_ROOT}/reconciled.log"

MISSING_EVIDENCE_ROOT="${TMP_ROOT}/missing-evidence"
make_patch "${MISSING_EVIDENCE_ROOT}" "000005_missing" "applied" "FAILED" "no"
write_reconciliation "${MISSING_EVIDENCE_ROOT}" "000005_missing" "PROJECT_DOCS/missing.md"
rm "${MISSING_EVIDENCE_ROOT}/PROJECT_DOCS/missing.md"
if python3 "${AUDITOR}" "${MISSING_EVIDENCE_ROOT}" --check --skip-git >/dev/null 2>&1; then
  echo "Expected missing reconciliation evidence to fail." >&2
  exit 1
fi

MISMATCH_ROOT="${TMP_ROOT}/mismatch"
make_patch "${MISMATCH_ROOT}" "000006_mismatch" "applied" "FAILED" "no"
write_reconciliation "${MISMATCH_ROOT}" "000006_mismatch" "PROJECT_DOCS/closure.md" "rolled_back" "FAILED"
if python3 "${AUDITOR}" "${MISMATCH_ROOT}" --check --skip-git >/dev/null 2>&1; then
  echo "Expected reconciliation status mismatch to fail." >&2
  exit 1
fi

STALE_ROOT="${TMP_ROOT}/stale"
make_patch "${STALE_ROOT}" "000007_success" "applied" "SUCCESS" "no"
write_reconciliation "${STALE_ROOT}" "000007_success" "PROJECT_DOCS/closure.md" "applied" "SUCCESS"
if python3 "${AUDITOR}" "${STALE_ROOT}" --check --skip-git >/dev/null 2>&1; then
  echo "Expected stale reconciliation to fail." >&2
  exit 1
fi

EMPTY_ARCHIVE_ROOT="${TMP_ROOT}/empty-archive-skeleton"
mkdir -p "${EMPTY_ARCHIVE_ROOT}/patches/archives/000008_removed/after/deep"
python3 "${AUDITOR}" "${EMPTY_ARCHIVE_ROOT}" --check --skip-git --report "${TMP_ROOT}/empty-archive-report.json" > "${TMP_ROOT}/empty-archive.log"
python3 - "${TMP_ROOT}/empty-archive-report.json" <<'PY_EMPTY_ARCHIVE'
import json
import sys
from pathlib import Path
report = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
assert report["status"] == "pass", report
assert report["summary"]["archives"] == 0, report
assert report["summary"]["emptyArchiveDirectories"] == 1, report
assert report["emptyArchiveDirectories"] == ["000008_removed"], report
assert not any(item["id"] == "PATCH_LOG_INVALID" for item in report["findings"]), report
PY_EMPTY_ARCHIVE

PARTIAL_ARCHIVE_ROOT="${TMP_ROOT}/partial-archive"
mkdir -p "${PARTIAL_ARCHIVE_ROOT}/patches/archives/000009_partial"
printf 'residual\n' > "${PARTIAL_ARCHIVE_ROOT}/patches/archives/000009_partial/residual.txt"
if python3 "${AUDITOR}" "${PARTIAL_ARCHIVE_ROOT}" --check --skip-git > "${TMP_ROOT}/partial-archive.log" 2>&1; then
  echo "Expected non-empty archive without patch-log.json to fail." >&2
  exit 1
fi
grep -q 'PATCH_LOG_INVALID 000009_partial' "${TMP_ROOT}/partial-archive.log"
echo "PATCH_STATE_AUDIT_IT=PASS"
