#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
ENGINE="${REPO_ROOT}/bin/patch.py"
WORK_ROOT="${REPO_ROOT}/build/patch-system-it"
RUN_ID="$(date +%Y%m%d_%H%M%S)_$$"
FIXTURE="${WORK_ROOT}/${RUN_ID}/fixture"
PATCHES="${WORK_ROOT}/${RUN_ID}/patches"
LOG="${WORK_ROOT}/${RUN_ID}/run.log"

mkdir -p "${FIXTURE}" "${PATCHES}" "$(dirname "${LOG}")"

log() {
  printf '%s\n' "$*" | tee -a "${LOG}"
}

run() {
  log "== $* =="
  "$@" >>"${LOG}" 2>&1
}

make_patch() {
  local name="$1"
  local zip_path="$2"
  local mode="$3"
  python3 - "$name" "$zip_path" "$mode" <<'PY'
import json
import sys
import zipfile
from pathlib import Path

name, zip_path, mode = sys.argv[1:4]
zip_path = Path(zip_path)
manifest = {"scope": "custom", "name": name}
with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as z:
    z.writestr("manifest.json", json.dumps(manifest, indent=2) + "\n")
    z.writestr(f"logs/CHANGELOG-{name}.md", f"# {name}\n\nFixture patch-system integration test.\n")
    if mode == "mixed":
        z.writestr("files/custom/existing.txt", "changed\n")
        z.writestr("files/custom/new-file.txt", "new\n")
        z.writestr("delete/custom/deleted.txt", "")
    elif mode == "new-only":
        z.writestr(f"files/custom/{name}.txt", f"{name}\n")
    else:
        raise SystemExit(f"unknown mode: {mode}")
PY
}

log "Fixture: ${FIXTURE}"
mkdir -p "${FIXTURE}/custom" "${FIXTURE}/patches/logs/custom"
printf 'original\n' > "${FIXTURE}/custom/existing.txt"
printf 'delete-me\n' > "${FIXTURE}/custom/deleted.txt"
cat > "${FIXTURE}/.env" <<'ENV'
PATCH_LOCAL_SCOPES=custom
PATCH_SCOPE_CUSTOM_PATHS=custom/**
PATCH_SCOPE_CUSTOM_LOG_DIR=custom
PATCH_LOCK_ROOT=patches/runtime/locks
PATCH_FULL_TEST_COMMAND=bash -lc 'printf full-test-ok\\n'
PATCH_TEST_SELECTOR_COMMAND_TEMPLATE=bash -lc 'printf selected-test-{test}\\n'
PATCH_EXPORT_COMMAND=bash -lc 'mkdir -p exports/text && printf export > exports/text/fixture_export_full_test.zip'
PATCH_TOOLING_SELFCHECK_COMMAND=none
ENV

PATCH1="${PATCHES}/fixture_mixed.zip"
PATCH2="${PATCHES}/fixture_background.zip"
make_patch "fixture_mixed" "${PATCH1}" mixed
make_patch "fixture_background" "${PATCH2}" new-only

run python3 "${ENGINE}" "${FIXTURE}" apply --dry-run "${PATCH1}"
run python3 "${ENGINE}" "${FIXTURE}" accept "${PATCH1}" --profile docs --no-full-test --no-export --skip-tooling-selfcheck

test -f "${FIXTURE}/custom/new-file.txt"
grep -qx 'changed' "${FIXTURE}/custom/existing.txt"
test ! -e "${FIXTURE}/custom/deleted.txt"
find "${FIXTURE}/patches/logs/accept" -name git-commit.sh -type f | grep -q .

run python3 "${ENGINE}" "${FIXTURE}" rollback --dry-run latest
run python3 "${ENGINE}" "${FIXTURE}" rollback latest

test ! -e "${FIXTURE}/custom/new-file.txt"
grep -qx 'original' "${FIXTURE}/custom/existing.txt"
grep -qx 'delete-me' "${FIXTURE}/custom/deleted.txt"
run python3 "${ENGINE}" "${FIXTURE}" show latest
grep -q 'Status:        rolled_back' "${LOG}"

if python3 "${ENGINE}" "${FIXTURE}" rollback latest >>"${LOG}" 2>&1; then
  log "ERROR: second rollback unexpectedly succeeded"
  exit 1
fi

LOCK_DIR="${FIXTURE}/patches/runtime/locks"
mkdir -p "${LOCK_DIR}"
python3 - "${LOCK_DIR}/project-write.lock" <<PY
import json, os, socket, sys
from datetime import datetime, timezone
path = sys.argv[1]
payload = {
  "projectRoot": "${FIXTURE}",
  "pid": os.getppid(),
  "host": socket.gethostname(),
  "command": "fixture-lock",
  "subject": "manual-lock",
  "startedAt": datetime.now(timezone.utc).isoformat(),
  "token": "fixture"
}
open(path, "w", encoding="utf-8").write(json.dumps(payload, indent=2) + "\n")
PY
if python3 "${ENGINE}" "${FIXTURE}" accept "${PATCH2}" --profile docs --no-full-test --no-export --skip-tooling-selfcheck >>"${LOG}" 2>&1; then
  log "ERROR: accept under active lock unexpectedly succeeded"
  exit 1
fi
grep -q 'Status:       BUSY' "${LOG}"
rm -f "${LOCK_DIR}/project-write.lock"

if [[ "${PATCH_SYSTEM_IT_WITH_BACKGROUND:-0}" == "1" ]]; then
BG_OUT="${WORK_ROOT}/${RUN_ID}/background.out"
  python3 "${ENGINE}" "${FIXTURE}" accept "${PATCH2}" --background --wait --profile docs --no-full-test --no-export --skip-tooling-selfcheck >"${BG_OUT}" 2>&1
  cat "${BG_OUT}" >>"${LOG}"
  grep -q 'Status:       RUNNING' "${BG_OUT}"
  SUMMARY_PATH="$(awk -F'Summary:[[:space:]]*' '/Summary:/ {print $2; exit}' "${BG_OUT}")"
  if [[ -z "${SUMMARY_PATH}" ]]; then
    log "ERROR: background summary path missing"
    exit 1
  fi
  for _ in $(seq 1 60); do
    if [[ -f "${SUMMARY_PATH}" ]] && grep -Eq 'STATUS=(SUCCESS|FAILED|ALREADY_APPLIED)' "${SUMMARY_PATH}"; then
      break
    fi
    sleep 1
  done
  cat "${SUMMARY_PATH}" >>"${LOG}"
  grep -q 'STATUS=SUCCESS' "${SUMMARY_PATH}"
  test -f "${FIXTURE}/custom/fixture_background.txt"
  
  test ! -e "${FIXTURE}/patches/runtime/locks/project-write.lock"
  
else
  log "SKIP: background fixture test (set PATCH_SYSTEM_IT_WITH_BACKGROUND=1 to enable)"
fi

log "PASS: patch-system integration and rollback fixture"
log "Log: ${LOG}"
