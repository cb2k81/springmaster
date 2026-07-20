#!/usr/bin/env bash
set -euo pipefail
set +H

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"
SOURCE_TARGET_NAME="${1:-zbm}"
SOURCE_DESCRIPTOR="${PROJECT_ROOT}/platform/update/targets/${SOURCE_TARGET_NAME}.env"

fail() {
  echo "[FAIL] $*" >&2
  exit 1
}

[[ -f "${SOURCE_DESCRIPTOR}" ]] || fail "target descriptor missing: ${SOURCE_DESCRIPTOR}"
descriptor_value() {
  local key="$1"
  sed -n "s/^${key}=//p" "${SOURCE_DESCRIPTOR}" | head -n 1
}

TARGET_PATH_VALUE="$(descriptor_value TARGET_PATH)"
TARGET_APP_NAME_VALUE="$(descriptor_value TARGET_APP_NAME)"
TARGET_BASE_PACKAGE_VALUE="$(descriptor_value TARGET_BASE_PACKAGE)"
TARGET_PORT_VALUE="$(descriptor_value TARGET_PORT)"
TARGET_DB_NAME_VALUE="$(descriptor_value TARGET_DB_NAME)"
TARGET_STAGE_DB_NAME_VALUE="$(descriptor_value TARGET_STAGE_DB_NAME)"
SOURCE_TARGET_PATH="${2:-${TARGET_PATH_VALUE}}"
[[ -n "${SOURCE_TARGET_PATH}" && -d "${SOURCE_TARGET_PATH}/.git" ]] || \
  fail "target Git repository missing: ${SOURCE_TARGET_PATH:-<empty>}"
[[ -z "$(git -C "${SOURCE_TARGET_PATH}" status --porcelain --untracked-files=all)" ]] || \
  fail "source target working tree must be clean"

WORK_ROOT="$(mktemp -d)"
trap 'rm -rf "${WORK_ROOT}"' EXIT
TARGET_COPY="${WORK_ROOT}/target"
TARGETS_DIR="${WORK_ROOT}/targets"
BUILD_DIR="${WORK_ROOT}/build"
FULL_TEST_MARKER="${WORK_ROOT}/full-test.marker"
FULL_TEST_COMMAND="${WORK_ROOT}/full-test-command.sh"
mkdir -p "${TARGETS_DIR}"

cat > "${FULL_TEST_COMMAND}" <<EOF
#!/usr/bin/env bash
set -euo pipefail
printf 'FULL_TEST_INVOKED\n' > "${FULL_TEST_MARKER}"
EOF
chmod +x "${FULL_TEST_COMMAND}"

git clone --quiet --no-hardlinks "${SOURCE_TARGET_PATH}" "${TARGET_COPY}"
for rel in .env patches/archives patches/applied patches/history; do
  if [[ -e "${SOURCE_TARGET_PATH}/${rel}" ]]; then
    mkdir -p "${TARGET_COPY}/$(dirname "${rel}")"
    cp -a "${SOURCE_TARGET_PATH}/${rel}" "${TARGET_COPY}/${rel}"
  fi
done

# The integration test proves explicit full-test invocation without coupling the
# generic Springmaster contract test to the target application's current Maven
# maturity. The real ZBM cutover runner must run the actual target Maven command.
printf '\nPATCH_FULL_TEST_COMMAND=%s\n' "${FULL_TEST_COMMAND}" >> "${TARGET_COPY}/.env"

cat > "${TARGETS_DIR}/${SOURCE_TARGET_NAME}.env" <<EOF
TARGET_NAME=${SOURCE_TARGET_NAME}
TARGET_STATUS=DELIVERY_ENABLED
TARGET_PATH=${TARGET_COPY}
TARGET_APP_NAME=${TARGET_APP_NAME_VALUE:-${SOURCE_TARGET_NAME}}
TARGET_BASE_PACKAGE=${TARGET_BASE_PACKAGE_VALUE:-}
TARGET_PORT=${TARGET_PORT_VALUE:-}
TARGET_DB_NAME=${TARGET_DB_NAME_VALUE:-}
TARGET_STAGE_DB_NAME=${TARGET_STAGE_DB_NAME_VALUE:-}
TARGET_LIFECYCLE=update-enabled
TARGET_INITIALIZATION_ALLOWED=false
TARGET_UPDATE_ALLOWED=true
TARGET_DELIVERY_ENABLED=true
TARGET_ALLOWED_PROFILES=tooling-cutover
TARGET_NOTES=Temporary tooling-cutover integration target.
EOF

