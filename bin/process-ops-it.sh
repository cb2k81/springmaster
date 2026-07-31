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
  if [[ -n "${EXTERNAL_ARTIFACT_ROOT:-}" ]]; then
    rm -rf -- "${EXTERNAL_ARTIFACT_ROOT}"
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
EXTERNAL_ARTIFACT_ROOT="$(python3 - "${PROJECT_ROOT}" <<'PY_ROOT'
import os, sys
from pathlib import Path
root=Path(sys.argv[1]).resolve()
for parent in root.parents:
    text=str(parent)
    if text in {"/", "/home", "/root", "/tmp", "/var/tmp", "/dev/shm"}:
        continue
    if any(text == prefix or text.startswith(prefix + "/") for prefix in ("/home", "/root", "/tmp", "/var/tmp", "/dev/shm")):
        continue
    if os.access(parent, os.W_OK | os.X_OK):
        print(parent / f".process-ops-it-artifacts-{os.getpid()}")
        break
else:
    raise SystemExit("no safe writable external artifact parent")
PY_ROOT
)"
ARTIFACT="${EXTERNAL_ARTIFACT_ROOT}/artifact.zip"

mkdir -p \
  "${REPO}/bin" \
  "${REPO}/.cocondo/tooling" \
  "${REPO}/contracts/governance/tooling" \
  "${EXTERNAL_ARTIFACT_ROOT}"
cp "${PROJECT_ROOT}/bin/process-ops.py" "${REPO}/bin/process-ops.py"
cp "${PROJECT_ROOT}/bin/process-ops.sh" "${REPO}/bin/process-ops.sh"
cp "${PROJECT_ROOT}/contracts/governance/tooling/process-operations-contract.json" "${REPO}/contracts/governance/tooling/process-operations-contract.json"
chmod +x "${REPO}/bin/process-ops.py" "${REPO}/bin/process-ops.sh"

cat > "${REPO}/.cocondo/tooling/project.env" <<'EOF'
CPATCH_PROJECT_ID=fixture-project
CPATCH_INTEGRATION_BRANCH=main
CPATCH_RUN_DIRECTORY=.git/cocondo-toolkit/runs
CPATCH_LOCK_DIRECTORY=.git/cocondo-toolkit/locks
CPATCH_ACCEPTED_DIRECTORY=.git/cocondo-toolkit/accepted
EOF
cat > "${REPO}/.cocondo/process.env" <<'EOF'
CPROCESS_CONFIG_VERSION=3
CPROCESS_STATE_DIRECTORY=.git/cocondo-process
CPROCESS_INCIDENT_DIRECTORY=.git/cocondo-process/incidents
CPROCESS_DELIVERY_DIRECTORY=.git/cocondo-process/deliveries
CPROCESS_ARTIFACT_AUTHORIZATION_RECORD=.git/cocondo-process/authorizations/artifact-root.json
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
    if [[ "${reference}" == "run-unresolved-1" ]]; then
      printf '%s\n' 'not-json'
      exit 9
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

# Candidate runtime policy must be read from the invoking worktree, not from
# the integration checkout. Simulate a main checkout that still has the older
# contract while the linked candidate already contains delivery inventory
# policy. A resolver launched from the candidate must remain functional.
CURRENT_STEP=fixture-integration-contract-lag
python3 - "${REPO}/contracts/governance/tooling/process-operations-contract.json" <<'PY_CONTRACT_LAG'
import json
import sys
from pathlib import Path
path = Path(sys.argv[1])
value = json.loads(path.read_text(encoding="utf-8"))
value.pop("deliveryInventoryPolicy", None)
path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
PY_CONTRACT_LAG
git -C "${REPO}" add contracts/governance/tooling/process-operations-contract.json
git -C "${REPO}" commit -q -m 'fixture integration contract lag'

CURRENT_STEP=process-ops-scenarios

export PROCESS_OPS_TEST_CALL_LOG="${CALL_LOG}"
: > "${CALL_LOG}"
export COCONDO_ARTIFACT_ROOT="${EXTERNAL_ARTIFACT_ROOT}"
export COCONDO_WORKTREE_ROOT="${TMP_ROOT}/worktrees"
mkdir -p \
  "${REPO}/.git/cocondo-toolkit/runs" \
  "${REPO}/.git/cocondo-toolkit/locks" \
  "${REPO}/.git/cocondo-toolkit/accepted" \
  "${REPO}/.git/cocondo-process/deliveries"

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
assert Path(value["processDeliveryRoot"]).resolve() == common / "cocondo-process/deliveries", value
assert Path(value["artifactAuthorizationRecord"]).resolve() == common / "cocondo-process/authorizations/artifact-root.json", value
PY

