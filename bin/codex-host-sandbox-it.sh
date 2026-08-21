#!/usr/bin/env bash
set -Eeuo pipefail
umask 077
export LC_ALL=C
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
TMP="${ROOT}/target/codex-host-sandbox-it"
rm -rf -- "${TMP}"
mkdir -p -- "${TMP}"
trap 'if [[ "${KEEP_CODEX_HOST_IT:-false}" != true ]]; then rm -rf -- "${TMP}"; fi' EXIT

REPO="${TMP}/repo"
mkdir -p "${REPO}/bin" "${REPO}/.cocondo/tooling" "${REPO}/contracts/governance/agent" "${REPO}/src/test/resources/tooling/codex-calibration-v1"
cp -- \
  "${ROOT}/bin/agent-task.py" \
  "${ROOT}/bin/agent-task.sh" \
  "${ROOT}/bin/codex-calibration.py" \
  "${ROOT}/bin/codex-calibration.sh" \
  "${ROOT}/bin/codex-host-sandbox.py" \
  "${ROOT}/bin/codex-host-sandbox.sh" \
  "${REPO}/bin/"
cp -- \
  "${ROOT}/contracts/governance/agent/codex-pilot-contract.json" \
  "${ROOT}/contracts/governance/agent/codex-host-qualification-contract.json" \
  "${REPO}/contracts/governance/agent/"
cp -- "${ROOT}/.cocondo/tooling/project.env" "${REPO}/.cocondo/tooling/project.env"
cp -- "${ROOT}/src/test/resources/tooling/codex-calibration-v1/task-1.txt" "${ROOT}/src/test/resources/tooling/codex-calibration-v1/task-2.txt" "${REPO}/src/test/resources/tooling/codex-calibration-v1/"
printf '%s\n' 'host sandbox fixture' > "${REPO}/README.md"
python3 - "${REPO}/contracts/governance/agent/codex-pilot-contract.json" <<'PY'
import json,sys
from pathlib import Path
p=Path(sys.argv[1])
d=json.loads(p.read_text(encoding="utf-8"))
d["pilot"]["currentLifecycle"]="PILOT_WRITE_READY"
import hashlib,platform
machine_path=Path("/etc/machine-id")
machine=machine_path.read_text(encoding="utf-8").strip() if machine_path.is_file() else platform.node()
host=hashlib.sha256(f"{machine}\n{platform.machine()}\n{platform.release()}\n".encode()).hexdigest()[:24]
d["writePromotion"]["hostId"]=host
d["writeAuthorizations"]["entries"]=[dict(d["writePromotion"])]
p.write_text(json.dumps(d,indent=2,sort_keys=True)+"\n",encoding="utf-8")
PY
chmod 755 "${REPO}/bin/agent-task.py" "${REPO}/bin/agent-task.sh" "${REPO}/bin/codex-calibration.py" "${REPO}/bin/codex-calibration.sh" "${REPO}/bin/codex-host-sandbox.py" "${REPO}/bin/codex-host-sandbox.sh"
git -c init.defaultRefFormat=files -C "${REPO}" init -q -b main
git -C "${REPO}" config user.name fixture
git -C "${REPO}" config user.email fixture@example.invalid
git -C "${REPO}" add -- .
git -C "${REPO}" commit -q -m fixture-host-foundation
mkdir -p "${TMP}/worktrees" "${TMP}/runs" "${TMP}/artifacts" "${TMP}/codex-home" "${TMP}/fake-bin"
printf '%s\n' '{"fixture":true}' > "${TMP}/codex-home/auth.json"
chmod 600 "${TMP}/codex-home/auth.json"

cat > "${TMP}/fake-bin/bwrap" <<'BWRAP'
#!/usr/bin/env python3
import os,subprocess,sys,time
args=sys.argv[1:]
if args==['--version']:
 print('bubblewrap 0.9.0-fixture'); raise SystemExit(0)
if '--' in args:
 i=args.index('--'); command=args[i+1:]
else:
 # smoke form without explicit --
 command=[]
 for i,a in enumerate(args):
  if a.startswith('/') and a not in {'/','/proc','/dev','/tmp','/var/tmp','/run'} and i>0 and args[i-1] not in {'--ro-bind','--bind','--tmpfs','--dev','--proc','--chdir'}:
   command=args[i:]; break
if not command: raise SystemExit(2)
if '--clearenv' in args:
 values={}
 for i,a in enumerate(args):
  if a=='--setenv' and i+2<len(args): values[args[i+1]]=args[i+2]
 if values.get('PATH')!='/usr/local/bin:/usr/bin:/bin': raise SystemExit(91)
chdir=os.getcwd()
if '--chdir' in args:
 chdir=args[args.index('--chdir')+1]
joined=' '.join(command)
if 'chatgpt.com' in joined and (os.path.basename(command[0]) in {'getent','curl'}):
 print('fixture control-plane reachable')
 raise SystemExit(0)
for token in ('git add -A','process-ops.sh patch-accept','../.codex-traversal-denied','.codex-escape-link','/.codex-denied','Downloads/.codex-denied','.codex-background-denied'):
 if token in joined:
  raise SystemExit(13)
# Deny absolute writes outside task for shell probes.
if command[:4]==['/bin/sh','-eu','-c'] and ' > ' in command[4]:
 target=command[4].split(' > ',1)[1].strip().strip("'\"")
 if target.startswith('/') and not os.path.realpath(target).startswith(os.path.realpath(chdir)+os.sep):
  raise SystemExit(13)
raise SystemExit(subprocess.run(command,cwd=chdir,env=os.environ.copy()).returncode)
BWRAP
cat > "${TMP}/fake-bin/codex" <<'CODEX'
#!/usr/bin/env python3
import os,subprocess,sys,time
args=sys.argv[1:]
if args==['--version']:
 print('codex-cli fixture-1'); raise SystemExit(0)
if args[:2]==['exec','--help']:
 print('fixture exec help'); raise SystemExit(0)
if args[:3]==['--ask-for-approval','never','exec']:
 args=args[2:]
if args and args[0]=='sandbox':
 if len(args)<3 or args[1]!='--' or args[2]=='linux':
  raise SystemExit(92)
 cmd=args[2:]
 joined=' '.join(cmd)
 if cmd==['/usr/bin/true']:
  raise SystemExit(0)
 if '.codex-inner-write' in joined:
  raise SystemExit(subprocess.run(cmd).returncode)
 raise SystemExit(13)
