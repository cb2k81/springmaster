#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TMP_ROOT="$(mktemp -d)"
trap 'rm -rf "${TMP_ROOT}"' EXIT
FIXTURE="${TMP_ROOT}/fixture"
HOME_DIR="${TMP_ROOT}/home"
PATCHES="${HOME_DIR}/Downloads"
mkdir -p "${FIXTURE}/bin" "${FIXTURE}/custom" "${PATCHES}"

cp "${SCRIPT_DIR}/patch.py" "${FIXTURE}/bin/patch.py"
cp "${SCRIPT_DIR}/patch.sh" "${FIXTURE}/bin/patch.sh"
chmod +x "${FIXTURE}/bin/patch.py" "${FIXTURE}/bin/patch.sh"

cat > "${FIXTURE}/.gitignore" <<'GITIGNORE'
patches/archives/
patches/runtime/
patches/logs/accept/
patches/logs/validation/
build/
target/
exports/
GITIGNORE

cat > "${FIXTURE}/.env.example" <<'ENV'
PATCH_LOCAL_SCOPES=custom
PATCH_SCOPE_CUSTOM_PATHS=custom/**
PATCH_SCOPE_CUSTOM_LOG_DIR=custom
PATCH_TOOLING_SELFCHECK_COMMAND=none
PATCH_TEST_SELECTOR_COMMAND_TEMPLATE=./bin/test-selector.sh {test}
PATCH_FULL_TEST_COMMAND=./bin/full-test.sh
PATCH_EXPORT_COMMAND=none
ENV

cat > "${FIXTURE}/bin/test-selector.sh" <<'TEST'
#!/usr/bin/env bash
set -euo pipefail
selector="${1:?selector required}"
if [[ "${selector}" == "hold" ]]; then
  sleep 3
fi
[[ "${selector}" != "fail" ]]
TEST

cat > "${FIXTURE}/bin/full-test.sh" <<'FULL'
#!/usr/bin/env bash
set -euo pipefail
test -f custom/value.txt
FULL
chmod +x "${FIXTURE}/bin/test-selector.sh" "${FIXTURE}/bin/full-test.sh"
printf 'baseline\n' > "${FIXTURE}/custom/value.txt"

(
  cd "${FIXTURE}"
  git init -q
  git config user.name 'Patch Run API Fixture'
  git config user.email 'patch-run-api@example.invalid'
  git config gc.auto 0
  git add .
  git commit -qm baseline
)

python3 - "${FIXTURE}" "${PATCHES}" <<'PY'
import hashlib
import json
import sys
import uuid
import zipfile
from pathlib import Path

root = Path(sys.argv[1])
out = Path(sys.argv[2])

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def write(patch_id, before_sha, value):
    name = patch_id.split('_', 1)[1]
    manifest = {
        'schemaVersion': 'springmaster.patch-manifest.v2',
        'artifactId': 'urn:uuid:' + str(uuid.uuid5(uuid.NAMESPACE_URL, 'patch-run-api:' + patch_id)),
        'id': patch_id,
        'patchId': patch_id,
        'name': name,
        'scope': 'custom',
        'baseline': {'expectedBeforeSha256': {
            'custom/value.txt': before_sha,
            f'patches/logs/custom/CHANGELOG-{patch_id}.md': None,
        }},
    }
    with zipfile.ZipFile(out / f'{patch_id}.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        archive.writestr('manifest.json', json.dumps(manifest, indent=2) + '\n')
        archive.writestr('files/custom/value.txt', value)
        archive.writestr(f'logs/CHANGELOG-{patch_id}.md', f'# {patch_id}\n')

baseline_sha = sha(root / 'custom/value.txt')
write('000001_run_api_success', baseline_sha, 'accepted\n')
accepted_sha = hashlib.sha256(b'accepted\n').hexdigest()
write('000002_run_api_whitespace', accepted_sha, 'bad trailing space \n')
write('000003_run_api_integrated_watch', accepted_sha, 'watched\n')
PY

START_ENV="$({
  cd "${FIXTURE}"
  HOME="${HOME_DIR}" ./bin/patch.sh accept "${PATCHES}/000001_run_api_success.zip" \
    --background --wait-for-lock --profile docs --test hold --no-full-test --no-export \
    --skip-tooling-selfcheck --commit --format env
})"
printf '%s\n' "${START_ENV}" > "${TMP_ROOT}/start.env"
grep -Fxq 'STATUS=STARTED' "${TMP_ROOT}/start.env"
grep -Fxq 'COMMAND=accept' "${TMP_ROOT}/start.env"
RUN_ID="$(sed -n 's/^RUN_ID=//p' "${TMP_ROOT}/start.env" | head -n 1)"
RUN_LOG_DIR="$(sed -n 's/^LOG_DIR=//p' "${TMP_ROOT}/start.env" | head -n 1)"
test -n "${RUN_ID}"
test -d "${RUN_LOG_DIR}"
test -f "${RUN_LOG_DIR}/invocation.json"
! grep -Fq "${PATCHES}/000001_run_api_success.zip" "${RUN_LOG_DIR}/run.log"
python3 - "${RUN_LOG_DIR}/invocation.json" "${RUN_ID}" <<'PY'
import json
import sys
from pathlib import Path

path = Path(sys.argv[1])
run_id = sys.argv[2]
data = json.loads(path.read_text(encoding='utf-8'))
assert data['schemaVersion'] == 'springmaster.patch-invocation.v1'
assert data['runId'] == run_id
assert data['subjectName'] == '000001_run_api_success.zip'
assert data['patchFileName'] == '000001_run_api_success.zip'
assert data['startFormat'] == 'env'
assert data['backgroundRequested'] is True
serialized = json.dumps(data, sort_keys=True)
assert '/Downloads/' not in serialized
assert '/home/' not in serialized
PY

(
  cd "${FIXTURE}"
  HOME="${HOME_DIR}" ./bin/patch.sh accept "${PATCHES}/000001_run_api_success.zip" \
    --background --wait-for-lock --profile docs --test hold --no-full-test --no-export \
    --skip-tooling-selfcheck --commit
) > "${TMP_ROOT}/active-duplicate.out"
grep -q 'Status:       ALREADY_RUNNING' "${TMP_ROOT}/active-duplicate.out"
grep -q "Run-ID:       ${RUN_ID}" "${TMP_ROOT}/active-duplicate.out"

(
  cd "${FIXTURE}"
  HOME="${HOME_DIR}" ./bin/patch.sh wait "${RUN_ID}" --interval 1 --timeout 60
) > "${TMP_ROOT}/wait.out"
grep -q 'status=SUCCESS' "${TMP_ROOT}/wait.out"

(
  cd "${FIXTURE}"
  HOME="${HOME_DIR}" ./bin/patch.sh status --patch 000001_run_api_success --format env
) > "${TMP_ROOT}/status.env"
grep -Fxq 'STATUS=APPLIED' "${TMP_ROOT}/status.env"
grep -Fxq 'GIT_COMMIT_STATUS=COMMITTED' "${TMP_ROOT}/status.env"
grep -Fxq "RUN_ID=${RUN_ID}" "${TMP_ROOT}/status.env"
grep -Eq '^ARTIFACT_ID=urn:uuid:[0-9a-f-]+$' "${TMP_ROOT}/status.env"
grep -Eq '^UPDATED_AT=.+$' "${TMP_ROOT}/status.env"
! grep -Fxq 'UPDATED_AT=-' "${TMP_ROOT}/status.env"

CANONICAL_ACCEPT="${FIXTURE}/patches/logs/accept/000001_run_api_success"
test -f "${CANONICAL_ACCEPT}/invocation.json"
RECORDED_RUN_LOG_DIR="$(
  python3 - "${CANONICAL_ACCEPT}/accepted.json" <<'PYJSON'
import json
import sys
print(json.load(open(sys.argv[1], encoding='utf-8')).get('runLogDir', ''))
PYJSON
)"
if [[ -n "${RECORDED_RUN_LOG_DIR}" && "${RECORDED_RUN_LOG_DIR}" != "${CANONICAL_ACCEPT}" ]]; then
  rm -rf "${RECORDED_RUN_LOG_DIR}"
fi
(
  cd "${FIXTURE}"
  HOME="${HOME_DIR}" ./bin/patch.sh status "${RUN_ID}" --format env
) > "${TMP_ROOT}/status-by-run-id-after-compaction.env"
grep -Fxq 'STATUS=APPLIED' "${TMP_ROOT}/status-by-run-id-after-compaction.env"
grep -Fxq "RUN_ID=${RUN_ID}" "${TMP_ROOT}/status-by-run-id-after-compaction.env"
grep -Eq '^ARTIFACT_ID=urn:uuid:[0-9a-f-]+$' "${TMP_ROOT}/status-by-run-id-after-compaction.env"
! grep -Fxq 'UPDATED_AT=-' "${TMP_ROOT}/status-by-run-id-after-compaction.env"

HEAD_AFTER_FIRST="$(git -C "${FIXTURE}" rev-parse HEAD)"
DUPLICATE_JSON="$({
  cd "${FIXTURE}"
  HOME="${HOME_DIR}" ./bin/patch.sh accept "${PATCHES}/000001_run_api_success.zip" \
    --background --wait-for-lock --profile docs --no-full-test --no-export \
    --skip-tooling-selfcheck --commit --format json
})"
printf '%s\n' "${DUPLICATE_JSON}" > "${TMP_ROOT}/duplicate.json"
python3 - "${TMP_ROOT}/duplicate.json" <<'PY'
import json
import sys
assert json.load(open(sys.argv[1], encoding='utf-8'))['status'] == 'ALREADY_APPLIED'
PY
test "$(git -C "${FIXTURE}" rev-parse HEAD)" = "${HEAD_AFTER_FIRST}"

CANONICAL_SHA_BEFORE="$(sha256sum "${CANONICAL_ACCEPT}/SUMMARY.txt" | awk '{print $1}')"
if (
  cd "${FIXTURE}"
  HOME="${HOME_DIR}" ./bin/patch.sh verify 000001_run_api_success --profile docs --test fail \
    --no-full-test --no-export --skip-tooling-selfcheck
) > "${TMP_ROOT}/verify.out" 2>&1; then
  echo 'Expected verify failure.' >&2
  exit 1
fi
CANONICAL_SHA_AFTER="$(sha256sum "${CANONICAL_ACCEPT}/SUMMARY.txt" | awk '{print $1}')"
test "${CANONICAL_SHA_BEFORE}" = "${CANONICAL_SHA_AFTER}"
find "${FIXTURE}/patches/logs/validation" -name SUMMARY.txt -type f -print0 \
  | xargs -0 grep -l '^STATUS=FAILED$' >/dev/null

WHITESPACE_HEAD="$(git -C "${FIXTURE}" rev-parse HEAD)"
if (
  cd "${FIXTURE}"
  HOME="${HOME_DIR}" ./bin/patch.sh accept "${PATCHES}/000002_run_api_whitespace.zip" \
    --profile docs --no-full-test --no-export --skip-tooling-selfcheck --commit
) > "${TMP_ROOT}/whitespace.out" 2>&1; then
  echo 'Expected whitespace patch to fail.' >&2
  exit 1
fi
test "$(git -C "${FIXTURE}" rev-parse HEAD)" = "${WHITESPACE_HEAD}"
grep -q 'Failed-Step:  whitespace' "${TMP_ROOT}/whitespace.out"
test ! -e "${FIXTURE}/patches/archives/000002_run_api_whitespace"
grep -Fxq 'accepted' "${FIXTURE}/custom/value.txt"

set +e
WATCH_OUTPUT="$({
  cd "${FIXTURE}"
  HOME="${HOME_DIR}" ./bin/patch.sh accept "${PATCHES}/000003_run_api_integrated_watch.zip" \
    --background --wait-for-lock --profile docs --test hold --no-full-test --no-export \
    --skip-tooling-selfcheck --commit --watch --watch-interval 1 --watch-timeout 60
} 2>&1)"
WATCH_RC=$?
set -e
printf '%s\n' "${WATCH_OUTPUT}" > "${TMP_ROOT}/integrated-watch.out"
if [[ "${WATCH_RC}" -ne 0 ]]; then
  cat "${TMP_ROOT}/integrated-watch.out" >&2
  exit "${WATCH_RC}"
fi
grep -q 'Status:       STARTED' "${TMP_ROOT}/integrated-watch.out"
grep -q 'status=RUNNING' "${TMP_ROOT}/integrated-watch.out"
grep -q 'status=SUCCESS' "${TMP_ROOT}/integrated-watch.out"
grep -Fxq 'watched' "${FIXTURE}/custom/value.txt"

grep -q '"subjectName": "000003_run_api_integrated_watch.zip"' \
  "${FIXTURE}/patches/logs/accept/000003_run_api_integrated_watch/invocation.json"

for command in status watch wait result; do
  if (
    cd "${FIXTURE}"
    HOME="${HOME_DIR}" ./bin/patch.sh "${command}" ""
  ) > "${TMP_ROOT}/${command}-empty.out" 2>&1; then
    echo "Expected ${command} with an empty reference to fail." >&2
    exit 1
  fi
  grep -q 'Run-ID oder Patch-Referenz darf nicht leer sein' "${TMP_ROOT}/${command}-empty.out"
done

mkdir -p "${FIXTURE}/patches/archives/000000_legacy_applied"
cat > "${FIXTURE}/patches/archives/000000_legacy_applied/patch-log.json" <<'JSON'
{
  "status": "applied",
  "name": "legacy_applied",
  "artifactId": "urn:uuid:00000000-0000-4000-8000-000000000000"
}
JSON

(
  cd "${FIXTURE}"
  HOME="${HOME_DIR}" ./bin/patch.sh doctor
) > "${TMP_ROOT}/doctor-legacy.out"
grep -q 'Status:        PASS' "${TMP_ROOT}/doctor-legacy.out"
grep -q 'Historical-Applied-Without-Canonical: 1' "${TMP_ROOT}/doctor-legacy.out"
grep -q 'WARNING HISTORICAL_APPLIED_WITHOUT_CANONICAL_ACCEPTANCE count=1' "${TMP_ROOT}/doctor-legacy.out"

mkdir -p "${FIXTURE}/patches/archives/999999_current_missing_acceptance"
cat > "${FIXTURE}/patches/archives/999999_current_missing_acceptance/patch-log.json" <<'JSON'
{
  "status": "applied",
  "name": "current_missing_acceptance",
  "artifactId": "urn:uuid:99999999-9999-4999-8999-999999999999"
}
JSON
if (
  cd "${FIXTURE}"
  HOME="${HOME_DIR}" ./bin/patch.sh doctor
) > "${TMP_ROOT}/doctor-current.out" 2>&1; then
  echo 'Expected post-cutover missing canonical acceptance to fail doctor.' >&2
  exit 1
fi
grep -q 'ERROR APPLIED_WITHOUT_CANONICAL_ACCEPTANCE 999999_current_missing_acceptance' "${TMP_ROOT}/doctor-current.out"
rm -rf "${FIXTURE}/patches/archives/999999_current_missing_acceptance"

(
  cd "${FIXTURE}"
  HOME="${HOME_DIR}" ./bin/patch.sh doctor
) > "${TMP_ROOT}/doctor.out"
grep -q 'Status:        PASS' "${TMP_ROOT}/doctor.out"

(
  cd "${FIXTURE}"
  HOME="${HOME_DIR}" ./bin/patch.sh result --patch 000003_run_api_integrated_watch --format env
) > "${TMP_ROOT}/result.env"
grep -Fxq 'STATUS=APPLIED' "${TMP_ROOT}/result.env"

UNEXPECTED_DOWNLOAD_FILES="$(
  find "${PATCHES}" -maxdepth 1 -type f ! -name '*.zip' -printf '%f\n' | sort
)"
test -z "${UNEXPECTED_DOWNLOAD_FILES}"

echo 'PATCH_RUN_API_IT=PASS'