# Configuration alone is not artifact-root authorization and must block before worker start.
printf 'feature-only\n' > "${FEATURE}/feature.tmp"
mkdir -p "${REPO}/patches/work"
printf 'stale\n' > "${REPO}/patches/work/stale.txt"
BEFORE_UNAUTHORIZED_CALLS="$(wc -l < "${CALL_LOG}" 2>/dev/null || printf 0)"
set +e
(
  cd "${FEATURE}"
  ./bin/process-ops.sh patch-dry-run "$(basename "${ARTIFACT}")" > "${TMP_ROOT}/artifact-unauthorized.out" 2>&1
)
UNAUTHORIZED_RC=$?
set -e
test "${UNAUTHORIZED_RC}" -eq 9
grep -F 'errorCode=ARTIFACT_ROOT_UNAUTHORIZED' "${TMP_ROOT}/artifact-unauthorized.out" >/dev/null
test "$(wc -l < "${CALL_LOG}" 2>/dev/null || printf 0)" -eq "${BEFORE_UNAUTHORIZED_CALLS}"
test ! -e "${REPO}/.git/cocondo-process/authorizations/artifact-root.json"

# Explicit authorization records the already existing canonical root without creating it.
AUTH_OUTPUT="${TMP_ROOT}/artifact-authorize.out"
(
  cd "${FEATURE}"
  ./bin/process-ops.sh artifact-root-authorize > "${AUTH_OUTPUT}"
)
grep -Fx 'authorizationDisposition=AUTHORIZED' "${AUTH_OUTPUT}" >/dev/null
test -d "${EXTERNAL_ARTIFACT_ROOT}"
test -f "${REPO}/.git/cocondo-process/authorizations/artifact-root.json"
(
  cd "${FEATURE}"
  ./bin/process-ops.sh artifact-root-status > "${TMP_ROOT}/artifact-status.out"
)
grep -Fx 'status=AUTHORIZED' "${TMP_ROOT}/artifact-status.out" >/dev/null

# A dirty feature worktree must not be confused with the clean integration worktree.
DRY_OUTPUT="${TMP_ROOT}/dry.out"
(
  cd "${FEATURE}"
  ./bin/process-ops.sh patch-dry-run "$(basename "${ARTIFACT}")" > "${DRY_OUTPUT}"
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
  ./bin/process-ops.sh patch-dry-run "$(basename "${ARTIFACT}")" > "${SECOND_DRY_OUTPUT}"
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
  ./bin/process-ops.sh patch-dry-run "$(basename "${ARTIFACT}")" > "${TMP_ROOT}/active-workspace.out" 2>&1
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
  ./bin/process-ops.sh patch-dry-run "$(basename "${ARTIFACT}")" > "${TMP_ROOT}/symlink-workspace.out" 2>&1
)
SYMLINK_RC=$?
set -e
test "${SYMLINK_RC}" -eq 9
grep -F 'errorCode=OPERATOR_WORKSPACE_SYMLINK_FORBIDDEN' "${TMP_ROOT}/symlink-workspace.out" >/dev/null
rm -rf "${REPO}/patches/work"
mkdir -p "${REPO}/patches/work"

# A symlinked operator-log component blocks project-local evidence writes.
rm -rf "${REPO}/patches/logs/validation/unscoped"
mkdir -p "${REPO}/patches/logs/validation"
ln -s "${TMP_ROOT}" "${REPO}/patches/logs/validation/unscoped"
set +e
(
  cd "${FEATURE}"
  ./bin/process-ops.sh patch-dry-run "$(basename "${ARTIFACT}")" > "${TMP_ROOT}/symlink-operator-log.out" 2>&1
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
  ./bin/process-ops.sh patch-dry-run "$(basename "${ARTIFACT}")" > "${TMP_ROOT}/tracked-workspace.out" 2>&1
)
TRACKED_RC=$?
set -e
test "${TRACKED_RC}" -eq 9
grep -F 'errorCode=OPERATOR_WORKSPACE_TRACKED_CONTENT' "${TMP_ROOT}/tracked-workspace.out" >/dev/null
test -f "${REPO}/patches/work/tracked.txt"
git -C "${REPO}" rm -q -f patches/work/tracked.txt
git -C "${REPO}" commit -qm 'remove tracked workspace fixture'

# Missing workspace root, root symlink, nested repository, special file and unresolved run all block before a worker start.
rm -rf "${REPO}/patches/work"
set +e
(
  cd "${FEATURE}"
  ./bin/process-ops.sh workspace-start --operation diagnose --subject missing > "${TMP_ROOT}/workspace-missing.out" 2>&1
)
MISSING_WORKSPACE_RC=$?
set -e
test "${MISSING_WORKSPACE_RC}" -eq 9
grep -F 'errorCode=OPERATOR_WORKSPACE_MISSING' "${TMP_ROOT}/workspace-missing.out" >/dev/null

ln -s "${TMP_ROOT}" "${REPO}/patches/work"
set +e
(
  cd "${FEATURE}"
  ./bin/process-ops.sh workspace-start --operation diagnose --subject root-symlink > "${TMP_ROOT}/workspace-root-symlink.out" 2>&1
)
ROOT_SYMLINK_RC=$?
set -e
test "${ROOT_SYMLINK_RC}" -eq 9
grep -F 'errorCode=OPERATOR_WORKSPACE_SYMLINK_FORBIDDEN' "${TMP_ROOT}/workspace-root-symlink.out" >/dev/null
rm -f "${REPO}/patches/work"