if args and args[0]=='exec':
 prompt=sys.stdin.read()
 print('{"type":"turn.started"}', flush=True)
 if 'fixture-process-fail' in prompt:
  print('fixture process failure', file=sys.stderr, flush=True)
  raise SystemExit(7)
 if 'fixture-streaming' in prompt:
  print('{"type":"item.completed","item":{"id":"item_stream","type":"agent_message","text":"stream-visible"}}', flush=True)
  time.sleep(4)
  print('{"type":"turn.completed"}', flush=True)
  raise SystemExit(0)
 if 'fixture-no-progress' in prompt:
  time.sleep(20)
  print('{"type":"turn.completed"}', flush=True)
  raise SystemExit(0)
 if 'fixture-active-timeout' in prompt:
  for index in range(100):
   print('{"type":"item.completed","item":{"id":"item_progress_%d","type":"agent_message","text":"progress"}}' % index, flush=True)
   time.sleep(0.2)
  print('{"type":"turn.completed"}', flush=True)
  raise SystemExit(0)
 if 'fixture-suspend-gap' in prompt:
  time.sleep(8)
  print('{"type":"item.completed","item":{"id":"item_suspend","type":"agent_message","text":"resumed"}}', flush=True)
  print('{"type":"turn.completed"}', flush=True)
  raise SystemExit(0)
 if 'fixture-error-item' in prompt:
  print('{"type":"item.completed","item":{"id":"item_error","type":"error","message":"fixture inner error"}}')
 elif 'fixture-command-fail' in prompt:
  print('{"type":"item.started","item":{"id":"item_cmd","type":"command_execution","command":"/usr/bin/false"}}')
  print('{"type":"item.completed","item":{"id":"item_cmd","type":"command_execution","command":"/usr/bin/false","status":"completed","exit_code":1,"aggregated_output":""}}')
 elif 'fixture implementation command' in prompt or 'fixture-command-success' in prompt:
  print('{"type":"item.started","item":{"id":"item_cmd","type":"command_execution","command":"/usr/bin/true"}}')
  print('{"type":"item.completed","item":{"id":"item_cmd","type":"command_execution","command":"/usr/bin/true","status":"completed","exit_code":0,"aggregated_output":""}}')
 else:
  print('{"type":"item.completed","item":{"id":"item_msg","type":"agent_message","text":"fixture pass"}}')
 print('{"type":"turn.completed"}')
 raise SystemExit(0)
raise SystemExit(2)
CODEX
cat > "${TMP}/fake-bin/codex-linux" <<'CODEX_LINUX'
#!/usr/bin/env python3
import subprocess,sys
args=sys.argv[1:]
if args==['--version']:
 print('codex-cli fixture-linux-subcommand'); raise SystemExit(0)
if args[:2]==['exec','--help']:
 print('fixture exec help'); raise SystemExit(0)
if args and args[0]=='sandbox':
 if len(args)<4 or args[1:3]!=['linux','--']:
  raise SystemExit(92)
 cmd=args[3:]
 if cmd==['/usr/bin/true']:
  raise SystemExit(0)
 raise SystemExit(13)
raise SystemExit(2)
CODEX_LINUX
chmod 755 "${TMP}/fake-bin/bwrap" "${TMP}/fake-bin/codex" "${TMP}/fake-bin/codex-linux"

export COCONDO_WORKTREE_ROOT="${TMP}/worktrees"
export COCONDO_AGENT_RUN_ROOT="${TMP}/runs"
export COCONDO_ARTIFACT_ROOT="${TMP}/artifacts"
export CODEX_HOME="${TMP}/codex-home"
mkdir -p "${TMP}/hostile-path"
export PATH="${TMP}/hostile-path:/usr/bin:/bin"

BASE="$(git -C "${REPO}" rev-parse HEAD)"
TASK_JSON="${TMP}/analysis-task.json"
python3 - "${TASK_JSON}" "${BASE}" <<'PY'
import json,sys
p,base=sys.argv[1:]
value={
 "schemaVersion":"springmaster.agent-task.v2","taskId":"CODEX-HOST-IT-ANALYSIS-001","pilotId":"springmaster-codex-pilot-v1",
 "repositoryId":"springmaster","mode":"analysis","baseCommit":base,"integrationBranch":"main","riskClass":"low","changeClasses":["test"],
 "allowedPaths":["README.md"],"forbiddenPaths":[".git/**","patches/**","exports/**","target/**","build/**","tmp/**"],
 "limits":{"maxChangedFiles":0,"maxNetAddedBytes":0},
 "capabilities":{"mayModifyTests":False,"mayModifyGovernance":False,"mayModifyContracts":False,"mayCommit":False,"mayPush":False,"network":"disabled"},
 "qualificationCommands":[{"id":"targeted-check","argv":["git","status","--short"],"timeoutSeconds":30},{"id":"diff-check","argv":["git","diff","--check"],"timeoutSeconds":30}],
 "requiredEvidence":["task-contract","task-contract-sha256","prepare-record","integration-pre-state","worktree-pre-state","operator-command-effect","operator-command-effect-sha256","invocation-record","invocation-record-sha256","changed-path-report","qualification-records","final-result","cleanup-disposition"],
 "completionCriteria":{"postcheckPass":True,"allQualificationCommandsPass":True,"requiredEvidenceComplete":True,"invocationRecordRequired":True,"explicitCleanupDisposition":True}
}
open(p,'w').write(json.dumps(value,indent=2)+'\n')
PY
PREP="$(${REPO}/bin/agent-task.sh --project-root "${REPO}" --format json prepare "${TASK_JSON}")"
TASK_WORKTREE="$(python3 -c 'import json,sys;print(json.load(sys.stdin)["worktreePath"])' <<<"${PREP}")"
PROMPT="${TMP}/analysis.prompt.txt"
printf '%s\n' 'Analyze only. Do not modify files.' > "${PROMPT}"

"${REPO}/bin/codex-host-sandbox.sh" --project-root "${REPO}" --bwrap "${TMP}/fake-bin/bwrap" --codex "${TMP}/fake-bin/codex" --format json inspect --out "${TMP}/inspect.json" >/dev/null
python3 - "${TMP}/inspect.json" <<'PY'
import json,sys
v=json.load(open(sys.argv[1])); assert v['status']=='PASS',v
assert v['checks']['outerSandboxDns']['exitCode']==0 and v['checks']['outerSandboxHttps']['exitCode']==0,v['checks']
PY
"${REPO}/bin/codex-host-sandbox.sh" --project-root "${REPO}" --bwrap "${TMP}/fake-bin/bwrap" --codex "${TMP}/fake-bin/codex-linux" --format json inspect --out "${TMP}/inspect-linux.json" >/dev/null
python3 - "${TMP}/inspect-linux.json" <<'PY_LINUX_FORM'
import json,sys
v=json.load(open(sys.argv[1])); assert v['status']=='PASS',v; assert v['codexSandboxCommandForm']=='linux-subcommand',v
print('CODEX_LINUX_SUBCOMMAND_FORM_FIXTURE=PASS')
PY_LINUX_FORM
"${REPO}/bin/codex-host-sandbox.sh" --project-root "${REPO}" --bwrap "${TMP}/fake-bin/bwrap" --codex "${TMP}/fake-bin/codex" --format json probe --task-worktree "${TASK_WORKTREE}" --out "${TMP}/probe.json" >/dev/null
python3 - "${TMP}/probe.json" <<'PY'
import json,sys
v=json.load(open(sys.argv[1])); assert v['status']=='PASS',v['findings']; assert len(v['probes'])==20
PY
test ! -e "${TMP}/runs/codex-host-probes"
printf '%s\n' 'PROBE_SCRATCH_CLEANUP_FIXTURE=PASS'
"${REPO}/bin/codex-host-sandbox.sh" --project-root "${REPO}" --bwrap "${TMP}/fake-bin/bwrap" --codex "${TMP}/fake-bin/codex" --format json invoke --task-id CODEX-HOST-IT-ANALYSIS-001 --prompt "${PROMPT}" --model fixture-model --out "${TMP}/invoke.json" >/dev/null
python3 - "${TMP}/invoke.json" <<'PY'
import json,sys
v=json.load(open(sys.argv[1])); assert v['status']=='PASS'; assert v['taskMode']=='analysis'
assert v['invocationStart']['sha256'] and v['heartbeat']['sha256'],v
start=json.load(open(v['invocationStart']['path'])); assert start['schemaVersion']=='springmaster.codex-invocation-start.v1' and start['process']['owner']=='foreground-compatibility',start
heartbeat=json.load(open(v['heartbeat']['path'])); assert heartbeat['status']=='COMPLETED',heartbeat
j=v['codexJsonlValidation']; assert j['status']=='PASS' and j['commandExecutionCompletedCount']==0 and j['errorEventCount']==0,j
a=v['authHandling']; assert a['permissionProfile']=='springmaster-read-only'; assert a['permissionProfileBase']==':read-only'; assert a['sandboxAuthPath']=='/run/codex-home/auth.json'; assert a['sandboxAuthAccess']=='deny'
e=json.load(open(v['effect']['path'])); argv=e['argv']; assert argv[:4]==['codex','--ask-for-approval','never','exec']; assert '--ignore-user-config' not in argv and '--sandbox' not in argv and '-s' not in argv
PY
"${REPO}/bin/codex-host-sandbox.sh" --project-root "${REPO}" --bwrap "${TMP}/fake-bin/bwrap" --codex "${TMP}/fake-bin/codex" qualify --inspect "${TMP}/inspect.json" --probe "${TMP}/probe.json" --analysis-invocation "${TMP}/invoke.json" --out "${TMP}/qualification.json" --check >/dev/null
python3 - "${TMP}/qualification.json" <<'PY'
import json,sys
v=json.load(open(sys.argv[1])); assert v['status']=='PASS'; assert v['portable'] is False; assert v['realCodex'] is True; assert v['writableCodexAuthorized'] is False
PY

