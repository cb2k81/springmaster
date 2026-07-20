#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
RUN_DIR="${PROJECT_ROOT}/build/documentation-gate-it/$(date +%Y%m%d_%H%M%S)_$$"
FIXTURE="${RUN_DIR}/fixture"
mkdir -p "${FIXTURE}/PROJECT_DOCS/TOOLING" "${FIXTURE}/bin"
cp "${SCRIPT_DIR}/documentation-gate.py" "${FIXTURE}/bin/documentation-gate.py"
printf '%s\n' '{"paths":["PROJECT_DOCS/legacy.md"]}' > "${FIXTURE}/PROJECT_DOCS/TOOLING/documentation-transition-baseline.json"
printf '# Legacy\n' > "${FIXTURE}/PROJECT_DOCS/legacy.md"
cat > "${FIXTURE}/PROJECT_DOCS/new.md" <<'DOC'
---
documentType: guide
status: active
scope: fixture
owner: test
validFrom: 2026-07-20
supersedes: none
---
# New
DOC
cat > "${FIXTURE}/PROJECT_DOCS/index.md" <<'DOC'
---
documentType: governance
status: active
scope: fixture
owner: test
validFrom: 2026-07-20
supersedes: none
---
# Index
- `PROJECT_DOCS/legacy.md`
- `PROJECT_DOCS/new.md`
DOC
python3 "${FIXTURE}/bin/documentation-gate.py" --root "${FIXTURE}" --out "${RUN_DIR}/pass.json" --check >/dev/null
printf '# Missing metadata\n' > "${FIXTURE}/PROJECT_DOCS/bad.md"
if python3 "${FIXTURE}/bin/documentation-gate.py" --root "${FIXTURE}" --out "${RUN_DIR}/fail.json" --check >/dev/null 2>&1; then
  echo 'ERROR: documentation gate accepted a new file without metadata' >&2
  exit 1
fi
grep -q 'NEW_DOCUMENT_METADATA_INVALID' "${RUN_DIR}/fail.json"
printf 'DOCUMENTATION_GATE_IT=PASS\n'
