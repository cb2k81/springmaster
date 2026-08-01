#!/usr/bin/env bash
set -Eeuo pipefail
umask 077
export LC_ALL=C
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
TMP="${ROOT}/target/codex-calibration-it"
rm -rf -- "${TMP}"
mkdir -p -- "${TMP}/source"
trap 'rm -rf -- "${TMP}"' EXIT
BASE="$(git -C "${ROOT}" rev-parse HEAD)"
PLAN="${TMP}/plan"
"${ROOT}/bin/codex-calibration.sh" materialize --out "${PLAN}" --baseline "${BASE}" >/dev/null
python3 - "${PLAN}" "${BASE}" <<'PY'
import json,sys
from pathlib import Path
root=Path(sys.argv[1]); base=sys.argv[2]
p=json.load(open(root/'calibration-plan.json'))
assert p['status']=='MATERIALIZED' and p['taskCount']==3 and p['implementationTaskCount']==2 and p['baselineCommit']==base
modes=[json.load(open(root/x['task']['path']))['mode'] for x in p['tasks']]
assert modes==['analysis','implementation','implementation']
analysis=json.load(open(root/p['tasks'][0]['task']['path']))
assert analysis['allowedPaths']==['src/test/resources/tooling/codex-calibration-v1/**']
assert analysis['limits']=={'maxChangedFiles':0,'maxNetAddedBytes':0}
assert [x['id'] for x in analysis['qualificationCommands']]==['diff-check']
assert json.load(open(root/p['tasks'][1]['task']['path']))['allowedPaths']==['src/test/resources/tooling/codex-calibration-v1/task-1.txt']
assert json.load(open(root/p['tasks'][2]['task']['path']))['allowedPaths']==['src/test/resources/tooling/codex-calibration-v1/task-2.txt']
assert (root/p['tasks'][1]['prompt']['path']).read_text().startswith('Run exactly ./bin/codex-change-bundle.sh apply.')
assert (root/p['tasks'][2]['prompt']['path']).read_text().startswith('Run exactly ./bin/codex-change-bundle.sh apply.')
PY
for task in "${PLAN}"/codex-calibration-*.json; do
  "${ROOT}/bin/agent-task.sh" validate "${task}" >/dev/null
done

python3 - "${TMP}/source" "${BASE}" <<'PY'
from pathlib import Path
import hashlib,json,sys
r=Path(sys.argv[1]); base=sys.argv[2]
def write(name,value):
 p=r/name; p.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n'); return p
def sh(p): return hashlib.sha256(p.read_bytes()).hexdigest()
host_probe=write('host-probe.json',{'status':'PASS'})
host_inspect=write('host-inspect.json',{'status':'PASS'})
host_analysis=write('host-analysis.json',{'status':'PASS'})
host=write('host.json',{
 'schemaVersion':'springmaster.codex-host-qualification-evidence.v1','status':'PASS','hostId':'fixture-host','baselineCommit':base,
 'portable':False,'realCodex':True,'probeCount':20,'inspect':{'path':str(host_inspect),'sha256':sh(host_inspect)},
 'mechanicalProbes':{'path':str(host_probe),'sha256':sh(host_probe)},'analysisInvocation':{'path':str(host_analysis),'sha256':sh(host_analysis)},
 'writableCodexAuthorized':False,'pilotWriteReady':False
})
analysis=write('analysis.json',{'operation':'invoke','status':'PASS','taskMode':'analysis','hostId':'fixture-host','baselineCommit':base,'codexCliVersion':'fixture-1','model':'fixture-model'})
for i in (1,2):
 write(f'inv{i}.json',{'operation':'invoke','status':'PASS','taskMode':'implementation','hostId':'fixture-host','baselineCommit':base,'codexCliVersion':'fixture-1','model':'fixture-model'})
 write(f'final{i}.json',{'status':'QUALIFIED','taskId':f'TASK-{i}'})
 patch=r/f'handoff{i}.patch'; patch.write_text(f'diff --git a/task-{i} b/task-{i}\n')
 write(f'handoff{i}.json',{'schemaVersion':'springmaster.agent-task-patch-handoff.v1','status':'VERIFIED','patchId':None,'deliveryId':None,'integrationAuthorized':False,'canonicalPatchArtifact':False,'isolatedApplyCheck':'PASS','patch':{'path':patch.name,'sha256':sh(patch)}})
 write(f'dry{i}.json',{'status':'DRY_RUN_SUCCEEDED','runId':f'dry-{i}'})
 write(f'accept{i}.json',{'schemaVersion':'cocondo.patch-acceptance.v2','status':'SUCCEEDED','patchId':f'00030{i}_calibration_{i}'})
manifest={
 'schemaVersion':'springmaster.codex-calibration-assembly.v1','hostQualification':'host.json','analysisInvocation':'analysis.json',
 'hostState':{'integrationStatusBefore':'','integrationStatusAfter':'','integrationHeadBefore':base,'integrationHeadAfter':'f'*40,'canonicalAcceptOnly':True,'unauthorizedIntegrationMutation':False,'unauthorizedGitCommonMutation':False}
}
for i in (1,2):
 manifest.update({f'implementation{i}Invocation':f'inv{i}.json',f'implementation{i}FinalResult':f'final{i}.json',f'implementation{i}Handoff':f'handoff{i}.json',f'implementation{i}DryRun':f'dry{i}.json',f'implementation{i}Acceptance':f'accept{i}.json'})
write('assembly.json',manifest)
PY
OUT="${TMP}/assembled"
"${ROOT}/bin/codex-calibration.sh" assemble --manifest "${TMP}/source/assembly.json" --out "${OUT}" >/dev/null
"${ROOT}/bin/codex-confinement-check.sh" --project-root "${ROOT}" verify --evidence "${OUT}" --candidate --check > "${TMP}/check.out"
grep -F 'CODEX_CONFINEMENT_STATUS=PASS' "${TMP}/check.out" >/dev/null
grep -F 'WRITABLE_CODEX_AUTHORIZED=false' "${TMP}/check.out" >/dev/null

# Fail closed when accepted patch identities are not distinct.
rm -rf "${OUT}"
python3 - "${TMP}/source/accept2.json" <<'PY'
import json,sys
p=sys.argv[1]; d=json.load(open(p)); d['patchId']='000301_calibration_1'; open(p,'w').write(json.dumps(d)+'\n')
PY
set +e
"${ROOT}/bin/codex-calibration.sh" assemble --manifest "${TMP}/source/assembly.json" --out "${OUT}" > "${TMP}/negative.out"
rc=$?
set -e
test "${rc}" -eq 2
grep -F 'ERROR_CODE=ACCEPTED_PATCH_ID_INVALID' "${TMP}/negative.out" >/dev/null
printf '%s\n' 'CODEX_CALIBRATION_IT=PASS'
