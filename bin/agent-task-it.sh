#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
TMP_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/agent-task-it.XXXXXX")"
CURRENT_STEP=bootstrap
cleanup() {
  local rc=$?
  trap - EXIT
  if [[ "${rc}" -ne 0 ]]; then
    printf '%s\n' 'AGENT_TASK_IT=FAILED' "FAILED_STEP=${CURRENT_STEP}" "FIXTURE_ROOT=${TMP_ROOT}" >&2
  fi
  rm -rf "${TMP_ROOT}"
  exit "${rc}"
}
trap cleanup EXIT

export HOME="${TMP_ROOT}/home"
export XDG_CONFIG_HOME="${TMP_ROOT}/xdg-config"
export GIT_CONFIG_NOSYSTEM=1
export GIT_CONFIG_GLOBAL=/dev/null
export GIT_TEMPLATE_DIR="${TMP_ROOT}/git-template"
export GIT_TERMINAL_PROMPT=0
mkdir -p "${HOME}" "${XDG_CONFIG_HOME}" "${GIT_TEMPLATE_DIR}"
unset GIT_DIR GIT_WORK_TREE GIT_COMMON_DIR GIT_INDEX_FILE
unset GIT_OBJECT_DIRECTORY GIT_ALTERNATE_OBJECT_DIRECTORIES

REPO="${TMP_ROOT}/repo"
mkdir -p "${REPO}/bin" "${REPO}/.cocondo/tooling" "${REPO}/contracts/governance/agent"
cp "${PROJECT_ROOT}/bin/agent-task.py" "${REPO}/bin/agent-task.py"
cp "${PROJECT_ROOT}/bin/agent-task.sh" "${REPO}/bin/agent-task.sh"
cp "${PROJECT_ROOT}/contracts/governance/agent/codex-pilot-contract.json" "${REPO}/contracts/governance/agent/codex-pilot-contract.json"
chmod +x "${REPO}/bin/agent-task.py" "${REPO}/bin/agent-task.sh"
cat > "${REPO}/.cocondo/tooling/project.env" <<'ENV'
CPATCH_PROJECT_ID=springmaster
CPATCH_INTEGRATION_BRANCH=main
ENV
printf '%s\n' 'baseline' > "${REPO}/README.md"
printf '%0100d\n' 0 > "${REPO}/large.txt"
CURRENT_STEP=git-init
git -c init.defaultRefFormat=files -C "${REPO}" init -q -b main
git -C "${REPO}" config user.email agent-task@example.invalid
git -C "${REPO}" config user.name agent-task-it
git -C "${REPO}" add .
git -C "${REPO}" commit -q -m baseline
BASE="$(git -C "${REPO}" rev-parse HEAD)"

export COCONDO_WORKTREE_ROOT="${TMP_ROOT}/worktrees"
export COCONDO_AGENT_RUN_ROOT="${TMP_ROOT}/runs"
export COCONDO_ARTIFACT_ROOT="${TMP_ROOT}/artifacts"
mkdir -p "${COCONDO_WORKTREE_ROOT}" "${COCONDO_AGENT_RUN_ROOT}" "${COCONDO_ARTIFACT_ROOT}"

make_task() {
  local task_id="$1"
  local mode="$2"
  local risk="$3"
  local change_classes_json="$4"
  local allowed="$5"
  local forbidden="$6"
  local max_files="$7"
  local max_bytes="$8"
  local commands_json="$9"
  local path="${10}"
  local may_tests="${11:-false}"
  local may_governance="${12:-false}"
  local may_contracts="${13:-false}"
  python3 - "${task_id}" "${mode}" "${risk}" "${change_classes_json}" "${allowed}" "${forbidden}" "${max_files}" "${max_bytes}" "${commands_json}" "${path}" "${may_tests}" "${may_governance}" "${may_contracts}" "${BASE}" <<'PY'
import json, sys
from pathlib import Path
(task_id, mode, risk, classes, allowed, forbidden, max_files, max_bytes,
 commands, target, may_tests, may_governance, may_contracts, base) = sys.argv[1:]
value = {
  "schemaVersion": "springmaster.agent-task.v2",
  "taskId": task_id,
  "pilotId": "springmaster-codex-pilot-v1",
  "repositoryId": "springmaster",
  "mode": mode,
  "baseCommit": base,
  "integrationBranch": "main",
  "riskClass": risk,
  "changeClasses": json.loads(classes),
  "allowedPaths": [allowed],
  "forbiddenPaths": [forbidden, ".git/**"],
  "limits": {"maxChangedFiles": int(max_files), "maxNetAddedBytes": int(max_bytes)},
  "capabilities": {
    "mayModifyTests": may_tests == "true",
    "mayModifyGovernance": may_governance == "true",
    "mayModifyContracts": may_contracts == "true",
    "mayCommit": False,
    "mayPush": False,
    "network": "disabled"
  },
  "qualificationCommands": json.loads(commands),
  "requiredEvidence": [
    "task-contract", "task-contract-sha256", "prepare-record", "integration-pre-state",
    "worktree-pre-state", "operator-command-effect", "operator-command-effect-sha256",
    "invocation-record", "invocation-record-sha256", "changed-path-report",
    "qualification-records", "final-result", "cleanup-disposition"
  ],
  "completionCriteria": {
    "postcheckPass": True,
    "allQualificationCommandsPass": True,
    "requiredEvidenceComplete": True,
    "invocationRecordRequired": True,
    "explicitCleanupDisposition": True
  }
}
Path(target).write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
PY
}

