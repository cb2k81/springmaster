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
cat > "${FIXTURE}/.gitignore" <<'EOF'
patches/archives/
patches/runtime/
patches/logs/accept/
build/
target/
exports/
EOF
cat > "${FIXTURE}/.env.example" <<'EOF'
PATCH_LOCAL_SCOPES=custom
PATCH_SCOPE_CUSTOM_PATHS=custom/**
PATCH_SCOPE_CUSTOM_LOG_DIR=custom
PATCH_FULL_TEST_COMMAND=./bin/full-test.sh
PATCH_EXPORT_COMMAND=none
EOF
cat > "${FIXTURE}/bin/full-test.sh" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
grep -Fxq 'qualified' custom/value.txt
EOF
chmod +x "${FIXTURE}/bin/full-test.sh"
printf 'baseline\n' > "${FIXTURE}/custom/value.txt"
(
  cd "${FIXTURE}"
  git init -q
  git config user.name 'Transactional Accept Fixture'
  git config user.email 'transaction@example.invalid'
  git add .
  git commit -qm baseline
)

python3 - "${FIXTURE}" "${PATCHES}" <<'PY'
import hashlib, json, sys, uuid, zipfile
from pathlib import Path
root=Path(sys.argv[1]); out=Path(sys.argv[2])
before=hashlib.sha256((root/'custom/value.txt').read_bytes()).hexdigest()
def write(patch_id,value):
    name=patch_id.split('_',1)[1]
    manifest={
      'schemaVersion':'springmaster.patch-manifest.v2',
      'artifactId':'urn:uuid:'+str(uuid.uuid5(uuid.NAMESPACE_URL,'transaction-it:'+patch_id)),
      'id':patch_id,'patchId':patch_id,'name':name,'scope':'custom',
      'baseline':{'expectedBeforeSha256':{
        'custom/value.txt':before,
        f'patches/logs/custom/CHANGELOG-{patch_id}.md':None,
      }},
    }
    with zipfile.ZipFile(out/f'{patch_id}.zip','w',zipfile.ZIP_DEFLATED) as z:
        z.writestr('manifest.json',json.dumps(manifest,indent=2)+'\n')
        z.writestr('files/custom/value.txt',value+'\n')
        z.writestr(f'logs/CHANGELOG-{patch_id}.md',f'# {patch_id}\n')
write('000001_transaction_failure','not-qualified')
write('000002_transaction_success','qualified')
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
  ./bin/patch.sh accept "${PATCHES}/000002_transaction_success.zip" \
    --profile code --skip-tooling-selfcheck --full-test --no-export --commit
) > "${TMP_ROOT}/success.log" 2>&1
test "$(git -C "${FIXTURE}" rev-parse HEAD)" != "${BASE_HEAD}"
test -z "$(git -C "${FIXTURE}" status --porcelain=v1 --untracked-files=all)"
grep -Fxq 'qualified' "${FIXTURE}/custom/value.txt"
test -f "${FIXTURE}/patches/archives/000002_transaction_success/patch-log.json"
grep -Fxq 'STATUS=SUCCESS' "${FIXTURE}/patches/logs/accept/000002_transaction_success/SUMMARY.txt"

echo 'PATCH_TRANSACTIONAL_ACCEPT_IT=PASS'