mkdir -p "${REPO}/patches/work/nested/.git"
set +e
(
  cd "${FEATURE}"
  ./bin/process-ops.sh workspace-start --operation incident --subject nested > "${TMP_ROOT}/workspace-nested.out" 2>&1
)
NESTED_RC=$?
set -e
test "${NESTED_RC}" -eq 9
grep -F 'errorCode=OPERATOR_WORKSPACE_NESTED_REPOSITORY' "${TMP_ROOT}/workspace-nested.out" >/dev/null
rm -rf "${REPO}/patches/work"

mkdir -p "${REPO}/patches/work"
mkfifo "${REPO}/patches/work/blocked.fifo"
set +e
(
  cd "${FEATURE}"
  ./bin/process-ops.sh workspace-start --operation incident --subject fifo > "${TMP_ROOT}/workspace-fifo.out" 2>&1
)
FIFO_RC=$?
set -e
test "${FIFO_RC}" -eq 9
grep -F 'errorCode=OPERATOR_WORKSPACE_SPECIAL_FILE_FORBIDDEN' "${TMP_ROOT}/workspace-fifo.out" >/dev/null
rm -rf "${REPO}/patches/work"

# The exact production helper rejects a real mount point.
python3 - "${PROJECT_ROOT}/bin/process-ops.py" <<'PY_MOUNT'
import importlib.util, sys
from pathlib import Path
spec=importlib.util.spec_from_file_location("process_ops", sys.argv[1])
module=importlib.util.module_from_spec(spec)
sys.modules[spec.name]=module
spec.loader.exec_module(module)
try:
    module.validate_workspace_tree(Path("/proc"))
except module.ProcessOpsError as exc:
    assert exc.code == "OPERATOR_WORKSPACE_MOUNT_FORBIDDEN", exc.code
else:
    raise AssertionError("mount point was not rejected")
PY_MOUNT

mkdir -p "${REPO}/patches/work"
cat > "${REPO}/patches/work/WORKSPACE.json" <<'JSON_UNRESOLVED'
{
  "schemaVersion": "cocondo.operator-workspace.v2",
  "operation": "patch-dry-run",
  "runId": "run-unresolved-1",
  "status": "RUNNING"
}
JSON_UNRESOLVED
set +e
(
  cd "${FEATURE}"
  ./bin/process-ops.sh workspace-start --operation diagnose --subject unresolved > "${TMP_ROOT}/workspace-unresolved.out" 2>&1
)
UNRESOLVED_RC=$?
set -e
test "${UNRESOLVED_RC}" -eq 9
grep -F 'errorCode=OPERATOR_WORKSPACE_STATUS_UNRESOLVED' "${TMP_ROOT}/workspace-unresolved.out" >/dev/null
rm -rf "${REPO}/patches/work"
mkdir -p "${REPO}/patches/work"

# Artifact authorization is bound to exact canonical path, configuration and inode.
cp "${REPO}/.git/cocondo-process/authorizations/artifact-root.json" "${TMP_ROOT}/authorization-good.json"
git -C "${REPO}" config cocondo.artifactRoot "${EXTERNAL_ARTIFACT_ROOT}/different"
set +e
(
  cd "${FEATURE}"
  ./bin/process-ops.sh artifact-root-status > "${TMP_ROOT}/artifact-ambiguous.out" 2>&1
)
AMBIGUOUS_RC=$?
set -e
test "${AMBIGUOUS_RC}" -eq 9
grep -F 'errorCode=ARTIFACT_ROOT_CONFIGURATION_AMBIGUOUS' "${TMP_ROOT}/artifact-ambiguous.out" >/dev/null
git -C "${REPO}" config --unset cocondo.artifactRoot

python3 - "${REPO}/.git/cocondo-process/authorizations/artifact-root.json" <<'PY_DAMAGE_AUTH'
import json, sys
p=sys.argv[1]
d=json.load(open(p))
d["canonicalPath"] = d["canonicalPath"] + "-other"
open(p,"w").write(json.dumps(d,indent=2,sort_keys=True)+"\n")
PY_DAMAGE_AUTH
set +e
(
  cd "${FEATURE}"
  ./bin/process-ops.sh artifact-root-status > "${TMP_ROOT}/artifact-mismatch.out" 2>&1
)
MISMATCH_RC=$?
set -e
test "${MISMATCH_RC}" -eq 9
grep -F 'errorCode=ARTIFACT_ROOT_AUTHORIZATION_MISMATCH' "${TMP_ROOT}/artifact-mismatch.out" >/dev/null
cp "${TMP_ROOT}/authorization-good.json" "${REPO}/.git/cocondo-process/authorizations/artifact-root.json"

