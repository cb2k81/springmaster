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
  local patch_id="$1"
  local zip_path="$2"
  local mode="$3"
  local expected_existing_sha="${4:-}"
  local expected_deleted_sha="${5:-}"
  python3 - "$patch_id" "$zip_path" "$mode" "$expected_existing_sha" "$expected_deleted_sha" <<'PY'
import json
import re
import sys
import zipfile
from pathlib import Path

patch_id, zip_path, mode, expected_existing_sha, expected_deleted_sha = sys.argv[1:6]
zip_path = Path(zip_path)
name = re.sub(r"^\d{6}_", "", patch_id)
manifest = {
    "id": patch_id,
    "patchId": patch_id,
    "scope": "custom",
    "name": name,
    "baseline": {"expectedBeforeSha256": {}},
}
baseline = manifest["baseline"]["expectedBeforeSha256"]
baseline[f"patches/logs/custom/CHANGELOG-{patch_id}.md"] = None
if mode == "mixed":
    if not expected_existing_sha or not expected_deleted_sha:
        raise SystemExit("mixed mode requires expected existing and deleted sha")
    baseline["custom/existing.txt"] = expected_existing_sha
    baseline["custom/new-file.txt"] = None
    baseline["custom/deleted.txt"] = expected_deleted_sha
elif mode == "new-only":
    baseline[f"custom/{name}.txt"] = None
elif mode == "hash-conflict":
    if not expected_existing_sha:
        raise SystemExit("hash-conflict mode requires expected existing sha")
    baseline["custom/existing.txt"] = expected_existing_sha
else:
    raise SystemExit(f"unknown mode: {mode}")

with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as z:
    z.writestr("manifest.json", json.dumps(manifest, indent=2) + "\n")
    z.writestr(f"logs/CHANGELOG-{patch_id}.md", f"# {patch_id}\n\nFixture patch-system integration test.\n")
    if mode == "mixed":
        z.writestr("files/custom/existing.txt", "changed\n")
        z.writestr("files/custom/new-file.txt", "new\n")
        z.writestr("delete/custom/deleted.txt", "")
    elif mode == "new-only":
        z.writestr(f"files/custom/{name}.txt", f"{name}\n")
    elif mode == "hash-conflict":
        z.writestr("files/custom/existing.txt", "guarded-change\n")
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

if command -v git >/dev/null 2>&1; then
  (
    cd "${FIXTURE}"
    git init -q
    git config user.email "patch-fixture@example.invalid"
    git config user.name "Patch Fixture"
    git add .env custom/existing.txt custom/deleted.txt
    git commit -qm "fixture baseline"
  ) >>"${LOG}" 2>&1
else
  log "SKIP: git fixture setup (git not available)"
fi

PATCH1="${PATCHES}/000001_fixture_mixed.zip"
PATCH2="${PATCHES}/000002_fixture_background.zip"
PATCH3="${PATCHES}/000003_fixture_hash_guard.zip"
EXISTING_SHA="$(sha256sum "${FIXTURE}/custom/existing.txt" | awk '{print $1}')"
DELETED_SHA="$(sha256sum "${FIXTURE}/custom/deleted.txt" | awk '{print $1}')"
make_patch "000001_fixture_mixed" "${PATCH1}" mixed "${EXISTING_SHA}" "${DELETED_SHA}"
make_patch "000002_fixture_background" "${PATCH2}" new-only

run python3 "${ENGINE}" "${FIXTURE}" live-baseline "${PATCH1}"
run python3 "${ENGINE}" "${FIXTURE}" apply --dry-run "${PATCH1}"
run python3 "${ENGINE}" "${FIXTURE}" accept "${PATCH1}" --profile docs --no-full-test --no-export --skip-tooling-selfcheck

test -f "${FIXTURE}/custom/new-file.txt"
grep -qx 'changed' "${FIXTURE}/custom/existing.txt"
test ! -e "${FIXTURE}/custom/deleted.txt"
find "${FIXTURE}/patches/logs/accept" -name git-commit.sh -type f | grep -q .

