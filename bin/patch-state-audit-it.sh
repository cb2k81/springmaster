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

echo "PATCH_STATE_AUDIT_IT=PASS"
