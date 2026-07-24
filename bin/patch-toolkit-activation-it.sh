#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
WORK_ROOT="${PROJECT_ROOT}/target/patch-toolkit-activation-it"
FIXTURE="${WORK_ROOT}/repo"

rm -rf "${WORK_ROOT}"
mkdir -p "${FIXTURE}"

"${PROJECT_ROOT}/bin/patch-toolkit-activation.sh" \
  --check \
  --out "${WORK_ROOT}/positive.json" \
  >/dev/null

"${PROJECT_ROOT}/bin/cpatch" workspace --help >/dev/null

for path in \
  .cocondo/tooling/project.env \
  .cocondo/tooling/tooling.lock.json \
  .cocondo/tooling/cocondo-toolkit.pyz \
  .cocondo/tooling/cocondo-toolkit.pyz.sha256 \
  platform/versions/platform.env \
  contracts/governance/tooling/patch-toolkit-activation-contract.json \
  src/test/resources/tooling/patch-toolkit-activation-v1/activation-evidence.json \
  PROJECT_DOCS/TOOLING/COCONDO_PATCH_TOOLKIT_ACTIVATION_REPORT.md \
  AGENTS.md \
  pom.xml \
  bin/cpatch \
  bin/patch.sh \
  bin/patch.py \
  bin/patch-toolkit-activation.py
 do
  mkdir -p "${FIXTURE}/$(dirname "${path}")"
  cp "${PROJECT_ROOT}/${path}" "${FIXTURE}/${path}"
 done

python3 - "${FIXTURE}/.cocondo/tooling/project.env" <<'PY'
from pathlib import Path
import sys
path = Path(sys.argv[1])
text = path.read_text(encoding="utf-8")
text = text.replace("CPATCH_REQUIRE_WORKTREE=true", "CPATCH_REQUIRE_WORKTREE=false")
path.write_text(text, encoding="utf-8")
PY

if python3 "${FIXTURE}/bin/patch-toolkit-activation.py" \
  --root "${FIXTURE}" \
  --check \
  --out "${WORK_ROOT}/negative.json" \
  >/dev/null 2>&1
then
  echo "[ERROR] Activation check accepted disabled worktree enforcement" >&2
  exit 1
fi

grep -q 'PROJECT_ENV_MISMATCH' "${WORK_ROOT}/negative.json"

set +e
LEGACY_OUTPUT="$("${PROJECT_ROOT}/bin/patch.sh" accept /nonexistent/patch.zip 2>&1)"
LEGACY_STATUS=$?
set -e

test "${LEGACY_STATUS}" -eq 78
printf '%s\n' "${LEGACY_OUTPUT}" | grep -q 'LEGACY_PATCH_MUTATION_DISABLED'

echo "PATCH_TOOLKIT_ACTIVATION_IT=PASS"