chmod 500 "${EXTERNAL_ARTIFACT_ROOT}"
set +e
(
  cd "${FEATURE}"
  ./bin/process-ops.sh artifact-root-status > "${TMP_ROOT}/artifact-mode.out" 2>&1
)
MODE_RC=$?
set -e
chmod 700 "${EXTERNAL_ARTIFACT_ROOT}"
test "${MODE_RC}" -eq 9
grep -F 'errorCode=ARTIFACT_ROOT_NOT_WRITABLE' "${TMP_ROOT}/artifact-mode.out" >/dev/null

# Typed delivery inventory ignores only declared historical metadata and reserves typed records.
mkdir -p "${REPO}/.git/cocondo-toolkit/runs/run-generic-null"
printf '%s\n' '{"runId":"run-generic-null","patchId":null,"title":"numbers 123456 and 654321 are text only"}' > "${REPO}/.git/cocondo-toolkit/runs/run-generic-null/run.json"
mkdir -p "${REPO}/.git/cocondo-toolkit/runs/run-legacy-numeric"
cat > "${REPO}/.git/cocondo-toolkit/runs/run-legacy-numeric/run.json" <<'JSON_LEGACY_NUMERIC'
{
  "schemaVersion": "cocondo.run-record.v1",
  "runId": "run-legacy-numeric",
  "command": "patch-dry-run",
  "patchId": "000996",
  "artifactId": "urn:uuid:12345678-1234-4234-8234-123456789abc",
  "status": "FAILED",
  "metadata": {
    "artifactFile": "scope__000996_legacy-qualified__12345678.zip"
  }
}
JSON_LEGACY_NUMERIC
mkdir -p "${REPO}/.git/cocondo-toolkit/runs/run-accepted-owner-failed"
printf '%s\n' '{"schemaVersion":"cocondo.run-record.v1","runId":"run-accepted-owner-failed","command":"patch-dry-run","patchId":"000994_old","artifactId":"urn:uuid:99999999-9999-4999-8999-999999999999","status":"FAILED"}' > "${REPO}/.git/cocondo-toolkit/runs/run-accepted-owner-failed/run.json"
mkdir -p "${REPO}/.git/cocondo-toolkit/runs/run-accepted-owner-success"
cat > "${REPO}/.git/cocondo-toolkit/runs/run-accepted-owner-success/run.json" <<'JSON_ACCEPTED_OWNER_RUN'
{
  "schemaVersion": "cocondo.run-record.v1",
  "runId": "run-accepted-owner-success",
  "command": "patch-accept",
  "patchId": "000994",
  "artifactId": "urn:uuid:aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee",
  "status": "SUCCEEDED",
  "metadata": {
    "artifactFile": "scope__000994_final__aaaaaaaa.zip"
  }
}
JSON_ACCEPTED_OWNER_RUN
cat > "${REPO}/.git/cocondo-toolkit/accepted/aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee.json" <<'JSON_ACCEPTED_OWNER'
{
  "schemaVersion": "cocondo.patch-acceptance.v2",
  "projectId": "fixture-project",
  "artifactId": "urn:uuid:aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee",
  "patchId": "000994"
}
JSON_ACCEPTED_OWNER
printf 'uuid=123456 random=654321\n' > "${REPO}/.git/cocondo-process/deliveries/000181-example-accept-discovery.env"
mkdir -p "${REPO}/.git/cocondo-process/deliveries/000997-failed-delivery"
mkdir -p "${REPO}/.git/cocondo-process/deliveries/000998-current-delivery"
INVENTORY_JSON="${TMP_ROOT}/inventory.json"
(
  cd "${FEATURE}"
  ./bin/process-ops.sh --format json delivery-next-id --name tooling-hardening --current-delivery 000998-current-delivery > "${INVENTORY_JSON}"
)
python3 - "${INVENTORY_JSON}" <<'PY_INVENTORY'
import json, sys
v=json.load(open(sys.argv[1]))
assert v["nextNumber"] == "001000", v
assert v["patchId"] == "001000_tooling-hardening", v
assert v["deliveryId"] == "001000-tooling-hardening", v
assert v["currentDeliveryExceptionCount"] == 1, v
assert v["summary"]["knownMetadataEntryCount"] == 1, v
assert v["summary"]["deliveryDirectoryCount"] == 2, v
assert v["summary"]["genericRunCount"] >= 1, v
assert v["summary"]["patchRunCount"] == 4, v
assert v["summary"]["legacyNumericPatchRunCount"] == 2, v
assert v["summary"]["acceptedPatchRecordCount"] == 1, v
assert v["summary"]["acceptedOwnerCount"] == 1, v
assert v["summary"]["historicalFailedAttemptCount"] == 1, v
legacy=[e for e in v["entries"] if e.get("entryType") == "legacy-numeric-patch-run"]
assert len(legacy) == 2, v
legacy_996=[e for e in legacy if e.get("legacyPatchId") == "000996"]
assert len(legacy_996) == 1, legacy
assert legacy_996[0]["patchId"] == "000996_legacy-qualified", legacy_996
accepted=[e for e in v["entries"] if e.get("entryType") == "accepted-patch-record"]
assert len(accepted) == 1, accepted
assert accepted[0]["patchId"] == "000994_final", accepted
failed=[e for e in v["entries"] if e.get("entryType") == "historical-failed-patch-run"]
assert len(failed) == 1, failed
assert failed[0]["patchId"] == "000994_old", failed
assert failed[0]["acceptedPatchId"] == "000994_final", failed
assert failed[0]["policy"] == "IGNORE_AND_COUNT", failed
assert "000994" in v["reservedNumbers"], v
assert "000996" in v["reservedNumbers"], v
assert "000998" not in v["reservedNumbers"], v
assert "123456" not in v["reservedNumbers"] and "654321" not in v["reservedNumbers"], v
PY_INVENTORY

