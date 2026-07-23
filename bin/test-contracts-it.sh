#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
RUN="${ROOT}/build/test-contracts-it/$(date +%Y%m%d_%H%M%S)_$$"
mkdir -p "$RUN"
python3 - "$ROOT" "$RUN" <<'PY'
import copy,json,shutil,subprocess,sys
from pathlib import Path
root=Path(sys.argv[1]); run=Path(sys.argv[2]); tool=root/'bin/test-contracts.py'
cases=json.loads((root/'src/test/resources/tooling/test-contracts-v1/expected-cases.json').read_text())['cases']
results=[];failures=[]
for exp in cases:
 cid=exp['id']; project=run/cid/'project'; project.mkdir(parents=True)
 for rel in ['pom.xml','src/test/java','src/test/resources/tooling','bin','platform/update/tests','contracts/governance/engineering','contracts/governance/testing']:
  src=root/rel; dst=project/rel
  if src.is_dir(): shutil.copytree(src,dst)
  elif src.is_file(): dst.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(src,dst)
 cr=project/'contracts/governance/testing'; out=run/cid/'report.json'
 suites=json.loads((cr/'test-suite-contract.json').read_text()); fixtures=json.loads((cr/'test-fixture-contract.json').read_text()); inv=json.loads((cr/'test-inventory-baseline.json').read_text())
 if cid=='duplicate-suite': suites['suites'].append(copy.deepcopy(suites['suites'][0]))
 elif cid=='unknown-runner': suites['suites'][0]['runnerId']='unknown-runner'
 elif cid=='unknown-profile': suites['suites'][0]['engineeringProfiles'].append('unknown')
 elif cid=='invalid-enforcement': suites['suites'][0]['enforcementMode']='strict'
 elif cid=='failsafe-unimplemented': suites['mavenBaseline']['failsafeImplemented']=True
 elif cid=='coverage-threshold-premature': suites['mavenBaseline']['coverageThresholds']=[{'scope':'all','line':80}]
 elif cid=='duplicate-inventory-path': inv['javaTests'].append(copy.deepcopy(inv['javaTests'][0]))
 elif cid=='unregistered-java-test':
  p=project/'src/test/java/example/UnexpectedTest.java';p.parent.mkdir(parents=True,exist_ok=True);p.write_text('class UnexpectedTest {}\n')
 elif cid=='missing-registered-test': (project/inv['javaTests'][0]['path']).unlink()
 elif cid=='unregistered-tooling-test':
  p=project/'bin/unexpected-it.sh';p.write_text('#!/usr/bin/env bash\nset -euo pipefail\n')
 elif cid=='orphan-fixture':
  p=project/'src/test/resources/tooling/orphan.json';p.write_text('{}\n')
 elif cid=='golden-missing-consumer': fixtures['fixtureEntries'][0]['consumers']=[]
 (cr/'test-suite-contract.json').write_text(json.dumps(suites,indent=2)+'\n')
 (cr/'test-fixture-contract.json').write_text(json.dumps(fixtures,indent=2)+'\n')
 (cr/'test-inventory-baseline.json').write_text(json.dumps(inv,indent=2)+'\n')
 if cid=='tool-error-missing-root': shutil.rmtree(cr)
 elif cid=='tool-error-malformed-contract': (cr/'test-suite-contract.json').write_text('{bad')
 cmd=[sys.executable,str(tool),'--project-root',str(project),'--contract-root',str(cr),'--out',str(out),'--check',exp.get('operation','all')]
 cp=subprocess.run(cmd,text=True,capture_output=True)
 report=json.loads(out.read_text()) if out.exists() else {}
 ok=cp.returncode==exp['expectedExit'] and report.get('status')==exp['expectedStatus']
 results.append({'id':cid,'passed':ok,'actualExit':cp.returncode,'actualStatus':report.get('status')})
 if not ok: failures.append(f"{cid}: {cp.returncode}/{report.get('status')} stderr={cp.stderr}")
summary={'schemaVersion':'springmaster.test-contracts-it-report.v1','status':'PASS' if not failures else 'FAIL','caseCount':len(results),'passedCount':sum(x['passed'] for x in results),'failedCount':len(failures),'results':results,'failures':failures}
(run/'REPORT.json').write_text(json.dumps(summary,indent=2)+'\n')
if failures:
 print('TEST_CONTRACTS_IT=FAIL');print('\n'.join(failures),file=sys.stderr);raise SystemExit(1)
print('TEST_CONTRACTS_IT=PASS');print(f'CASES={len(results)}');print(f'REPORT={run/"REPORT.json"}')
PY