record_invocation() {
  local task_id="$1"
  local worktree="$2"
  local stem
  stem="$(tr '[:upper:]' '[:lower:]' <<<"${task_id}")"
  local status="${3:-COMPLETED}"
  local exit_code="${4:-0}"
  local effect="${COCONDO_ARTIFACT_ROOT}/${stem}-effect.json"
  local record="${COCONDO_ARTIFACT_ROOT}/${stem}-record.json"
  local task_contract="${COCONDO_AGENT_RUN_ROOT}/${stem}/task-contract.json"
  python3 - "${task_id}" "${worktree}" "${effect}" "${record}" "${status}" "${exit_code}" "${task_contract}" <<'PY'
import json, sys
from pathlib import Path
task_id, worktree, effect_path, record_path, status, exit_code, task_path = sys.argv[1:]
exit_code = int(exit_code)
mode = json.loads(Path(task_path).read_text(encoding="utf-8"))["mode"]
model = "fixture-model"
if mode == "implementation":
    cli_sandbox = "workspace-write"
    record_sandbox = "linux-bwrap-workspace-write"
    writes = ["task-worktree"]
    mutation = "task-worktree-only"
else:
    cli_sandbox = "read-only"
    record_sandbox = "linux-bwrap-read-only"
    writes = []
    mutation = "none"
argv = [
  "codex", "exec", "--ephemeral", "--ignore-user-config", "--ignore-rules", "--json",
  "--model", model, "--sandbox", cli_sandbox, "--ask-for-approval", "never",
  "fixture-calibration"
]
effect = {
  "schemaVersion": "springmaster.operator-command-effect.v1",
  "commandId": "codex-calibration",
  "taskId": task_id,
  "purpose": "Agent-task integration fixture calibration",
  "argv": argv,
  "workingDirectory": worktree,
  "reads": ["task-worktree"],
  "writes": writes,
  "network": "codex-control-plane-only",
  "repositoryMutation": mutation,
  "destructiveActions": [],
  "directoryCreationPolicy": "declared-task-paths-only",
  "overwritePolicy": "declared-task-paths-only",
  "environmentInputs": ["PATH"]
}
record = {
  "schemaVersion": "springmaster.codex-invocation-record.v1",
  "taskId": task_id,
  "commandId": "codex-calibration",
  "recordedAt": "2026-07-27T00:00:02Z",
  "agent": {"name": "codex", "cliVersion": "fixture-1", "model": model},
  "execution": {
    "argv": argv,
    "workingDirectory": worktree,
    "sandboxProfile": record_sandbox,
    "approvalPolicy": "never",
    "platformSandbox": {
      "implementation": "linux-bwrap",
      "workspaceRoot": worktree,
      "additionalWritableRoots": [],
      "operatorHomeWritable": False,
      "operatorDownloadsWritable": False,
      "integrationWorktreeWritable": False,
      "gitCommonDirectoryWritable": False,
      "externalRunRootWritable": False,
      "externalArtifactRootWritable": False,
      "temporaryDirectoriesWritable": False
    },
    "environmentKeys": ["PATH"],
    "startedAt": "2026-07-27T00:00:00Z",
    "finishedAt": "2026-07-27T00:00:01Z",
    "exitCode": exit_code,
    "status": status
  }
}
Path(effect_path).write_text(json.dumps(effect, indent=2) + "\n", encoding="utf-8")
Path(record_path).write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
PY
  "${REPO}/bin/agent-task.sh" --project-root "${REPO}" record-invocation "${task_id}" --effect "${effect}" --record "${record}" >/dev/null
}


