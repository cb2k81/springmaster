#!/usr/bin/env bash
set -Eeuo pipefail
umask 077
export LC_ALL=C
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
TMP="${ROOT}/target/codex-change-bundle-it"
rm -rf -- "${TMP}"
mkdir -p -- "${TMP}/source" "${TMP}/artifact-root"
# Keep this fixture hermetic even when the caller has configured the real
# project artifact root for governed operations. The fixture bundle must be
# validated against its own synthetic artifact root.
export COCONDO_ARTIFACT_ROOT="${TMP}/artifact-root"
trap 'rm -rf -- "${TMP}"' EXIT

REPO="${TMP}/source"
(
  cd "${REPO}"
  git init -q
  git config user.email fixture@example.invalid
  git config user.name Fixture
  git config cocondo.artifactRoot "${TMP}/artifact-root"
  mkdir -p src/test/fixture
  printf 'BASE\n' > src/test/fixture/value.txt
  git add .
  git commit -qm baseline
)
BASE="$(git -C "${REPO}" rev-parse HEAD)"
TASK_ID="CODEX-BUNDLE-FIXTURE-001"
CONTRACT="${TMP}/task-contract.json"
python3 - "${CONTRACT}" "${BASE}" "${TASK_ID}" <<'PY'
import json,sys
path,base,task=sys.argv[1:]
value={
 'schemaVersion':'springmaster.agent-task.v2','taskId':task,'pilotId':'springmaster-codex-pilot-v1','repositoryId':'springmaster','mode':'implementation','baseCommit':base,'integrationBranch':'main','riskClass':'low','changeClasses':['fixture','test'],
 'allowedPaths':['src/test/fixture/value.txt','src/test/fixture/new.txt'],'forbiddenPaths':['.git/**'],
 'limits':{'maxChangedFiles':2,'maxNetAddedBytes':4096},'capabilities':{'mayModifyTests':True,'mayModifyGovernance':False,'mayModifyContracts':False,'mayCommit':False,'mayPush':False,'network':'disabled'},
 'qualificationCommands':[{'id':'diff-check','argv':['git','diff','--check'],'timeoutSeconds':30}],
 'requiredEvidence':['task-contract'],'completionCriteria':{'postcheckPass':True,'allQualificationCommandsPass':True,'requiredEvidenceComplete':True,'invocationRecordRequired':True,'explicitCleanupDisposition':True}
}
open(path,'w').write(json.dumps(value,indent=2,sort_keys=True)+'\n')
PY

make_bundle() {
  local output="$1"
  local task="$2"
  local source_hash="$3"
  local path_override="${4:-src/test/fixture/value.txt}"
  python3 - "${output}" "${BASE}" "${task}" "${source_hash}" "${path_override}" <<'PY'
import hashlib,json,sys,zipfile
out,base,task,source,path=sys.argv[1:]
payload=b'TARGET\n'
manifest={'schemaVersion':'springmaster.codex-change-bundle.v1','bundleId':'fixture-bundle-001','taskId':task,'repositoryId':'springmaster','baseCommit':base,'operations':[
 {'path':path,'operation':'replace','sourceSha256':source,'targetSha256':hashlib.sha256(payload).hexdigest(),'mode':'100644'},
 {'path':'src/test/fixture/new.txt','operation':'create','sourceSha256':None,'targetSha256':hashlib.sha256(b'NEW\n').hexdigest(),'mode':'100644'}
]}
with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED) as z:
 z.writestr('manifest.json',json.dumps(manifest,sort_keys=True,separators=(',',':'))+'\n')
 z.writestr('payload/'+path,payload)
 z.writestr('payload/src/test/fixture/new.txt',b'NEW\n')
PY
}

SOURCE_HASH="$(sha256sum "${REPO}/src/test/fixture/value.txt" | awk '{print $1}')"
BUNDLE="${TMP}/artifact-root/fixture.zip"
make_bundle "${BUNDLE}" "${TASK_ID}" "${SOURCE_HASH}"

