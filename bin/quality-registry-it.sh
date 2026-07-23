#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
RUN="${ROOT}/build/quality-registry-it/$(date +%Y%m%d_%H%M%S)_$$"
mkdir -p "$RUN"
python3 - "$ROOT" "$RUN" <<'PY'
import copy, json, shutil, subprocess, sys
from pathlib import Path
root=Path(sys.argv[1]); run=Path(sys.argv[2]); source=root/'contracts/governance/quality'; tool=root/'bin/quality-registry.py'
cases=json.loads((root/'src/test/resources/tooling/quality-registry-v1/expected-cases.json').read_text())['cases']
results=[]; failures=[]
for exp in cases:
    cid=exp['id']; d=run/cid; cr=d/'contracts'; shutil.copytree(source,cr); out=d/'report.json'; op=exp.get('operation','all')
    cat=json.loads((cr/'quality-rule-catalog.json').read_text()); reg=json.loads((cr/'gate-registry.json').read_text())
    if cid=='duplicate-rule': cat['rules'].append(copy.deepcopy(cat['rules'][0]))
    elif cid=='duplicate-gate': reg['gates'].append(copy.deepcopy(reg['gates'][0]))
    elif cid=='invalid-rule-id': cat['rules'][0]['ruleId']='bad'
    elif cid=='normative-text-forbidden': cat['rules'][0]['normativeText']='forbidden duplicate'
    elif cid=='unknown-gate-reference': cat['rules'][0]['gateIds']=['unknown-gate-v1']
    elif cid=='unknown-rule-reference': reg['gates'][0]['ruleIds'].append('UNKNOWN-RULE-001')
    elif cid=='missing-source-path': cat['rules'][0]['normativeSource']['path']='missing.md'
    elif cid=='missing-source-section': cat['rules'][0]['normativeSource']['section']='missing section'
    elif cid=='missing-entrypoint': reg['gates'][0]['entrypoint']='bin/missing.sh'
    elif cid=='missing-input-contract': reg['gates'][0]['inputContracts'].append('contracts/missing.json')
    elif cid=='strict-default-forbidden': reg['gates'][0]['defaultEnforcementMode']='strict'
    elif cid=='planned-rule-unmapped':
        x=next(r for r in cat['rules'] if r['ruleId'].startswith('ENG-')); x.pop('plannedGateId',None); x['gateIds']=[]
    elif cid=='nonreciprocal-rule-gate': reg['gates'][0]['ruleIds'].pop()
    elif cid=='invalid-testability': cat['rules'][0]['testabilityClass']='magic'
    (cr/'quality-rule-catalog.json').write_text(json.dumps(cat,indent=2)+'\n')
    (cr/'gate-registry.json').write_text(json.dumps(reg,indent=2)+'\n')
    if cid=='tool-error-missing-root': shutil.rmtree(cr)
    cmd=[sys.executable,str(tool),'--project-root',str(root),'--contract-root',str(cr),'--out',str(out),'--check',op]
    cp=subprocess.run(cmd,text=True,capture_output=True)
    report=json.loads(out.read_text()) if out.exists() else {}
    ok=cp.returncode==exp['expectedExit'] and report.get('status')==exp['expectedStatus']
    results.append({'id':cid,'passed':ok,'actualExit':cp.returncode,'actualStatus':report.get('status')})
    if not ok: failures.append(f"{cid}: {cp.returncode}/{report.get('status')} stderr={cp.stderr}")
summary={'schemaVersion':'springmaster.quality-registry-it-report.v1','status':'PASS' if not failures else 'FAIL','caseCount':len(results),'passedCount':sum(x['passed'] for x in results),'failedCount':len(failures),'results':results,'failures':failures}
(run/'REPORT.json').write_text(json.dumps(summary,indent=2)+'\n')
if failures:
    print('QUALITY_REGISTRY_IT=FAIL'); print('\n'.join(failures),file=sys.stderr); raise SystemExit(1)
print('QUALITY_REGISTRY_IT=PASS'); print(f'CASES={len(results)}'); print(f'REPORT={run/"REPORT.json"}')
PY