printf 'unknown\n' > "${REPO}/.git/cocondo-process/deliveries/000996-unknown.txt"
set +e
(
  cd "${FEATURE}"
  ./bin/process-ops.sh delivery-inventory > "${TMP_ROOT}/inventory-unknown.out" 2>&1
)
UNKNOWN_RC=$?
set -e
test "${UNKNOWN_RC}" -eq 9
grep -F 'errorCode=DELIVERY_INVENTORY_UNKNOWN_ENTRY' "${TMP_ROOT}/inventory-unknown.out" >/dev/null
rm -f "${REPO}/.git/cocondo-process/deliveries/000996-unknown.txt"

ln -s "${TMP_ROOT}" "${REPO}/.git/cocondo-process/deliveries/000996-symlink"
set +e
(
  cd "${FEATURE}"
  ./bin/process-ops.sh delivery-inventory > "${TMP_ROOT}/inventory-symlink.out" 2>&1
)
INVENTORY_SYMLINK_RC=$?
set -e
test "${INVENTORY_SYMLINK_RC}" -eq 9
grep -F 'errorCode=DELIVERY_INVENTORY_SYMLINK' "${TMP_ROOT}/inventory-symlink.out" >/dev/null
rm -f "${REPO}/.git/cocondo-process/deliveries/000996-symlink"

mkfifo "${REPO}/.git/cocondo-process/deliveries/000996-special"
set +e
(
  cd "${FEATURE}"
  ./bin/process-ops.sh delivery-inventory > "${TMP_ROOT}/inventory-special.out" 2>&1
)
INVENTORY_SPECIAL_RC=$?
set -e
test "${INVENTORY_SPECIAL_RC}" -eq 9
grep -F 'errorCode=DELIVERY_INVENTORY_SPECIAL_FILE' "${TMP_ROOT}/inventory-special.out" >/dev/null
rm -f "${REPO}/.git/cocondo-process/deliveries/000996-special"

mkdir -p "${REPO}/.git/cocondo-toolkit/runs/run-invalid-json"
printf '{\n' > "${REPO}/.git/cocondo-toolkit/runs/run-invalid-json/run.json"
set +e
(
  cd "${FEATURE}"
  ./bin/process-ops.sh delivery-inventory > "${TMP_ROOT}/inventory-json.out" 2>&1
)
INVENTORY_JSON_RC=$?
set -e
test "${INVENTORY_JSON_RC}" -eq 9
grep -F 'errorCode=DELIVERY_RUN_RECORD_INVALID' "${TMP_ROOT}/inventory-json.out" >/dev/null
rm -rf "${REPO}/.git/cocondo-toolkit/runs/run-invalid-json"

mkdir -p "${REPO}/.git/cocondo-toolkit/runs/run-null-scoped"
printf '%s\n' '{"runId":"run-null-scoped","patchId":null,"operation":"accept"}' > "${REPO}/.git/cocondo-toolkit/runs/run-null-scoped/run.json"
set +e
(
  cd "${FEATURE}"
  ./bin/process-ops.sh delivery-inventory > "${TMP_ROOT}/inventory-null-scoped.out" 2>&1
)
NULL_SCOPED_RC=$?
set -e
test "${NULL_SCOPED_RC}" -eq 9
grep -F 'errorCode=DELIVERY_RUN_PATCH_ID_MISSING' "${TMP_ROOT}/inventory-null-scoped.out" >/dev/null
rm -rf "${REPO}/.git/cocondo-toolkit/runs/run-null-scoped"

mkdir -p "${REPO}/.git/cocondo-toolkit/runs/run-conflict"
printf '%s\n' '{"runId":"run-conflict","patchId":"000999_other"}' > "${REPO}/.git/cocondo-toolkit/runs/run-conflict/run.json"
set +e
(
  cd "${FEATURE}"
  ./bin/process-ops.sh delivery-inventory > "${TMP_ROOT}/inventory-conflict.out" 2>&1
)
CONFLICT_RC=$?
set -e
test "${CONFLICT_RC}" -eq 9
grep -F 'errorCode=DELIVERY_PATCH_IDENTITY_CONFLICT' "${TMP_ROOT}/inventory-conflict.out" >/dev/null
rm -rf "${REPO}/.git/cocondo-toolkit/runs/run-conflict"

