#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"
WORK_ROOT="$(mktemp -d)"
trap 'rm -rf "${WORK_ROOT}"' EXIT
TARGET_ROOT="${WORK_ROOT}/target"
OUTPUT_ROOT="${WORK_ROOT}/output"
mkdir -p "${TARGET_ROOT}/platform/versions"
cat > "${TARGET_ROOT}/platform/versions/platform.env" <<'EOF'
PLATFORM_NAME=managed-fixture
PLATFORM_VERSION=0.15.0-foundation
PLATFORM_CORE_VERSION=0.3.6
PLATFORM_TOOLING_VERSION=0.5.0
PLATFORM_DEMO_VERSION=0.0.0
PLATFORM_BASE_PACKAGE=de.cocondo.fixture
EOF
ARTIFACT_ID=urn:uuid:11111111-1111-4111-8111-111111111111
PATCH_ID=000002_springmaster_platform_update_core_for_managed-fixture
python3 "${PROJECT_ROOT}/platform/update/tools/target-managed-state.py" synthesize \
  --target-root "${TARGET_ROOT}" \
  --output-root "${OUTPUT_ROOT}" \
  --target-name managed-fixture \
  --profile core \
  --artifact-id "${ARTIFACT_ID}" \
  --patch-id "${PATCH_ID}" \
  --master-env "${PROJECT_ROOT}/platform/versions/platform.env" \
  --rules "${PROJECT_ROOT}/platform/update/rules/profiles.json" >/dev/null
cp -a "${OUTPUT_ROOT}/." "${TARGET_ROOT}/"
python3 "${PROJECT_ROOT}/platform/update/tools/target-managed-state.py" verify \
  --target-root "${TARGET_ROOT}" \
  --target-name managed-fixture \
  --profile core \
  --artifact-id "${ARTIFACT_ID}" \
  --patch-id "${PATCH_ID}" >/dev/null
CORE_EXPECTED="$(sed -n 's/^PLATFORM_CORE_VERSION=//p' "${PROJECT_ROOT}/platform/versions/platform.env")"
grep -Fxq "PLATFORM_CORE_VERSION=${CORE_EXPECTED}" "${TARGET_ROOT}/platform/versions/platform.env"
grep -Fxq 'PLATFORM_TOOLING_VERSION=0.5.0' "${TARGET_ROOT}/platform/versions/platform.env"
grep -Fxq "PLATFORM_STATE_PATCH=${PATCH_ID}" "${TARGET_ROOT}/platform/versions/platform.env"
grep -Fxq 'PLATFORM_BASELINE_KIND=managed-target' "${TARGET_ROOT}/platform/versions/platform.env"
python3 - "${TARGET_ROOT}/platform/update/managed-state.json" <<'PY'
import json,sys
state=json.load(open(sys.argv[1],encoding='utf-8'))
assert state['schemaVersion']=='springmaster.managed-target-state.v1'
assert state['updatedComponents']==['PLATFORM_CORE_VERSION']
assert state['installedVersions']['PLATFORM_TOOLING_VERSION']=='0.5.0'
PY
echo "PLATFORM_UPDATE_MANAGED_STATE_IT=PASS"
