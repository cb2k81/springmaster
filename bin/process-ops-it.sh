#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
TMP_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/process-ops-it.XXXXXX")"
CURRENT_STEP=bootstrap
cleanup() {
  local rc=$?
  trap - EXIT
  if [[ "${rc}" -ne 0 ]]; then
    printf '%s\n' \
      'PROCESS_OPS_IT=FAILED' \
      "FAILED_STEP=${CURRENT_STEP}" \
      "FIXTURE_ROOT=${TMP_ROOT}" >&2
  fi
  rm -rf "${TMP_ROOT}"
  exit "${rc}"
}
trap cleanup EXIT

# Git fixtures must not inherit operator-specific configuration, templates,
# hooks, credentials or an experimental default reference backend.
FIXTURE_HOME="${TMP_ROOT}/home"
FIXTURE_XDG_CONFIG_HOME="${TMP_ROOT}/xdg-config"
FIXTURE_TEMPLATE_DIR="${TMP_ROOT}/git-template"
mkdir -p \
  "${FIXTURE_HOME}" \
  "${FIXTURE_XDG_CONFIG_HOME}" \
  "${FIXTURE_TEMPLATE_DIR}"

export HOME="${FIXTURE_HOME}"
export XDG_CONFIG_HOME="${FIXTURE_XDG_CONFIG_HOME}"
export GIT_CONFIG_NOSYSTEM=1
export GIT_CONFIG_GLOBAL=/dev/null
export GIT_TEMPLATE_DIR="${FIXTURE_TEMPLATE_DIR}"
export GIT_TERMINAL_PROMPT=0
unset GIT_DIR GIT_WORK_TREE GIT_COMMON_DIR GIT_INDEX_FILE
unset GIT_OBJECT_DIRECTORY GIT_ALTERNATE_OBJECT_DIRECTORIES

REPO="${TMP_ROOT}/repo"
FEATURE="${TMP_ROOT}/feature"
CALL_LOG="${TMP_ROOT}/calls.log"
ARTIFACT="${TMP_ROOT}/artifact.zip"

mkdir -p "${REPO}/bin" "${REPO}/.cocondo/tooling"
cp "${PROJECT_ROOT}/bin/process-ops.py" "${REPO}/bin/process-ops.py"
cp "${PROJECT_ROOT}/bin/process-ops.sh" "${REPO}/bin/process-ops.sh"
chmod +x "${REPO}/bin/process-ops.py" "${REPO}/bin/process-ops.sh"

cat > "${REPO}/.cocondo/tooling/project.env" <<'EOF'
CPATCH_PROJECT_ID=fixture-project
CPATCH_INTEGRATION_BRANCH=main
CPATCH_RUN_DIRECTORY=.git/cocondo-toolkit/runs
CPATCH_LOCK_DIRECTORY=.git/cocondo-toolkit/locks
CPATCH_ACCEPTED_DIRECTORY=.git/cocondo-toolkit/accepted
EOF
cat > "${REPO}/.cocondo/process.env" <<'EOF'
CPROCESS_CONFIG_VERSION=2
CPROCESS_STATE_DIRECTORY=.git/cocondo-process
CPROCESS_INCIDENT_DIRECTORY=.git/cocondo-process/incidents
CPROCESS_OPERATOR_LOG_DIRECTORY=patches/logs/validation
CPROCESS_WORK_DIRECTORY=patches/work
EOF
printf '%s\n' \
  'patches/logs/validation/' \
  'patches/work/' \
  > "${REPO}/.gitignore"

