#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"
WORK_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/springmaster-s01-delivery.XXXXXX")"
trap 'rm -rf "${WORK_ROOT}"' EXIT
TARGET_ROOT="${WORK_ROOT}/target"
TARGET_DIR="${WORK_ROOT}/targets"
BUILD_ROOT="${WORK_ROOT}/build"
TARGET_NAME="s01-fixture"

mkdir -p "${TARGET_ROOT}/bin" "${TARGET_ROOT}/platform/versions" "${TARGET_DIR}" "${BUILD_ROOT}"
cp "${PROJECT_ROOT}/bin/patch.py" "${TARGET_ROOT}/bin/patch.py"
cp "${PROJECT_ROOT}/bin/patch.sh" "${TARGET_ROOT}/bin/patch.sh"
cp "${PROJECT_ROOT}/platform/versions/platform.env" "${TARGET_ROOT}/platform/versions/platform.env"
chmod +x "${TARGET_ROOT}/bin/patch.py" "${TARGET_ROOT}/bin/patch.sh"
printf '%s\n' 'build/' 'exports/' 'patches/archives/' 'patches/runtime/' > "${TARGET_ROOT}/.gitignore"
printf '%s\n' \
  'PATCH_LOCAL_SCOPES=docs' \
  'PATCH_SCOPE_DOCS_PATHS=PROJECT_DOCS/**;platform/**;patches/logs/docs/**' \
  'PATCH_SCOPE_DOCS_LOG_DIR=docs' > "${TARGET_ROOT}/.env"
(
  cd "${TARGET_ROOT}"
  git init -q -b main
  git config user.name 'S01 Disposable Delivery Fixture'
  git config user.email 's01-delivery@example.invalid'
  git add .
  git commit -qm baseline
)
cat > "${TARGET_DIR}/${TARGET_NAME}.env" <<EOF
TARGET_NAME=${TARGET_NAME}
TARGET_STATUS=DISPOSABLE_FIXTURE
TARGET_PATH=${TARGET_ROOT}
TARGET_APP_NAME=${TARGET_NAME}
TARGET_BASE_PACKAGE=example.fixture
TARGET_PORT=0
TARGET_DB_NAME=fixture
TARGET_STAGE_DB_NAME=fixture_stage
TARGET_LIFECYCLE=disposable
TARGET_INITIALIZATION_ALLOWED=false
TARGET_UPDATE_ALLOWED=true
TARGET_DELIVERY_ENABLED=false
TARGET_ALLOWED_PROFILES=platform-update-doc
TARGET_NOTES=Repository-owned disposable S01 fixture.
EOF

run_update() {
  PLATFORM_UPDATE_TARGET_DIR="${TARGET_DIR}" \
  PLATFORM_UPDATE_BUILD_WORKSPACE_DIR="${BUILD_ROOT}" \
    "${PROJECT_ROOT}/bin/platform-update.sh" "$@"
}

SOURCE_HEAD_BEFORE="$(git -C "${PROJECT_ROOT}" rev-parse HEAD)"
SOURCE_STATUS_BEFORE="$(git -C "${PROJECT_ROOT}" status --porcelain=v1 --untracked-files=all)"
TARGET_HEAD_BEFORE="$(git -C "${TARGET_ROOT}" rev-parse HEAD)"
TARGET_TREE_BEFORE="$(git -C "${TARGET_ROOT}" rev-parse HEAD^{tree})"
TARGET_STATUS_BEFORE="$(git -C "${TARGET_ROOT}" status --porcelain=v1 --untracked-files=all)"

GENERATE_OUTPUT="$(run_update generate "${TARGET_NAME}" --profile platform-update-doc)"
printf '%s\n' "${GENERATE_OUTPUT}" > "${WORK_ROOT}/generate.log"
ZIP_PATH="$(printf '%s\n' "${GENERATE_OUTPUT}" | sed -n 's/^  ZIP:[[:space:]]*//p' | tail -n 1)"
REPORT_PATH="$(printf '%s\n' "${GENERATE_OUTPUT}" | sed -n 's/^  Preflight:[[:space:]]*//p' | tail -n 1)"
test -f "${ZIP_PATH}"
test -f "${REPORT_PATH}"
python3 - "${ZIP_PATH}" "${REPORT_PATH}" "${TARGET_NAME}" <<'PY'
import json,sys,zipfile
with zipfile.ZipFile(sys.argv[1]) as archive:
    manifest=json.loads(archive.read("manifest.json"))
projection=manifest["canonicalArtifactModel"]
canonical=projection["manifest"]
assert projection["adapterId"]=="springmaster.platform-update.legacy-v2-target-adapter.v1"
assert projection["selectionPolicy"]=="target-capability-only"
assert canonical["schemaVersion"]=="cocondo.patch-manifest.v5"
assert canonical["artifactId"]==manifest["artifactId"]
assert canonical["patchId"]==manifest["patchId"]
assert canonical["target"]["requiredProjectId"]==manifest["requires"]["target"]==sys.argv[3]
assert canonical["target"]["allowedScopes"]==[manifest["scope"]]
assert {op["path"]:op["beforeSha256"] for op in canonical["operations"]}==manifest["baseline"]["expectedBeforeSha256"]
assert manifest["requires"]["managedState"]["artifactId"]==manifest["artifactId"]
assert manifest["requires"]["managedState"]["patchId"]==manifest["patchId"]
assert manifest["requires"]["managedState"]["compatibility"]==manifest["requires"]["compatibility"]
report=json.load(open(sys.argv[2],encoding="utf-8"))
assert report["status"]=="PASS" and report["artifactId"]==manifest["artifactId"]
PY

run_update preflight "${TARGET_NAME}" --zip "${ZIP_PATH}" --output "${BUILD_ROOT}/target-preflight" \
  > "${WORK_ROOT}/preflight.log"
grep -q 'Status:[[:space:]]*PASSED' "${WORK_ROOT}/preflight.log"
run_update apply-plan "${TARGET_NAME}" --zip "${ZIP_PATH}" --output "${BUILD_ROOT}/apply-plan" \
  > "${WORK_ROOT}/apply-plan.log"
grep -q 'Status:[[:space:]]*REVIEW_REQUIRED' "${WORK_ROOT}/apply-plan.log"

test "$(git -C "${PROJECT_ROOT}" rev-parse HEAD)" = "${SOURCE_HEAD_BEFORE}"
test "$(git -C "${PROJECT_ROOT}" status --porcelain=v1 --untracked-files=all)" = "${SOURCE_STATUS_BEFORE}"
test "$(git -C "${TARGET_ROOT}" rev-parse HEAD)" = "${TARGET_HEAD_BEFORE}"
test "$(git -C "${TARGET_ROOT}" rev-parse HEAD^{tree})" = "${TARGET_TREE_BEFORE}"
test "$(git -C "${TARGET_ROOT}" status --porcelain=v1 --untracked-files=all)" = "${TARGET_STATUS_BEFORE}"
echo 'PLATFORM_UPDATE_DELIVERY_CONTRACT=PASS'
echo 'REGISTERED_TARGET_FALLBACK=false'
echo 'TARGET_APPLY_INVOKED=false'
