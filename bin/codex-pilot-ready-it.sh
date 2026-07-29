#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
EXPECTED_CASES="${PROJECT_ROOT}/src/test/resources/tooling/codex-pilot-readiness-v1/expected-cases.json"
TMP_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/codex-pilot-ready-it.XXXXXX")"
CURRENT_STEP=bootstrap
cleanup() {
  local rc=$?
  trap - EXIT
  if [[ "${rc}" -ne 0 ]]; then
    printf '%s\n' 'CODEX_PILOT_READY_IT=FAILED' "FAILED_STEP=${CURRENT_STEP}" "FIXTURE_ROOT=${TMP_ROOT}" >&2
  fi
  rm -rf "${TMP_ROOT}"
  exit "${rc}"
}
trap cleanup EXIT

python3 - "${EXPECTED_CASES}" <<'PY'
import json, sys
from pathlib import Path
value=json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
assert value['schemaVersion']=='springmaster.codex-pilot-readiness-fixture.v1'
assert [case['expectedExit'] for case in value['cases']] == [0,1,2,1]
PY

CURRENT_STEP=positive-candidate
POSITIVE_OUT="${TMP_ROOT}/positive.out"
"${PROJECT_ROOT}/bin/codex-pilot-ready.sh" project --candidate --check --skip-self-tests > "${POSITIVE_OUT}"
grep -Fx 'CODEX_PILOT_READINESS=PROJECT_READY' "${POSITIVE_OUT}" >/dev/null
grep -Fx 'NEXT_ACTION=CODEX_CALIBRATION' "${POSITIVE_OUT}" >/dev/null
grep -Fx 'WRITABLE_CODEX_AUTHORIZED=false' "${POSITIVE_OUT}" >/dev/null

CURRENT_STEP=fixture-copy
FIXTURE="${TMP_ROOT}/fixture"
mkdir -p "${FIXTURE}"
(
  cd "${PROJECT_ROOT}"
  tar \
    --exclude=.git \
    --exclude=target \
    --exclude=build \
    --exclude=tmp \
    --exclude=exports \
    --exclude=patches/runtime \
    --exclude=patches/archives \
    --exclude=patches/logs/validation \
    --exclude=patches/logs/accept \
    -cf - .
) | (cd "${FIXTURE}" && tar -xf -)
export HOME="${TMP_ROOT}/home"
export XDG_CONFIG_HOME="${TMP_ROOT}/xdg-config"
export GIT_CONFIG_NOSYSTEM=1
export GIT_CONFIG_GLOBAL=/dev/null
export GIT_TEMPLATE_DIR="${TMP_ROOT}/git-template"
export GIT_TERMINAL_PROMPT=0
mkdir -p "${HOME}" "${XDG_CONFIG_HOME}" "${GIT_TEMPLATE_DIR}"
git -c init.defaultRefFormat=files -C "${FIXTURE}" init -q -b main
git -C "${FIXTURE}" config user.email codex-ready@example.invalid
git -C "${FIXTURE}" config user.name codex-pilot-ready-it
git -C "${FIXTURE}" add .
git -C "${FIXTURE}" commit -q -m fixture

CURRENT_STEP=version-closure-project-env
ENV_DRIFT="${TMP_ROOT}/env-drift"
cp -a "${FIXTURE}" "${ENV_DRIFT}"
sed -i 's/^CPATCH_TOOLKIT_VERSION=.*/CPATCH_TOOLKIT_VERSION=9.9.9/' "${ENV_DRIFT}/.cocondo/tooling/project.env"
set +e
"${ENV_DRIFT}/bin/codex-pilot-ready.sh" --project-root "${ENV_DRIFT}" project --candidate --check --skip-self-tests \
  --out-json "${TMP_ROOT}/env-drift.json" >/dev/null
RC=$?
set -e
test "${RC}" -eq 1
python3 - "${TMP_ROOT}/env-drift.json" <<'PYCHECK'
import json, sys
from pathlib import Path
value=json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
item=next(x for x in value['findings'] if x['code']=='CPATCH_CONFIG_INVALID' and x.get('details',{}).get('key')=='CPATCH_TOOLKIT_VERSION')
assert item['details']['expected']=='1.1.2', item
assert item['details']['actual']=='9.9.9', item
PYCHECK

