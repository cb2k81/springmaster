#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"
TOOL="${PROJECT_ROOT}/platform/update/tools/compatibility-matrix.py"
MATRIX="${PROJECT_ROOT}/platform/update/compatibility/platform-compatibility-matrix.json"
MASTER="${PROJECT_ROOT}/platform/versions/platform.env"
WORK_ROOT="$(mktemp -d)"
trap 'rm -rf "${WORK_ROOT}"' EXIT
python3 "${TOOL}" --matrix "${MATRIX}" validate >/dev/null
cat > "${WORK_ROOT}/n-minus-one.env" <<'EOF'
PLATFORM_CORE_VERSION=0.3.6
PLATFORM_TOOLING_VERSION=0.5.0
EOF
python3 "${TOOL}" --matrix "${MATRIX}" check --profile core --target-env "${WORK_ROOT}/n-minus-one.env" --master-env "${MASTER}" >/dev/null
cat > "${WORK_ROOT}/too-old.env" <<'EOF'
PLATFORM_CORE_VERSION=0.3.5
EOF
if python3 "${TOOL}" --matrix "${MATRIX}" check --profile core --target-env "${WORK_ROOT}/too-old.env" --master-env "${MASTER}" >/dev/null 2>&1; then
  echo '[FAIL] too-old Core source was accepted' >&2
  exit 1
fi
cat > "${WORK_ROOT}/downgrade.env" <<'EOF'
PLATFORM_CORE_VERSION=0.99.0
EOF
if python3 "${TOOL}" --matrix "${MATRIX}" check --profile core --target-env "${WORK_ROOT}/downgrade.env" --master-env "${MASTER}" >/dev/null 2>&1; then
  echo '[FAIL] downgrade source was accepted' >&2
  exit 1
fi
cat > "${WORK_ROOT}/missing.env" <<'EOF'
PLATFORM_CORE_VERSION=0.3.6
EOF
python3 "${TOOL}" --matrix "${MATRIX}" check --profile defaults --target-env "${WORK_ROOT}/missing.env" --master-env "${MASTER}" --json | grep -q '"sourceAssumed": true'
if python3 "${TOOL}" --matrix "${MATRIX}" check --profile tooling --target-env "${WORK_ROOT}/missing.env" --master-env "${MASTER}" >/dev/null 2>&1; then
  echo '[FAIL] missing mandatory tooling source version was accepted' >&2
  exit 1
fi
echo 'PLATFORM_UPDATE_COMPATIBILITY_MATRIX_IT=PASS'
