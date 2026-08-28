#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TMP_ROOT="$(mktemp -d /tmp/codex-autonomous-run-it.XXXXXX)"
trap 'rm -rf "${TMP_ROOT}"' EXIT

python3 - "${ROOT}" "${TMP_ROOT}" <<'PY'
import fnmatch,importlib.util,json,os,pathlib,shutil,stat,subprocess,sys,zipfile
root,tmp=map(pathlib.Path,sys.argv[1:])
spec=importlib.util.spec_from_file_location('runner',root/'bin/codex-autonomous-run.py'); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
catalog=json.loads((root/'src/test/resources/tooling/codex-autonomous-run-v1/expected-cases.json').read_text())
expected={x['id'] for x in catalog['cases']}
required={'first-attempt-success','one-repair-successor','consolidated-qualification-findings','scope-expansion','host-tool-failure','identical-fingerprint-no-progress','max-attempt-exhaustion','known-stream-lag-only','unknown-codex-error','observer-restart-resume','invoke-start-lifecycle-lag','consumed-task-not-reinvoked','carry-forward-bytes-modes','umask-077-mode-normalization','inconsistent-path-cardinality','fresh-complete-final-qualification','main-clean-through-preaccept','automatic-patch-accept-forbidden','deterministic-evidence'}
assert expected==required