cat > "${REPO}/bin/cpatch" <<'SH2'
#!/usr/bin/env bash
set -u
printf 'cwd=%s args=%s\n' "$PWD" "$*" >> "${PROCESS_OPS_TEST_CALL_LOG:?}"
command="${1:-}"
case "$command" in
  apply)
    printf '%s\n' '{"ok":true,"runId":"run-dry-1","status":"STARTED","phase":"spawned","logFile":"fixture-run.log"}'
    exit 0
    ;;
  accept)
    printf '%s\n' '{"ok":true,"runId":"run-accept-1","status":"STARTED","phase":"spawned","logFile":"fixture-run.log"}'
    exit 0
    ;;
  status)
    reference="${2:-run-dry-1}"
    if [[ "${reference}" == "run-active-1" ]]; then
      printf '%s\n' '{"ok":true,"runId":"run-active-1","status":"RUNNING","phase":"validation:targeted","logFile":"fixture-active.log"}'
      exit 0
    fi
    printf '%s\n' "${PROCESS_OPS_TEST_STATUS_JSON:-{\"ok\":true,\"runId\":\"run-dry-1\",\"patchId\":\"000999_fixture\",\"artifactId\":\"urn:uuid:11111111-1111-4111-8111-111111111111\",\"status\":\"FAILED\",\"phase\":\"failed\",\"exitCode\":7,\"logFile\":\"fixture-run.log\"}}"
    exit "${PROCESS_OPS_TEST_STATUS_RC:-7}"
    ;;
  result)
    printf '%s\n' '{"ok":false,"runId":"run-dry-1","status":"FAILED","phase":"failed","exitCode":7,"logFile":"fixture-run.log"}'
    exit 7
    ;;
  diagnose)
    output=""
    while (($#)); do
      if [[ "$1" == "--output" ]]; then
        shift
        output="$1"
      fi
      shift || true
    done
    if [[ -n "$output" ]]; then
      mkdir -p "$(dirname "$output")"
      printf '%s\n' '{"run":{"runId":"run-dry-1","status":"FAILED"},"logTail":"fixture"}' > "$output"
    fi
    printf '%s\n' '{"ok":true,"runId":"run-dry-1","status":"FAILED","phase":"failed","exitCode":7}'
    exit 0
    ;;
  *)
    printf '%s\n' '{"ok":false,"errorCode":"UNEXPECTED_FIXTURE_COMMAND"}'
    exit 9
    ;;
esac
SH2

cat > "${REPO}/bin/crun" <<'SH2'
#!/usr/bin/env bash
set -u
printf 'cwd=%s args=%s\n' "$PWD" "$*" >> "${PROCESS_OPS_TEST_CALL_LOG:?}"
case "${1:-}" in
  start)
    printf '%s\n' '{"ok":true,"runId":"run-generic-1","status":"STARTED","phase":"spawned","logFile":"fixture-generic.log"}'
    ;;
  status)
    reference="${2:-}"
    if [[ "$reference" == "run-singleton-1" || "$reference" == "run-singleton-2" ]]; then
      printf '{"ok":true,"runId":"%s","status":"RUNNING","phase":"work","logFile":"fixture-singleton.log"}\n' "$reference"
    else
      printf '%s\n' '{"ok":true,"runId":"run-generic-1","status":"SUCCEEDED","phase":"completed","exitCode":0,"logFile":"fixture-generic.log"}'
    fi
    ;;
  *)
    printf '%s\n' '{"ok":false,"errorCode":"UNEXPECTED_FIXTURE_COMMAND"}'
    exit 9
    ;;
esac
SH2
chmod +x "${REPO}/bin/cpatch" "${REPO}/bin/crun"

touch "${ARTIFACT}"

CURRENT_STEP=fixture-git-init
git -c init.defaultRefFormat=files \
  -C "${REPO}" init -q -b main
CURRENT_STEP=fixture-baseline-commit
git -C "${REPO}" config user.email process-ops@example.invalid
git -C "${REPO}" config user.name process-ops-it
git -C "${REPO}" add .
git -C "${REPO}" commit -q -m baseline

# Historical tracked validation evidence below the shared operator-log root is
# compatible with new run-scoped runtime logs.
CURRENT_STEP=fixture-historical-operator-log-evidence
mkdir -p "${REPO}/patches/logs/validation/000001_historical"
printf 'historical evidence\n' > "${REPO}/patches/logs/validation/000001_historical/00-evidence.log"
git -C "${REPO}" add -f patches/logs/validation/000001_historical/00-evidence.log
git -C "${REPO}" commit -q -m 'historical operator log evidence fixture'

CURRENT_STEP=fixture-linked-worktree
git -C "${REPO}" worktree add -q -b change/fixture "${FEATURE}" main
CURRENT_STEP=process-ops-scenarios

