#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
WORK_ROOT="${PROJECT_ROOT}/target/observability-contract-it"
rm -rf "${WORK_ROOT}"
mkdir -p "${WORK_ROOT}/repo"
cp -a "${PROJECT_ROOT}/contracts" "${WORK_ROOT}/repo/"
cp -a "${PROJECT_ROOT}/src" "${WORK_ROOT}/repo/"
"${PROJECT_ROOT}/bin/observability-contract.sh" --check --out "${WORK_ROOT}/positive.json" >/dev/null
sed -i 's/include-stacktrace: never/include-stacktrace: always/' "${WORK_ROOT}/repo/src/main/resources/application.yml"
if python3 "${PROJECT_ROOT}/bin/observability-contract.py" --root "${WORK_ROOT}/repo" --check --out "${WORK_ROOT}/negative.json" >/dev/null 2>&1; then
  echo "[ERROR] Observability contract accepted public stack traces" >&2
  exit 1
fi
grep -q 'ERROR_STACKTRACE_NOT_HARDENED' "${WORK_ROOT}/negative.json"
echo "OBSERVABILITY_CONTRACT_IT=PASS"
