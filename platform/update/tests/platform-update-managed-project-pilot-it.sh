#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"
WORK_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/springmaster-s01-compatibility.XXXXXX")"
trap 'rm -rf "${WORK_ROOT}"' EXIT
TARGET_ROOT="${WORK_ROOT}/target"
TARGET_DIR="${WORK_ROOT}/targets"
BUILD_ROOT="${WORK_ROOT}/build"
TARGET_NAME="s01-compat"

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
  git config user.name 'S01 Disposable Compatibility Fixture'
  git config user.email 's01-compat@example.invalid'
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
TARGET_NOTES=Repository-owned disposable S01 compatibility fixture.
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
ORIGINAL_ZIP="$(printf '%s\n' "${GENERATE_OUTPUT}" | sed -n 's/^  ZIP:[[:space:]]*//p' | tail -n 1)"
test -f "${ORIGINAL_ZIP}"
PLAN_OUTPUT="$(run_update compatibility-plan "${TARGET_NAME}" --zip "${ORIGINAL_ZIP}" \
  --output "${BUILD_ROOT}/compatibility-plan")"
printf '%s\n' "${PLAN_OUTPUT}" > "${WORK_ROOT}/compatibility-plan.log"
COMPATIBILITY_ZIP="$(printf '%s\n' "${PLAN_OUTPUT}" | sed -n 's/^  Compatibility ZIP:[[:space:]]*//p' | tail -n 1)"
test -f "${COMPATIBILITY_ZIP}"
grep -q 'Status:[[:space:]]*REVIEW_REQUIRED' "${WORK_ROOT}/compatibility-plan.log"

python3 - "${ORIGINAL_ZIP}" "${COMPATIBILITY_ZIP}" "${TARGET_NAME}" <<'PY'
import json,re,sys,zipfile
def manifest(path):
    with zipfile.ZipFile(path) as archive:
        return json.loads(archive.read("manifest.json")),set(archive.namelist())
original,_=manifest(sys.argv[1])
compat,names=manifest(sys.argv[2])
canonical=compat["canonicalArtifactModel"]["manifest"]
assert compat["type"]=="platform-update-compatibility"
assert compat["schemaVersion"]=="springmaster.patch-manifest.v2"
assert re.fullmatch(r"\d{6}_springmaster_platform_update_compatibility_for_s01-compat",compat["patchId"])
assert compat["scope"]=="root"
assert compat["requires"]["target"]==canonical["target"]["requiredProjectId"]==sys.argv[3]
assert compat["requires"]["requestedPatchScope"]==original["scope"]=="docs"
assert canonical["schemaVersion"]=="cocondo.patch-manifest.v5"
assert canonical["target"]["allowedScopes"]==["root"]
assert compat["artifactId"]==canonical["artifactId"]
assert compat["patchId"]==canonical["patchId"]
assert {op["path"]:op["beforeSha256"] for op in canonical["operations"]}==compat["baseline"]["expectedBeforeSha256"]
assert any(name.startswith("files/PROJECT_DOCS/PLATFORM_UPDATES/") for name in names)
assert any(name.startswith("logs/CHANGELOG-") for name in names)
PY

run_update preflight "${TARGET_NAME}" --zip "${COMPATIBILITY_ZIP}" \
  --output "${BUILD_ROOT}/compatibility-preflight" > "${WORK_ROOT}/compatibility-preflight.log"
grep -q 'Status:[[:space:]]*PASSED' "${WORK_ROOT}/compatibility-preflight.log"

test "$(git -C "${PROJECT_ROOT}" rev-parse HEAD)" = "${SOURCE_HEAD_BEFORE}"
test "$(git -C "${PROJECT_ROOT}" status --porcelain=v1 --untracked-files=all)" = "${SOURCE_STATUS_BEFORE}"
test "$(git -C "${TARGET_ROOT}" rev-parse HEAD)" = "${TARGET_HEAD_BEFORE}"
test "$(git -C "${TARGET_ROOT}" rev-parse HEAD^{tree})" = "${TARGET_TREE_BEFORE}"
test "$(git -C "${TARGET_ROOT}" status --porcelain=v1 --untracked-files=all)" = "${TARGET_STATUS_BEFORE}"
echo 'PLATFORM_UPDATE_MANAGED_PROJECT_PILOT=PASS'
echo 'LEGACY_V2_ADAPTER=target-capability-only'
echo 'TARGET_APPLY_INVOKED=false'