# Finish the analysis task so the fixture can prepare a separate implementation task.
"${REPO}/bin/agent-task.sh" --project-root "${REPO}" --format json postcheck CODEX-HOST-IT-ANALYSIS-001 >/dev/null
"${REPO}/bin/agent-task.sh" --project-root "${REPO}" --format json qualify CODEX-HOST-IT-ANALYSIS-001 >/dev/null
"${REPO}/bin/agent-task.sh" --project-root "${REPO}" --format json cleanup CODEX-HOST-IT-ANALYSIS-001 >/dev/null

IMPLEMENTATION_TASK_JSON="${TMP}/implementation-task.json"
python3 - "${IMPLEMENTATION_TASK_JSON}" "${BASE}" <<'PY'
import json,sys
p,base=sys.argv[1:]
value={
 "schemaVersion":"springmaster.agent-task.v2","taskId":"CODEX-HOST-IT-IMPLEMENTATION-001","pilotId":"springmaster-codex-pilot-v1",
 "repositoryId":"springmaster","mode":"implementation","baseCommit":base,"integrationBranch":"main","riskClass":"low","changeClasses":["test"],
 "allowedPaths":["README.md"],"forbiddenPaths":[".git/**","patches/**","exports/**","target/**","build/**","tmp/**"],
 "limits":{"maxChangedFiles":1,"maxNetAddedBytes":4096},
 "capabilities":{"mayModifyTests":True,"mayModifyGovernance":False,"mayModifyContracts":False,"mayCommit":False,"mayPush":False,"network":"disabled"},
 "qualificationCommands":[{"id":"targeted-check","argv":["git","status","--short"],"timeoutSeconds":30},{"id":"diff-check","argv":["git","diff","--check"],"timeoutSeconds":30}],
 "requiredEvidence":["task-contract","task-contract-sha256","prepare-record","integration-pre-state","worktree-pre-state","operator-command-effect","operator-command-effect-sha256","invocation-record","invocation-record-sha256","changed-path-report","qualification-records","final-result","cleanup-disposition"],
 "completionCriteria":{"postcheckPass":True,"allQualificationCommandsPass":True,"requiredEvidenceComplete":True,"invocationRecordRequired":True,"explicitCleanupDisposition":True}
}
open(p,'w').write(json.dumps(value,indent=2)+'\n')
PY
IMPLEMENTATION_PREP="$(${REPO}/bin/agent-task.sh --project-root "${REPO}" --format json prepare "${IMPLEMENTATION_TASK_JSON}")"
python3 -c 'import json,sys; v=json.load(sys.stdin); assert v["status"]=="PREPARED",v' <<<"${IMPLEMENTATION_PREP}"
IMPLEMENTATION_PROMPT="${TMP}/implementation.prompt.txt"
printf '%s\n' 'Run the fixture implementation command.' > "${IMPLEMENTATION_PROMPT}"
CHANGE_BUNDLE="${TMP}/artifacts/change-bundles/fixture.zip"
mkdir -p "$(dirname "${CHANGE_BUNDLE}")"
printf '%s\n' 'fixture change bundle' > "${CHANGE_BUNDLE}"
"${REPO}/bin/codex-host-sandbox.sh" --project-root "${REPO}" --bwrap "${TMP}/fake-bin/bwrap" --codex "${TMP}/fake-bin/codex" --format json invoke --task-id CODEX-HOST-IT-IMPLEMENTATION-001 --prompt "${IMPLEMENTATION_PROMPT}" --model fixture-model --change-bundle "${CHANGE_BUNDLE}" --out "${TMP}/implementation-invoke.json" >/dev/null
python3 - "${TMP}/implementation-invoke.json" <<'PY'
import json,sys
v=json.load(open(sys.argv[1])); assert v['status']=='PASS' and v['taskMode']=='implementation',v
j=v['codexJsonlValidation']; assert j['status']=='PASS' and j['commandExecutionCompletedCount']==1 and j['errorEventCount']==0,j
e=json.load(open(v['effect']['path'])); assert e['reads']==['task-worktree','external-artifact-root-read-only'],e
assert e['writes']==['task-worktree'],e
assert 'SPRINGMASTER_CODEX_CHANGE_BUNDLE' in e['environmentInputs'],e
PY
"${REPO}/bin/agent-task.sh" --project-root "${REPO}" --format json postcheck CODEX-HOST-IT-IMPLEMENTATION-001 >/dev/null
"${REPO}/bin/agent-task.sh" --project-root "${REPO}" --format json qualify CODEX-HOST-IT-IMPLEMENTATION-001 >/dev/null
"${REPO}/bin/agent-task.sh" --project-root "${REPO}" --format json cleanup CODEX-HOST-IT-IMPLEMENTATION-001 >/dev/null
printf '%s\n' 'CHANGE_BUNDLE_READ_SCOPE_FIXTURE=PASS'

