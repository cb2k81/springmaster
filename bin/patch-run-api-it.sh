#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TMP_ROOT="$(mktemp -d)"
trap 'rm -rf "${TMP_ROOT}"' EXIT
FIXTURE="${TMP_ROOT}/fixture"
PATCHES="${TMP_ROOT}/patches"
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
PY

START_OUT="${TMP_ROOT}/start.out"
(
  cd "${FIXTURE}"
  ./bin/patch.sh accept "${PATCHES}/000001_run_api_success.zip" \
    --background --wait-for-lock --profile docs --test hold --no-full-test --no-export \
    --skip-tooling-selfcheck --commit
) > "${START_OUT}"

RUN_ID="$(sed -n 's/^[[:space:]]*Run-ID:[[:space:]]*//p' "${START_OUT}" | head -n 1)"
test -n "${RUN_ID}"
(
  cd "${FIXTURE}"
  ./bin/patch.sh accept "${PATCHES}/000001_run_api_success.zip" \
    --background --wait-for-lock --profile docs --test hold --no-full-test --no-export \
    --skip-tooling-selfcheck --commit
) > "${TMP_ROOT}/active-duplicate.out"
grep -q 'Status:       ALREADY_RUNNING' "${TMP_ROOT}/active-duplicate.out"
grep -q "Run-ID:       ${RUN_ID}" "${TMP_ROOT}/active-duplicate.out"
(
  cd "${FIXTURE}"
  ./bin/patch.sh wait "${RUN_ID}" --interval 1 --timeout 60
) > "${TMP_ROOT}/wait.out"
grep -q 'status=SUCCESS' "${TMP_ROOT}/wait.out"

(
  cd "${FIXTURE}"
  ./bin/patch.sh status 000001_run_api_success --format env
) > "${TMP_ROOT}/status.env"
grep -Fxq 'STATUS=APPLIED' "${TMP_ROOT}/status.env"
grep -Fxq 'GIT_COMMIT_STATUS=COMMITTED' "${TMP_ROOT}/status.env"
grep -Fxq "RUN_ID=${RUN_ID}" "${TMP_ROOT}/status.env"
grep -Eq '^ARTIFACT_ID=urn:uuid:[0-9a-f-]+$' "${TMP_ROOT}/status.env"
grep -Eq '^UPDATED_AT=.+$' "${TMP_ROOT}/status.env"
! grep -Fxq 'UPDATED_AT=-' "${TMP_ROOT}/status.env"

CANONICAL_ACCEPT="${FIXTURE}/patches/logs/accept/000001_run_api_success"
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
  ./bin/patch.sh status "${RUN_ID}" --format env
) > "${TMP_ROOT}/status-by-run-id-after-compaction.env"
grep -Fxq 'STATUS=APPLIED' "${TMP_ROOT}/status-by-run-id-after-compaction.env"
grep -Fxq "RUN_ID=${RUN_ID}" "${TMP_ROOT}/status-by-run-id-after-compaction.env"
grep -Eq '^ARTIFACT_ID=urn:uuid:[0-9a-f-]+$' "${TMP_ROOT}/status-by-run-id-after-compaction.env"
! grep -Fxq 'UPDATED_AT=-' "${TMP_ROOT}/status-by-run-id-after-compaction.env"

HEAD_AFTER_FIRST="$(git -C "${FIXTURE}" rev-parse HEAD)"
(
  cd "${FIXTURE}"
  ./bin/patch.sh accept "${PATCHES}/000001_run_api_success.zip" \
    --background --wait-for-lock --profile docs --no-full-test --no-export \
    --skip-tooling-selfcheck --commit
) > "${TMP_ROOT}/duplicate.out"
grep -q 'Status:       ALREADY_APPLIED' "${TMP_ROOT}/duplicate.out"
test "$(git -C "${FIXTURE}" rev-parse HEAD)" = "${HEAD_AFTER_FIRST}"

test -f "${FIXTURE}/patches/logs/accept/000001_run_api_success/SUMMARY.txt"
CANONICAL_SHA_BEFORE="$(sha256sum "${FIXTURE}/patches/logs/accept/000001_run_api_success/SUMMARY.txt" | awk '{print $1}')"
if (
  cd "${FIXTURE}"
  ./bin/patch.sh verify 000001_run_api_success --profile docs --test fail \
    --no-full-test --no-export --skip-tooling-selfcheck
) > "${TMP_ROOT}/verify.out" 2>&1; then
  echo 'Expected verify failure.' >&2
  exit 1
fi
CANONICAL_SHA_AFTER="$(sha256sum "${FIXTURE}/patches/logs/accept/000001_run_api_success/SUMMARY.txt" | awk '{print $1}')"
test "${CANONICAL_SHA_BEFORE}" = "${CANONICAL_SHA_AFTER}"
find "${FIXTURE}/patches/logs/validation" -name SUMMARY.txt -type f -print0 \
  | xargs -0 grep -l '^STATUS=FAILED$' >/dev/null

WHITESPACE_HEAD="$(git -C "${FIXTURE}" rev-parse HEAD)"
if (
  cd "${FIXTURE}"
  ./bin/patch.sh accept "${PATCHES}/000002_run_api_whitespace.zip" \
    --profile docs --no-full-test --no-export --skip-tooling-selfcheck --commit
) > "${TMP_ROOT}/whitespace.out" 2>&1; then
  echo 'Expected whitespace patch to fail.' >&2
  exit 1
fi
test "$(git -C "${FIXTURE}" rev-parse HEAD)" = "${WHITESPACE_HEAD}"
grep -q 'Failed-Step:  whitespace' "${TMP_ROOT}/whitespace.out"
test ! -e "${FIXTURE}/patches/archives/000002_run_api_whitespace"
grep -Fxq 'accepted' "${FIXTURE}/custom/value.txt"

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
  ./bin/patch.sh doctor
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
  ./bin/patch.sh doctor
) > "${TMP_ROOT}/doctor-current.out" 2>&1; then
  echo 'Expected post-cutover missing canonical acceptance to fail doctor.' >&2
  exit 1
fi
grep -q 'ERROR APPLIED_WITHOUT_CANONICAL_ACCEPTANCE 999999_current_missing_acceptance' "${TMP_ROOT}/doctor-current.out"
rm -rf "${FIXTURE}/patches/archives/999999_current_missing_acceptance"

(
  cd "${FIXTURE}"
  ./bin/patch.sh doctor
) > "${TMP_ROOT}/doctor.out"
grep -q 'Status:        PASS' "${TMP_ROOT}/doctor.out"

(
  cd "${FIXTURE}"
  ./bin/patch.sh result 000001_run_api_success --format env
) > "${TMP_ROOT}/result.env"
grep -Fxq 'STATUS=APPLIED' "${TMP_ROOT}/result.env"

echo 'PATCH_RUN_API_IT=PASS'
