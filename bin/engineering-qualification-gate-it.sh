#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
RUN_DIR="${PROJECT_ROOT}/build/engineering-qualification-gate-it/$(date +%Y%m%d_%H%M%S)_$$"
mkdir -p "${RUN_DIR}"

python3 - "${PROJECT_ROOT}" "${RUN_DIR}" <<'PYEOF'
from __future__ import annotations
import copy
import json
import shutil
import subprocess
import sys
from pathlib import Path

project_root=Path(sys.argv[1])
run_dir=Path(sys.argv[2])
expectations=json.loads((project_root/'src/test/resources/tooling/engineering-qualification-gate-v1/expected-cases.json').read_text(encoding='utf-8'))['cases']
tool=project_root/'bin/engineering-qualification-gate.py'
source_engineering=project_root/'contracts/governance/engineering'
source_quality=project_root/'contracts/governance/quality'
source_testing=project_root/'contracts/governance/testing'
checks=['quality-registry-v1','test-contracts-v1','documentation-gate-v2','project-directory-gate-v1','sprint-gate-v1']

def write(path:Path,value:object):
 path.parent.mkdir(parents=True,exist_ok=True); path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def classification(*,classes=None,risk='high',flags=None):
 return {
  'schemaVersion':'springmaster.engineering-change-classification.v1','changeId':'SPRINGMASTER-S04',
  'classes':classes or ['contract','quality-rule','tooling','test'],'declaredRiskLevel':risk,
  'riskIndicators':['public-or-reusable-contract'],
  'flags':flags or {'governanceMigration':False,'strictPromotion':False,'periodicAudit':False,'releaseCandidate':False},
 }

def profile_selection(required):
 return {'schemaVersion':'springmaster.engineering-profile-selection.v1','requiredProfiles':required,'optionalProfiles':['fast']}

def executions(required):
 result=[]
 for profile in required:
  if profile=='release': continue
  for check in checks:
   result.append({'executionId':f'EXEC-{profile.upper()}-{check.upper()}','profileId':profile,'checkId':check,'status':'passed','command':f'./bin/{check}.sh --check','reportRefs':[f'build/evidence/{profile}/{check}.json']})
 return result

def evidence(cls,required,status='qualified'):
 return {
  'schemaVersion':'springmaster.engineering-evidence.v1','evidenceId':'ENG-EVID-SPRINGMASTER-S04','changeRef':'SPRINGMASTER-S04','sprintRef':'SPRINGMASTER-SPRINT-001',
  'baseline':{'gitHead':'2353022e246397b160c458debda2dd0b746ce60c','dirty':False,'sourceExportSha256':'c3e385a2c8c6070e9521d5e51f5e5f4f843921bb70ba4b1a47c77696280ff301'},
  'acceptedScope':{'desiredResult':'Materialize report-only engineering qualification gate','requirements':['EQP-REQ-001','EQP-REQ-004'],'paths':['contracts/governance/engineering/**','bin/engineering-qualification-gate*'],'outOfScope':['strict promotion','release qualification']},
  'classification':copy.deepcopy(cls),'profileSelection':profile_selection(required),
  'ruleSources':['PROJECT_DOCS/GOVERNANCE/ENGINEERING_GOVERNANCE.md','PROJECT_DOCS/GOVERNANCE/QUALITY_GATE_GOVERNANCE.md','PROJECT_DOCS/GOVERNANCE/TEST_GOVERNANCE.md'],
  'executions':executions(required),'findings':[],'deferrals':['release-profile-unqualified'],'technicalDebt':[],
  'impact':{'version':'minor','projectNew':'assessment-deferred-to-s05','managedProjects':'assessment-deferred-to-s05','dependencies':'none','documentation':'engineering-governance-and-sprint-evidence'},
  'artifactFamilies':['engineering-qualification-gate','quality-registry','test-inventory'],'technicalStatus':status,
  'completionRef':'ENG-COMP-SPRINGMASTER-S04' if status in {'qualified','qualified-with-findings'} else None,
 }

def completion(status='qualified',criterion='passed'):
 return {
  'schemaVersion':'springmaster.engineering-completion.v1','completionId':'ENG-COMP-SPRINGMASTER-S04','changeRef':'SPRINGMASTER-S04','evidenceRef':'ENG-EVID-SPRINGMASTER-S04','status':status,
  'criterionResults':[{'criterionId':f'ENG-COMP-{i:03d}','status':criterion} for i in range(1,15)],
  'openBlockingFindingIds':[],'openToolErrorIds':[],'acceptedFindingIds':[],
  'reviewers':['springmaster-maintainers'] if status in {'qualified','qualified-with-findings'} else [],
  'completedAt':'2026-07-23' if status in {'qualified','qualified-with-findings'} else None,'cancellationReason':None,
 }