# Prove that a terminal non-zero command inside an implementation turn is
# iterative development evidence, not an invocation failure. The turn itself,
# error events, JSONL integrity, command completion, and outer process exit
# remain fail-closed.
IMPL_FAIL_TASK_JSON="${TMP}/implementation-intermediate-fail-task.json"
python3 - "${IMPL_FAIL_TASK_JSON}" "${BASE}" <<'PY_IMPL_FAIL_TASK'
import json,sys
p,base=sys.argv[1:]
value={
 "schemaVersion":"springmaster.agent-task.v2","taskId":"CODEX-HOST-IT-IMPL-INTERMEDIATE-FAIL-001","pilotId":"springmaster-codex-pilot-v1",
 "repositoryId":"springmaster","mode":"implementation","baseCommit":base,"integrationBranch":"main","riskClass":"low","changeClasses":["test"],
 "allowedPaths":["README.md"],"forbiddenPaths":[".git/**","patches/**","exports/**","target/**","build/**","tmp/**"],
 "limits":{"maxChangedFiles":1,"maxNetAddedBytes":4096},
 "capabilities":{"mayModifyTests":True,"mayModifyGovernance":False,"mayModifyContracts":False,"mayCommit":False,"mayPush":False,"network":"disabled"},
 "qualificationCommands":[{"id":"targeted-check","argv":["git","status","--short"],"timeoutSeconds":30},{"id":"diff-check","argv":["git","diff","--check"],"timeoutSeconds":30}],
 "requiredEvidence":["task-contract","task-contract-sha256","prepare-record","integration-pre-state","worktree-pre-state","operator-command-effect","operator-command-effect-sha256","invocation-record","invocation-record-sha256","changed-path-report","qualification-records","final-result","cleanup-disposition"],
 "completionCriteria":{"postcheckPass":True,"allQualificationCommandsPass":True,"requiredEvidenceComplete":True,"invocationRecordRequired":True,"explicitCleanupDisposition":True}
}
open(p,'w').write(json.dumps(value,indent=2)+'\n')
PY_IMPL_FAIL_TASK
"${REPO}/bin/agent-task.sh" --project-root "${REPO}" --format json prepare "${IMPL_FAIL_TASK_JSON}" >/dev/null
IMPL_FAIL_PROMPT="${TMP}/implementation-intermediate-fail.prompt.txt"
printf '%s\n' 'fixture-command-fail' > "${IMPL_FAIL_PROMPT}"
"${REPO}/bin/codex-host-sandbox.sh" \
  --project-root "${REPO}" \
  --bwrap "${TMP}/fake-bin/bwrap" \
  --codex "${TMP}/fake-bin/codex" \
  --format json \
  invoke \
  --task-id CODEX-HOST-IT-IMPL-INTERMEDIATE-FAIL-001 \
  --prompt "${IMPL_FAIL_PROMPT}" \
  --model fixture-model \
  --change-bundle "${CHANGE_BUNDLE}" \
  --out "${TMP}/implementation-intermediate-fail-invoke.json" >/dev/null
python3 - "${TMP}/implementation-intermediate-fail-invoke.json" <<'PY_IMPL_FAIL_REPORT'
import json,sys
v=json.load(open(sys.argv[1]))
assert v['status']=='PASS' and v['taskMode']=='implementation',v
j=v['codexJsonlValidation']
assert j['status']=='PASS',j
assert j['commandExecutionCompletedCount']==1,j
validation=json.load(open(j['path']))
assert validation['status']=='PASS',validation
assert validation['commandExecutionCompletedCount']==1,validation
assert validation['commandExecutionFailedCount']==1,validation
assert validation['intermediateCommandFailureAllowed'] is True,validation
assert validation['findings']==[],validation
PY_IMPL_FAIL_REPORT
"${REPO}/bin/agent-task.sh" --project-root "${REPO}" --format json postcheck CODEX-HOST-IT-IMPL-INTERMEDIATE-FAIL-001 >/dev/null
"${REPO}/bin/agent-task.sh" --project-root "${REPO}" --format json qualify CODEX-HOST-IT-IMPL-INTERMEDIATE-FAIL-001 >/dev/null
"${REPO}/bin/agent-task.sh" --project-root "${REPO}" --format json cleanup CODEX-HOST-IT-IMPL-INTERMEDIATE-FAIL-001 >/dev/null
printf '%s\n' 'IMPLEMENTATION_INTERMEDIATE_COMMAND_FAILURE_ALLOWED=PASS'

set +e
COCONDO_ARTIFACT_ROOT="${TMP}/missing" "${REPO}/bin/codex-host-sandbox.sh" --project-root "${REPO}" --bwrap "${TMP}/fake-bin/bwrap" --codex "${TMP}/fake-bin/codex" inspect --out "${TMP}/negative.json" >/dev/null
rc=$?
set -e
test "${rc}" -eq 2
python3 - "${TMP}/negative.json" <<'PY'
import json,sys
v=json.load(open(sys.argv[1])); assert v['status']=='TOOL_ERROR'; assert v['errorCode']=='EXTERNAL_ROOT_INVALID'
PY
python3 - "${REPO}/bin/codex-host-sandbox.py" "${TMP}" <<'PY_PROFILE'
import importlib.util,stat,sys
from pathlib import Path
modp=Path(sys.argv[1]); tmp=Path(sys.argv[2]); spec=importlib.util.spec_from_file_location('host_under_test',modp); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
for writable,name,base in ((False,'springmaster-read-only',':read-only'),(True,'springmaster-workspace',':workspace')):
 h=tmp/('profile-rw' if writable else 'profile-ro'); h.mkdir(); (h/'auth.json').write_text('{}\n'); (h/'auth.json').chmod(0o600); meta=m.write_private_codex_config(h,writable_task=writable); text=(h/'config.toml').read_text(); assert meta['permissionProfile']==name; assert meta['permissionProfileBase']==base; assert meta['sandboxAuthAccess']=='deny'; assert f'default_permissions = "{name}"' in text; assert f'extends = "{base}"' in text; assert '"/run/codex-home/auth.json" = "deny"' in text; assert stat.S_IMODE((h/'config.toml').stat().st_mode)==0o600
fake=tmp/'resolver-host'; (fake/'etc').mkdir(parents=True); (fake/'run/systemd/resolve').mkdir(parents=True); target=fake/'run/systemd/resolve/stub-resolv.conf'; target.write_text('nameserver 127.0.0.53\n'); (fake/'etc/resolv.conf').symlink_to('../run/systemd/resolve/stub-resolv.conf')
private=tmp/'resolver-private'; private.mkdir(); meta=m.prepare_resolver_dependency(private,resolv_conf=fake/'etc/resolv.conf',host_run=fake/'run'); assert meta['resolverReexposedReadOnly'] is True; assert meta['resolverSandboxPath']=='/run/systemd/resolve/stub-resolv.conf'; args=m.resolver_bwrap_args(private,meta); assert args[-3:]==['--ro-bind',str(private/'host-resolv.conf'),'/run/systemd/resolve/stub-resolv.conf']; assert '--dir' in args
broken=tmp/'resolver-broken'; broken.mkdir(); (broken/'resolv.conf').symlink_to('missing'); private2=tmp/'resolver-private-2'; private2.mkdir()
try:
 m.prepare_resolver_dependency(private2,resolv_conf=broken/'resolv.conf',host_run=fake/'run')
except m.HostError as exc:
 assert exc.code=='HOST_RESOLVER_INVALID'
else:
 raise AssertionError('broken resolver accepted')
print('PRIVATE_CODEX_PERMISSION_PROFILE_FIXTURE=PASS')
print('PRIVATE_RUN_RESOLVER_REEXPOSURE_FIXTURE=PASS')
PY_PROFILE