DIFF_COMMANDS='[{"id":"diff-check","argv":["git","diff","--check"],"timeoutSeconds":30}]'

CURRENT_STEP=validate-prepare-pass
TASK1="${TMP_ROOT}/task1.json"
make_task AGENT-FIXTURE-001 implementation low '["fixture"]' README.md forbidden.txt 2 4096 "${DIFF_COMMANDS}" "${TASK1}"
"${REPO}/bin/agent-task.sh" --project-root "${REPO}" validate "${TASK1}" >/dev/null
PREPARE1="$("${REPO}/bin/agent-task.sh" --project-root "${REPO}" --format json prepare "${TASK1}")"
WORKTREE1="$(python3 -c 'import json,sys;print(json.load(sys.stdin)["worktreePath"])' <<<"${PREPARE1}")"
test "$(git -C "${WORKTREE1}" branch --show-current)" = ''
record_invocation AGENT-FIXTURE-001 "${WORKTREE1}"
printf '%s\n' 'changed' > "${WORKTREE1}/README.md"
"${REPO}/bin/agent-task.sh" --project-root "${REPO}" postcheck AGENT-FIXTURE-001 >/dev/null
"${REPO}/bin/agent-task.sh" --project-root "${REPO}" qualify AGENT-FIXTURE-001 >/dev/null
"${REPO}/bin/agent-task.sh" --project-root "${REPO}" cleanup AGENT-FIXTURE-001 --discard >/dev/null
test ! -e "${WORKTREE1}"
grep -F '"codexInvocation": "RECORDED"' "${COCONDO_AGENT_RUN_ROOT}/agent-fixture-001/final-result.json" >/dev/null
grep -F '"complete": true' "${COCONDO_AGENT_RUN_ROOT}/agent-fixture-001/cleanup-disposition.json" >/dev/null

CURRENT_STEP=missing-invocation-blocks-qualification
TASK2="${TMP_ROOT}/task2.json"
make_task AGENT-FIXTURE-002 implementation low '["fixture"]' README.md forbidden.txt 2 4096 "${DIFF_COMMANDS}" "${TASK2}"
PREPARE2="$("${REPO}/bin/agent-task.sh" --project-root "${REPO}" --format json prepare "${TASK2}")"
WORKTREE2="$(python3 -c 'import json,sys;print(json.load(sys.stdin)["worktreePath"])' <<<"${PREPARE2}")"
set +e
"${REPO}/bin/agent-task.sh" --project-root "${REPO}" qualify AGENT-FIXTURE-002 > "${TMP_ROOT}/missing-invocation.out"
RC=$?
set -e
test "${RC}" -eq 2
grep -F 'errorCode=INVOCATION_RECORD_REQUIRED' "${TMP_ROOT}/missing-invocation.out" >/dev/null
set +e
"${REPO}/bin/agent-task.sh" --project-root "${REPO}" cleanup AGENT-FIXTURE-002 --discard >/dev/null
RC=$?
set -e
test "${RC}" -eq 1
test ! -e "${WORKTREE2}"

CURRENT_STEP=analysis-write-forbidden
TASK3="${TMP_ROOT}/task3.json"
make_task AGENT-FIXTURE-003 analysis low '["analysis"]' README.md forbidden.txt 0 0 "${DIFF_COMMANDS}" "${TASK3}"
PREPARE3="$("${REPO}/bin/agent-task.sh" --project-root "${REPO}" --format json prepare "${TASK3}")"
WORKTREE3="$(python3 -c 'import json,sys;print(json.load(sys.stdin)["worktreePath"])' <<<"${PREPARE3}")"
record_invocation AGENT-FIXTURE-003 "${WORKTREE3}"
printf '%s\n' 'analysis-must-not-write' > "${WORKTREE3}/README.md"
set +e
"${REPO}/bin/agent-task.sh" --project-root "${REPO}" postcheck AGENT-FIXTURE-003 >/dev/null
RC=$?
set -e
test "${RC}" -eq 1
grep -F 'TASK_MODE_WRITE_FORBIDDEN' "${COCONDO_AGENT_RUN_ROOT}/agent-fixture-003/changed-path-report.json" >/dev/null
set +e
"${REPO}/bin/agent-task.sh" --project-root "${REPO}" cleanup AGENT-FIXTURE-003 --discard >/dev/null
RC=$?
set -e
test "${RC}" -eq 1

