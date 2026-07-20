#!/usr/bin/env bash
set -euo pipefail
set +H

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"
SOURCE_TARGET_NAME="${1:-zbm}"
SOURCE_DESCRIPTOR="${PROJECT_ROOT}/platform/update/targets/${SOURCE_TARGET_NAME}.env"

fail() {
  echo "[FAIL] $*" >&2
  exit 1
}

[[ -f "${SOURCE_DESCRIPTOR}" ]] || fail "target descriptor missing: ${SOURCE_DESCRIPTOR}"
descriptor_value() {
  local key="$1"
  sed -n "s/^${key}=//p" "${SOURCE_DESCRIPTOR}" | head -n 1
}

TARGET_PATH_VALUE="$(descriptor_value TARGET_PATH)"
TARGET_APP_NAME_VALUE="$(descriptor_value TARGET_APP_NAME)"
TARGET_BASE_PACKAGE_VALUE="$(descriptor_value TARGET_BASE_PACKAGE)"
TARGET_PORT_VALUE="$(descriptor_value TARGET_PORT)"
TARGET_DB_NAME_VALUE="$(descriptor_value TARGET_DB_NAME)"
TARGET_STAGE_DB_NAME_VALUE="$(descriptor_value TARGET_STAGE_DB_NAME)"
SOURCE_TARGET_PATH="${2:-${TARGET_PATH_VALUE}}"
REAL_FULL_TEST="${CORE_DELIVERY_REAL_FULL_TEST:-false}"

[[ -n "${SOURCE_TARGET_PATH}" && -d "${SOURCE_TARGET_PATH}/.git" ]] || \
  fail "target Git repository missing: ${SOURCE_TARGET_PATH:-<empty>}"
[[ -z "$(git -C "${SOURCE_TARGET_PATH}" status --porcelain --untracked-files=all)" ]] || \
  fail "source target working tree must be clean"

SOURCE_HEAD_BEFORE="$(git -C "${SOURCE_TARGET_PATH}" rev-parse HEAD)"
SOURCE_LATEST_BEFORE="$(cd "${SOURCE_TARGET_PATH}" && ./bin/patch.sh show latest 2>/dev/null | sed -n 's/^Patch-ID:[[:space:]]*//p' | head -n 1 || true)"
[[ "${SOURCE_LATEST_BEFORE}" =~ ^([0-9]{6})_ ]] || \
  fail "cannot derive latest source target patch: ${SOURCE_LATEST_BEFORE}"

WORK_ROOT="$(mktemp -d)"
KEEP_WORK_ROOT="${CORE_DELIVERY_KEEP_WORK_ROOT:-false}"
cleanup_work_root() {
  local rc="$?"
  trap - EXIT
  if [[ "${rc}" -ne 0 || "${KEEP_WORK_ROOT}" == "true" ]]; then
    echo "[INFO] Core delivery work root preserved: ${WORK_ROOT}" >&2
  else
    rm -rf "${WORK_ROOT}"
  fi
  exit "${rc}"
}
trap cleanup_work_root EXIT
TARGET_COPY="${WORK_ROOT}/target"
TARGETS_DIR="${WORK_ROOT}/targets"
BUILD_DIR="${WORK_ROOT}/build"
FULL_TEST_MARKER="${WORK_ROOT}/full-test.marker"
FULL_TEST_COMMAND="${WORK_ROOT}/full-test-command.sh"
mkdir -p "${TARGETS_DIR}"

git clone --quiet --no-hardlinks "${SOURCE_TARGET_PATH}" "${TARGET_COPY}"
if [[ -f "${SOURCE_TARGET_PATH}/.env" ]]; then
  cp -a "${SOURCE_TARGET_PATH}/.env" "${TARGET_COPY}/.env"