python3 - "${REPO}/bin/codex-host-sandbox.py" "${REPO}" "${TMP}" <<'PY_PLAN_INPUT'
import hashlib,importlib.util,json,sys
from pathlib import Path
modp=Path(sys.argv[1]); repo=Path(sys.argv[2]); tmp=Path(sys.argv[3])
spec=importlib.util.spec_from_file_location('host_plan_input_under_test',modp); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
contract=json.load(open(repo/'contracts/governance/agent/codex-host-qualification-contract.json',encoding='utf-8'))
base=m.git(repo,'rev-parse','HEAD'); host=m.host_id(); task_id=f'CODEX-HOSTCAL-ANALYSIS-A777-{host.upper()}'
plan_dir=tmp/'artifacts/host-plan-input'; plan_dir.mkdir(parents=True)
plan=plan_dir/'calibration-plan.json'
value={'schemaVersion':'springmaster.codex-calibration-plan.v2','status':'MATERIALIZED','purpose':'HOST_REQUALIFICATION','baselineCommit':base,'hostId':host,'tasks':[{'taskId':task_id,'mode':'analysis'}]}
plan.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n',encoding='utf-8')
plan_sha=hashlib.sha256(plan.read_bytes()).hexdigest()
run_dir=tmp/'plan-input-run-record'; run_dir.mkdir(parents=True)
(run_dir/'prepare-record.json').write_text(json.dumps({'taskAuthorization':{'source':'sibling-host-calibration-plan','calibrationPlanPath':str(plan.resolve()),'calibrationPlanSha256':plan_sha}},indent=2)+'\n',encoding='utf-8')
task={'taskId':task_id,'mode':'analysis','baseCommit':base}
result=m.host_calibration_plan_input(ctx={'artifactRoot':(tmp/'artifacts').resolve()},root=repo,run_dir=run_dir,task_contract=task,task_id=task_id,mode='analysis',contract=contract)
assert result is not None,result
source,target,env_name=result
assert source==plan.resolve() and target==Path('/run/codex-input/calibration-plan.json') and env_name=='SPRINGMASTER_CODEX_CALIBRATION_PLAN',result
private=tmp/'plan-input-private'; private.mkdir(); (private/'auth.json').write_text('{}\n'); (private/'auth.json').chmod(0o600)
resolver={'resolverReexposedReadOnly':False}
args=m.bwrap_prefix(bwrap=Path('/usr/bin/bwrap'),ctx={'worktreeRoot':tmp.resolve(),'operatorHome':Path('/nonexistent-home')},task=tmp,private_home=private,resolver=resolver,writable_task=False,extra_env={env_name:str(target)},readonly_inputs=[(source,target)])
joined='\n'.join(args)
assert '--ro-bind\n'+str(source)+'\n'+str(target) in joined, args
assert '--setenv\nSPRINGMASTER_CODEX_CALIBRATION_PLAN\n/run/codex-input/calibration-plan.json' in joined,args
plan.write_text(plan.read_text(encoding='utf-8')+' ',encoding='utf-8')
try:
 m.host_calibration_plan_input(ctx={'artifactRoot':(tmp/'artifacts').resolve()},root=repo,run_dir=run_dir,task_contract=task,task_id=task_id,mode='analysis',contract=contract)
except m.HostError as exc:
 assert exc.code=='CALIBRATION_PLAN_INPUT_HASH_MISMATCH',exc.code
else:
 raise AssertionError('calibration plan hash drift accepted')
print('HOST_CALIBRATION_PLAN_INPUT_FIXTURE=PASS')
PY_PLAN_INPUT

python3 - "${REPO}/bin/codex-host-sandbox.py" <<'PY_ACTIVE_TIME'
import importlib.util,sys
from pathlib import Path
modp=Path(sys.argv[1]); spec=importlib.util.spec_from_file_location('host_active_time_under_test',modp); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
credited,excluded=m.active_time_credit(1905.0,10.0)
assert credited==10.0 and excluded==1895.0,(credited,excluded)
credited2,excluded2=m.active_time_credit(2.0,10.0)
assert credited2==2.0 and excluded2==0.0,(credited2,excluded2)
print('ACTIVE_TIME_SUSPEND_GAP_OVER_1800_FIXTURE=PASS')
PY_ACTIVE_TIME

python3 - "${REPO}/bin/codex-host-sandbox.py" "${REPO}/contracts/governance/agent/codex-host-qualification-contract.json" <<'PY_JSONL'
import importlib.util,json,sys
from pathlib import Path
modp=Path(sys.argv[1]); contract=json.load(open(sys.argv[2],encoding='utf-8'))
spec=importlib.util.spec_from_file_location('host_jsonl_under_test',modp); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)

def ev(*lines): return '\n'.join(lines)+'\n'
analysis_ok=m.validate_codex_jsonl(ev('{"type":"turn.started"}','{"type":"turn.completed"}'),'analysis',contract)
assert analysis_ok['status']=='PASS',analysis_ok
impl_ok=m.validate_codex_jsonl(ev(
 '{"type":"turn.started"}',
 '{"type":"item.started","item":{"id":"c1","type":"command_execution","command":"/usr/bin/true"}}',
 '{"type":"item.completed","item":{"id":"c1","type":"command_execution","status":"completed","exit_code":0}}',
 '{"type":"turn.completed"}'),'implementation',contract)
assert impl_ok['status']=='PASS',impl_ok
impl_command_fail=m.validate_codex_jsonl(ev(
 '{"type":"turn.started"}',
 '{"type":"item.started","item":{"id":"c1","type":"command_execution","command":"/usr/bin/false"}}',
 '{"type":"item.completed","item":{"id":"c1","type":"command_execution","status":"failed","exit_code":7}}',
 '{"type":"turn.completed"}'),'implementation',contract)
assert impl_command_fail['status']=='PASS',impl_command_fail
assert impl_command_fail['commandExecutionFailedCount']==1,impl_command_fail
assert impl_command_fail['intermediateCommandFailureAllowed'] is True,impl_command_fail

for name,text,mode in (
 ('malformed',ev('{not-json}','{"type":"turn.completed"}'),'analysis'),
 ('error-item',ev('{"type":"turn.started"}','{"type":"item.completed","item":{"id":"e1","type":"error","message":"boom"}}','{"type":"turn.completed"}'),'analysis'),
 ('impl-no-command',ev('{"type":"turn.started"}','{"type":"turn.completed"}'),'implementation'),
 ('impl-command-incomplete',ev('{"type":"turn.started"}','{"type":"item.started","item":{"id":"c1","type":"command_execution"}}','{"type":"turn.completed"}'),'implementation'),
 ('analysis-command-fail',ev('{"type":"turn.started"}','{"type":"item.completed","item":{"id":"c1","type":"command_execution","status":"failed","exit_code":7}}','{"type":"turn.completed"}'),'analysis'),
):
 result=m.validate_codex_jsonl(text,mode,contract)
 assert result['status']=='FAILED',(name,result)
print('CODEX_JSONL_VALIDATION_FIXTURES=PASS_8_OF_8')
PY_JSONL
rm -rf -- "${REPO}/bin/__pycache__"