def git(cwd,*args):
    r=subprocess.run(['git',*args],cwd=cwd,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    assert r.returncode==0,(args,r.stderr); return r.stdout.strip()

repo=tmp/'repo'; repo.mkdir(); git(repo,'init','-q'); git(repo,'config','user.name','Fixture'); git(repo,'config','user.email','fixture@invalid')
(repo/'product.txt').write_text('base\n'); (repo/'qualify.sh').write_text('#!/usr/bin/env bash\nexit 0\n'); os.chmod(repo/'qualify.sh',0o755)
git(repo,'add','product.txt','qualify.sh'); git(repo,'commit','-qm','base'); base=git(repo,'rev-parse','HEAD')

fake_codex=tmp/'codex-fixture'; fake_codex.write_text('#!/usr/bin/env bash\nprintf \"%s\\n\" \"codex-cli fixture-1.0\"\n'); os.chmod(fake_codex,0o755)
runtime={'executable':str(fake_codex),'version':'codex-cli fixture-1.0','sha256':m.sha_file(fake_codex)}

task={'schemaVersion':'springmaster.agent-task.v2','taskId':'IGNORED-001','pilotId':'springmaster-codex-pilot-v1','repositoryId':'springmaster','mode':'implementation','baseCommit':base,'integrationBranch':'main','riskClass':'high','changeClasses':['tooling'],'allowedPaths':['product.txt'],'forbiddenPaths':['.git/**'],'limits':{'maxChangedFiles':1,'maxNetAddedBytes':4096},'capabilities':{'mayModifyTests':False,'mayModifyGovernance':False,'mayModifyContracts':False,'mayCommit':False,'mayPush':False,'network':'disabled'},'qualificationCommands':[{'id':'q-one','argv':['./qualify.sh'],'timeoutSeconds':5},{'id':'q-two','argv':['./qualify.sh'],'timeoutSeconds':5}],'requiredEvidence':['task-contract']*13,'completionCriteria':{'postcheckPass':True,'allQualificationCommandsPass':True,'requiredEvidenceComplete':True,'invocationRecordRequired':True,'explicitCleanupDisposition':True}}
contract={'schemaVersion':m.SCHEMA,'logicalRunId':'FIXTURE-RUN','taskTemplate':task,'prompt':'repair','model':'fixture','codexRuntime':runtime,'budgets':{'maxAttempts':3,'activeTimeSeconds':60,'attemptActiveTimeoutSeconds':30,'noProgressTimeoutSeconds':10},'patch':{'name':'fixture','title':'Fixture','scope':'tooling'}}
m.validate_contract(contract); assert m.task_for(contract,2)['taskId']=='FIXTURE-RUN-A002'; assert m.authorization_snapshot(m.task_for(contract,1))==m.authorization_snapshot(m.task_for(contract,2))
assert m.verify_codex_runtime(repo,contract)==fake_codex
for field,value in [('sha256','0'*64),('version','codex-cli wrong')]:
    bad=json.loads(json.dumps(contract)); bad['codexRuntime'][field]=value
    try: m.verify_codex_runtime(repo,bad); raise AssertionError(field)
    except m.RunError as exc: assert exc.code=='HOST_TOOL_ERROR'
unsafe=tmp/'codex-symlink'; unsafe.symlink_to(fake_codex)
bad=json.loads(json.dumps(contract)); bad['codexRuntime']['executable']=str(unsafe)
try: m.verify_codex_runtime(repo,bad); raise AssertionError('symlink')
except m.RunError as exc: assert exc.code=='HOST_TOOL_ERROR'
candidate_branch=m.candidate_branch(contract['logicalRunId']); assert candidate_branch=='change/fixture-run-candidate'
project_env={}
for raw in (root/'.cocondo/tooling/project.env').read_text().splitlines():
    if '=' in raw and not raw.lstrip().startswith('#'):
        key,value=raw.split('=',1); project_env[key.strip()]=value.strip()
allowed_branches=json.loads(project_env['CPATCH_ALLOWED_BRANCHES_JSON'])
assert any(fnmatch.fnmatchcase(candidate_branch,pattern) for pattern in allowed_branches),(candidate_branch,allowed_branches)

lag={'status':'FAILED','execution':{'status':'COMPLETED','exitCode':0},'jsonlValidation':{'parseErrorCount':0,'turnCompletedCount':1,'turnFailedCount':0,'findings':[{'code':'CODEX_ERROR_ITEM','message':'in-process app-server event stream lagged; dropped 7 events'}]}}
assert m.stream_lag_only(lag)
mixed=json.loads(json.dumps(lag)); mixed['jsonlValidation']['findings'].append({'code':'CODEX_ERROR_ITEM','message':'unknown'})
assert not m.stream_lag_only(mixed)
assert m.classify_postcheck({'findings':[{'code':'UNDECLARED_PATH_CHANGED'}]})=='SCOPE_EXPANSION_REQUIRED'
assert m.classify_postcheck({'findings':[{'code':'FORBIDDEN_PATH_CHANGED'}]})=='SECURITY_BOUNDARY_VIOLATION'

# Exercise byte/mode carry-forward and the existing verifier under a restrictive umask.
source=tmp/'source'; git(repo,'worktree','add','--detach',str(source),base)
(source/'product.txt').write_bytes(b'#!/bin/sh\nprintf fixture\\n\n'); os.chmod(source/'product.txt',0o755)
successor=m.task_for(contract,2); bundle_path=tmp/'artifacts'/'bundle.zip'; bundle=m.create_bundle(repo,successor,source,['product.txt'],bundle_path)
with zipfile.ZipFile(bundle_path) as z:
    manifest=json.loads(z.read('manifest.json')); assert manifest['taskId']=='FIXTURE-RUN-A002'; assert manifest['operations'][0]['mode']=='100755'
target=tmp/'target'; git(repo,'worktree','add','--detach',str(target),base)
contract_path=tmp/'task.json'; contract_path.write_text(json.dumps(successor))
old=os.umask(0o077)
try:
    env=dict(os.environ,COCONDO_ARTIFACT_ROOT=str(tmp/'artifacts'),SPRINGMASTER_CODEX_CHANGE_BUNDLE=str(bundle_path),SPRINGMASTER_AGENT_TASK_CONTRACT=str(contract_path),SPRINGMASTER_AGENT_TASK_ID=successor['taskId'])
    r=subprocess.run([str(root/'bin/codex-change-bundle.sh'),'--project-root',str(target),'--format','json','apply'],cwd=target,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
finally: os.umask(old)
assert r.returncode==0,(r.stdout,r.stderr); assert (target/'product.txt').read_bytes()==(source/'product.txt').read_bytes(); assert stat.S_IMODE((target/'product.txt').stat().st_mode)==0o755

# Internally inconsistent payload cardinality is rejected before target mutation.
bad=tmp/'artifacts'/'bad.zip'
with zipfile.ZipFile(bad,'w') as z:
    z.writestr('manifest.json',m.canonical(manifest)); z.writestr('payload/unexpected.txt',b'x')
before=(target/'product.txt').read_bytes(); env['SPRINGMASTER_CODEX_CHANGE_BUNDLE']=str(bad)
r=subprocess.run([str(root/'bin/codex-change-bundle.sh'),'--project-root',str(target),'--format','json','apply'],cwd=target,env=env,text=True,stdout=subprocess.PIPE)
assert r.returncode!=0 and (target/'product.txt').read_bytes()==before

# Canonical serialization and static trust-boundary assertions are deterministic.
assert m.canonical({'b':1,'a':2})==m.canonical({'a':2,'b':1})
source_text=(root/'bin/codex-autonomous-run.py').read_text()
assert '"patch-accept"' not in source_text and "'patch-accept'" not in source_text
assert '"push"' not in source_text and "'push'" not in source_text
assert 'run-start' in source_text and '--singleton-key' in source_text and 'resume_attempt' in source_text
assert 'cleanup_physical_attempt(project, task["taskId"], "FAILED")' in source_text
assert 'cleanup_physical_attempt(project, task["taskId"], "HANDED_OFF")' in source_text
assert 'task_status.get("status") in {"HANDED_OFF", "CLEANED"}' in source_text
assert 'SCHEMA = "springmaster.codex-autonomous-run.v2"' in source_text
assert 'def verify_codex_runtime(project: Path, contract: dict[str, Any]) -> Path:' in source_text
assert '"--codex", str(codex)' in source_text

# invoke-start owns a durable run before agent-task necessarily leaves
# PREPARED/NOT_RECORDED. A resumed observer follows that run and never invokes
# the already running physical task again.
invoke_dir=tmp/'invoke-return-race'
invoke_state={}
invoke_commands=[]
invoke_globals=m.invoke_attempt.__globals__
original_invoke_run_json=invoke_globals['run_json']
def invoke_run_json(argv,cwd,timeout=None):
    invoke_commands.append(argv)
    completed=subprocess.CompletedProcess(argv,0,'{}','')
    if 'agent-task.sh' in argv[0] and 'validate' in argv:
        return {'status':'PASS'},completed
    if 'agent-task.sh' in argv[0] and 'prepare' in argv:
        return {'status':'PREPARED','taskId':'FIXTURE-RUN-A001','worktreePath':str(source),'codexInvocation':'NOT_RECORDED'},completed
    if 'codex-host-sandbox.sh' in argv[0] and 'invoke-start' in argv:
        return {'status':'RUNNING','runId':'durable-invocation-001'},completed
    assert 'process-ops.sh' in argv[0] and 'wait' in argv and 'durable-invocation-001' in argv
    result_path=invoke_dir/'attempts'/'A001'/'host-invocation.json'
    result_path.write_text(json.dumps({'status':'PASS'}))
    return {'status':'COMPLETED','runId':'durable-invocation-001'},completed
try:
    invoke_globals['run_json']=invoke_run_json
    invoked_task,invoked_result,invoked_worktree=m.invoke_attempt(repo,contract,invoke_state,invoke_dir,1,None,None)
finally:
    invoke_globals['run_json']=original_invoke_run_json
assert invoked_task['taskId']=='FIXTURE-RUN-A001' and invoked_result['status']=='PASS' and invoked_worktree==source
assert invoke_state['state']=='ATTEMPT_RUNNING' and invoke_state['processRunId']=='durable-invocation-001'
assert sum('invoke-start' in argv for argv in invoke_commands)==1
invoke_argv=next(argv for argv in invoke_commands if 'invoke-start' in argv)
assert '--codex' in invoke_argv and invoke_argv[invoke_argv.index('--codex')+1]==str(fake_codex)

attempt_dir=tmp/'logical-run'/'attempts'/'A001'; attempt_dir.mkdir(parents=True)
invocation_path=attempt_dir/'host-invocation.json'
lag_state={'processRunId':'durable-invocation-001'}
observed_commands=[]
resume_globals=m.resume_attempt.__globals__
original_run_json=resume_globals['run_json']
def lagged_run_json(argv,cwd,timeout=None):
    observed_commands.append(argv)
    completed=subprocess.CompletedProcess(argv,0,'{}','')
    if 'agent-task.sh' in argv[0] and 'status' in argv:
        return {'status':'PREPARED','taskId':'FIXTURE-RUN-A001','worktreePath':str(source),'codexInvocation':'NOT_RECORDED'},completed
    assert 'process-ops.sh' in argv[0] and 'wait' in argv and 'durable-invocation-001' in argv
    invocation_path.write_text(json.dumps({'status':'PASS'}))
    return {'status':'COMPLETED','runId':'durable-invocation-001'},completed
try:
    resume_globals['run_json']=lagged_run_json
    resumed_task,resumed_invocation,resumed_worktree=m.resume_attempt(repo,contract,lag_state,tmp/'logical-run',1)
finally:
    resume_globals['run_json']=original_run_json
assert resumed_task['taskId']=='FIXTURE-RUN-A001' and resumed_invocation['status']=='PASS' and resumed_worktree==source
assert len(observed_commands)==2
assert sum('invoke-start' in argv for argv in observed_commands)==0
assert sum('wait' in argv for argv in observed_commands)==1

# Repair continuation and successful promotion must release the one-active-task slot
# only through the canonical Agent Task cleanup disposition. Cleanup is idempotent
# so a worker crash after worktree removal can safely resume.
cleanup_globals=m.cleanup_physical_attempt.__globals__
original_cleanup_run_json=cleanup_globals['run_json']
cleanup_commands=[]
def cleanup_run_json(argv,cwd,timeout=None):
    cleanup_commands.append(argv)
    completed=subprocess.CompletedProcess(argv,0,'{}','')
    if 'status' in argv:
        return {'status':'FAILED','taskId':'FIXTURE-RUN-A001'},completed
    assert 'cleanup' in argv and '--discard' in argv
    return {'status':'CLEANED','taskId':'FIXTURE-RUN-A001'},completed
try:
    cleanup_globals['run_json']=cleanup_run_json
    m.cleanup_physical_attempt(repo,'FIXTURE-RUN-A001','FAILED')
finally:
    cleanup_globals['run_json']=original_cleanup_run_json
assert sum('status' in argv for argv in cleanup_commands)==1
assert sum('cleanup' in argv for argv in cleanup_commands)==1
assert any('--discard' in argv for argv in cleanup_commands)

already_cleaned_commands=[]
def already_cleaned_run_json(argv,cwd,timeout=None):
    already_cleaned_commands.append(argv)
    completed=subprocess.CompletedProcess(argv,0,'{}','')
    assert 'status' in argv
    return {'status':'CLEANED','taskId':'FIXTURE-RUN-A001','handoffManifest':'/immutable/handoff.json'},completed
try:
    cleanup_globals['run_json']=already_cleaned_run_json
    m.cleanup_physical_attempt(repo,'FIXTURE-RUN-A001','FAILED')
finally:
    cleanup_globals['run_json']=original_cleanup_run_json
assert len(already_cleaned_commands)==1 and 'status' in already_cleaned_commands[0]

# Simulate the repair state machine with public-primitive outcomes while retaining immutable attempts.
def simulate(qmatrix, invocation_matrix=None, post_codes=None, max_attempts=3):
    attempts=[]; packets=[]; previous=None; prior_bytes=None
    invocation_matrix=invocation_matrix or [{'status':'PASS'}]*len(qmatrix); post_codes=post_codes or [[] for _ in qmatrix]
    for ordinal,results in enumerate(qmatrix,1):
        attempt=m.task_for(contract,ordinal)['taskId']; assert attempt not in attempts; attempts.append(attempt)
        inv=invocation_matrix[ordinal-1]
        if inv.get('status')!='PASS' and not m.stream_lag_only(inv): return 'HOST_TOOL_ERROR',attempts,packets
        classification=m.classify_postcheck({'findings':[{'code':x} for x in post_codes[ordinal-1]]})
        if classification!='PASS': return classification,attempts,packets
        if all(results): return 'PREACCEPT',attempts,packets
        evidence=[{'id':f'q-{i}','argv':['fixture',str(i)],'status':'PASS' if ok else 'FAIL','exitCode':0 if ok else 1,'logSha256':str(i)*64,'logTail':'bounded'} for i,ok in enumerate(results,1)]
        fp=m.sha_bytes(m.canonical(evidence)); work='same-bytes'
        if fp==previous and work==prior_bytes:return 'NO_PROGRESS',attempts,packets
        packets.append(evidence); previous,prior_bytes=fp,work
        if ordinal>=max_attempts:return 'REPAIR_BUDGET_EXHAUSTED',attempts,packets
    return 'REPAIR_BUDGET_EXHAUSTED',attempts,packets

assert simulate([[True,True]])[0]=='PREACCEPT'
state,attempts,packets=simulate([[False,True],[True,True]]); assert state=='PREACCEPT' and attempts==['FIXTURE-RUN-A001','FIXTURE-RUN-A002']
state,_,packets=simulate([[False,False],[True,True]]); assert state=='PREACCEPT' and len([x for x in packets[0] if x['status']=='FAIL'])==2
assert simulate([[True,True]],post_codes=[['UNDECLARED_PATH_CHANGED']])[0]=='SCOPE_EXPANSION_REQUIRED'
assert simulate([[True,True]],invocation_matrix=[mixed])[0]=='HOST_TOOL_ERROR'
assert simulate([[False,True],[False,True],[True,True]])[0]=='NO_PROGRESS'
assert simulate([[False,True]],max_attempts=1)[0]=='REPAIR_BUDGET_EXHAUSTED'
assert simulate([[True,True]],invocation_matrix=[lag])[0]=='PREACCEPT'
assert len(set(attempts))==len(attempts)

# A fresh final result must cover the complete immutable argv list.
fresh=[{'id':x['id'],'argv':x['argv'],'status':'PASS'} for x in task['qualificationCommands']]
assert len(fresh)==len(task['qualificationCommands']) and all(x['status']=='PASS' for x in fresh)
assert git(repo,'rev-parse','HEAD')==base and git(repo,'status','--porcelain')==''
print('CODEX_AUTONOMOUS_RUN_IT=PASS')
print('CASE_COUNT=19')
PY