if command -v git >/dev/null 2>&1; then
  GIT_SCRIPT="$(find "${FIXTURE}/patches/logs/accept" -name git-commit.sh -type f | sort | tail -1)"
  printf '%s\n' 'foreign' > "${FIXTURE}/foreign-staged.txt"
  (cd "${FIXTURE}" && git add foreign-staged.txt) >>"${LOG}" 2>&1
  if bash "${GIT_SCRIPT}" >>"${LOG}" 2>&1; then
    log "ERROR: git commit script accepted foreign pre-staged file"
    exit 1
  fi
  grep -q 'GIT_INDEX_DIRTY' "${LOG}"
  (cd "${FIXTURE}" && git reset -q HEAD foreign-staged.txt && rm -f foreign-staged.txt) >>"${LOG}" 2>&1
else
  log "SKIP: git index guard fixture test (git not available)"
fi



if command -v git >/dev/null 2>&1; then
  COMMIT_FIXTURE="${WORK_ROOT}/${RUN_ID}/commit-fixture"
  COMMIT_PATCH="${PATCHES}/000001_fixture_commit.zip"
  mkdir -p "${COMMIT_FIXTURE}/custom" "${COMMIT_FIXTURE}/patches/logs/custom"
  cat > "${COMMIT_FIXTURE}/.env" <<'ENV'
PATCH_LOCAL_SCOPES=custom
PATCH_SCOPE_CUSTOM_PATHS=custom/**
PATCH_SCOPE_CUSTOM_LOG_DIR=custom
PATCH_LOCK_ROOT=patches/runtime/locks
PATCH_FULL_TEST_COMMAND=bash -lc 'printf full-test-ok\n'
PATCH_TEST_SELECTOR_COMMAND_TEMPLATE=bash -lc 'printf selected-test-{test}\n'
PATCH_EXPORT_COMMAND=bash -lc 'mkdir -p exports/text && printf export > exports/text/fixture_export_full_test.zip'
PATCH_TOOLING_SELFCHECK_COMMAND=none
ENV
  (
    cd "${COMMIT_FIXTURE}"
    git init -q
    git config user.email "patch-fixture@example.invalid"
    git config user.name "Patch Fixture"
    git add .env
    git commit -qm "commit fixture baseline"
  ) >>"${LOG}" 2>&1
  make_patch "000001_fixture_commit" "${COMMIT_PATCH}" new-only
  run python3 "${ENGINE}" "${COMMIT_FIXTURE}" accept "${COMMIT_PATCH}" --profile docs --no-full-test --no-export --skip-tooling-selfcheck --commit
  (cd "${COMMIT_FIXTURE}" && git log --oneline -1) >>"${LOG}" 2>&1
  (cd "${COMMIT_FIXTURE}" && git log --oneline -1 | grep -q 'patch(custom): 000001_fixture_commit')
  (cd "${COMMIT_FIXTURE}" && git ls-files custom/fixture_commit.txt | grep -q 'custom/fixture_commit.txt')
  COMMIT_SUMMARY="$(find "${COMMIT_FIXTURE}/patches/logs/accept" -name SUMMARY.txt -type f | sort | tail -1)"
  grep -q 'GIT_COMMIT_STATUS=COMMITTED' "${COMMIT_SUMMARY}"
  grep -q 'GIT_COMMIT_HASH=' "${COMMIT_SUMMARY}"
else
  log "SKIP: direct accept --commit fixture test (git not available)"
fi

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

EXPECTED_SHA="$(sha256sum "${FIXTURE}/custom/existing.txt" | awk '{print $1}')"
make_patch "000003_fixture_hash_guard" "${PATCH3}" hash-conflict "${EXPECTED_SHA}"
printf 'foreign-change\n' > "${FIXTURE}/custom/existing.txt"
if python3 "${ENGINE}" "${FIXTURE}" live-baseline "${PATCH3}" >>"${LOG}" 2>&1; then
  log "ERROR: live baseline hash conflict was not detected"
  exit 1
fi
grep -q 'LIVE_BASELINE_HASH_MISMATCH' "${LOG}"
if python3 "${ENGINE}" "${FIXTURE}" apply --dry-run "${PATCH3}" >>"${LOG}" 2>&1; then
  log "ERROR: baseline hash conflict was not detected"
  exit 1
fi
grep -q 'BASELINE_CONFLICT' "${LOG}"
printf 'original\n' > "${FIXTURE}/custom/existing.txt"
run python3 "${ENGINE}" "${FIXTURE}" live-baseline "${PATCH3}"
run python3 "${ENGINE}" "${FIXTURE}" apply --dry-run "${PATCH3}"

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
