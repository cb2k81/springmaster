#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"
WORK_ROOT="${1:-${PROJECT_ROOT}/target/platform-update-managed-project-pilot}"
TARGET_NAME=managed-pilot
TARGET_ROOT="${WORK_ROOT}/target"
TARGETS_DIR="${WORK_ROOT}/targets"
BUILD_ROOT="${WORK_ROOT}/build"
FULL_TEST_LOG="${WORK_ROOT}/full-test.log"
FULL_TEST_COMMAND="${WORK_ROOT}/full-test-command.sh"
fail(){ echo "[FAIL] $*" >&2; exit 1; }
rm -rf "${WORK_ROOT}"; mkdir -p "${TARGETS_DIR}" "${BUILD_ROOT}"
MASTER_CORE="$(sed -n 's/^PLATFORM_CORE_VERSION=//p' "${PROJECT_ROOT}/platform/versions/platform.env")"
MASTER_TOOLING="$(sed -n 's/^PLATFORM_TOOLING_VERSION=//p' "${PROJECT_ROOT}/platform/versions/platform.env")"
SOURCE_HEAD="$(git -C "${PROJECT_ROOT}" rev-parse HEAD)"
SOURCE_STATUS="$(git -C "${PROJECT_ROOT}" status --porcelain --untracked-files=all)"
"${PROJECT_ROOT}/bin/project-new.sh" create --name "${TARGET_NAME}" --path "${TARGET_ROOT}" --group-id de.cocondo.managedpilot --base-package de.cocondo.managedpilot --core-version 0.3.6 --tooling-version 0.5.0 > "${WORK_ROOT}/project-new.log"
cat > "${FULL_TEST_COMMAND}" <<EOF
#!/usr/bin/env bash
set -euo pipefail
printf 'FULL_TEST %s\n' "\$(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "${FULL_TEST_LOG}"
EOF
chmod +x "${FULL_TEST_COMMAND}"
cat > "${TARGET_ROOT}/.env" <<EOF
PATCH_FULL_TEST_COMMAND=${FULL_TEST_COMMAND}
EOF
git -C "${TARGET_ROOT}" init -q
git -C "${TARGET_ROOT}" config user.name "Springmaster Pilot"
git -C "${TARGET_ROOT}" config user.email "springmaster-pilot@example.invalid"
git -C "${TARGET_ROOT}" add -A
if git -C "${TARGET_ROOT}" check-ignore -q patches/archives/000001_project_new_bootstrap/manifest.json; then fail "bootstrap archive must remain trackable"; fi
mkdir -p "${TARGET_ROOT}/patches/archives/999999_future"; printf '{}\n' > "${TARGET_ROOT}/patches/archives/999999_future/manifest.json"
git -C "${TARGET_ROOT}" check-ignore -q patches/archives/999999_future/manifest.json || fail "future archives must be ignored"
rm -rf "${TARGET_ROOT}/patches/archives/999999_future"
git -C "${TARGET_ROOT}" commit -q -m "Managed target pilot baseline"
cat > "${TARGETS_DIR}/${TARGET_NAME}.env" <<EOF
TARGET_NAME=${TARGET_NAME}
TARGET_STATUS=DELIVERY_ENABLED
TARGET_PATH=${TARGET_ROOT}
TARGET_APP_NAME=${TARGET_NAME}
TARGET_BASE_PACKAGE=de.cocondo.managedpilot
TARGET_PORT=8080
TARGET_DB_NAME=managed_pilot
TARGET_STAGE_DB_NAME=managed_pilot_build
TARGET_LIFECYCLE=update-enabled
TARGET_INITIALIZATION_ALLOWED=false
TARGET_UPDATE_ALLOWED=true
TARGET_DELIVERY_ENABLED=true
TARGET_ALLOWED_PROFILES=tooling-cutover,core
TARGET_NOTES=Isolated self-contained P2 managed lifecycle pilot.
EOF
run_update(){ PLATFORM_UPDATE_TARGET_DIR="${TARGETS_DIR}" PLATFORM_UPDATE_BUILD_WORKSPACE_DIR="${BUILD_ROOT}" "${PROJECT_ROOT}/bin/platform-update.sh" "$@"; }
apply_profile(){
  local profile="$1" component="$2" output zip patch_id apply_output export_path
  run_update compatibility-check "${TARGET_NAME}" --profile "${profile}" > "${WORK_ROOT}/${profile}-compatibility.log"
  grep -q '^PLATFORM_UPDATE_COMPATIBILITY=PASS$' "${WORK_ROOT}/${profile}-compatibility.log" || fail "compatibility failed for ${profile}"
  output="$(run_update generate "${TARGET_NAME}" --profile "${profile}")"; printf '%s\n' "${output}" > "${WORK_ROOT}/${profile}-generate.log"
  zip="$(printf '%s\n' "${output}" | sed -n 's/^  ZIP:[[:space:]]*//p' | tail -n 1)"; [[ -f "${zip}" ]] || fail "generated ZIP missing for ${profile}"
  patch_id="$(python3 - "${zip}" <<'PY_PATCH_ID'
import json,sys,zipfile
with zipfile.ZipFile(sys.argv[1]) as zf: print(json.loads(zf.read('manifest.json'))['patchId'])
PY_PATCH_ID
)"
  run_update preflight "${TARGET_NAME}" --zip "${zip}" > "${WORK_ROOT}/${profile}-preflight.log"
  grep -q 'Status:[[:space:]]*PASSED' "${WORK_ROOT}/${profile}-preflight.log" || fail "target preflight failed for ${profile}"
  apply_output="$(run_update target-apply "${TARGET_NAME}" --zip "${zip}")"; printf '%s\n' "${apply_output}" > "${WORK_ROOT}/${profile}-apply.log"
  grep -q 'Status:[[:space:]]*OK' "${WORK_ROOT}/${profile}-apply.log" || fail "target apply failed for ${profile}"
  python3 - "${TARGET_ROOT}" "${patch_id}" "${profile}" "${component}" <<'PY_STATE'