failures=[]; results=[]
for expected in expectations:
 cid=expected['id']; case=run_dir/cid; er=case/'engineering'; qr=case/'quality'; tr=case/'testing'
 shutil.copytree(source_engineering,er); shutil.copytree(source_quality,qr); shutil.copytree(source_testing,tr)
 out=case/'report.json'; cpath=case/'classification.json'; epath=case/'evidence.json'; compath=case/'completion.json'
 op=expected['operation']
 cls=classification(); required=['qualification']; ev=evidence(cls,required); comp=completion()
 if cid=='qualification-with-findings-valid':
  ev['technicalStatus']='qualified-with-findings'; ev['findings']=[{'findingId':'F-WARN','severity':'WARNING','status':'accepted','message':'Accepted non-blocking finding'}]
  comp=completion('qualified-with-findings'); comp['acceptedFindingIds']=['F-WARN']
 elif cid=='audit-valid':
  cls=classification(flags={'governanceMigration':True,'strictPromotion':False,'periodicAudit':False,'releaseCandidate':False}); required=['qualification','audit']; ev=evidence(cls,required)
 elif cid=='profile-selection-mismatch': ev['profileSelection']['requiredProfiles']=['fast']
 elif cid=='classification-record-mismatch': ev['classification']['classes']=['documentation']
 elif cid=='missing-required-check': ev['executions']=[x for x in ev['executions'] if x['checkId']!='sprint-gate-v1']
 elif cid=='required-check-blocked': ev['executions'][0]['status']='blocked'
 elif cid=='required-check-tool-error': ev['executions'][0]['status']='tool-error'
 elif cid=='unknown-check-id': ev['executions'][0]['checkId']='unknown-gate-v1'
 elif cid=='duplicate-check-execution': ev['executions'].append(copy.deepcopy(ev['executions'][0]))
 elif cid=='passed-check-without-report': ev['executions'][0]['reportRefs']=[]
 elif cid=='completion-status-mismatch': comp['status']='incomplete'; comp['reviewers']=[]; comp['completedAt']=None; comp['criterionResults'][0]['status']='pending'
 elif cid=='qualified-open-blocker': comp['openBlockingFindingIds']=['F-BLOCK']
 elif cid=='completion-pending-criterion': comp['criterionResults'][0]['status']='pending'
 elif cid=='release-profile-unsupported':
  cls=classification(classes=['release','build'],flags={'governanceMigration':False,'strictPromotion':False,'periodicAudit':False,'releaseCandidate':True}); required=['qualification','audit','release']; ev=evidence(cls,required)
 elif cid=='contracts-missing-gate-descriptor':
  reg=json.loads((qr/'gate-registry.json').read_text()); reg['gates']=[x for x in reg['gates'] if x.get('gateId')!='engineering-qualification-gate-v1']; write(qr/'gate-registry.json',reg)
 elif cid=='contracts-nonreciprocal-rule':
  reg=json.loads((qr/'gate-registry.json').read_text()); gate=next(x for x in reg['gates'] if x.get('gateId')=='engineering-qualification-gate-v1'); gate['ruleIds'].remove('ENG-QUAL-004'); write(qr/'gate-registry.json',reg)
 elif cid=='tool-error-missing-contract-root': shutil.rmtree(er)
 if op=='qualification':
  write(cpath,cls); write(epath,ev); write(compath,comp)
  if cid=='tool-error-malformed-input': cpath.write_text('{not-json\n',encoding='utf-8')
 command=[sys.executable,str(tool),'--project-root',str(project_root),'--contract-root',str(er),'--quality-root',str(qr),'--testing-root',str(tr),'--out',str(out),'--check',op]
 if op=='qualification': command += ['--classification',str(cpath),'--evidence',str(epath),'--completion',str(compath)]
 cp=subprocess.run(command,text=True,capture_output=True)
 report=json.loads(out.read_text()) if out.is_file() else {}
 ok=cp.returncode==expected['expectedExit'] and report.get('status')==expected['expectedStatus']
 if cid=='qualification-valid' and report.get('details',{}).get('requiredProfiles')!=['qualification']: ok=False
 if cid=='audit-valid' and report.get('details',{}).get('requiredProfiles')!=['qualification','audit']: ok=False
 results.append({'id':cid,'expectedExit':expected['expectedExit'],'actualExit':cp.returncode,'expectedStatus':expected['expectedStatus'],'actualStatus':report.get('status'),'passed':ok})
 if not ok: failures.append(f"{cid}: expected {expected['expectedExit']}/{expected['expectedStatus']} got {cp.returncode}/{report.get('status')} stdout={cp.stdout!r} stderr={cp.stderr!r}")
summary={'schemaVersion':'springmaster.engineering-qualification-gate-it-report.v1','status':'PASS' if not failures else 'FAIL','caseCount':len(results),'passedCount':sum(x['passed'] for x in results),'failedCount':len(failures),'results':results,'failures':failures}
write(run_dir/'REPORT.json',summary)
if failures:
 print('ENGINEERING_QUALIFICATION_GATE_IT=FAIL'); print('\n'.join(failures),file=sys.stderr); raise SystemExit(1)
print('ENGINEERING_QUALIFICATION_GATE_IT=PASS'); print(f'CASES={len(results)}'); print(f'REPORT={run_dir/"REPORT.json"}')
PYEOF