git -C "${REPO}" checkout -q --detach "${BASE}"
(
  cd "${REPO}"
  SPRINGMASTER_CODEX_CHANGE_BUNDLE="${BUNDLE}" \
  SPRINGMASTER_AGENT_TASK_CONTRACT="${CONTRACT}" \
  SPRINGMASTER_AGENT_TASK_ID="${TASK_ID}" \
  "${ROOT}/bin/codex-change-bundle.sh" --project-root "${REPO}" --format json apply > "${TMP}/positive.json"
)
grep -F '"status": "APPLIED"' "${TMP}/positive.json" >/dev/null
test "$(cat "${REPO}/src/test/fixture/value.txt")" = TARGET
test "$(cat "${REPO}/src/test/fixture/new.txt")" = NEW

(
  cd "${REPO}"
  SPRINGMASTER_CODEX_CHANGE_BUNDLE="${BUNDLE}" SPRINGMASTER_AGENT_TASK_CONTRACT="${CONTRACT}" SPRINGMASTER_AGENT_TASK_ID="${TASK_ID}" \
  "${ROOT}/bin/codex-change-bundle.sh" --project-root "${REPO}" --format json apply > "${TMP}/idempotent.json"
)
grep -F '"status": "ALREADY_APPLIED"' "${TMP}/idempotent.json" >/dev/null

git -C "${REPO}" reset -q --hard "${BASE}"
rm -f "${REPO}/src/test/fixture/new.txt"
printf 'DRIFT\n' > "${REPO}/src/test/fixture/value.txt"
set +e
(
  cd "${REPO}"
  SPRINGMASTER_CODEX_CHANGE_BUNDLE="${BUNDLE}" SPRINGMASTER_AGENT_TASK_CONTRACT="${CONTRACT}" SPRINGMASTER_AGENT_TASK_ID="${TASK_ID}" \
  "${ROOT}/bin/codex-change-bundle.sh" --project-root "${REPO}" --format json apply > "${TMP}/drift.json"
)
RC=$?
set -e
test "${RC}" -eq 2
grep -F 'BUNDLE_SOURCE_STATE_MISMATCH' "${TMP}/drift.json" >/dev/null

git -C "${REPO}" reset -q --hard "${BASE}"
rm -f "${REPO}/src/test/fixture/new.txt"
OUTSIDE="${TMP}/outside.zip"
cp "${BUNDLE}" "${OUTSIDE}"
set +e
(
  cd "${REPO}"
  SPRINGMASTER_CODEX_CHANGE_BUNDLE="${OUTSIDE}" SPRINGMASTER_AGENT_TASK_CONTRACT="${CONTRACT}" SPRINGMASTER_AGENT_TASK_ID="${TASK_ID}" \
  "${ROOT}/bin/codex-change-bundle.sh" --project-root "${REPO}" --format json apply > "${TMP}/outside.json"
)
RC=$?
set -e
test "${RC}" -eq 2
grep -F 'BUNDLE_OUTSIDE_ARTIFACT_ROOT' "${TMP}/outside.json" >/dev/null

BAD="${TMP}/artifact-root/bad-path.zip"
make_bundle "${BAD}" "${TASK_ID}" "${SOURCE_HASH}" 'PROJECT_DOCS/forbidden.md'
set +e
(
  cd "${REPO}"
  SPRINGMASTER_CODEX_CHANGE_BUNDLE="${BAD}" SPRINGMASTER_AGENT_TASK_CONTRACT="${CONTRACT}" SPRINGMASTER_AGENT_TASK_ID="${TASK_ID}" \
  "${ROOT}/bin/codex-change-bundle.sh" --project-root "${REPO}" --format json apply > "${TMP}/bad-path.json"
)
RC=$?
set -e
test "${RC}" -eq 2
grep -F 'BUNDLE_PATH_OUTSIDE_TASK_SCOPE' "${TMP}/bad-path.json" >/dev/null

printf '%s\n' 'CODEX_CHANGE_BUNDLE_IT=PASS'
