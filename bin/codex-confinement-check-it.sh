#!/usr/bin/env bash
set -Eeuo pipefail
umask 077
export LC_ALL=C
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
TMP="${ROOT}/target/codex-confinement-check-it"
EVIDENCE="${TMP}/evidence"
rm -rf -- "${TMP}"
mkdir -p -- "${EVIDENCE}/logs" "${EVIDENCE}/handoffs"
trap 'rm -rf -- "${TMP}"' EXIT
BASE="$(git -C "${ROOT}" rev-parse HEAD)"

make_evidence() {
 rm -rf -- "${EVIDENCE}"
 mkdir -p -- "${EVIDENCE}/logs" "${EVIDENCE}/handoffs"
 python3 - "${ROOT}" "${EVIDENCE}" "${BASE}" <<'PY'
from pathlib import Path
import hashlib,json,sys
project=Path(sys.argv[1]); root=Path(sys.argv[2]); base=sys.argv[3]
contract=json.load(open(project/'contracts/governance/agent/codex-confinement-contract.json'))
def write(path,value): path.parent.mkdir(parents=True,exist_ok=True); path.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n'); return path
def rec(path,base_root=root): return {'path':path.relative_to(base_root).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
host=write(root/'host.json',{'schemaVersion':'springmaster.codex-host-qualification-evidence.v1','status':'PASS','portable':False,'realCodex':True,'baselineCommit':base,'hostId':'fixture-host','probeCount':20,'writableCodexAuthorized':False,'pilotWriteReady':False})
negative=[]
for item in contract['requiredNegativeProbes']:
 p=write(root/'logs'/f"negative-{item['id']}.json",{'id':item['id'],'attempted':True,'outcome':item['expectedOutcome']})
 negative.append({'id':item['id'],'attempted':True,'outcome':item['expectedOutcome'],'log':rec(p)})
positive=[]
for item in contract['requiredPositiveCases']:
 p=write(root/'logs'/f"positive-{item['id']}.json",{'id':item['id'],'outcome':'PASS'})
 row={'id':item['id'],'outcome':'PASS','log':rec(p)}
 if item.get('patchHandoffRequired'):
  d=root/'handoffs'/item['id']; d.mkdir(parents=True)
  patch=d/'change.patch'; patch.write_text('diff --git a/a b/a\n')
  handoff=write(d/'handoff.json',{'schemaVersion':'springmaster.agent-task-patch-handoff.v1','status':'VERIFIED','patchId':None,'deliveryId':None,'integrationAuthorized':False,'canonicalPatchArtifact':False,'isolatedApplyCheck':'PASS','patch':{'path':patch.name,'sha256':hashlib.sha256(patch.read_bytes()).hexdigest()}})
  row['handoffManifest']=rec(handoff)
 positive.append(row)
manifest={
 'schemaVersion':'springmaster.codex-confinement-evidence.v2','status':'COMPLETE','projectId':'springmaster','integrationBranch':'main','baselineCommit':base,'generatedAt':'2026-07-31T08:00:00Z',
 'hostQualification':rec(host),
 'runtime':{'realCodex':True,'codexCliVersion':'fixture-1','model':'fixture-model','sandboxImplementation':'linux-bwrap','approvalPolicy':'never','additionalWritableRoots':[],'forbiddenFlagsPresent':[]},
 'hostState':{'integrationStatusBefore':'','integrationStatusAfter':'','integrationHeadBefore':base,'integrationHeadAfter':'f'*40,'canonicalAcceptOnly':True,'unauthorizedIntegrationMutation':False,'unauthorizedGitCommonMutation':False},
 'negativeProbes':negative,'positiveCases':positive,
 'patchFlow':{'directProjectWrite':False,'directIntegrationWrite':False,'directGitCommonWrite':False,'patchHandoffRequired':True,'handoffCount':2,'automaticAccept':False,'patchAcceptCount':2,'acceptedCalibrationCount':2,'patchDryRunCount':2,'integrationAuthorized':False},
 'promotion':{'writableCodexAuthorized':False,'pilotWriteReady':False,'separateCommittedPromotionRequired':True}
}
write(root/'confinement-evidence.json',manifest)
PY
}

make_evidence
"${ROOT}/bin/codex-confinement-check.sh" --project-root "${ROOT}" verify --evidence "${EVIDENCE}" --candidate --check > "${TMP}/positive.out"
grep -F 'CODEX_CONFINEMENT_STATUS=PASS' "${TMP}/positive.out" >/dev/null

make_evidence
python3 - "${EVIDENCE}/confinement-evidence.json" <<'PY'
import json,sys
p=sys.argv[1]; d=json.load(open(p)); d['hostQualification']['sha256']='0'*64; open(p,'w').write(json.dumps(d)+'\n')
PY
set +e
"${ROOT}/bin/codex-confinement-check.sh" --project-root "${ROOT}" verify --evidence "${EVIDENCE}" --candidate --check > "${TMP}/host-hash.out"
rc=$?
set -e
test "${rc}" -eq 1
grep -F 'EVIDENCE_FILE_HASH_MISMATCH' "${TMP}/host-hash.out" >/dev/null

make_evidence
python3 - "${EVIDENCE}/confinement-evidence.json" <<'PY'
import json,sys
p=sys.argv[1]; d=json.load(open(p)); d['patchFlow']['patchAcceptCount']=1; open(p,'w').write(json.dumps(d)+'\n')
PY
set +e
"${ROOT}/bin/codex-confinement-check.sh" --project-root "${ROOT}" verify --evidence "${EVIDENCE}" --candidate --check > "${TMP}/accept-count.out"
rc=$?
set -e
test "${rc}" -eq 1
grep -F 'PATCH_FLOW_INVALID' "${TMP}/accept-count.out" >/dev/null

make_evidence
python3 - "${EVIDENCE}/confinement-evidence.json" <<'PY'
import json,sys
p=sys.argv[1]; d=json.load(open(p)); d['promotion']['pilotWriteReady']=True; open(p,'w').write(json.dumps(d)+'\n')
PY
set +e
"${ROOT}/bin/codex-confinement-check.sh" --project-root "${ROOT}" verify --evidence "${EVIDENCE}" --candidate --check > "${TMP}/promotion.out"
rc=$?
set -e
test "${rc}" -eq 1
grep -F 'PREMATURE_CODEX_PROMOTION' "${TMP}/promotion.out" >/dev/null
printf '%s\n' 'CODEX_CONFINEMENT_CHECK_IT=PASS'