# Prove that an outer Codex exit 0 with an inner error is still a failed governed
# invocation, while immutable invocation evidence remains recorded for disposition.
NEG_TASK_JSON="${TMP}/implementation-error-task.json"
python3 - "${NEG_TASK_JSON}" "${BASE}" <<'PY_NEG_TASK'
import json,sys
p,base=sys.argv[1:]
value={
 "schemaVersion":"springmaster.agent-task.v2","taskId":"CODEX-HOST-IT-IMPL-ERROR-001","pilotId":"springmaster-codex-pilot-v1",
 "repositoryId":"springmaster","mode":"implementation","baseCommit":base,"integrationBranch":"main","riskClass":"low","changeClasses":["test"],
 "allowedPaths":["README.md"],"forbiddenPaths":[".git/**","patches/**","exports/**","target/**","build/**","tmp/**"],
 "limits":{"maxChangedFiles":1,"maxNetAddedBytes":4096},
 "capabilities":{"mayModifyTests":True,"mayModifyGovernance":False,"mayModifyContracts":False,"mayCommit":False,"mayPush":False,"network":"disabled"},
 "qualificationCommands":[{"id":"targeted-check","argv":["git","status","--short"],"timeoutSeconds":30},{"id":"diff-check","argv":["git","diff","--check"],"timeoutSeconds":30}],
 "requiredEvidence":["task-contract","task-contract-sha256","prepare-record","integration-pre-state","worktree-pre-state","operator-command-effect","operator-command-effect-sha256","invocation-record","invocation-record-sha256","changed-path-report","qualification-records","final-result","cleanup-disposition"],
 "completionCriteria":{"postcheckPass":True,"allQualificationCommandsPass":True,"requiredEvidenceComplete":True,"invocationRecordRequired":True,"explicitCleanupDisposition":True}
}
open(p,'w').write(json.dumps(value,indent=2)+'\n')
PY_NEG_TASK
"${REPO}/bin/agent-task.sh" --project-root "${REPO}" --format json prepare "${NEG_TASK_JSON}" >/dev/null
NEG_PROMPT="${TMP}/implementation-error.prompt.txt"
printf '%s\n' 'fixture-error-item' > "${NEG_PROMPT}"
set +e
"${REPO}/bin/codex-host-sandbox.sh" --project-root "${REPO}" --bwrap "${TMP}/fake-bin/bwrap" --codex "${TMP}/fake-bin/codex" --format json invoke --task-id CODEX-HOST-IT-IMPL-ERROR-001 --prompt "${NEG_PROMPT}" --model fixture-model --change-bundle "${CHANGE_BUNDLE}" --out "${TMP}/implementation-error-invoke.json" >/dev/null
NEG_RC=$?
set -e
test "${NEG_RC}" -eq 1
python3 - "${TMP}/implementation-error-invoke.json" <<'PY_NEG_REPORT'
import json,sys
v=json.load(open(sys.argv[1])); assert v['status']=='FAILED' and v['exitCode']==0,v
j=v['codexJsonlValidation']; assert j['status']=='FAILED' and j['errorEventCount']==1 and j['commandExecutionCompletedCount']==0,j
PY_NEG_REPORT
NEG_STATUS="$(${REPO}/bin/agent-task.sh --project-root "${REPO}" --format json status CODEX-HOST-IT-IMPL-ERROR-001)"
python3 -c 'import json,sys; v=json.load(sys.stdin); assert v["status"]=="PREPARED" and v["codexInvocation"]=="RECORDED",v' <<<"${NEG_STATUS}"
printf '%s\n' 'CODEX_OUTER_ZERO_INNER_ERROR_FAIL_CLOSED=PASS'
set +e
NEG_CLEANUP="$(${REPO}/bin/agent-task.sh --project-root "${REPO}" --format json cleanup CODEX-HOST-IT-IMPL-ERROR-001)"
NEG_CLEANUP_RC=$?
set -e
test "${NEG_CLEANUP_RC}" -eq 1
python3 -c 'import json,sys;v=json.load(sys.stdin);assert v["status"]=="CLEANED_INCOMPLETE",v' <<<"${NEG_CLEANUP}"

# Durable-evidence runtime fixtures: a real process failure, active-time timeout,
# no-progress timeout, streaming visibility, and an actual SIGSTOP/SIGCONT gap.
prepare_runtime_analysis_task() {
  local task_id="$1"
  local task_json="${TMP}/${task_id,,}.json"
  python3 - "${task_json}" "${BASE}" "${task_id}" <<'PY_RUNTIME_TASK'
import json,sys
p,base,task_id=sys.argv[1:]
value={
 "schemaVersion":"springmaster.agent-task.v2","taskId":task_id,"pilotId":"springmaster-codex-pilot-v1",
 "repositoryId":"springmaster","mode":"analysis","baseCommit":base,"integrationBranch":"main","riskClass":"low","changeClasses":["test"],
 "allowedPaths":["README.md"],"forbiddenPaths":[".git/**","patches/**","exports/**","target/**","build/**","tmp/**"],
 "limits":{"maxChangedFiles":0,"maxNetAddedBytes":0},
 "capabilities":{"mayModifyTests":False,"mayModifyGovernance":False,"mayModifyContracts":False,"mayCommit":False,"mayPush":False,"network":"disabled"},
 "qualificationCommands":[{"id":"targeted-check","argv":["git","status","--short"],"timeoutSeconds":30},{"id":"diff-check","argv":["git","diff","--check"],"timeoutSeconds":30}],
 "requiredEvidence":["task-contract","task-contract-sha256","prepare-record","integration-pre-state","worktree-pre-state","operator-command-effect","operator-command-effect-sha256","invocation-record","invocation-record-sha256","changed-path-report","qualification-records","final-result","cleanup-disposition"],
 "completionCriteria":{"postcheckPass":True,"allQualificationCommandsPass":True,"requiredEvidenceComplete":True,"invocationRecordRequired":True,"explicitCleanupDisposition":True}
}
open(p,'w').write(json.dumps(value,indent=2)+'\n')
PY_RUNTIME_TASK
  "${REPO}/bin/agent-task.sh" --project-root "${REPO}" --format json prepare "${task_json}" >/dev/null
}
cleanup_incomplete_runtime_task() {
  local task_id="$1"
  set +e
  "${REPO}/bin/agent-task.sh" --project-root "${REPO}" --format json cleanup "${task_id}" --discard >/dev/null
  local rc=$?
  set -e
  test "${rc}" -eq 1
}