# An accepted owner suppresses only terminal failed run attempts. A non-failed
# different run identity remains a blocking conflict.
mkdir -p "${REPO}/.git/cocondo-toolkit/runs/run-accepted-owner-nonfailed-conflict"
printf '%s\n' '{"schemaVersion":"cocondo.run-record.v1","runId":"run-accepted-owner-nonfailed-conflict","command":"patch-dry-run","patchId":"000994_other","artifactId":"urn:uuid:88888888-8888-4888-8888-888888888888","status":"DRY_RUN_SUCCEEDED"}' > "${REPO}/.git/cocondo-toolkit/runs/run-accepted-owner-nonfailed-conflict/run.json"
set +e
(
  cd "${FEATURE}"
  ./bin/process-ops.sh delivery-inventory > "${TMP_ROOT}/inventory-accepted-owner-nonfailed.out" 2>&1
)
ACCEPTED_OWNER_NONFAILED_RC=$?
set -e
test "${ACCEPTED_OWNER_NONFAILED_RC}" -eq 9
grep -F 'errorCode=DELIVERY_PATCH_IDENTITY_CONFLICT' "${TMP_ROOT}/inventory-accepted-owner-nonfailed.out" >/dev/null
rm -rf "${REPO}/.git/cocondo-toolkit/runs/run-accepted-owner-nonfailed-conflict"

# A delivery identity may not be hidden by accepted-owner authority.
mkdir -p "${REPO}/.git/cocondo-process/deliveries/000994-other"
cat > "${REPO}/.git/cocondo-process/deliveries/000994-other/delivery.json" <<'JSON_ACCEPTED_DELIVERY_CONFLICT'
{
  "schemaVersion": "cocondo.delivery-record.v1",
  "deliveryId": "000994-other",
  "patchId": "000994_other",
  "name": "other",
  "revision": "r1"
}
JSON_ACCEPTED_DELIVERY_CONFLICT
set +e
(
  cd "${FEATURE}"
  ./bin/process-ops.sh delivery-inventory > "${TMP_ROOT}/inventory-accepted-delivery-conflict.out" 2>&1
)
ACCEPTED_DELIVERY_CONFLICT_RC=$?
set -e
test "${ACCEPTED_DELIVERY_CONFLICT_RC}" -eq 9
grep -F 'errorCode=DELIVERY_PATCH_IDENTITY_CONFLICT' "${TMP_ROOT}/inventory-accepted-delivery-conflict.out" >/dev/null
rm -rf "${REPO}/.git/cocondo-process/deliveries/000994-other"

# Two accepted owners for one number are always blocking.
cat > "${REPO}/.git/cocondo-toolkit/accepted/11111111-1111-4111-8111-111111111111.json" <<'JSON_ACCEPTED_CONFLICT_A'
{"schemaVersion":"cocondo.patch-acceptance.v2","projectId":"fixture-project","artifactId":"urn:uuid:11111111-1111-4111-8111-111111111111","patchId":"000993_a"}
JSON_ACCEPTED_CONFLICT_A
cat > "${REPO}/.git/cocondo-toolkit/accepted/22222222-2222-4222-8222-222222222222.json" <<'JSON_ACCEPTED_CONFLICT_B'
{"schemaVersion":"cocondo.patch-acceptance.v2","projectId":"fixture-project","artifactId":"urn:uuid:22222222-2222-4222-8222-222222222222","patchId":"000993_b"}
JSON_ACCEPTED_CONFLICT_B
set +e
(
  cd "${FEATURE}"
  ./bin/process-ops.sh delivery-inventory > "${TMP_ROOT}/inventory-multiple-accepted.out" 2>&1
)
MULTIPLE_ACCEPTED_RC=$?
set -e
test "${MULTIPLE_ACCEPTED_RC}" -eq 9
grep -F 'errorCode=DELIVERY_PATCH_IDENTITY_CONFLICT' "${TMP_ROOT}/inventory-multiple-accepted.out" >/dev/null
rm -f \
  "${REPO}/.git/cocondo-toolkit/accepted/11111111-1111-4111-8111-111111111111.json" \
  "${REPO}/.git/cocondo-toolkit/accepted/22222222-2222-4222-8222-222222222222.json"

# A numeric accepted record requires one matching successful patch-accept run.
cat > "${REPO}/.git/cocondo-toolkit/accepted/33333333-3333-4333-8333-333333333333.json" <<'JSON_ACCEPTED_UNRESOLVED'
{"schemaVersion":"cocondo.patch-acceptance.v2","projectId":"fixture-project","artifactId":"urn:uuid:33333333-3333-4333-8333-333333333333","patchId":"000992"}
JSON_ACCEPTED_UNRESOLVED
set +e
(
  cd "${FEATURE}"
  ./bin/process-ops.sh delivery-inventory > "${TMP_ROOT}/inventory-accepted-unresolved.out" 2>&1
)
ACCEPTED_UNRESOLVED_RC=$?
set -e
test "${ACCEPTED_UNRESOLVED_RC}" -eq 9
grep -F 'errorCode=DELIVERY_ACCEPTED_PATCH_ID_UNRESOLVED' "${TMP_ROOT}/inventory-accepted-unresolved.out" >/dev/null
rm -f "${REPO}/.git/cocondo-toolkit/accepted/33333333-3333-4333-8333-333333333333.json"