export PROCESS_OPS_TEST_CALL_LOG="${CALL_LOG}"
export COCONDO_ARTIFACT_ROOT="${TMP_ROOT}"
export COCONDO_WORKTREE_ROOT="${TMP_ROOT}/worktrees"

RESOLVE_JSON="${TMP_ROOT}/resolve.json"
(
  cd "${FEATURE}"
  ./bin/process-ops.sh --format json resolve > "${RESOLVE_JSON}"
)
python3 - "${RESOLVE_JSON}" "${REPO}" "${FEATURE}" <<'PY'
import json
import sys
from pathlib import Path
value = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
assert Path(value["integrationRoot"]).resolve() == Path(sys.argv[2]).resolve(), value
assert Path(value["currentRoot"]).resolve() == Path(sys.argv[3]).resolve(), value
assert value["projectId"] == "fixture-project", value
common = Path(value["gitCommonDir"]).resolve()
assert Path(value["toolkitRunRoot"]).resolve() == common / "cocondo-toolkit/runs", value
assert Path(value["processStateRoot"]).resolve() == common / "cocondo-process", value
assert Path(value["operatorLogRoot"]).resolve() == Path(sys.argv[2]).resolve() / "patches/logs/validation", value
assert Path(value["operatorWorkRoot"]).resolve() == Path(sys.argv[2]).resolve() / "patches/work", value
PY

# A dirty feature worktree must not be confused with the clean integration worktree.
printf 'feature-only\n' > "${FEATURE}/feature.tmp"
mkdir -p "${REPO}/patches/work"
printf 'stale\n' > "${REPO}/patches/work/stale.txt"
DRY_OUTPUT="${TMP_ROOT}/dry.out"
(
  cd "${FEATURE}"
  ./bin/process-ops.sh patch-dry-run "${ARTIFACT}" > "${DRY_OUTPUT}"
)
grep -Fx 'runId=run-dry-1' "${DRY_OUTPUT}" >/dev/null
grep -F "cwd=${REPO} args=apply ${ARTIFACT} --dry-run --profile auto --format json" "${CALL_LOG}" >/dev/null

test -n "$(find "${REPO}/.git/cocondo-process/operations" -type f -name '*patch-dry-run*.json' -print -quit)"
test ! -e "${REPO}/patches/work/stale.txt"
test -f "${REPO}/patches/work/WORKSPACE.json"
grep -q '"runId": "run-dry-1"' "${REPO}/patches/work/WORKSPACE.json"
test -n "$(find "${REPO}/patches/logs/validation" -type f -name '*patch-dry-run.json' -print -quit)"
test -f "${REPO}/patches/logs/validation/000001_historical/00-evidence.log"
git -C "${REPO}" check-ignore -q -- patches/logs/validation/000999_fixture/run-dry-1/.probe

git -C "${FEATURE}" clean -fdq

# A terminal FAILED status remains terminal-safe even if cpatch itself returns non-zero.
STATUS_OUTPUT="${TMP_ROOT}/status.out"
(
  cd "${FEATURE}"
  ./bin/process-ops.sh status run-dry-1 > "${STATUS_OUTPUT}"
)
grep -Fx 'status=FAILED' "${STATUS_OUTPUT}" >/dev/null
grep -Fx 'exitCode=7' "${STATUS_OUTPUT}" >/dev/null

test "$(wc -l < "${STATUS_OUTPUT}")" -le 16