CURRENT_STEP=forbidden-path
TASK4="${TMP_ROOT}/task4.json"
make_task AGENT-FIXTURE-004 implementation low '["fixture"]' README.md forbidden.txt 2 4096 "${DIFF_COMMANDS}" "${TASK4}"
PREPARE4="$("${REPO}/bin/agent-task.sh" --project-root "${REPO}" --format json prepare "${TASK4}")"
WORKTREE4="$(python3 -c 'import json,sys;print(json.load(sys.stdin)["worktreePath"])' <<<"${PREPARE4}")"
printf '%s\n' 'forbidden' > "${WORKTREE4}/forbidden.txt"
set +e
"${REPO}/bin/agent-task.sh" --project-root "${REPO}" postcheck AGENT-FIXTURE-004 > "${TMP_ROOT}/forbidden.out"
RC=$?
set -e
test "${RC}" -eq 1
grep -F 'FORBIDDEN_PATH_CHANGED' "${COCONDO_AGENT_RUN_ROOT}/agent-fixture-004/changed-path-report.json" >/dev/null
set +e
"${REPO}/bin/agent-task.sh" --project-root "${REPO}" cleanup AGENT-FIXTURE-004 --discard >/dev/null
RC=$?
set -e
test "${RC}" -eq 1

CURRENT_STEP=net-added-byte-semantics
TASK5="${TMP_ROOT}/task5.json"
make_task AGENT-FIXTURE-005 implementation low '["fixture"]' large.txt forbidden.txt 1 0 "${DIFF_COMMANDS}" "${TASK5}"
PREPARE5="$("${REPO}/bin/agent-task.sh" --project-root "${REPO}" --format json prepare "${TASK5}")"
WORKTREE5="$(python3 -c 'import json,sys;print(json.load(sys.stdin)["worktreePath"])' <<<"${PREPARE5}")"
record_invocation AGENT-FIXTURE-005 "${WORKTREE5}"
printf '%0100d\n' 1 > "${WORKTREE5}/large.txt"
"${REPO}/bin/agent-task.sh" --project-root "${REPO}" postcheck AGENT-FIXTURE-005 >/dev/null
grep -F '"netAddedBytes": 0' "${COCONDO_AGENT_RUN_ROOT}/agent-fixture-005/changed-path-report.json" >/dev/null
"${REPO}/bin/agent-task.sh" --project-root "${REPO}" qualify AGENT-FIXTURE-005 >/dev/null
"${REPO}/bin/agent-task.sh" --project-root "${REPO}" cleanup AGENT-FIXTURE-005 --discard >/dev/null

CURRENT_STEP=integration-dirty
TASK6="${TMP_ROOT}/task6.json"
make_task AGENT-FIXTURE-006 implementation low '["fixture"]' README.md forbidden.txt 2 4096 "${DIFF_COMMANDS}" "${TASK6}"
printf '%s\n' dirty > "${REPO}/dirty.tmp"
set +e
"${REPO}/bin/agent-task.sh" --project-root "${REPO}" prepare "${TASK6}" > "${TMP_ROOT}/dirty.out"
RC=$?
set -e
test "${RC}" -eq 2
grep -F 'errorCode=INTEGRATION_TREE_DIRTY' "${TMP_ROOT}/dirty.out" >/dev/null
rm -f "${REPO}/dirty.tmp"

CURRENT_STEP=missing-root-not-created
OLD_WORKTREE_ROOT="${COCONDO_WORKTREE_ROOT}"
export COCONDO_WORKTREE_ROOT="${TMP_ROOT}/missing-worktrees"
test ! -e "${COCONDO_WORKTREE_ROOT}"
set +e
"${REPO}/bin/agent-task.sh" --project-root "${REPO}" prepare "${TASK6}" > "${TMP_ROOT}/missing-root.out"
RC=$?
set -e
test "${RC}" -eq 2
grep -F 'errorCode=EXTERNAL_ROOT_MISSING' "${TMP_ROOT}/missing-root.out" >/dev/null
test ! -e "${COCONDO_WORKTREE_ROOT}"
export COCONDO_WORKTREE_ROOT="${OLD_WORKTREE_ROOT}"

