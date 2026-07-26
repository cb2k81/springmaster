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
mkdir -p "${REPO}/bin" "${REPO}/.cocondo/tooling"
cp "${PROJECT_ROOT}/bin/agent-task.py" "${REPO}/bin/agent-task.py"
cp "${PROJECT_ROOT}/bin/agent-task.sh" "${REPO}/bin/agent-task.sh"
chmod +x "${REPO}/bin/agent-task.py" "${REPO}/bin/agent-task.sh"
cat > "${REPO}/.cocondo/tooling/project.env" <<'EOF'
CPATCH_PROJECT_ID=springmaster
CPATCH_INTEGRATION_BRANCH=main
EOF
printf '%s\n' 'baseline' > "${REPO}/README.md"
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
  local allowed="$2"
  local forbidden="$3"
  local path="$4"
  cat > "${path}" <<EOF
{
  "schemaVersion": "springmaster.agent-task.v1",
  "taskId": "${task_id}",
  "pilotId": "springmaster-codex-pilot-v1",
  "repositoryId": "springmaster",
  "mode": "implementation",
  "baseCommit": "${BASE}",
  "integrationBranch": "main",
  "riskClass": "low",
  "changeClasses": ["fixture"],
  "allowedPaths": ["${allowed}"],
  "forbiddenPaths": ["${forbidden}", ".git/**"],
  "limits": {"maxChangedFiles": 2, "maxAddedBytes": 4096},
  "capabilities": {
    "mayModifyTests": false,
    "mayModifyGovernance": false,
    "mayModifyContracts": false,
    "mayCommit": false,
    "mayPush": false,
    "network": "disabled"
  },
  "qualificationCommands": [
    {"id": "diff-check", "argv": ["git", "diff", "--check"], "timeoutSeconds": 30}
  ],
  "requiredEvidence": [
    "task-contract", "task-contract-sha256", "prepare-record", "integration-pre-state",
    "worktree-pre-state", "changed-path-report", "qualification-records", "final-result",
    "cleanup-disposition"
  ],
  "completionCriteria": ["fixture complete"]
}
EOF
}

CURRENT_STEP=validate-prepare-pass
TASK1="${TMP_ROOT}/task1.json"
make_task AGENT-FIXTURE-001 README.md forbidden.txt "${TASK1}"
"${REPO}/bin/agent-task.sh" --project-root "${REPO}" validate "${TASK1}" >/dev/null
PREPARE1="$("${REPO}/bin/agent-task.sh" --project-root "${REPO}" --format json prepare "${TASK1}")"
WORKTREE1="$(python3 -c 'import json,sys;print(json.load(sys.stdin)["worktreePath"])' <<<"${PREPARE1}")"
test "$(git -C "${WORKTREE1}" branch --show-current)" = ''
printf '%s\n' 'changed' > "${WORKTREE1}/README.md"
"${REPO}/bin/agent-task.sh" --project-root "${REPO}" postcheck AGENT-FIXTURE-001 >/dev/null
"${REPO}/bin/agent-task.sh" --project-root "${REPO}" qualify AGENT-FIXTURE-001 >/dev/null
"${REPO}/bin/agent-task.sh" --project-root "${REPO}" cleanup AGENT-FIXTURE-001 --discard >/dev/null
test ! -e "${WORKTREE1}"

grep -F '"codexInvocation": "NOT_PERFORMED"' "${COCONDO_AGENT_RUN_ROOT}/agent-fixture-001/prepare-record.json" >/dev/null
grep -F '"integrationAuthorized": false' "${COCONDO_AGENT_RUN_ROOT}/agent-fixture-001/final-result.json" >/dev/null

CURRENT_STEP=forbidden-path
TASK2="${TMP_ROOT}/task2.json"
make_task AGENT-FIXTURE-002 README.md forbidden.txt "${TASK2}"
PREPARE2="$("${REPO}/bin/agent-task.sh" --project-root "${REPO}" --format json prepare "${TASK2}")"
WORKTREE2="$(python3 -c 'import json,sys;print(json.load(sys.stdin)["worktreePath"])' <<<"${PREPARE2}")"
printf '%s\n' 'forbidden' > "${WORKTREE2}/forbidden.txt"
set +e
"${REPO}/bin/agent-task.sh" --project-root "${REPO}" postcheck AGENT-FIXTURE-002 > "${TMP_ROOT}/forbidden.out"
RC=$?
set -e
test "${RC}" -eq 1
grep -F 'findingCount=' "${TMP_ROOT}/forbidden.out" >/dev/null
grep -F 'FORBIDDEN_PATH_CHANGED' "${COCONDO_AGENT_RUN_ROOT}/agent-fixture-002/changed-path-report.json" >/dev/null
"${REPO}/bin/agent-task.sh" --project-root "${REPO}" cleanup AGENT-FIXTURE-002 --discard >/dev/null

CURRENT_STEP=integration-dirty
TASK3="${TMP_ROOT}/task3.json"
make_task AGENT-FIXTURE-003 README.md forbidden.txt "${TASK3}"
printf '%s\n' dirty > "${REPO}/dirty.tmp"
set +e
"${REPO}/bin/agent-task.sh" --project-root "${REPO}" prepare "${TASK3}" > "${TMP_ROOT}/dirty.out"
RC=$?
set -e
test "${RC}" -eq 2
grep -F 'errorCode=INTEGRATION_TREE_DIRTY' "${TMP_ROOT}/dirty.out" >/dev/null
rm -f "${REPO}/dirty.tmp"

CURRENT_STEP=root-overlap
OLD_WORKTREE_ROOT="${COCONDO_WORKTREE_ROOT}"
export COCONDO_WORKTREE_ROOT="${REPO}/nested-worktrees"
mkdir -p "${COCONDO_WORKTREE_ROOT}"
set +e
"${REPO}/bin/agent-task.sh" --project-root "${REPO}" prepare "${TASK3}" > "${TMP_ROOT}/overlap.out"
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
"${REPO}/bin/agent-task.sh" --project-root "${REPO}" prepare "${TASK3}" > "${TMP_ROOT}/symlink.out"
RC=$?
set -e
test "${RC}" -eq 2
grep -F 'errorCode=EXTERNAL_ROOT_SYMLINK' "${TMP_ROOT}/symlink.out" >/dev/null
export COCONDO_AGENT_RUN_ROOT="${OLD_RUN_ROOT}"

CURRENT_STEP=forbidden-command-contract
python3 - "${TASK3}" <<'PY'
import json, sys
from pathlib import Path
p=Path(sys.argv[1]); d=json.loads(p.read_text()); d['qualificationCommands'][0]['argv']=['git','push']; p.write_text(json.dumps(d))
PY
set +e
"${REPO}/bin/agent-task.sh" --project-root "${REPO}" validate "${TASK3}" > "${TMP_ROOT}/command.out"
RC=$?
set -e
test "${RC}" -eq 2
grep -F 'errorCode=TASK_COMMAND_FORBIDDEN' "${TMP_ROOT}/command.out" >/dev/null

printf '%s\n' 'AGENT_TASK_IT=PASS'