# Tracked content in the exact current run directory remains fail-closed even
# though tracked historical sibling evidence below the shared root is allowed.
CURRENT_STEP=tracked-current-operator-run-log
printf 'tracked conflict\n' > "${REPO}/patches/logs/validation/000999_fixture/run-dry-1/tracked-conflict.log"
git -C "${REPO}" add -f patches/logs/validation/000999_fixture/run-dry-1/tracked-conflict.log
git -C "${REPO}" commit -qm 'tracked current operator run log fixture'
set +e
(
  cd "${FEATURE}"
  ./bin/process-ops.sh status run-dry-1 > "${TMP_ROOT}/tracked-current-log.out" 2>&1
)
TRACKED_CURRENT_LOG_RC=$?
set -e
test "${TRACKED_CURRENT_LOG_RC}" -eq 9
grep -F 'errorCode=OPERATOR_LOG_TRACKED_CONTENT' "${TMP_ROOT}/tracked-current-log.out" >/dev/null
grep -F 'path=patches/logs/validation/000999_fixture/run-dry-1' "${TMP_ROOT}/tracked-current-log.out" >/dev/null
git -C "${REPO}" rm -q -f patches/logs/validation/000999_fixture/run-dry-1/tracked-conflict.log
git -C "${REPO}" commit -qm 'remove tracked current operator run log fixture'
CURRENT_STEP=process-ops-scenarios

# A terminal patch run can be packaged as exactly one deterministic diagnostic handoff ZIP.
RUN_EVIDENCE_DIR="${REPO}/.git/cocondo-toolkit/runs/run-dry-1"
mkdir -p "${RUN_EVIDENCE_DIR}/validation"
printf '%s\n' '{"runId":"run-dry-1","patchId":"000999_fixture","status":"FAILED"}' > "${RUN_EVIDENCE_DIR}/run.json"
printf '%s\n' 'fixture run log' > "${RUN_EVIDENCE_DIR}/run.log"
printf '%s\n' '{"complete":false}' > "${RUN_EVIDENCE_DIR}/validation/stages.json"
printf '%s\n' 'fixture validator log' > "${RUN_EVIDENCE_DIR}/validation/02-targeted.log"
HANDOFF_OUTPUT="${TMP_ROOT}/handoff.out"
(
  cd "${FEATURE}"
  ./bin/process-ops.sh diagnostic-handoff run-dry-1 > "${HANDOFF_OUTPUT}"
)
HANDOFF_ZIP="$(sed -n 's/^diagnosticArchive=//p' "${HANDOFF_OUTPUT}")"
test -f "${HANDOFF_ZIP}"
test "$(find "${REPO}/patches/work" -maxdepth 1 -type f -name '*.zip' | wc -l | tr -d ' ')" -eq 1
python3 - "${HANDOFF_ZIP}" <<'PY_HANDOFF'
import zipfile
import sys
with zipfile.ZipFile(sys.argv[1]) as archive:
    names=set(archive.namelist())
required={"MANIFEST.sha256","summary.json","status.json","diagnose.json","WORKSPACE.json","canonical-run/run.json","canonical-run/run.log","canonical-run/validation/stages.json","canonical-run/validation/02-targeted.log"}
missing=sorted(required-names)
assert not missing, missing
PY_HANDOFF

# Generic detached commands do not clean or mutate the current patch workflow workspace.
WORKSPACE_HASH_BEFORE="$(sha256sum "${REPO}/patches/work/WORKSPACE.json" | awk '{print $1}')"

# Generic detached commands are delegated directly to crun, without a second supervisor.
RUN_OUTPUT="${TMP_ROOT}/run.out"
(
  cd "${FEATURE}"
  ./bin/process-ops.sh run-start --name fixture --cwd . -- printf ok > "${RUN_OUTPUT}"
)
grep -Fx 'runId=run-generic-1' "${RUN_OUTPUT}" >/dev/null
grep -F "cwd=${REPO} args=start --name fixture --cwd ${FEATURE} --format json -- printf ok" "${CALL_LOG}" >/dev/null
test "$(sha256sum "${REPO}/patches/work/WORKSPACE.json" | awk '{print $1}')" = "${WORKSPACE_HASH_BEFORE}"
test -f "${HANDOFF_ZIP}"

# A new patch workflow safely removes terminal prior-workflow data.
SECOND_DRY_OUTPUT="${TMP_ROOT}/second-dry.out"
(
  cd "${FEATURE}"
  ./bin/process-ops.sh patch-dry-run "${ARTIFACT}" > "${SECOND_DRY_OUTPUT}"
)
test ! -e "${HANDOFF_ZIP}"
test "$(find "${REPO}/patches/work" -mindepth 1 -maxdepth 1 | wc -l | tr -d ' ')" -eq 1
test -f "${REPO}/patches/work/WORKSPACE.json"

