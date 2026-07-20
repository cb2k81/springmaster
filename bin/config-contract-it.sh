#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
WORK_ROOT="${PROJECT_ROOT}/target/config-contract-it"
rm -rf "${WORK_ROOT}"
mkdir -p "${WORK_ROOT}/repo"
cp -a "${PROJECT_ROOT}/contracts" "${WORK_ROOT}/repo/"
cp -a "${PROJECT_ROOT}/PROJECT_DOCS" "${WORK_ROOT}/repo/"
cp -a "${PROJECT_ROOT}/bin" "${WORK_ROOT}/repo/"
cp -a "${PROJECT_ROOT}/src" "${WORK_ROOT}/repo/"
cp "${PROJECT_ROOT}/.env.example" "${WORK_ROOT}/repo/.env.example"
"${PROJECT_ROOT}/bin/config-contract.sh" --check --out "${WORK_ROOT}/positive.json" >/dev/null
printf '\nAPP_UNKNOWN=value\n' >> "${WORK_ROOT}/repo/.env.example"
if python3 "${WORK_ROOT}/repo/bin/config-contract.py" --root "${WORK_ROOT}/repo" --check --out "${WORK_ROOT}/negative.json" >/dev/null 2>&1; then
  echo "[ERROR] Configuration contract accepted an undeclared variable" >&2
  exit 1
fi
grep -q 'VARIABLE_UNDECLARED' "${WORK_ROOT}/negative.json"
echo "CONFIG_CONTRACT_IT=PASS"
