#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
WORK_ROOT="${PROJECT_ROOT}/target/db-migration-contract-it"
rm -rf "${WORK_ROOT}"
mkdir -p "${WORK_ROOT}/repo"
cp -a "${PROJECT_ROOT}/contracts" "${WORK_ROOT}/repo/"
mkdir -p "${WORK_ROOT}/repo/src/main/resources/db/changelog"
cp -a "${PROJECT_ROOT}/src/main/resources/db/changelog/." "${WORK_ROOT}/repo/src/main/resources/db/changelog/"
"${PROJECT_ROOT}/bin/db-migration-contract.sh" --check --out "${WORK_ROOT}/positive.json" >/dev/null
python3 - "${WORK_ROOT}/repo/src/main/resources/db/changelog/changes/db.changelog-0000-foundation.xml" <<'PY'
from pathlib import Path
import sys
path = Path(sys.argv[1])
text = path.read_text(encoding="utf-8")
text = text.replace('<tagDatabase tag="springmaster-foundation"/>', '<dropTable tableName="unsafe"/>')
path.write_text(text, encoding="utf-8")
PY
if python3 "${PROJECT_ROOT}/bin/db-migration-contract.py" --root "${WORK_ROOT}/repo" --check --out "${WORK_ROOT}/negative.json" >/dev/null 2>&1; then
  echo "[ERROR] Migration contract accepted destructive change without rollback" >&2
  exit 1
fi
grep -q 'DESTRUCTIVE_ROLLBACK_MISSING' "${WORK_ROOT}/negative.json"
echo "DB_MIGRATION_CONTRACT_IT=PASS"