# An active prior patch workflow blocks cleanup and no new cpatch start occurs.
python3 - "${REPO}/patches/work/WORKSPACE.json" <<'PY_ACTIVE'
import json,sys
p=sys.argv[1]
d=json.load(open(p))
d["runId"]="run-active-1"
d["status"]="RUNNING"
open(p,"w").write(json.dumps(d,indent=2,sort_keys=True)+"\n")
PY_ACTIVE
BEFORE_ACTIVE_CALLS="$(grep -c 'args=apply ' "${CALL_LOG}" || true)"
set +e
(
  cd "${FEATURE}"
  ./bin/process-ops.sh patch-dry-run "${ARTIFACT}" > "${TMP_ROOT}/active-workspace.out" 2>&1
)
ACTIVE_RC=$?
set -e
test "${ACTIVE_RC}" -eq 9
grep -F 'errorCode=OPERATOR_WORKSPACE_ACTIVE' "${TMP_ROOT}/active-workspace.out" >/dev/null
test "$(grep -c 'args=apply ' "${CALL_LOG}" || true)" -eq "${BEFORE_ACTIVE_CALLS}"

# Symlink content blocks cleanup fail-closed.
rm -rf "${REPO}/patches/work"
mkdir -p "${REPO}/patches/work"
ln -s "${TMP_ROOT}" "${REPO}/patches/work/escape"
set +e
(
  cd "${FEATURE}"
  ./bin/process-ops.sh patch-dry-run "${ARTIFACT}" > "${TMP_ROOT}/symlink-workspace.out" 2>&1
)
SYMLINK_RC=$?
set -e
test "${SYMLINK_RC}" -eq 9
grep -F 'errorCode=OPERATOR_WORKSPACE_SYMLINK_FORBIDDEN' "${TMP_ROOT}/symlink-workspace.out" >/dev/null
rm -rf "${REPO}/patches/work"

# A symlinked operator-log component blocks project-local evidence writes.
rm -rf "${REPO}/patches/logs/validation/unscoped"
mkdir -p "${REPO}/patches/logs/validation"
ln -s "${TMP_ROOT}" "${REPO}/patches/logs/validation/unscoped"
set +e
(
  cd "${FEATURE}"
  ./bin/process-ops.sh patch-dry-run "${ARTIFACT}" > "${TMP_ROOT}/symlink-operator-log.out" 2>&1
)
LOG_SYMLINK_RC=$?
set -e
test "${LOG_SYMLINK_RC}" -eq 9
grep -F 'errorCode=OPERATOR_LOG_SYMLINK_FORBIDDEN' "${TMP_ROOT}/symlink-operator-log.out" >/dev/null
rm -f "${REPO}/patches/logs/validation/unscoped"

# Tracked content below the workspace is never deleted.
mkdir -p "${REPO}/patches/work"
printf 'tracked\n' > "${REPO}/patches/work/tracked.txt"
git -C "${REPO}" add -f patches/work/tracked.txt
git -C "${REPO}" commit -qm 'tracked workspace fixture'
set +e
(
  cd "${FEATURE}"
  ./bin/process-ops.sh patch-dry-run "${ARTIFACT}" > "${TMP_ROOT}/tracked-workspace.out" 2>&1
)
TRACKED_RC=$?
set -e
test "${TRACKED_RC}" -eq 9
grep -F 'errorCode=OPERATOR_WORKSPACE_TRACKED_CONTENT' "${TMP_ROOT}/tracked-workspace.out" >/dev/null
test -f "${REPO}/patches/work/tracked.txt"
git -C "${REPO}" rm -q -f patches/work/tracked.txt
git -C "${REPO}" commit -qm 'remove tracked workspace fixture'

