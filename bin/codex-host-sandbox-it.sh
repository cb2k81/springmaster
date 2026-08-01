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
mkdir -p "${REPO}/bin" "${REPO}/.cocondo/tooling" "${REPO}/contracts/governance/agent"
cp -- \
  "${ROOT}/bin/agent-task.py" \
  "${ROOT}/bin/agent-task.sh" \
  "${ROOT}/bin/codex-host-sandbox.py" \
  "${ROOT}/bin/codex-host-sandbox.sh" \
  "${REPO}/bin/"
cp -- \
  "${ROOT}/contracts/governance/agent/codex-pilot-contract.json" \
  "${ROOT}/contracts/governance/agent/codex-host-qualification-contract.json" \
  "${REPO}/contracts/governance/agent/"
cp -- "${ROOT}/.cocondo/tooling/project.env" "${REPO}/.cocondo/tooling/project.env"
printf '%s\n' 'host sandbox fixture' > "${REPO}/README.md"
python3 - "${REPO}/contracts/governance/agent/codex-pilot-contract.json" <<'PY'
import json,sys
from pathlib import Path
p=Path(sys.argv[1])
d=json.loads(p.read_text(encoding="utf-8"))
d["pilot"]["currentLifecycle"]="PILOT_WRITE_READY"
p.write_text(json.dumps(d,indent=2,sort_keys=True)+"\n",encoding="utf-8")
PY
chmod 755 "${REPO}/bin/agent-task.py" "${REPO}/bin/agent-task.sh" "${REPO}/bin/codex-host-sandbox.py" "${REPO}/bin/codex-host-sandbox.sh"
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
import os,subprocess,sys
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
import os,subprocess,sys
args=sys.argv[1:]
if args==['--version']:
 print('codex-cli fixture-1'); raise SystemExit(0)
if args[:2]==['exec','--help']:
 print('fixture exec help'); raise SystemExit(0)
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
 _=sys.stdin.read()
 print('{"type":"message","role":"assistant","content":"fixture pass"}')
 raise SystemExit(0)
raise SystemExit(2)
CODEX
chmod 755 "${TMP}/fake-bin/bwrap" "${TMP}/fake-bin/codex"

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
PY
"${REPO}/bin/codex-host-sandbox.sh" --project-root "${REPO}" --bwrap "${TMP}/fake-bin/bwrap" --codex "${TMP}/fake-bin/codex" --format json probe --task-worktree "${TASK_WORKTREE}" --out "${TMP}/probe.json" >/dev/null
python3 - "${TMP}/probe.json" <<'PY'
import json,sys
v=json.load(open(sys.argv[1])); assert v['status']=='PASS',v['findings']; assert len(v['probes'])==20
PY
"${REPO}/bin/codex-host-sandbox.sh" --project-root "${REPO}" --bwrap "${TMP}/fake-bin/bwrap" --codex "${TMP}/fake-bin/codex" --format json invoke --task-id CODEX-HOST-IT-ANALYSIS-001 --prompt "${PROMPT}" --model fixture-model --out "${TMP}/invoke.json" >/dev/null
python3 - "${TMP}/invoke.json" <<'PY'
import json,sys
v=json.load(open(sys.argv[1])); assert v['status']=='PASS'; assert v['taskMode']=='analysis'
PY
"${REPO}/bin/codex-host-sandbox.sh" --project-root "${REPO}" --bwrap "${TMP}/fake-bin/bwrap" --codex "${TMP}/fake-bin/codex" qualify --inspect "${TMP}/inspect.json" --probe "${TMP}/probe.json" --analysis-invocation "${TMP}/invoke.json" --out "${TMP}/qualification.json" --check >/dev/null
python3 - "${TMP}/qualification.json" <<'PY'
import json,sys
v=json.load(open(sys.argv[1])); assert v['status']=='PASS'; assert v['portable'] is False; assert v['realCodex'] is True; assert v['writableCodexAuthorized'] is False
PY

set +e
COCONDO_ARTIFACT_ROOT="${TMP}/missing" "${REPO}/bin/codex-host-sandbox.sh" --project-root "${REPO}" --bwrap "${TMP}/fake-bin/bwrap" --codex "${TMP}/fake-bin/codex" inspect --out "${TMP}/negative.json" >/dev/null
rc=$?
set -e
test "${rc}" -eq 2
python3 - "${TMP}/negative.json" <<'PY'
import json,sys
v=json.load(open(sys.argv[1])); assert v['status']=='TOOL_ERROR'; assert v['errorCode']=='EXTERNAL_ROOT_INVALID'
PY
printf '%s\n' 'CODEX_HOST_SANDBOX_IT=PASS'