latest_before="$(cd "${TARGET_COPY}" && ./bin/patch.sh show latest | sed -n 's/^Patch-ID:[[:space:]]*//p' | head -n 1)"
[[ "${latest_before}" =~ ^([0-9]{6})_ ]] || fail "cannot derive latest target patch: ${latest_before}"
expected_number="$(printf '%06d' "$((10#${BASH_REMATCH[1]} + 1))")"

run_update() {
  PLATFORM_UPDATE_TARGET_DIR="${TARGETS_DIR}" \
  PLATFORM_UPDATE_BUILD_WORKSPACE_DIR="${BUILD_DIR}" \
    "${PROJECT_ROOT}/bin/platform-update.sh" "$@"
}

output="$(run_update generate "${SOURCE_TARGET_NAME}" --profile tooling-cutover)"
printf '%s\n' "${output}" > "${WORK_ROOT}/generate.log"
zip_path="$(printf '%s\n' "${output}" | sed -n 's/^  ZIP:[[:space:]]*//p' | tail -n 1)"
report_path="$(printf '%s\n' "${output}" | sed -n 's/^  Preflight:[[:space:]]*//p' | tail -n 1)"
[[ -f "${zip_path}" ]] || fail "generated ZIP missing: ${zip_path}"
[[ -f "${report_path}" ]] || fail "producer preflight report missing: ${report_path}"

generated_id="$(python3 - "${zip_path}" <<'PY'
import json,sys,zipfile
with zipfile.ZipFile(sys.argv[1]) as zf:
    print(json.loads(zf.read('manifest.json'))['patchId'])
PY
)"
[[ "${generated_id}" == "${expected_number}_springmaster_platform_update_tooling-cutover_for_${SOURCE_TARGET_NAME}" ]] || \
  fail "unexpected target-bound patch id: ${generated_id}"

python3 - "${zip_path}" "${TARGET_COPY}" "${PROJECT_ROOT}" <<'PY'
import hashlib,json,stat,sys,uuid,zipfile
from pathlib import Path
zip_path=Path(sys.argv[1]); target=Path(sys.argv[2]); source=Path(sys.argv[3])
with zipfile.ZipFile(zip_path) as zf:
    manifest=json.loads(zf.read('manifest.json'))
    names=[n for n in zf.namelist() if not n.endswith('/')]
    ops=[]
    for name in names:
        if name.startswith('files/'):
            ops.append((name,name[6:]))
        elif name.startswith('logs/'):
            ops.append((name,'patches/logs/tooling/'+Path(name).name))
    expected=manifest['baseline']['expectedBeforeSha256']
    assert manifest['schemaVersion']=='springmaster.patch-manifest.v2'
    assert manifest['id']==manifest['patchId']
    assert manifest['artifactId']==f"urn:uuid:{uuid.UUID(manifest['artifactId'].removeprefix('urn:uuid:'))}"
    assert manifest['scope']=='tooling'
    assert manifest['requires']['target']
    assert manifest['requires']['profile']=='tooling-cutover'
    assert set(expected)=={target_path for _,target_path in ops}
    assert 'files/export.config.json' in names
    cutover_config=json.loads(zf.read('files/export.config.json'))
    target_config=json.loads((target/'export.config.json').read_text())
    assert cutover_config['projectKey']==target_config['projectKey']
    assert 'patches/logs/validation/**' in cutover_config['globalExclude']
    for member,target_path in ops:
        current=target/target_path
        actual=hashlib.sha256(current.read_bytes()).hexdigest() if current.is_file() else None
        assert expected[target_path]==actual, (target_path,expected[target_path],actual)
        if current.is_file():
            payload=zf.read(member)
            payload_exec=bool((zf.getinfo(member).external_attr>>16)&0o111)
            current_exec=bool(stat.S_IMODE(current.stat().st_mode)&0o111)
            assert hashlib.sha256(payload).hexdigest()!=actual or payload_exec!=current_exec, target_path
    required=[
        'bin/dbtool.sh',
        'bin/patch-artifact-preflight.py',
        'bin/patch-artifact-preflight-it.sh',
        'bin/export-integrity-check.py',
        'bin/export-integrity-it.sh',
    ]
    for rel in required:
        source_file=source/rel
        target_file=target/rel
        differs=(not target_file.is_file() or source_file.read_bytes()!=target_file.read_bytes() or bool(source_file.stat().st_mode&0o111)!=bool(target_file.stat().st_mode&0o111))
        if differs:
            assert 'files/'+rel in names, rel
report=json.loads(Path(sys.argv[1]).parent.parent.joinpath('manifests',manifest['patchId']+'_producer_preflight','REPORT.json').read_text())
assert report['status']=='PASS'
assert report['artifactId']==manifest['artifactId']
PY

run_update preflight "${SOURCE_TARGET_NAME}" --zip "${zip_path}" > "${WORK_ROOT}/target-preflight.log"
grep -q 'Status:[[:space:]]*PASSED' "${WORK_ROOT}/target-preflight.log" || fail "target dry-run did not pass"

mutation_path="bin/patch.sh"
cp "${TARGET_COPY}/${mutation_path}" "${WORK_ROOT}/patch.sh.before"
printf '\n# integration mutation\n' >> "${TARGET_COPY}/${mutation_path}"
if run_update preflight "${SOURCE_TARGET_NAME}" --zip "${zip_path}" >"${WORK_ROOT}/baseline-negative.log" 2>&1; then
  fail "baseline mutation was not rejected"
fi
mv "${WORK_ROOT}/patch.sh.before" "${TARGET_COPY}/${mutation_path}"
chmod +x "${TARGET_COPY}/${mutation_path}"

git -C "${TARGET_COPY}" checkout -- "${mutation_path}"
printf '\n# dirty target\n' >> "${TARGET_COPY}/${mutation_path}"
if run_update generate "${SOURCE_TARGET_NAME}" --profile tooling-cutover --dry-run >"${WORK_ROOT}/dirty-negative.log" 2>&1; then
  fail "dirty target was not rejected"
fi
git -C "${TARGET_COPY}" checkout -- "${mutation_path}"

sed -i 's/^TARGET_ALLOWED_PROFILES=.*/TARGET_ALLOWED_PROFILES=core/' "${TARGETS_DIR}/${SOURCE_TARGET_NAME}.env"
if run_update generate "${SOURCE_TARGET_NAME}" --profile tooling-cutover --dry-run >"${WORK_ROOT}/profile-negative.log" 2>&1; then
  fail "disallowed profile was not rejected"
fi
sed -i 's/^TARGET_ALLOWED_PROFILES=.*/TARGET_ALLOWED_PROFILES=tooling-cutover/' "${TARGETS_DIR}/${SOURCE_TARGET_NAME}.env"

source_head_before="$(git -C "${SOURCE_TARGET_PATH}" rev-parse HEAD)"
source_status_before="$(git -C "${SOURCE_TARGET_PATH}" status --porcelain --untracked-files=all)"
source_latest_before="$(cd "${SOURCE_TARGET_PATH}" && ./bin/patch.sh show latest | sed -n 's/^Patch-ID:[[:space:]]*//p' | head -n 1)"

apply_output="$(run_update target-apply "${SOURCE_TARGET_NAME}" --zip "${zip_path}")"
printf '%s\n' "${apply_output}" > "${WORK_ROOT}/target-apply.log"
grep -q 'Status:[[:space:]]*OK' "${WORK_ROOT}/target-apply.log" || fail "isolated target apply did not succeed"
grep -q 'Validation:[[:space:]]*profile=tooling, full-test=True' "${WORK_ROOT}/target-apply.log" || \
  fail "target apply did not report the mandatory tooling full-test policy"

accept_dir="${TARGET_COPY}/patches/logs/validation/platform-update-${generated_id}"
accept_summary="${accept_dir}/SUMMARY.txt"
[[ -f "${accept_summary}" ]] || fail "isolated target accept summary missing: ${accept_summary}"
grep -Fxq 'STATUS=SUCCESS' "${accept_summary}" || fail "isolated target accept status is not SUCCESS"
grep -Fxq 'PROFILE=tooling' "${accept_summary}" || fail "isolated target accept profile is not tooling"
grep -Fxq 'FULL_TEST=True' "${accept_summary}" || fail "isolated target accept did not run the full-test command"
grep -Fxq 'EXPORT=False' "${accept_summary}" || fail "isolated target accept unexpectedly owned the export"
grep -Fxq 'LATEST_EXPORT=-' "${accept_summary}" || fail "isolated target accept unexpectedly reported an export"
[[ -f "${FULL_TEST_MARKER}" ]] || fail "explicit full-test command was not invoked"

target_export="$(sed -n 's/^  Export-Pfad:[[:space:]]*//p' "${WORK_ROOT}/target-apply.log" | tail -n 1)"
[[ -n "${target_export}" && -f "${target_export}" ]] || fail "target-apply closure export missing: ${target_export:-<empty>}"
[[ "$(basename "${target_export}")" == "${SOURCE_TARGET_NAME}_export_full_"*.zip ]] || \
  fail "target export inherited the wrong project key: ${target_export}"
python3 "${TARGET_COPY}/bin/export-integrity-check.py" \
  "${target_export}" --source-root "${TARGET_COPY}" --require-evidence \
  > "${WORK_ROOT}/target-export-integrity.log"

python3 - "${target_export}" "${generated_id}" "${SOURCE_TARGET_NAME}" <<'PY'
import json,sys,zipfile
from pathlib import PurePosixPath
with zipfile.ZipFile(sys.argv[1]) as zf:
    meta_name=next(n for n in zf.namelist() if n.endswith('.meta.json'))
    meta=json.loads(zf.read(meta_name))
    assert meta['projectKey']==sys.argv[3]
    assert meta['projectKeySource']=='APP_EXPORT_PROJECT_KEY'
    evidence_name=str(PurePosixPath(meta_name).parent / meta['closureEvidenceFile'])
    evidence=json.loads(zf.read(evidence_name))['sourceEvidence']
    assert evidence['patchId']==sys.argv[2]
    assert evidence['artifactId'].startswith('urn:uuid:')
    assert evidence['generatedProfile']=='tooling-cutover'
    assert evidence['acceptProfile']=='tooling'
    assert evidence['fullTest'] is True
    assert evidence['acceptExport'] is False
    assert evidence['producerArtifactPreflight']=='PASS'
    assert evidence['targetDryRun']=='PASS'
    assert evidence['targetAccept']=='SUCCESS'
PY

python3 - "${TARGET_COPY}/export.config.json" <<'PY'
import json,sys
config=json.load(open(sys.argv[1],encoding='utf-8'))
assert 'patches/logs/validation/**' in config['globalExclude']
PY

latest_after="$(cd "${TARGET_COPY}" && ./bin/patch.sh show latest | sed -n 's/^Patch-ID:[[:space:]]*//p' | head -n 1)"
[[ "${latest_after}" == "${generated_id}" ]] || fail "isolated target latest patch mismatch: ${latest_after}"

[[ "$(git -C "${SOURCE_TARGET_PATH}" rev-parse HEAD)" == "${source_head_before}" ]] || \
  fail "source target HEAD changed during isolated delivery test"
[[ "$(git -C "${SOURCE_TARGET_PATH}" status --porcelain --untracked-files=all)" == "${source_status_before}" ]] || \
  fail "source target working tree changed during isolated delivery test"
source_latest_after="$(cd "${SOURCE_TARGET_PATH}" && ./bin/patch.sh show latest | sed -n 's/^Patch-ID:[[:space:]]*//p' | head -n 1)"
[[ "${source_latest_after}" == "${source_latest_before}" ]] || \
  fail "source target latest patch changed during isolated delivery test"

echo "PLATFORM_UPDATE_DELIVERY_CONTRACT_IT=PASS"
echo "TARGET=${SOURCE_TARGET_NAME}"
echo "SOURCE_LATEST=${latest_before}"
echo "GENERATED_PATCH=${generated_id}"
echo "GENERATED_ZIP_SHA256=$(sha256sum "${zip_path}" | awk '{print $1}')"
echo "TARGET_ACCEPT_PROFILE=tooling"
echo "TARGET_FULL_TEST_INVOKED=True"
echo "TARGET_ACCEPT_EXPORT=False"
echo "TARGET_EXPORT=${target_export}"
echo "TARGET_EXPORT_EVIDENCE=PASS"
echo "SOURCE_TARGET_MUTATION=NONE"
