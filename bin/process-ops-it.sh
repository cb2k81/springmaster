#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
TMP_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/process-ops-it.XXXXXX")"
trap 'rm -rf "${TMP_ROOT}"' EXIT

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
CPROCESS_CONFIG_VERSION=1
CPROCESS_STATE_DIRECTORY=.git/cocondo-process
CPROCESS_INCIDENT_DIRECTORY=.git/cocondo-process/incidents
EOF

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
    printf '%s\n' "${PROCESS_OPS_TEST_STATUS_JSON:-{\"ok\":true,\"runId\":\"run-dry-1\",\"status\":\"FAILED\",\"phase\":\"failed\",\"exitCode\":7,\"logFile\":\"fixture-run.log\"}}"
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

git -C "${REPO}" init -q -b main
git -C "${REPO}" config user.email process-ops@example.invalid
git -C "${REPO}" config user.name process-ops-it
git -C "${REPO}" add .
git -C "${REPO}" commit -q -m baseline
git -C "${REPO}" worktree add -q -b change/fixture "${FEATURE}" main

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
PY

# A dirty feature worktree must not be confused with the clean integration worktree.
printf 'feature-only\n' > "${FEATURE}/feature.tmp"
DRY_OUTPUT="${TMP_ROOT}/dry.out"
(
  cd "${FEATURE}"
  ./bin/process-ops.sh patch-dry-run "${ARTIFACT}" > "${DRY_OUTPUT}"
)
grep -Fx 'runId=run-dry-1' "${DRY_OUTPUT}" >/dev/null
grep -F "cwd=${REPO} args=apply ${ARTIFACT} --dry-run --profile auto --format json" "${CALL_LOG}" >/dev/null

test -n "$(find "${REPO}/.git/cocondo-process/operations" -type f -name '*patch-dry-run*.json' -print -quit)"

git -C "${FEATURE}" clean -fdq

# A terminal FAILED status remains terminal-safe even if cpatch itself returns non-zero.
STATUS_OUTPUT="${TMP_ROOT}/status.out"
(
  cd "${FEATURE}"
  ./bin/process-ops.sh status run-dry-1 > "${STATUS_OUTPUT}"
)
grep -Fx 'status=FAILED' "${STATUS_OUTPUT}" >/dev/null
grep -Fx 'exitCode=7' "${STATUS_OUTPUT}" >/dev/null

test "$(wc -l < "${STATUS_OUTPUT}")" -le 12

# Generic detached commands are delegated directly to crun, without a second supervisor.
RUN_OUTPUT="${TMP_ROOT}/run.out"
(
  cd "${FEATURE}"
  ./bin/process-ops.sh run-start --name fixture --cwd . -- printf ok > "${RUN_OUTPUT}"
)
grep -Fx 'runId=run-generic-1' "${RUN_OUTPUT}" >/dev/null
grep -F "cwd=${REPO} args=start --name fixture --cwd ${FEATURE} --format json -- printf ok" "${CALL_LOG}" >/dev/null

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

printf '%s\n' 'PROCESS_OPS_IT=PASS'