prepare_runtime_analysis_task CODEX-HOST-IT-PROCESS-FAIL-001
printf '%s\n' 'fixture-process-fail' > "${TMP}/process-fail.prompt.txt"
set +e
"${REPO}/bin/codex-host-sandbox.sh" --project-root "${REPO}" --bwrap "${TMP}/fake-bin/bwrap" --codex "${TMP}/fake-bin/codex" --format json invoke --task-id CODEX-HOST-IT-PROCESS-FAIL-001 --prompt "${TMP}/process-fail.prompt.txt" --model fixture-model --out "${TMP}/process-fail.json" >/dev/null
PROCESS_FAIL_RC=$?
set -e
test "${PROCESS_FAIL_RC}" -eq 1
python3 - "${TMP}/process-fail.json" <<'PY_PROCESS_FAIL'
import json,sys
v=json.load(open(sys.argv[1])); assert v['status']=='FAILED' and v['exitCode']==7,v
assert v['invocationStart']['sha256'] and v['stderr']['sha256'],v
inv=json.load(open(v['invocation']['path'])); assert inv['execution']['status']=='FAILED' and inv['execution']['exitCode']==7,inv
PY_PROCESS_FAIL
PROCESS_FAIL_STATUS="$(${REPO}/bin/agent-task.sh --project-root "${REPO}" --format json status CODEX-HOST-IT-PROCESS-FAIL-001)"
python3 -c 'import json,sys;v=json.load(sys.stdin);assert v["codexInvocation"]=="RECORDED",v' <<<"${PROCESS_FAIL_STATUS}"
cleanup_incomplete_runtime_task CODEX-HOST-IT-PROCESS-FAIL-001
printf '%s\n' 'STARTED_FAILED_PROCESS_RECORDED_FIXTURE=PASS'

# Shorten the fixture heartbeat only; production contract remains 2s/10s.
python3 - "${REPO}/contracts/governance/agent/codex-host-qualification-contract.json" <<'PY_FAST_HEARTBEAT'
import json,sys
p=sys.argv[1]; v=json.load(open(p,encoding='utf-8')); v['durableInvocation']['heartbeatIntervalSeconds']=1; v['durableInvocation']['maxActiveCreditPerHeartbeatSeconds']=1
open(p,'w',encoding='utf-8').write(json.dumps(v,indent=2,sort_keys=True)+'\n')
PY_FAST_HEARTBEAT
git -C "${REPO}" add -- contracts/governance/agent/codex-host-qualification-contract.json
git -C "${REPO}" commit -q -m fixture-fast-heartbeat
BASE="$(git -C "${REPO}" rev-parse HEAD)"

prepare_runtime_analysis_task CODEX-HOST-IT-STREAMING-001
printf '%s\n' 'fixture-streaming' > "${TMP}/streaming.prompt.txt"
"${REPO}/bin/codex-host-sandbox.sh" --project-root "${REPO}" --bwrap "${TMP}/fake-bin/bwrap" --codex "${TMP}/fake-bin/codex" --format json invoke --task-id CODEX-HOST-IT-STREAMING-001 --prompt "${TMP}/streaming.prompt.txt" --model fixture-model --out "${TMP}/streaming.json" >/dev/null &
STREAM_PID=$!
FIXTURE_HOST_ID="$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["hostId"])' "${TMP}/inspect.json")"
STREAM_EVIDENCE="${TMP}/artifacts/codex-host-qualification/${FIXTURE_HOST_ID}/${BASE}/codex-host-it-streaming-001"
for _ in $(seq 1 50); do
  if [[ -s "${STREAM_EVIDENCE}/codex.stdout.jsonl" && -f "${STREAM_EVIDENCE}/heartbeat.json" ]]; then break; fi
  sleep 0.1
done
test -s "${STREAM_EVIDENCE}/codex.stdout.jsonl"
test -f "${STREAM_EVIDENCE}/heartbeat.json"
kill -0 "${STREAM_PID}"
wait "${STREAM_PID}"
python3 - "${TMP}/streaming.json" <<'PY_STREAMING'
import json,sys
v=json.load(open(sys.argv[1])); assert v['status']=='PASS',v
PY_STREAMING
"${REPO}/bin/agent-task.sh" --project-root "${REPO}" postcheck CODEX-HOST-IT-STREAMING-001 >/dev/null
"${REPO}/bin/agent-task.sh" --project-root "${REPO}" qualify CODEX-HOST-IT-STREAMING-001 >/dev/null
"${REPO}/bin/agent-task.sh" --project-root "${REPO}" cleanup CODEX-HOST-IT-STREAMING-001 >/dev/null
printf '%s\n' 'STREAMING_EVIDENCE_VISIBLE_WHILE_RUNNING_FIXTURE=PASS'

prepare_runtime_analysis_task CODEX-HOST-IT-ACTIVE-TIMEOUT-001
printf '%s\n' 'fixture-active-timeout' > "${TMP}/active-timeout.prompt.txt"
set +e
"${REPO}/bin/codex-host-sandbox.sh" --project-root "${REPO}" --bwrap "${TMP}/fake-bin/bwrap" --codex "${TMP}/fake-bin/codex" --format json invoke --task-id CODEX-HOST-IT-ACTIVE-TIMEOUT-001 --prompt "${TMP}/active-timeout.prompt.txt" --model fixture-model --active-timeout-seconds 2 --out "${TMP}/active-timeout.json" >/dev/null
ACTIVE_TIMEOUT_RC=$?
set -e
test "${ACTIVE_TIMEOUT_RC}" -eq 1
python3 - "${TMP}/active-timeout.json" <<'PY_ACTIVE_TIMEOUT'
import json,sys
v=json.load(open(sys.argv[1])); assert v['status']=='FAILED' and v['terminalReason']=='ACTIVE_TIME_TIMEOUT',v
for key in ('invocationStart','invocation','heartbeat','stdout','stderr'): assert v[key]['sha256'],(key,v)
inv=json.load(open(v['invocation']['path'])); assert inv['execution']['status']=='INTERRUPTED',inv
PY_ACTIVE_TIMEOUT
cleanup_incomplete_runtime_task CODEX-HOST-IT-ACTIVE-TIMEOUT-001
printf '%s\n' 'ACTIVE_TIME_TIMEOUT_EVIDENCE_FIXTURE=PASS'

prepare_runtime_analysis_task CODEX-HOST-IT-NO-PROGRESS-001
printf '%s\n' 'fixture-no-progress' > "${TMP}/no-progress.prompt.txt"
set +e
"${REPO}/bin/codex-host-sandbox.sh" --project-root "${REPO}" --bwrap "${TMP}/fake-bin/bwrap" --codex "${TMP}/fake-bin/codex" --format json invoke --task-id CODEX-HOST-IT-NO-PROGRESS-001 --prompt "${TMP}/no-progress.prompt.txt" --model fixture-model --active-timeout-seconds 20 --no-progress-timeout-seconds 2 --out "${TMP}/no-progress.json" >/dev/null
NO_PROGRESS_RC=$?
set -e
test "${NO_PROGRESS_RC}" -eq 1
python3 - "${TMP}/no-progress.json" <<'PY_NO_PROGRESS'
import json,sys
v=json.load(open(sys.argv[1])); assert v['status']=='FAILED' and v['terminalReason']=='NO_PROGRESS_TIMEOUT',v
assert v['activeElapsedSeconds'] >= 2,v
PY_NO_PROGRESS
cleanup_incomplete_runtime_task CODEX-HOST-IT-NO-PROGRESS-001
printf '%s\n' 'NO_PROGRESS_ACTIVE_TIME_TIMEOUT_FIXTURE=PASS'