import json,sys
from pathlib import Path
r=Path(sys.argv[1]); pid,profile,component=sys.argv[2:]
v={}
for line in (r/'platform/versions/platform.env').read_text().splitlines():
    if '=' in line and not line.lstrip().startswith('#'):
        k,x=line.split('=',1); v[k]=x
state=json.loads((r/'platform/update/managed-state.json').read_text()); decision=json.loads((r/'platform/update/compatibility-decision.json').read_text())
assert v['PLATFORM_STATE_PATCH']==pid and v['PLATFORM_BASELINE_KIND']=='managed-target'
assert state['patchId']==pid and state['profile']==profile and state['compatibility']==decision
assert decision['status']=='PASS' and decision['profile']==profile
assert state['installedVersions'][component]==v[component]
PY_STATE
  export_path="$(printf '%s\n' "${apply_output}" | sed -n 's/^  Export-Pfad:[[:space:]]*//p' | tail -n 1)"; [[ -f "${export_path}" ]] || fail "closure export missing for ${profile}"
  python3 "${TARGET_ROOT}/bin/export-integrity-check.py" "${export_path}" --source-root "${TARGET_ROOT}" --require-evidence > "${WORK_ROOT}/${profile}-export-integrity.log"
}
apply_profile tooling-cutover PLATFORM_TOOLING_VERSION
[[ "$(sed -n 's/^PLATFORM_TOOLING_VERSION=//p' "${TARGET_ROOT}/platform/versions/platform.env")" == "${MASTER_TOOLING}" ]] || fail "tooling version not updated"
apply_profile core PLATFORM_CORE_VERSION
[[ "$(sed -n 's/^PLATFORM_CORE_VERSION=//p' "${TARGET_ROOT}/platform/versions/platform.env")" == "${MASTER_CORE}" ]] || fail "core version not updated"
[[ "$(sed -n 's/^PLATFORM_TOOLING_VERSION=//p' "${TARGET_ROOT}/platform/versions/platform.env")" == "${MASTER_TOOLING}" ]] || fail "core update changed tooling version"
[[ "$(wc -l < "${FULL_TEST_LOG}")" -eq 2 ]] || fail "expected two target full-test invocations"
[[ -z "$(git -C "${TARGET_ROOT}" status --porcelain --untracked-files=all)" ]] || fail "managed target must be clean after committed applies"
[[ "$(git -C "${PROJECT_ROOT}" rev-parse HEAD)" == "${SOURCE_HEAD}" ]] || fail "Springmaster HEAD changed"
[[ "$(git -C "${PROJECT_ROOT}" status --porcelain --untracked-files=all)" == "${SOURCE_STATUS}" ]] || fail "Springmaster working tree changed"
echo "PLATFORM_UPDATE_MANAGED_PROJECT_PILOT_IT=PASS"
echo "TARGET=${TARGET_NAME}"
echo "TOOLING_VERSION=${MASTER_TOOLING}"
echo "CORE_VERSION=${MASTER_CORE}"
echo "TARGET_PATH=${TARGET_ROOT}"
echo "REAL_TARGET_MUTATION=NONE"