CURRENT_STEP=root-overlap
export COCONDO_WORKTREE_ROOT="${REPO}/nested-worktrees"
mkdir -p "${COCONDO_WORKTREE_ROOT}"
set +e
"${REPO}/bin/agent-task.sh" --project-root "${REPO}" prepare "${TASK6}" > "${TMP_ROOT}/overlap.out"
RC=$?
set -e
test "${RC}" -eq 2
grep -F 'errorCode=EXTERNAL_ROOT_PROJECT_OVERLAP' "${TMP_ROOT}/overlap.out" >/dev/null
rm -rf "${COCONDO_WORKTREE_ROOT}"
export COCONDO_WORKTREE_ROOT="${OLD_WORKTREE_ROOT}"

CURRENT_STEP=symlink-root
REAL_RUNS="${TMP_ROOT}/real-runs"
LINK_RUNS="${TMP_ROOT}/linked-runs"
mkdir -p "${REAL_RUNS}"
ln -s "${REAL_RUNS}" "${LINK_RUNS}"
OLD_RUN_ROOT="${COCONDO_AGENT_RUN_ROOT}"
export COCONDO_AGENT_RUN_ROOT="${LINK_RUNS}"
set +e
"${REPO}/bin/agent-task.sh" --project-root "${REPO}" prepare "${TASK6}" > "${TMP_ROOT}/symlink.out"
RC=$?
set -e
test "${RC}" -eq 2
grep -F 'errorCode=EXTERNAL_ROOT_SYMLINK' "${TMP_ROOT}/symlink.out" >/dev/null
export COCONDO_AGENT_RUN_ROOT="${OLD_RUN_ROOT}"

CURRENT_STEP=invalid-active-run-record
mkdir -p "${COCONDO_AGENT_RUN_ROOT}/broken-run"
printf '%s\n' '{ invalid' > "${COCONDO_AGENT_RUN_ROOT}/broken-run/run.json"
set +e
"${REPO}/bin/agent-task.sh" --project-root "${REPO}" prepare "${TASK6}" > "${TMP_ROOT}/broken-run.out"
RC=$?
set -e
test "${RC}" -eq 2
grep -F 'errorCode=ACTIVE_TASK_RECORD_INVALID' "${TMP_ROOT}/broken-run.out" >/dev/null
rm -rf "${COCONDO_AGENT_RUN_ROOT}/broken-run"

CURRENT_STEP=invalid-active-run-status
mkdir -p "${COCONDO_AGENT_RUN_ROOT}/agent-broken-state"
printf '%s
' '{"taskId":"AGENT-BROKEN-STATE","status":"TYPO"}' > "${COCONDO_AGENT_RUN_ROOT}/agent-broken-state/run.json"
set +e
"${REPO}/bin/agent-task.sh" --project-root "${REPO}" prepare "${TASK6}" > "${TMP_ROOT}/broken-state.out"
RC=$?
set -e
test "${RC}" -eq 2
grep -F 'errorCode=ACTIVE_TASK_RECORD_INVALID' "${TMP_ROOT}/broken-state.out" >/dev/null
rm -rf "${COCONDO_AGENT_RUN_ROOT}/agent-broken-state"

CURRENT_STEP=failed-invocation-blocks-postcheck
TASK10="${TMP_ROOT}/task10.json"
make_task AGENT-FIXTURE-010 implementation low '["fixture"]' README.md forbidden.txt 2 4096 "${DIFF_COMMANDS}" "${TASK10}"
PREPARE10="$("${REPO}/bin/agent-task.sh" --project-root "${REPO}" --format json prepare "${TASK10}")"
WORKTREE10="$(python3 -c 'import json,sys;print(json.load(sys.stdin)["worktreePath"])' <<<"${PREPARE10}")"
record_invocation AGENT-FIXTURE-010 "${WORKTREE10}" FAILED 7
set +e
"${REPO}/bin/agent-task.sh" --project-root "${REPO}" postcheck AGENT-FIXTURE-010 >/dev/null
RC=$?
set -e
test "${RC}" -eq 1
grep -F 'CODEX_INVOCATION_NOT_COMPLETED' "${COCONDO_AGENT_RUN_ROOT}/agent-fixture-010/changed-path-report.json" >/dev/null
set +e
"${REPO}/bin/agent-task.sh" --project-root "${REPO}" cleanup AGENT-FIXTURE-010 --discard >/dev/null
RC=$?
set -e
test "${RC}" -eq 1