prepare_runtime_analysis_task CODEX-HOST-IT-SUSPEND-GAP-001
printf '%s\n' 'fixture-suspend-gap' > "${TMP}/suspend-gap.prompt.txt"
"${REPO}/bin/codex-host-sandbox.sh" --project-root "${REPO}" --bwrap "${TMP}/fake-bin/bwrap" --codex "${TMP}/fake-bin/codex" --format json invoke --task-id CODEX-HOST-IT-SUSPEND-GAP-001 --prompt "${TMP}/suspend-gap.prompt.txt" --model fixture-model --active-timeout-seconds 20 --out "${TMP}/suspend-gap.json" >/dev/null &
SUSPEND_LAUNCH_PID=$!
SUSPEND_EVIDENCE="${TMP}/artifacts/codex-host-qualification/${FIXTURE_HOST_ID}/${BASE}/codex-host-it-suspend-gap-001"
SUSPEND_WORKER_PID=""
SUSPEND_CODEX_PGID=""
for _ in $(seq 1 100); do
  if [[ -s "${SUSPEND_EVIDENCE}/heartbeat.json" ]]; then
    read -r SUSPEND_WORKER_PID SUSPEND_CODEX_PGID < <(
      python3 - "${SUSPEND_EVIDENCE}/heartbeat.json" <<'PY_SUSPEND_PIDS'
import json,sys
v=json.load(open(sys.argv[1]))
worker=v.get('workerPid')
codex_pgid=v.get('codexPgid')
if isinstance(worker,int) and worker > 1 and isinstance(codex_pgid,int) and codex_pgid > 1:
    print(worker,codex_pgid)
PY_SUSPEND_PIDS
    )
    if [[ "${SUSPEND_WORKER_PID}" =~ ^[0-9]+$ && "${SUSPEND_CODEX_PGID}" =~ ^[0-9]+$ ]] \
      && kill -0 "${SUSPEND_WORKER_PID}" 2>/dev/null \
      && kill -0 -- "-${SUSPEND_CODEX_PGID}" 2>/dev/null; then
      break
    fi
  fi
  SUSPEND_WORKER_PID=""
  SUSPEND_CODEX_PGID=""
  sleep 0.1
done
[[ "${SUSPEND_WORKER_PID}" =~ ^[0-9]+$ ]]
[[ "${SUSPEND_CODEX_PGID}" =~ ^[0-9]+$ ]]
kill -STOP -- "-${SUSPEND_CODEX_PGID}"
kill -STOP "${SUSPEND_WORKER_PID}"
WORKER_STATE=""
CODEX_STATE=""
for _ in $(seq 1 50); do
  WORKER_STATE="$(awk '/^State:/ {print $2}' "/proc/${SUSPEND_WORKER_PID}/status" 2>/dev/null || true)"
  CODEX_STATE="$(awk '/^State:/ {print $2}' "/proc/${SUSPEND_CODEX_PGID}/status" 2>/dev/null || true)"
  if [[ "${WORKER_STATE}" == "T" && "${CODEX_STATE}" == "T" ]]; then
    break
  fi
  sleep 0.05
done
[[ "${WORKER_STATE}" == "T" ]]
[[ "${CODEX_STATE}" == "T" ]]
sleep 3
kill -CONT -- "-${SUSPEND_CODEX_PGID}"
kill -CONT "${SUSPEND_WORKER_PID}"
wait "${SUSPEND_LAUNCH_PID}"
python3 - "${TMP}/suspend-gap.json" <<'PY_SUSPEND'
import json,sys
v=json.load(open(sys.argv[1])); assert v['status']=='PASS',v
assert v['excludedGapSeconds'] >= 1.5,v
PY_SUSPEND
"${REPO}/bin/agent-task.sh" --project-root "${REPO}" postcheck CODEX-HOST-IT-SUSPEND-GAP-001 >/dev/null
"${REPO}/bin/agent-task.sh" --project-root "${REPO}" qualify CODEX-HOST-IT-SUSPEND-GAP-001 >/dev/null
"${REPO}/bin/agent-task.sh" --project-root "${REPO}" cleanup CODEX-HOST-IT-SUSPEND-GAP-001 >/dev/null
printf '%s\n' 'SIGSTOP_SIGCONT_ACTIVE_GAP_FIXTURE=PASS'

# End-to-end: an unpromoted host-requalification analysis consumes the exact
# sibling plan recorded by agent-task prepare, without operator plan discovery.
python3 - "${REPO}/contracts/governance/agent/codex-pilot-contract.json" <<'PY_UNPROMOTE'
import json,sys
from pathlib import Path
p=Path(sys.argv[1]); v=json.loads(p.read_text(encoding='utf-8'))
other='0'*24
v['writePromotion']['hostId']=other
v['writeAuthorizations']['entries']=[dict(v['writePromotion'])]
p.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n',encoding='utf-8')
PY_UNPROMOTE
git -C "${REPO}" add -- contracts/governance/agent/codex-pilot-contract.json
git -C "${REPO}" commit -q -m fixture-unpromoted-host
HOST_BASE="$(git -C "${REPO}" rev-parse HEAD)"
HOST_PLAN="${TMP}/artifacts/host-requalification-e2e"
"${REPO}/bin/codex-calibration.sh" materialize --out "${HOST_PLAN}" --baseline "${HOST_BASE}" --attempt 777 --host-requalification >/dev/null
HOST_ID="$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["hostId"])' "${HOST_PLAN}/calibration-plan.json")"
HOST_TASK_ID="CODEX-HOSTCAL-ANALYSIS-A777-${HOST_ID^^}"
HOST_TASK="${HOST_PLAN}/${HOST_TASK_ID,,}.json"
HOST_PROMPT="${HOST_PLAN}/${HOST_TASK_ID,,}.prompt.txt"
HOST_PREP="$(${REPO}/bin/agent-task.sh --project-root "${REPO}" --format json prepare "${HOST_TASK}")"
python3 -c 'import json,sys;v=json.load(sys.stdin);assert v["taskAuthorization"]["source"]=="sibling-host-calibration-plan",v' <<<"${HOST_PREP}"
"${REPO}/bin/codex-host-sandbox.sh" --project-root "${REPO}" --bwrap "${TMP}/fake-bin/bwrap" --codex "${TMP}/fake-bin/codex" --format json invoke --task-id "${HOST_TASK_ID}" --prompt "${HOST_PROMPT}" --model fixture-model --out "${TMP}/host-plan-input-invoke.json" >/dev/null
python3 - "${TMP}/host-plan-input-invoke.json" <<'PY_HOST_INPUT_E2E'
import json,sys
v=json.load(open(sys.argv[1])); assert v['status']=='PASS' and v['taskMode']=='analysis',v
e=json.load(open(v['effect']['path']))
assert e['reads']==['task-worktree','host-calibration-plan-read-only'],e
assert 'SPRINGMASTER_CODEX_CALIBRATION_PLAN' in e['environmentInputs'],e
print('HOST_CALIBRATION_PLAN_INPUT_E2E=PASS')
PY_HOST_INPUT_E2E
"${REPO}/bin/agent-task.sh" --project-root "${REPO}" --format json postcheck "${HOST_TASK_ID}" >/dev/null
"${REPO}/bin/agent-task.sh" --project-root "${REPO}" --format json qualify "${HOST_TASK_ID}" >/dev/null
"${REPO}/bin/agent-task.sh" --project-root "${REPO}" --format json cleanup "${HOST_TASK_ID}" >/dev/null

printf '%s\n' 'CODEX_HOST_SANDBOX_IT=PASS'