set +e
(
  cd "${FEATURE}"
  ./bin/process-ops.sh delivery-inventory --current-delivery 000995-missing > "${TMP_ROOT}/inventory-current.out" 2>&1
)
CURRENT_RC=$?
set -e
test "${CURRENT_RC}" -eq 9
grep -F 'errorCode=CURRENT_DELIVERY_EXCEPTION_INVALID' "${TMP_ROOT}/inventory-current.out" >/dev/null

# Forbidden and unsafe artifact roots fail independently of an authorization record.
for forbidden_root in /home /tmp /var/tmp /dev/shm "${REPO}" "${REPO}/.git"; do
  set +e
  (
    cd "${FEATURE}"
    COCONDO_ARTIFACT_ROOT="${forbidden_root}" ./bin/process-ops.sh artifact-root-status > "${TMP_ROOT}/artifact-forbidden.out" 2>&1
  )
  FORBIDDEN_RC=$?
  set -e
  test "${FORBIDDEN_RC}" -eq 9
  grep -F 'errorCode=ARTIFACT_ROOT_FORBIDDEN' "${TMP_ROOT}/artifact-forbidden.out" >/dev/null
done

MISSING_ARTIFACT_ROOT="${EXTERNAL_ARTIFACT_ROOT}-missing"
rm -rf "${MISSING_ARTIFACT_ROOT}"
set +e
(
  cd "${FEATURE}"
  COCONDO_ARTIFACT_ROOT="${MISSING_ARTIFACT_ROOT}" ./bin/process-ops.sh artifact-root-status > "${TMP_ROOT}/artifact-missing.out" 2>&1
)
MISSING_ARTIFACT_RC=$?
set -e
test "${MISSING_ARTIFACT_RC}" -eq 9
grep -F 'errorCode=ARTIFACT_ROOT_MISSING' "${TMP_ROOT}/artifact-missing.out" >/dev/null

ARTIFACT_ROOT_LINK="${EXTERNAL_ARTIFACT_ROOT}-link"
rm -f "${ARTIFACT_ROOT_LINK}"
ln -s "${EXTERNAL_ARTIFACT_ROOT}" "${ARTIFACT_ROOT_LINK}"
set +e
(
  cd "${FEATURE}"
  COCONDO_ARTIFACT_ROOT="${ARTIFACT_ROOT_LINK}" ./bin/process-ops.sh artifact-root-status > "${TMP_ROOT}/artifact-symlink.out" 2>&1
)
ARTIFACT_SYMLINK_RC=$?
set -e
test "${ARTIFACT_SYMLINK_RC}" -eq 9
grep -F 'errorCode=ARTIFACT_ROOT_SYMLINK_FORBIDDEN' "${TMP_ROOT}/artifact-symlink.out" >/dev/null
rm -f "${ARTIFACT_ROOT_LINK}"

# Delivery records must be readable and identities must stay canonical and consistent.
mkdir -p "${REPO}/.git/cocondo-process/deliveries/000996-invalid-record"
printf '{\n' > "${REPO}/.git/cocondo-process/deliveries/000996-invalid-record/delivery.json"
set +e
(
  cd "${FEATURE}"
  ./bin/process-ops.sh delivery-inventory > "${TMP_ROOT}/delivery-record-json.out" 2>&1
)
DELIVERY_RECORD_JSON_RC=$?
set -e
test "${DELIVERY_RECORD_JSON_RC}" -eq 9
grep -F 'errorCode=DELIVERY_RECORD_INVALID' "${TMP_ROOT}/delivery-record-json.out" >/dev/null
rm -rf "${REPO}/.git/cocondo-process/deliveries/000996-invalid-record"

mkdir -p "${REPO}/.git/cocondo-toolkit/runs/run-invalid-patch-id"
printf '%s\n' '{"runId":"run-invalid-patch-id","patchId":"999_bad"}' > "${REPO}/.git/cocondo-toolkit/runs/run-invalid-patch-id/run.json"
set +e
(
  cd "${FEATURE}"
  ./bin/process-ops.sh delivery-inventory > "${TMP_ROOT}/inventory-invalid-patch.out" 2>&1
)
INVALID_PATCH_RC=$?
set -e
test "${INVALID_PATCH_RC}" -eq 9
grep -F 'errorCode=DELIVERY_PATCH_ID_INVALID' "${TMP_ROOT}/inventory-invalid-patch.out" >/dev/null
rm -rf "${REPO}/.git/cocondo-toolkit/runs/run-invalid-patch-id"