CURRENT_STEP=qualification-policy
TASK7="${TMP_ROOT}/task7.json"
make_task AGENT-FIXTURE-007 implementation medium '["fixture"]' README.md forbidden.txt 2 4096 "${DIFF_COMMANDS}" "${TASK7}"
set +e
"${REPO}/bin/agent-task.sh" --project-root "${REPO}" validate "${TASK7}" > "${TMP_ROOT}/qualification-policy.out"
RC=$?
set -e
test "${RC}" -eq 2
grep -F 'errorCode=TASK_QUALIFICATION_INCOMPLETE' "${TMP_ROOT}/qualification-policy.out" >/dev/null

CURRENT_STEP=critical-implementation-blocked
CRITICAL_COMMANDS='[
  {"id":"diff-check","argv":["git","diff","--check"],"timeoutSeconds":30},
  {"id":"targeted-check","argv":["git","status","--short"],"timeoutSeconds":30},
  {"id":"broad-check","argv":["git","status","--short"],"timeoutSeconds":30},
  {"id":"critical-check","argv":["git","status","--short"],"timeoutSeconds":30}
]'
TASK8="${TMP_ROOT}/task8.json"
make_task AGENT-FIXTURE-008 implementation critical '["fixture"]' README.md forbidden.txt 2 4096 "${CRITICAL_COMMANDS}" "${TASK8}"
set +e
"${REPO}/bin/agent-task.sh" --project-root "${REPO}" validate "${TASK8}" > "${TMP_ROOT}/critical.out"
RC=$?
set -e
test "${RC}" -eq 2
grep -F 'errorCode=TASK_RISK_MODE_FORBIDDEN' "${TMP_ROOT}/critical.out" >/dev/null

CURRENT_STEP=invocation-source-boundary
TASK9="${TMP_ROOT}/task9.json"
make_task AGENT-FIXTURE-009 implementation low '["fixture"]' README.md forbidden.txt 2 4096 "${DIFF_COMMANDS}" "${TASK9}"
PREPARE9="$("${REPO}/bin/agent-task.sh" --project-root "${REPO}" --format json prepare "${TASK9}")"
WORKTREE9="$(python3 -c 'import json,sys;print(json.load(sys.stdin)["worktreePath"])' <<<"${PREPARE9}")"
record_invocation AGENT-FIXTURE-009 "${WORKTREE9}"
python3 - "${COCONDO_AGENT_RUN_ROOT}/agent-fixture-009/invocation-record.json" <<'PY'
from pathlib import Path
p=Path(__import__('sys').argv[1]); p.write_text(p.read_text() + " ", encoding='utf-8')
PY
set +e
"${REPO}/bin/agent-task.sh" --project-root "${REPO}" postcheck AGENT-FIXTURE-009 >/dev/null
RC=$?
set -e
test "${RC}" -eq 1
grep -F 'INVOCATION_EVIDENCE_MUTATED' "${COCONDO_AGENT_RUN_ROOT}/agent-fixture-009/changed-path-report.json" >/dev/null
set +e
"${REPO}/bin/agent-task.sh" --project-root "${REPO}" cleanup AGENT-FIXTURE-009 --discard >/dev/null
RC=$?
set -e
test "${RC}" -eq 1