# Singleton start reuses an existing active run and repairs the canonical pointer.
SINGLETON_NAME='cocondo-singleton:fixture-project:revision-prepare'
SINGLETON_RUN_DIR="${REPO}/.git/cocondo-toolkit/runs/run-singleton-1"
mkdir -p "${SINGLETON_RUN_DIR}"
cat > "${SINGLETON_RUN_DIR}/run.json" <<EOF
{
  "schemaVersion": "cocondo.run-record.v1",
  "runId": "run-singleton-1",
  "command": "generic-run",
  "status": "RUNNING",
  "metadata": {"name": "${SINGLETON_NAME}"}
}
EOF
BEFORE_SINGLETON_STARTS="$(grep -c 'args=start ' "${CALL_LOG}" || true)"
SINGLETON_OUTPUT="${TMP_ROOT}/singleton.out"
(
  cd "${FEATURE}"
  ./bin/process-ops.sh run-start \
    --name ignored-by-singleton \
    --singleton-key revision-prepare \
    --cwd . \
    -- printf singleton > "${SINGLETON_OUTPUT}"
)
grep -Fx 'runId=run-singleton-1' "${SINGLETON_OUTPUT}" >/dev/null
grep -Fx 'startDisposition=REUSED_ACTIVE' "${SINGLETON_OUTPUT}" >/dev/null
test "$(grep -c 'args=start ' "${CALL_LOG}" || true)" -eq "${BEFORE_SINGLETON_STARTS}"
test "$(cat "${REPO}/.git/cocondo-process/pointers/revision-prepare.run-id")" = 'run-singleton-1'

# Multiple active records for one singleton key fail closed and do not start a worker.
SINGLETON_RUN_DIR_2="${REPO}/.git/cocondo-toolkit/runs/run-singleton-2"
mkdir -p "${SINGLETON_RUN_DIR_2}"
cat > "${SINGLETON_RUN_DIR_2}/run.json" <<EOF
{
  "schemaVersion": "cocondo.run-record.v1",
  "runId": "run-singleton-2",
  "command": "generic-run",
  "status": "RUNNING",
  "metadata": {"name": "${SINGLETON_NAME}"}
}
EOF
BEFORE_MULTI_STARTS="$(grep -c 'args=start ' "${CALL_LOG}" || true)"
set +e
(
  cd "${FEATURE}"
  ./bin/process-ops.sh run-start \
    --singleton-key revision-prepare \
    --cwd . \
    -- printf duplicate > "${TMP_ROOT}/multiple.out" 2>&1
)
MULTIPLE_RC=$?
set -e
test "${MULTIPLE_RC}" -eq 9
grep -F 'errorCode=MULTIPLE_ACTIVE_SINGLETON_RUNS' "${TMP_ROOT}/multiple.out" >/dev/null
test "$(grep -c 'args=start ' "${CALL_LOG}" || true)" -eq "${BEFORE_MULTI_STARTS}"
rm -rf "${SINGLETON_RUN_DIR_2}"

# A dirty integration worktree blocks mutation before cpatch is called.
printf 'dirty\n' > "${REPO}/dirty.tmp"
BEFORE_CALLS="$(wc -l < "${CALL_LOG}")"
set +e
(
  cd "${FEATURE}"
  ./bin/process-ops.sh patch-accept "${ARTIFACT}" > "${TMP_ROOT}/dirty.out" 2>&1
)
DIRTY_RC=$?
set -e
test "${DIRTY_RC}" -eq 9
grep -F 'errorCode=INTEGRATION_WORKTREE_DIRTY' "${TMP_ROOT}/dirty.out" >/dev/null
test "$(wc -l < "${CALL_LOG}")" -eq "${BEFORE_CALLS}"
rm -f "${REPO}/dirty.tmp"

# The implementation must not contain environment-specific paths or nested detachment.
if grep -En '/mnt/data|/opt/cocondo|/home/[^ ]+|\bnohup\b|\bsetsid\b' \
  "${PROJECT_ROOT}/bin/process-ops.py" \
  "${PROJECT_ROOT}/bin/process-ops.sh"; then
  echo 'Environment-specific path or nested detachment found' >&2
  exit 1
fi

# Tool execution must leave both worktrees clean.
test -z "$(git -C "${REPO}" status --porcelain=v1 --untracked-files=all)"
test -z "$(git -C "${FEATURE}" status --porcelain=v1 --untracked-files=all)"

CURRENT_STEP=completed
printf '%s\n' 'PROCESS_OPS_IT=PASS'
