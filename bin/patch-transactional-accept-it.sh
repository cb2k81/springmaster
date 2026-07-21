#!/usr/bin/env bash
set -euo pipefail

# The integration test may itself run inside a transactional accept child.
# Its fixture must always exercise the public/top-level transaction boundary.
unset PATCH_ACCEPT_WORKTREE_CHILD PATCH_ACCEPT_LOG_DIR PATCH_BACKGROUND_CHILD

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
build/
target/
exports/
GITIGNORE
cat > "${FIXTURE}/.env.example" <<'ENV'
PATCH_LOCAL_SCOPES=custom
PATCH_SCOPE_CUSTOM_PATHS=custom/**
PATCH_SCOPE_CUSTOM_LOG_DIR=custom
PATCH_FULL_TEST_COMMAND=./bin/full-test.sh
PATCH_TEST_SELECTOR_COMMAND_TEMPLATE=./bin/test-selector.sh {test}
PATCH_EXPORT_COMMAND=none
ENV
cat > "${FIXTURE}/bin/full-test.sh" <<'FULLTEST'
#!/usr/bin/env bash
set -euo pipefail
grep -Fxq 'qualified' custom/value.txt
FULLTEST
cat > "${FIXTURE}/bin/tooling-selfcheck.sh" <<'TOOLING'
#!/usr/bin/env bash
set -euo pipefail
test -z "${PATCH_ACCEPT_WORKTREE_CHILD:-}"
test -z "${PATCH_ACCEPT_LOG_DIR:-}"
test -z "${PATCH_BACKGROUND_CHILD:-}"
TOOLING
cat > "${FIXTURE}/bin/test-selector.sh" <<'TESTSELECTOR'
#!/usr/bin/env bash
set -euo pipefail
selector="${1:?test selector required}"
grep -Fxq -- "${selector}" custom/expected-test-selectors.txt
TESTSELECTOR
chmod +x \
  "${FIXTURE}/bin/full-test.sh" \
  "${FIXTURE}/bin/tooling-selfcheck.sh" \
  "${FIXTURE}/bin/test-selector.sh"
printf 'baseline\n' > "${FIXTURE}/custom/value.txt"
LONG_SELECTOR='CatalogItemJpaQueryRepositoryTest,CatalogItemPersistenceContractTest,CatalogItemServiceSpringContextTest,CatalogItemServiceTest,CatalogItemControllerTest,CatalogItemOpenApiDetailLookupContractTest,CatalogItemOpenApiQueryContractTest,CatalogItemOpenApiRequestValidationContractTest,CatalogItemOpenApiWriteContractTest,DomainEntityPersistenceMappingTest,SpringmasterQueryContractReportTest'
printf '%s\n' \
  "${LONG_SELECTOR}" \
  'Collision+Selector' \
  'Collision Selector' \
  > "${FIXTURE}/custom/expected-test-selectors.txt"
(
  cd "${FIXTURE}"
  git init -q
  git config user.name 'Transactional Accept Fixture'
  git config user.email 'transaction@example.invalid'
  git config gc.auto 0
  git add .
  git commit -qm baseline
)

python3 - "${FIXTURE}" "${PATCHES}" <<'PY'
import hashlib, json, sys, uuid, zipfile
from pathlib import Path
root=Path(sys.argv[1]); out=Path(sys.argv[2])

def digest(value):
    return hashlib.sha256((value+'\n').encode()).hexdigest()

def write(patch_id,before_value,after_value):
    name=patch_id.split('_',1)[1]
    manifest={
      'schemaVersion':'springmaster.patch-manifest.v2',
      'artifactId':'urn:uuid:'+str(uuid.uuid5(uuid.NAMESPACE_URL,'transaction-it:'+patch_id)),
      'id':patch_id,'patchId':patch_id,'name':name,'scope':'custom',
      'baseline':{'expectedBeforeSha256':{
        'custom/value.txt':digest(before_value),
        f'patches/logs/custom/CHANGELOG-{patch_id}.md':None,
      }},
    }
    with zipfile.ZipFile(out/f'{patch_id}.zip','w',zipfile.ZIP_DEFLATED) as z:
        z.writestr('manifest.json',json.dumps(manifest,indent=2)+'\n')
        z.writestr('files/custom/value.txt',after_value+'\n')
        z.writestr(f'logs/CHANGELOG-{patch_id}.md',f'# {patch_id}\n')

write('000001_transaction_failure','baseline','not-qualified')
write('000002_transaction_validation_env','baseline','env-isolated')
write('000003_transaction_success','env-isolated','qualified')
write('000004_transaction_long_test_selector','qualified','long-selector-qualified')
PY

BASE_HEAD="$(git -C "${FIXTURE}" rev-parse HEAD)"
if (
  cd "${FIXTURE}"
  ./bin/patch.sh accept "${PATCHES}/000001_transaction_failure.zip" \
    --profile code --skip-tooling-selfcheck --full-test --no-export --commit
) > "${TMP_ROOT}/failure.log" 2>&1; then
  echo 'Expected transactional failure patch to fail.' >&2
  exit 1
fi
test "$(git -C "${FIXTURE}" rev-parse HEAD)" = "${BASE_HEAD}"
test -z "$(git -C "${FIXTURE}" status --porcelain=v1 --untracked-files=all)"
grep -Fxq 'baseline' "${FIXTURE}/custom/value.txt"
test ! -e "${FIXTURE}/patches/archives/000001_transaction_failure"
grep -q 'Failed-Step:  worktree-validation' "${TMP_ROOT}/failure.log"

(
  cd "${FIXTURE}"
  ./bin/patch.sh accept "${PATCHES}/000002_transaction_validation_env.zip" \
    --profile tooling --no-full-test --no-export --commit
) > "${TMP_ROOT}/environment.log" 2>&1
test -z "$(git -C "${FIXTURE}" status --porcelain=v1 --untracked-files=all)"
grep -Fxq 'env-isolated' "${FIXTURE}/custom/value.txt"
test -f "${FIXTURE}/patches/archives/000002_transaction_validation_env/patch-log.json"
grep -Fxq 'STATUS=SUCCESS' "${FIXTURE}/patches/logs/accept/000002_transaction_validation_env/SUMMARY.txt"

ENV_HEAD="$(git -C "${FIXTURE}" rev-parse HEAD)"
test "${ENV_HEAD}" != "${BASE_HEAD}"
(
  cd "${FIXTURE}"
  ./bin/patch.sh accept "${PATCHES}/000003_transaction_success.zip" \
    --profile code --skip-tooling-selfcheck --full-test --no-export --commit
) > "${TMP_ROOT}/success.log" 2>&1
test "$(git -C "${FIXTURE}" rev-parse HEAD)" != "${ENV_HEAD}"
test -z "$(git -C "${FIXTURE}" status --porcelain=v1 --untracked-files=all)"
grep -Fxq 'qualified' "${FIXTURE}/custom/value.txt"
test -f "${FIXTURE}/patches/archives/000003_transaction_success/patch-log.json"
grep -Fxq 'STATUS=SUCCESS' "${FIXTURE}/patches/logs/accept/000003_transaction_success/SUMMARY.txt"

LONG_SELECTOR_HEAD="$(git -C "${FIXTURE}" rev-parse HEAD)"
(
  cd "${FIXTURE}"
  ./bin/patch.sh accept "${PATCHES}/000004_transaction_long_test_selector.zip" \
    --profile tooling \
    --test "${LONG_SELECTOR}" \
    --test 'Collision+Selector' \
    --test 'Collision Selector' \
    --no-full-test --no-export --commit
) > "${TMP_ROOT}/long-selector.log" 2>&1
test "$(git -C "${FIXTURE}" rev-parse HEAD)" != "${LONG_SELECTOR_HEAD}"
test -z "$(git -C "${FIXTURE}" status --porcelain=v1 --untracked-files=all)"
grep -Fxq 'long-selector-qualified' "${FIXTURE}/custom/value.txt"
test -f "${FIXTURE}/patches/archives/000004_transaction_long_test_selector/patch-log.json"
grep -Fxq 'STATUS=SUCCESS' "${FIXTURE}/patches/logs/accept/000004_transaction_long_test_selector/SUMMARY.txt"

python3 - "${FIXTURE}" "${LONG_SELECTOR}" <<'PY'
from pathlib import Path
import re
import sys

fixture = Path(sys.argv[1])
long_selector = sys.argv[2]
log_dir = fixture / 'patches/logs/accept/000004_transaction_long_test_selector/child-accept'
logs = sorted(log_dir.glob('test-*.log'))
if len(logs) != 3:
    raise SystemExit(f'Expected three selector logs, found {len(logs)}: {logs}')

names = [path.name for path in logs]
if len(names) != len(set(names)):
    raise SystemExit(f'Test selector log names are not unique: {names}')
for name in names:
    if len(name.encode('utf-8')) > 120:
        raise SystemExit(f'Test selector log basename exceeds 120 bytes: {name}')

long_logs = [path for path in logs if long_selector in path.read_text(encoding='utf-8')]
if len(long_logs) != 1:
    raise SystemExit(f'Long selector was not preserved in exactly one log: {long_logs}')
if not re.search(r'-[0-9a-f]{12}\.log$', long_logs[0].name):
    raise SystemExit(f'Long selector log lacks deterministic digest suffix: {long_logs[0].name}')

for selector in ('Collision+Selector', 'Collision Selector'):
    matches = [path for path in logs if selector in path.read_text(encoding='utf-8')]
    if len(matches) != 1:
        raise SystemExit(f'Selector was not preserved in exactly one log: {selector}: {matches}')
PY

echo 'PATCH_TRANSACTIONAL_ACCEPT_IT=PASS'
