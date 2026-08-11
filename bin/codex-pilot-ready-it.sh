#!/usr/bin/env bash
set -Eeuo pipefail
umask 077
export LC_ALL=C
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
TMP="${ROOT}/target/codex-pilot-ready-it"
rm -rf -- "${TMP}"
mkdir -p -- "${TMP}"
trap 'if [[ "${KEEP_CODEX_READY_IT:-false}" != true ]]; then rm -rf -- "${TMP}"; fi' EXIT
python3 - "${ROOT}/src/test/resources/tooling/codex-pilot-readiness-v1/expected-cases.json" <<'PY'
import json,sys
v=json.load(open(sys.argv[1])); assert v['schemaVersion']=='springmaster.codex-pilot-readiness-fixture.v1'; assert len(v['cases'])==6
PY
FIXTURE="${TMP}/fixture"
mkdir -p "${FIXTURE}"
(
 cd "${ROOT}"
 tar --exclude=.git --exclude=target --exclude=build --exclude=tmp --exclude=exports --exclude=patches/runtime --exclude=patches/archives -cf - .
) | (cd "${FIXTURE}" && tar -xf -)
printf '%s\n' 'fixture-toolkit' > "${FIXTURE}/.cocondo/tooling/cocondo-toolkit.pyz"
python3 - "${FIXTURE}" <<'PY'
from pathlib import Path
import hashlib,json,sys
r=Path(sys.argv[1]); binary=r/'.cocondo/tooling/cocondo-toolkit.pyz'; h=hashlib.sha256(binary.read_bytes()).hexdigest()
(r/'.cocondo/tooling/cocondo-toolkit.pyz.sha256').write_text(f'{h}  cocondo-toolkit.pyz\n')
for rel,key in [('contracts/governance/tooling/patch-toolkit-activation-contract.json','runtimeSha256'),('src/test/resources/tooling/patch-toolkit-activation-v1/activation-evidence.json','runtimeSha256')]:
 p=r/rel; d=json.load(open(p)); d[key]=h; p.write_text(json.dumps(d,indent=2)+'\n')
p=r/'.cocondo/tooling/tooling.lock.json'; d=json.load(open(p)); d['sha256']=h; p.write_text(json.dumps(d,indent=2)+'\n')
PY
export HOME="${TMP}/home" XDG_CONFIG_HOME="${TMP}/xdg" GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null GIT_TEMPLATE_DIR="${TMP}/git-template" GIT_TERMINAL_PROMPT=0
mkdir -p "${HOME}" "${XDG_CONFIG_HOME}" "${GIT_TEMPLATE_DIR}"
git -C "${FIXTURE}" init -q -b main
git -C "${FIXTURE}" config user.name fixture
git -C "${FIXTURE}" config user.email fixture@example.invalid
git -C "${FIXTURE}" add .
git -C "${FIXTURE}" commit -q -m fixture

"${FIXTURE}/bin/codex-pilot-ready.sh" --project-root "${FIXTURE}" project --candidate --check --skip-self-tests > "${TMP}/positive.out"
grep -Fx 'CODEX_PILOT_READINESS=PROJECT_READY' "${TMP}/positive.out" >/dev/null
grep -Fx 'WRITABLE_CODEX_AUTHORIZED=false' "${TMP}/positive.out" >/dev/null
grep -Fx 'PILOT_WRITE_READY=false' "${TMP}/positive.out" >/dev/null