make_invalid_invocation_files() {
  local task_id="$1"
  local worktree="$2"
  local mutation="$3"
  local stem
  stem="$(tr '[:upper:]' '[:lower:]' <<<"${task_id}")"
  local effect="${COCONDO_ARTIFACT_ROOT}/${stem}-effect.json"
  local record="${COCONDO_ARTIFACT_ROOT}/${stem}-record.json"
  python3 - "${task_id}" "${worktree}" "${mutation}" "${effect}" "${record}" "${COCONDO_ARTIFACT_ROOT}/agent-fixture-001-effect.json" "${COCONDO_ARTIFACT_ROOT}/agent-fixture-001-record.json" <<'PY'
import json, sys
from pathlib import Path
task_id, worktree, mutation, effect_target, record_target, effect_source, record_source = sys.argv[1:]
effect=json.loads(Path(effect_source).read_text(encoding="utf-8"))
record=json.loads(Path(record_source).read_text(encoding="utf-8"))
effect["taskId"]=task_id
effect["workingDirectory"]=worktree
record["taskId"]=task_id
record["execution"]["workingDirectory"]=worktree
record["execution"]["platformSandbox"]["workspaceRoot"]=worktree
if mutation == "add-dir":
    effect["argv"] += ["--add-dir", "/home/fixture-user/Downloads"]
    record["execution"]["argv"] = list(effect["argv"])
elif mutation == "danger":
    effect["argv"].append("--dangerously-bypass-approvals-and-sandbox")
    record["execution"]["argv"] = list(effect["argv"])
elif mutation == "extra-write-root":
    record["execution"]["platformSandbox"]["additionalWritableRoots"]=["/home/fixture-user/Downloads"]
elif mutation == "operator-downloads-writable":
    record["execution"]["platformSandbox"]["operatorDownloadsWritable"]=True
else:
    raise SystemExit(f"unknown mutation: {mutation}")
Path(effect_target).write_text(json.dumps(effect, indent=2)+"\n", encoding="utf-8")
Path(record_target).write_text(json.dumps(record, indent=2)+"\n", encoding="utf-8")
PY
}

assert_invalid_invocation() {
  local task_id="$1"
  local mutation="$2"
  local expected_code="$3"
  local task_file="${TMP_ROOT}/${task_id}.json"
  make_task "${task_id}" implementation low '["fixture"]' README.md forbidden.txt 2 4096 "${DIFF_COMMANDS}" "${task_file}"
  local prepared worktree stem effect record
  prepared="$("${REPO}/bin/agent-task.sh" --project-root "${REPO}" --format json prepare "${task_file}")"
  worktree="$(python3 -c 'import json,sys;print(json.load(sys.stdin)["worktreePath"])' <<<"${prepared}")"
  stem="$(tr '[:upper:]' '[:lower:]' <<<"${task_id}")"
  effect="${COCONDO_ARTIFACT_ROOT}/${stem}-effect.json"
  record="${COCONDO_ARTIFACT_ROOT}/${stem}-record.json"
  make_invalid_invocation_files "${task_id}" "${worktree}" "${mutation}"
  set +e
  "${REPO}/bin/agent-task.sh" --project-root "${REPO}" record-invocation "${task_id}" --effect "${effect}" --record "${record}" > "${TMP_ROOT}/${stem}.out"
  local rc=$?
  set -e
  test "${rc}" -eq 2
  grep -F "errorCode=${expected_code}" "${TMP_ROOT}/${stem}.out" >/dev/null
  set +e
  "${REPO}/bin/agent-task.sh" --project-root "${REPO}" cleanup "${task_id}" --discard >/dev/null
  rc=$?
  set -e
  test "${rc}" -eq 1
}

CURRENT_STEP=codex-add-dir-forbidden
assert_invalid_invocation AGENT-FIXTURE-011 add-dir INVOCATION_FLAG_FORBIDDEN

CURRENT_STEP=codex-danger-flag-forbidden
assert_invalid_invocation AGENT-FIXTURE-012 danger INVOCATION_FLAG_FORBIDDEN

CURRENT_STEP=codex-additional-write-root-forbidden
assert_invalid_invocation AGENT-FIXTURE-013 extra-write-root INVOCATION_ADDITIONAL_WRITE_ROOT_FORBIDDEN

CURRENT_STEP=codex-operator-downloads-write-forbidden
assert_invalid_invocation AGENT-FIXTURE-014 operator-downloads-writable INVOCATION_HOST_WRITE_SCOPE_FORBIDDEN

CURRENT_STEP=forbidden-command-contract
python3 - "${TASK6}" <<'PY'
import json, sys
from pathlib import Path
p=Path(sys.argv[1]); d=json.loads(p.read_text()); d['qualificationCommands'][0]['argv']=['git','push']; p.write_text(json.dumps(d))
PY
set +e
"${REPO}/bin/agent-task.sh" --project-root "${REPO}" validate "${TASK6}" > "${TMP_ROOT}/command.out"
RC=$?
set -e
test "${RC}" -eq 2
grep -F 'errorCode=TASK_COMMAND_FORBIDDEN' "${TMP_ROOT}/command.out" >/dev/null

printf '%s\n' 'AGENT_TASK_IT=PASS'