CURRENT_STEP=version-closure-lock
LOCK_DRIFT="${TMP_ROOT}/lock-drift"
cp -a "${FIXTURE}" "${LOCK_DRIFT}"
python3 - "${LOCK_DRIFT}/.cocondo/tooling/tooling.lock.json" <<'PYCHECK'
import json, sys
from pathlib import Path
path=Path(sys.argv[1])
value=json.loads(path.read_text(encoding='utf-8'))
value['toolkitVersion']='9.9.9'
path.write_text(json.dumps(value,indent=2)+"\n",encoding='utf-8')
PYCHECK
set +e
"${LOCK_DRIFT}/bin/codex-pilot-ready.sh" --project-root "${LOCK_DRIFT}" project --candidate --check --skip-self-tests \
  --out-json "${TMP_ROOT}/lock-drift.json" >/dev/null
RC=$?
set -e
test "${RC}" -eq 1
python3 - "${TMP_ROOT}/lock-drift.json" <<'PYCHECK'
import json, sys
from pathlib import Path
value=json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
assert any(x['code']=='CPATCH_VERSION_CLOSURE_INVALID' and x.get('details',{}).get('source')=='.cocondo/tooling/tooling.lock.json' for x in value['findings']), value
PYCHECK

CURRENT_STEP=version-closure-runtime
RUNTIME_DRIFT="${TMP_ROOT}/runtime-drift"
cp -a "${FIXTURE}" "${RUNTIME_DRIFT}"
printf 'drift' >> "${RUNTIME_DRIFT}/.cocondo/tooling/cocondo-toolkit.pyz"
set +e
"${RUNTIME_DRIFT}/bin/codex-pilot-ready.sh" --project-root "${RUNTIME_DRIFT}" project --candidate --check --skip-self-tests \
  --out-json "${TMP_ROOT}/runtime-drift.json" >/dev/null
RC=$?
set -e
test "${RC}" -eq 1
python3 - "${TMP_ROOT}/runtime-drift.json" <<'PYCHECK'
import json, sys
from pathlib import Path
value=json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
assert any(x['code']=='CPATCH_VERSION_CLOSURE_INVALID' and x.get('details',{}).get('source')=='.cocondo/tooling/cocondo-toolkit.pyz' for x in value['findings']), value
PYCHECK

CURRENT_STEP=missing-source-finding
MISSING="${TMP_ROOT}/missing"
cp -a "${FIXTURE}" "${MISSING}"
rm -f "${MISSING}/PROJECT_DOCS/ADR/ADR-0015-controlled-ai-assisted-development-pilot.md"
set +e
"${MISSING}/bin/codex-pilot-ready.sh" --project-root "${MISSING}" project --candidate --check --skip-self-tests \
  --out-json "${TMP_ROOT}/missing.json" >/dev/null
RC=$?
set -e
test "${RC}" -eq 1
python3 - "${TMP_ROOT}/missing.json" <<'PY'
import json, sys
from pathlib import Path
value=json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
assert value['status']=='FINDINGS', value
assert any(item['code']=='REQUIRED_FILE_MISSING' for item in value['findings']), value
PY

CURRENT_STEP=invalid-json-tool-error
INVALID="${TMP_ROOT}/invalid"
cp -a "${FIXTURE}" "${INVALID}"
printf '%s\n' '{ invalid' > "${INVALID}/contracts/governance/agent/codex-pilot-contract.json"
set +e
"${INVALID}/bin/codex-pilot-ready.sh" --project-root "${INVALID}" project --candidate --check --skip-self-tests \
  --out-json "${TMP_ROOT}/invalid.json" >/dev/null
RC=$?
set -e
test "${RC}" -eq 2
python3 - "${TMP_ROOT}/invalid.json" <<'PY'
import json, sys
from pathlib import Path
value=json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
assert value['status']=='TOOL_ERROR', value
assert value['toolError']['code']=='JSON_INVALID', value
PY

CURRENT_STEP=live-roots-finding
LIVE="${TMP_ROOT}/live"
cp -a "${FIXTURE}" "${LIVE}"
unset COCONDO_WORKTREE_ROOT COCONDO_AGENT_RUN_ROOT COCONDO_ARTIFACT_ROOT
# The exported fixture intentionally has no toolkit binary. Create a fixture-only
# placeholder so this case isolates the external-root findings.
touch "${LIVE}/.cocondo/tooling/cocondo-toolkit.pyz"
set +e
"${LIVE}/bin/codex-pilot-ready.sh" --project-root "${LIVE}" project --live --check --skip-self-tests \
  --out-json "${TMP_ROOT}/live.json" >/dev/null
RC=$?
set -e
test "${RC}" -eq 1
python3 - "${TMP_ROOT}/live.json" <<'PY'
import json, sys
from pathlib import Path
value=json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
assert value['status']=='FINDINGS', value
assert any(item['code']=='EXTERNAL_ROOT_UNSET' for item in value['findings']), value
PY

printf '%s\n' 'CODEX_PILOT_READY_IT=PASS'