mkdir -p "${REPO}/.git/cocondo-toolkit/runs/run-unverified-numeric"
printf '%s\n' '{"schemaVersion":"cocondo.run-record.v1","runId":"run-unverified-numeric","command":"patch-dry-run","patchId":"000995","artifactId":"urn:uuid:aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa","metadata":{"artifactFile":"scope__000995_missing-token.zip"}}' > "${REPO}/.git/cocondo-toolkit/runs/run-unverified-numeric/run.json"
set +e
(
  cd "${FEATURE}"
  ./bin/process-ops.sh delivery-inventory > "${TMP_ROOT}/inventory-unverified-numeric.out" 2>&1
)
UNVERIFIED_NUMERIC_RC=$?
set -e
test "${UNVERIFIED_NUMERIC_RC}" -eq 9
grep -F 'errorCode=DELIVERY_LEGACY_PATCH_RUN_UNVERIFIED' "${TMP_ROOT}/inventory-unverified-numeric.out" >/dev/null
rm -rf "${REPO}/.git/cocondo-toolkit/runs/run-unverified-numeric"

mkdir -p "${REPO}/.git/cocondo-toolkit/runs/run-conflicting-numeric"
printf '%s\n' '{"schemaVersion":"cocondo.run-record.v1","runId":"run-conflicting-numeric","command":"patch-accept","patchId":"000995","artifactId":"urn:uuid:aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa","metadata":{"artifactFile":"scope__000994_conflict__aaaaaaaa.zip"}}' > "${REPO}/.git/cocondo-toolkit/runs/run-conflicting-numeric/run.json"
set +e
(
  cd "${FEATURE}"
  ./bin/process-ops.sh delivery-inventory > "${TMP_ROOT}/inventory-conflicting-numeric.out" 2>&1
)
CONFLICTING_NUMERIC_RC=$?
set -e
test "${CONFLICTING_NUMERIC_RC}" -eq 9
grep -F 'errorCode=DELIVERY_LEGACY_PATCH_RUN_IDENTITY_CONFLICT' "${TMP_ROOT}/inventory-conflicting-numeric.out" >/dev/null
rm -rf "${REPO}/.git/cocondo-toolkit/runs/run-conflicting-numeric"

mkdir -p "${REPO}/.git/cocondo-process/deliveries/000999-other"
cat > "${REPO}/.git/cocondo-process/deliveries/000999-other/delivery.json" <<'JSON_CONFLICT'
{
  "schemaVersion": "cocondo.delivery-record.v1",
  "deliveryId": "000999-other",
  "patchId": "000999_other",
  "name": "other",
  "revision": "r1"
}
JSON_CONFLICT
set +e
(
  cd "${FEATURE}"
  ./bin/process-ops.sh delivery-inventory > "${TMP_ROOT}/delivery-run-conflict.out" 2>&1
)
DELIVERY_RUN_CONFLICT_RC=$?
set -e
test "${DELIVERY_RUN_CONFLICT_RC}" -eq 9
grep -F 'errorCode=DELIVERY_PATCH_IDENTITY_CONFLICT' "${TMP_ROOT}/delivery-run-conflict.out" >/dev/null
rm -rf "${REPO}/.git/cocondo-process/deliveries/000999-other"

# Delivery preparation uses only Git-common state, invokes workspace cleanup and creates one immutable record.
printf 'delivery stale\n' > "${REPO}/patches/work/delivery-stale.txt"
DELIVERY_PREPARE_JSON="${TMP_ROOT}/delivery-prepare.json"
(
  cd "${FEATURE}"
  ./bin/process-ops.sh --format json delivery-prepare --name tooling-hardening --revision candidate-r1 > "${DELIVERY_PREPARE_JSON}"
)
python3 - "${DELIVERY_PREPARE_JSON}" "${REPO}" <<'PY_DELIVERY_PREPARE'
import json, sys
from pathlib import Path
v=json.load(open(sys.argv[1]))
root=Path(sys.argv[2])
assert v["deliveryId"] == "001000-tooling-hardening", v
assert v["patchId"] == "001000_tooling-hardening", v
assert v["artifactRootUsed"] is False, v
assert v["artifactPublication"] == "NOT_STARTED", v
assert v["immutableRevision"] is True, v
assert v["workspaceCleanupRemovedEntries"] == 1, v
record=root / ".git/cocondo-process/deliveries/001000-tooling-hardening/delivery.json"
assert record.is_file(), record
assert json.load(open(record))["revision"] == "candidate-r1"
assert not (root / "patches/work/delivery-stale.txt").exists()
PY_DELIVERY_PREPARE

set +e
(
  cd "${FEATURE}"
  ./bin/process-ops.sh delivery-prepare --name tooling-hardening --revision candidate-r1 > "${TMP_ROOT}/delivery-duplicate.out" 2>&1
)
DUPLICATE_DELIVERY_RC=$?
set -e
test "${DUPLICATE_DELIVERY_RC}" -eq 9
# The existing prepared identity is reserved; a second call receives a new identity rather than overwriting it.
grep -F 'errorCode=DELIVERY_REVISION_ALREADY_PREPARED' "${TMP_ROOT}/delivery-duplicate.out" >/dev/null

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
  ./bin/process-ops.sh patch-accept "$(basename "${ARTIFACT}")" > "${TMP_ROOT}/dirty.out" 2>&1
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
