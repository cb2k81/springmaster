#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
CHECKER="${SCRIPT_DIR}/core-persistence-newness-contract.py"
python3 "${CHECKER}" "${PROJECT_ROOT}" --check >/dev/null
TMP_ROOT="$(mktemp -d)"
trap 'rm -rf "${TMP_ROOT}"' EXIT
for path in \
  contracts/core/persistence-newness-contract.json \
  src/main/java/de/cocondo/system/entity/DomainEntity.java \
  src/test/java/de/cocondo/system/entity/DomainEntityPersistenceMappingTest.java; do
  mkdir -p "${TMP_ROOT}/$(dirname "${path}")"
  cp "${PROJECT_ROOT}/${path}" "${TMP_ROOT}/${path}"
done
for path in \
  PROJECT_DOCS/DEMO/CATALOGITEM_PERSISTENT_CANDIDATE_SLICE.md \
  src/test/java/de/cocondo/platform/demo/catalog/CatalogItemPersistenceContractTest.java; do
  if [[ -f "${PROJECT_ROOT}/${path}" ]]; then
    mkdir -p "${TMP_ROOT}/$(dirname "${path}")"
    cp "${PROJECT_ROOT}/${path}" "${TMP_ROOT}/${path}"
  fi
done
status="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["status"])' "${TMP_ROOT}/contracts/core/persistence-newness-contract.json")"
python3 - "${TMP_ROOT}/src/main/java/de/cocondo/system/entity/DomainEntity.java" "${status}" <<'PY'
from pathlib import Path
import sys
p=Path(sys.argv[1]); status=sys.argv[2]; s=p.read_text()
if status == 'decided':
    s=s.replace('private Long persistenceVersion = 0L;', 'private Long persistenceVersion;')
else:
    s=s.replace('private Long persistenceVersion;', 'private Long persistenceVersion = 0L;')
p.write_text(s)
PY
if python3 "${CHECKER}" "${TMP_ROOT}" --check >/dev/null 2>&1; then
  echo 'Expected partial newness transition to fail.' >&2
  exit 1
fi
cp "${PROJECT_ROOT}/src/main/java/de/cocondo/system/entity/DomainEntity.java" \
  "${TMP_ROOT}/src/main/java/de/cocondo/system/entity/DomainEntity.java"
python3 - "${TMP_ROOT}/contracts/core/persistence-newness-contract.json" <<'PY'
from pathlib import Path
import json,sys
p=Path(sys.argv[1]); d=json.loads(p.read_text()); d['status']='unknown'; p.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
PY
if python3 "${CHECKER}" "${TMP_ROOT}" --check >/dev/null 2>&1; then
  echo 'Expected unknown contract status to fail.' >&2
  exit 1
fi
echo 'CORE_PERSISTENCE_NEWNESS_CONTRACT_IT=PASS'