PROMOTED="${TMP}/promoted"; cp -a "${FIXTURE}" "${PROMOTED}"
python3 - "${PROMOTED}/contracts/governance/agent/codex-pilot-contract.json" <<'PY_PROMOTED'
import json,sys
p=sys.argv[1]; d=json.load(open(p,encoding="utf-8"))
d["pilot"]["currentLifecycle"]="PILOT_WRITE_READY"
d["pilot"]["cutoverLifecycle"]="PROMOTED"
d["projectReadiness"].update({"doesNotAuthorizeWritableCodex":False,"nextAction":"CODEX_PILOT_TASK","successStatus":"PILOT_WRITE_READY"})
d["confinementCalibration"]["writableCodexAuthorized"]=True
d["confinementCalibration"]["pilotWriteReady"]=True
d["writePromotion"]={
  "schemaVersion":"springmaster.codex-write-promotion.v1",
  "decision":"CODEX_CUTOVER_ACCEPTED",
  "sourceConfinementEvidenceSchemaVersion":"springmaster.codex-confinement-evidence.v2",
  "sourceConfinementEvidenceSha256":"a"*64,
  "sourceConfinementBaselineCommit":"b"*40,
  "promotedFromHead":"c"*40,
  "hostId":"d"*24,
  "acceptedPatchIds":["000212_calibration_1","000213_calibration_2"],
  "acceptedPatchCount":2,
  "evidenceStatus":"PASS",
  "writableCodexAuthorized":True,
  "pilotWriteReady":True,
  "promotionAuthority":"trusted-operator-accepted-patch",
  "decidedAt":"2026-08-10T00:00:00Z"
}
open(p,'w',encoding='utf-8').write(json.dumps(d,indent=2,sort_keys=True)+'\n')
PY_PROMOTED
git -C "${PROMOTED}" add contracts/governance/agent/codex-pilot-contract.json
git -C "${PROMOTED}" commit -q -m promoted
"${PROMOTED}/bin/codex-pilot-ready.sh" --project-root "${PROMOTED}" project --candidate --check --skip-self-tests > "${TMP}/promoted.out"
grep -Fx 'CODEX_PILOT_READINESS=PILOT_WRITE_READY' "${TMP}/promoted.out" >/dev/null
grep -Fx 'NEXT_ACTION=CODEX_PILOT_TASK' "${TMP}/promoted.out" >/dev/null
grep -Fx 'WRITABLE_CODEX_AUTHORIZED=true' "${TMP}/promoted.out" >/dev/null
grep -Fx 'PILOT_WRITE_READY=true' "${TMP}/promoted.out" >/dev/null

case_finding() {
 local name="$1" file="$2" code="$3"
 set +e
 "${file}/bin/codex-pilot-ready.sh" --project-root "${file}" project --candidate --check --skip-self-tests --out-json "${TMP}/${name}.json" >/dev/null
 local rc=$?
 set -e
 test "${rc}" -eq 1
 python3 - "${TMP}/${name}.json" "${code}" <<'PY'
import json,sys
v=json.load(open(sys.argv[1])); assert any(x['code']==sys.argv[2] for x in v['findings']),v
PY
}
MISSING="${TMP}/missing"; cp -a "${FIXTURE}" "${MISSING}"; rm "${MISSING}/PROJECT_DOCS/ADR/ADR-0015-controlled-ai-assisted-development-pilot.md"; case_finding missing "${MISSING}" REQUIRED_FILE_MISSING
INVALID="${TMP}/invalid"; cp -a "${FIXTURE}" "${INVALID}"; printf '%s\n' '{ invalid' > "${INVALID}/contracts/governance/agent/codex-pilot-contract.json"
set +e
"${INVALID}/bin/codex-pilot-ready.sh" --project-root "${INVALID}" project --candidate --check --skip-self-tests --out-json "${TMP}/invalid.json" >/dev/null
rc=$?
set -e
test "${rc}" -eq 2
python3 - "${TMP}/invalid.json" <<'PY'
import json,sys
v=json.load(open(sys.argv[1])); assert v['status']=='TOOL_ERROR' and v['toolError']['code']=='JSON_INVALID'
PY
CONF="${TMP}/confinement"; cp -a "${FIXTURE}" "${CONF}"; python3 - "${CONF}/contracts/governance/agent/codex-confinement-contract.json" <<'PY'
import json,sys
p=sys.argv[1]; d=json.load(open(p)); d['realCodexInvocationRequired']=False; open(p,'w').write(json.dumps(d)+'\n')
PY
case_finding confinement "${CONF}" CONFINEMENT_POLICY_INVALID
HOST="${TMP}/host"; cp -a "${FIXTURE}" "${HOST}"; python3 - "${HOST}/contracts/governance/agent/codex-host-qualification-contract.json" <<'PY'
import json,sys
p=sys.argv[1]; d=json.load(open(p)); d['securityBoundary']['additionalWritableRoots']=['/unsafe']; open(p,'w').write(json.dumps(d)+'\n')
PY
case_finding host "${HOST}" CONFINEMENT_POLICY_INVALID
LIVE="${TMP}/live"; cp -a "${FIXTURE}" "${LIVE}"; unset COCONDO_WORKTREE_ROOT COCONDO_AGENT_RUN_ROOT COCONDO_ARTIFACT_ROOT
set +e
"${LIVE}/bin/codex-pilot-ready.sh" --project-root "${LIVE}" project --live --check --skip-self-tests --out-json "${TMP}/live.json" >/dev/null
rc=$?
set -e
test "${rc}" -eq 1
python3 - "${TMP}/live.json" <<'PY'
import json,sys
v=json.load(open(sys.argv[1])); assert any(x['code']=='EXTERNAL_ROOT_UNSET' for x in v['findings'])
PY
printf '%s\n' 'CODEX_PILOT_READY_IT=PASS'