fi
for rel in patches/archives patches/applied patches/history; do
  source_runtime="${SOURCE_TARGET_PATH}/${rel}"
  target_runtime="${TARGET_COPY}/${rel}"
  if [[ -d "${source_runtime}" ]]; then
    mkdir -p "${target_runtime}"
    cp -a "${source_runtime}/." "${target_runtime}/"
  elif [[ -e "${source_runtime}" ]]; then
    fail "source target runtime path is not a directory: ${source_runtime}"
  fi
done

TARGET_COPY_LATEST_BEFORE="$(cd "${TARGET_COPY}" && ./bin/patch.sh show latest 2>/dev/null | sed -n 's/^Patch-ID:[[:space:]]*//p' | head -n 1 || true)"
[[ "${TARGET_COPY_LATEST_BEFORE}" == "${SOURCE_LATEST_BEFORE}" ]] || \
  fail "isolated target patch registry mismatch: source=${SOURCE_LATEST_BEFORE} clone=${TARGET_COPY_LATEST_BEFORE:-<empty>}"
[[ "${TARGET_COPY_LATEST_BEFORE}" =~ ^([0-9]{6})_ ]] || \
  fail "cannot derive latest isolated target patch: ${TARGET_COPY_LATEST_BEFORE}"
EXPECTED_NUMBER="$(printf '%06d' "$((10#${BASH_REMATCH[1]} + 1))")"
EXPECTED_PATCH_ID="${EXPECTED_NUMBER}_springmaster_platform_update_core_for_${SOURCE_TARGET_NAME}"

if [[ "${REAL_FULL_TEST}" != "true" ]]; then
  cat > "${FULL_TEST_COMMAND}" <<MARKER_EOF
#!/usr/bin/env bash
set -euo pipefail
printf 'FULL_TEST_INVOKED\n' > "${FULL_TEST_MARKER}"
MARKER_EOF
  chmod +x "${FULL_TEST_COMMAND}"
  printf '\nPATCH_FULL_TEST_COMMAND=%q\n' "${FULL_TEST_COMMAND}" >> "${TARGET_COPY}/.env"
fi

cat > "${TARGETS_DIR}/${SOURCE_TARGET_NAME}.env" <<TARGET_EOF
TARGET_NAME=${SOURCE_TARGET_NAME}
TARGET_STATUS=DELIVERY_ENABLED
TARGET_PATH=${TARGET_COPY}
TARGET_APP_NAME=${TARGET_APP_NAME_VALUE:-${SOURCE_TARGET_NAME}}
TARGET_BASE_PACKAGE=${TARGET_BASE_PACKAGE_VALUE:-}
TARGET_PORT=${TARGET_PORT_VALUE:-}
TARGET_DB_NAME=${TARGET_DB_NAME_VALUE:-}
TARGET_STAGE_DB_NAME=${TARGET_STAGE_DB_NAME_VALUE:-}
TARGET_LIFECYCLE=update-enabled
TARGET_INITIALIZATION_ALLOWED=false
TARGET_UPDATE_ALLOWED=true
TARGET_DELIVERY_ENABLED=true
TARGET_ALLOWED_PROFILES=core
TARGET_NOTES=Temporary Core 0.3.6 delivery integration target.
TARGET_EOF

run_update() {
  PLATFORM_UPDATE_TARGET_DIR="${TARGETS_DIR}" \
  PLATFORM_UPDATE_BUILD_WORKSPACE_DIR="${BUILD_DIR}" \
    "${PROJECT_ROOT}/bin/platform-update.sh" "$@"
}

OUTPUT="$(run_update generate "${SOURCE_TARGET_NAME}" --profile core)"
printf '%s\n' "${OUTPUT}" > "${WORK_ROOT}/generate.log"
ZIP_PATH="$(printf '%s\n' "${OUTPUT}" | sed -n 's/^  ZIP:[[:space:]]*//p' | tail -n 1)"
REPORT_PATH="$(printf '%s\n' "${OUTPUT}" | sed -n 's/^  Preflight:[[:space:]]*//p' | tail -n 1)"
[[ -f "${ZIP_PATH}" ]] || fail "generated ZIP missing: ${ZIP_PATH}"
[[ -f "${REPORT_PATH}" ]] || fail "producer preflight report missing: ${REPORT_PATH}"
GENERATED_PATCH_ID="$(python3 - "${ZIP_PATH}" <<'PY_ID'
import json
import sys
import uuid
import zipfile
with zipfile.ZipFile(sys.argv[1]) as zf:
    manifest=json.loads(zf.read('manifest.json'))
print(manifest.get('patchId',''))
PY_ID
)"
[[ "${GENERATED_PATCH_ID}" == "${EXPECTED_PATCH_ID}" ]] || \
  fail "unexpected generated patch id: expected=${EXPECTED_PATCH_ID} actual=${GENERATED_PATCH_ID:-<empty>} sourceLatest=${SOURCE_LATEST_BEFORE} cloneLatest=${TARGET_COPY_LATEST_BEFORE}"

python3 - "${ZIP_PATH}" "${TARGET_COPY}" "${EXPECTED_PATCH_ID}" <<'PY'
import hashlib
import json
import sys
import zipfile
from pathlib import Path

zip_path=Path(sys.argv[1])
target=Path(sys.argv[2])
expected_id=sys.argv[3]
with zipfile.ZipFile(zip_path) as zf:
    manifest=json.loads(zf.read('manifest.json'))
    names=[name for name in zf.namelist() if not name.endswith('/')]
    assert manifest['schemaVersion']=='springmaster.patch-manifest.v2'
    assert manifest['id']==manifest['patchId']==expected_id, (manifest.get('id'),manifest.get('patchId'),expected_id)
    assert manifest['artifactId']==f"urn:uuid:{uuid.UUID(manifest['artifactId'].removeprefix('urn:uuid:'))}"
    assert manifest['scope']=='core'
    assert manifest['requires']['profile']=='core'
    assert manifest['requires']['target']=='zbm'
    assert manifest['requires']['masterCoreVersion']=='0.3.6'
    assert 'files/pom.xml' not in names
    assert 'files/platform/versions/platform.env' in names
    assert 'files/platform/update/managed-state.json' in names
    assert 'files/platform/update/compatibility-decision.json' in names
    for name in names:
        if name.startswith('files/src/main/java/') or name.startswith('files/src/test/java/'):
            assert '/de/cocondo/system/' in name, name
            assert '/de/cocondo/zbm/' not in name, name
            assert '/de/cocondo/platform/' not in name, name
        assert not name.startswith('files/PROJECT_DOCS/DEMO/'), name
        assert not name.startswith('files/PROJECT_DOCS/TOOLING/'), name
    ops=[]
    for name in names:
        if name.startswith('files/'):
            ops.append((name,name[6:]))
        elif name.startswith('logs/'):
            ops.append((name,'patches/logs/core/'+Path(name).name))
    expected=manifest['baseline']['expectedBeforeSha256']
    assert set(expected)=={target_path for _,target_path in ops}
    for member,target_path in ops:
        current=target/target_path
        actual=hashlib.sha256(current.read_bytes()).hexdigest() if current.is_file() else None
        assert expected[target_path]==actual, (target_path,expected[target_path],actual)
PY

run_update preflight "${SOURCE_TARGET_NAME}" --zip "${ZIP_PATH}" > "${WORK_ROOT}/preflight.log"
grep -q 'Status:[[:space:]]*PASSED' "${WORK_ROOT}/preflight.log" || fail "target dry-run did not pass"

CORE_VERSION_BEFORE="$(sed -n 's/^PLATFORM_CORE_VERSION=//p' "${TARGET_COPY}/platform/versions/platform.env")"
MASTER_CORE_VERSION="$(sed -n 's/^PLATFORM_CORE_VERSION=//p' "${PROJECT_ROOT}/platform/versions/platform.env")"
APPLY_OUTPUT="$(run_update target-apply "${SOURCE_TARGET_NAME}" --zip "${ZIP_PATH}")"
printf '%s\n' "${APPLY_OUTPUT}" > "${WORK_ROOT}/target-apply.log"
grep -q 'Status:[[:space:]]*OK' "${WORK_ROOT}/target-apply.log" || fail "target apply did not finish OK"

if [[ "${REAL_FULL_TEST}" != "true" ]]; then
  [[ -f "${FULL_TEST_MARKER}" ]] || fail "full-test invocation marker missing"
fi

LATEST_AFTER="$(cd "${TARGET_COPY}" && ./bin/patch.sh show latest | sed -n 's/^Patch-ID:[[:space:]]*//p' | head -n 1)"
[[ "${LATEST_AFTER}" == "${EXPECTED_PATCH_ID}" ]] || fail "unexpected latest patch: ${LATEST_AFTER}"
CORE_VERSION_AFTER="$(sed -n 's/^PLATFORM_CORE_VERSION=//p' "${TARGET_COPY}/platform/versions/platform.env")"
[[ "${CORE_VERSION_AFTER}" == "${MASTER_CORE_VERSION}" ]] || fail "core profile did not atomically update target Core version"
[[ "${CORE_VERSION_AFTER}" != "${CORE_VERSION_BEFORE}" || "${CORE_VERSION_BEFORE}" == "${MASTER_CORE_VERSION}" ]] || fail "core version transition was not observable"
python3 - "${TARGET_COPY}" "${EXPECTED_PATCH_ID}" <<'PY_MANAGED_CORE'
import json,sys
from pathlib import Path
root=Path(sys.argv[1]); patch_id=sys.argv[2]
state=json.loads((root/'platform/update/managed-state.json').read_text())
decision=json.loads((root/'platform/update/compatibility-decision.json').read_text())
assert state['patchId']==patch_id
assert state['profile']=='core'
assert state['platformStatePatch']==patch_id
assert state['compatibility']==decision
assert decision['status']=='PASS'
assert decision['profile']=='core'
PY_MANAGED_CORE

[[ -z "$(git -C "${TARGET_COPY}" status --porcelain --untracked-files=all)" ]] || fail "target must be clean after committed core apply"

EXPORT_PATH="$(printf '%s\n' "${APPLY_OUTPUT}" | sed -n 's/^  Export-Pfad:[[:space:]]*//p' | tail -n 1)"
[[ -f "${EXPORT_PATH}" ]] || fail "target closure export missing: ${EXPORT_PATH}"
python3 "${TARGET_COPY}/bin/export-integrity-check.py" \
  "${EXPORT_PATH}" --source-root "${TARGET_COPY}" --require-evidence \
  > "${WORK_ROOT}/export-integrity.log"

[[ "$(git -C "${SOURCE_TARGET_PATH}" rev-parse HEAD)" == "${SOURCE_HEAD_BEFORE}" ]] || \
  fail "source target HEAD changed"
[[ -z "$(git -C "${SOURCE_TARGET_PATH}" status --porcelain --untracked-files=all)" ]] || \
  fail "source target working tree changed"
SOURCE_LATEST_AFTER="$(cd "${SOURCE_TARGET_PATH}" && ./bin/patch.sh show latest | sed -n 's/^Patch-ID:[[:space:]]*//p' | head -n 1)"
[[ "${SOURCE_LATEST_AFTER}" == "${SOURCE_LATEST_BEFORE}" ]] || fail "source target latest patch changed"

echo "CORE_DELIVERY_CONTRACT=PASS"
echo "TARGET=${SOURCE_TARGET_NAME}"
echo "PATCH_ID=${EXPECTED_PATCH_ID}"
echo "REAL_FULL_TEST=${REAL_FULL_TEST}"
echo "SOURCE_TARGET_MUTATED=NO"
echo "SOURCE_LATEST_BEFORE=${SOURCE_LATEST_BEFORE}"
echo "TARGET_COPY_LATEST_BEFORE=${TARGET_COPY_LATEST_BEFORE}"
echo "TARGET_EXPORT=${EXPORT_PATH}"
