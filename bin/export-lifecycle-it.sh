#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "${TMP_DIR}"' EXIT

fail_test() {
  echo "ERROR: $*" >&2
  exit 1
}

for command in git python3 sha256sum unzip; do
  command -v "${command}" >/dev/null 2>&1 || fail_test "required command is missing: ${command}"
done

SANDBOX="${TMP_DIR}/project"
FAKE_HOME="${TMP_DIR}/home"
mkdir -p \
  "${SANDBOX}/bin/lib/core" \
  "${SANDBOX}/exports/text" \
  "${FAKE_HOME}/Downloads"

cp "${PROJECT_ROOT}/bin/export.sh" "${SANDBOX}/bin/export.sh"
cp "${PROJECT_ROOT}/bin/init.env.sh" "${SANDBOX}/bin/init.env.sh"
cp "${PROJECT_ROOT}/bin/lib/core/env.sh" "${SANDBOX}/bin/lib/core/env.sh"
cp "${PROJECT_ROOT}/bin/lib/core/log.sh" "${SANDBOX}/bin/lib/core/log.sh"
chmod 755 "${SANDBOX}/bin/export.sh"

printf '# fixture\n' > "${SANDBOX}/README.md"
printf 'fixture payload\n' > "${SANDBOX}/sample.txt"
printf 'exports/\n' > "${SANDBOX}/.gitignore"
printf 'must remain local\n' > "${SANDBOX}/exports/text/keep.txt"
printf 'downloads sentinel\n' > "${FAKE_HOME}/Downloads/sentinel.txt"

cat > "${SANDBOX}/export.config.json" <<'JSON'
{
  "projectKey": "fixture",
  "defaultProfile": "full",
  "outputDirectory": "exports/text",
  "metaFile": true,
  "maxFileSizeBytes": 2097152,
  "globalExclude": ["exports/**", ".git/**", "build/**", "tmp/**"],
  "profiles": {
    "full": {
      "include": ["README.md", "sample.txt", "bin/**", "export.config.json"],
      "exclude": []
    }
  },
  "splitProfiles": {
    "baseline": ["full"]
  }
}
JSON

(
  cd "${SANDBOX}"
  git init -q
  git config user.name "Export Lifecycle Fixture"
  git config user.email "fixture@example.invalid"
  git add .
  git commit -qm baseline
)

LEGACY_DIR="${SANDBOX}/exports/text/fixture_export_full_legacy"
LEGACY_ZIP="${SANDBOX}/exports/text/fixture_export_full_legacy.zip"
mkdir -p "${LEGACY_DIR}"
printf 'legacy unpacked payload\n' > "${LEGACY_DIR}/fixture_export_full.txt"
printf 'legacy archive placeholder\n' > "${LEGACY_ZIP}"

run_export() {
  (
    cd "${SANDBOX}"
    HOME="${FAKE_HOME}" APP_EXPORT_PROJECT_KEY=fixture ./bin/export.sh full --zip
  )
}

current_zip() {
  find "${SANDBOX}/exports/text" -maxdepth 1 -type f \
    -name 'fixture_export_full_*.zip' -print -quit
}

assert_current_export_set() {
  local zip="$1"
  local checksum="${zip}.sha256"
  [[ -f "${zip}" ]] || fail_test "current ZIP is missing: ${zip}"
  [[ -f "${checksum}" ]] || fail_test "current checksum is missing: ${checksum}"

  local expected_line
  expected_line="$(sha256sum "${zip}" | awk '{print $1}')  $(basename "${zip}")"
  [[ "$(cat "${checksum}")" == "${expected_line}" ]] \
    || fail_test "portable checksum does not match the ZIP"

  (
    cd "$(dirname "${zip}")"
    sha256sum -c "$(basename "${checksum}")" >/dev/null
  )
  unzip -tq "${zip}" >/dev/null
  unzip -Z1 "${zip}" | grep -q '/fixture_export_full.meta.json$' \
    || fail_test "metadata is not packaged inside the ZIP"
  unzip -Z1 "${zip}" | grep -q '/fixture_export_full.txt$' \
    || fail_test "text export is not packaged inside the ZIP"

  [[ ! -d "${zip%.zip}" ]] \
    || fail_test "unpacked export directory remained next to the ZIP"

  local current_count
  current_count="$(find "${SANDBOX}/exports/text" -maxdepth 1 -type f \
    -name 'fixture_export_*' | wc -l | tr -d ' ')"
  [[ "${current_count}" == "2" ]] \
    || fail_test "expected ZIP plus checksum as the only current export artifacts, found ${current_count}"
}

FIRST_REL="$(run_export)"
FIRST_ZIP="${SANDBOX}/${FIRST_REL}"
assert_current_export_set "${FIRST_ZIP}"
[[ -d "${SANDBOX}/exports/text/Archiv/$(basename "${LEGACY_DIR}")" ]] \
  || fail_test "legacy unpacked export directory was not archived"
[[ -f "${SANDBOX}/exports/text/Archiv/$(basename "${LEGACY_ZIP}")" ]] \
  || fail_test "legacy ZIP without checksum was not archived"
[[ "$(cd "${SANDBOX}" && APP_EXPORT_PROJECT_KEY=fixture ./bin/export.sh --current)" == "${FIRST_REL}" ]] \
  || fail_test "--current did not resolve the first export"

printf 'dirty change\n' >> "${SANDBOX}/sample.txt"
if (
  cd "${SANDBOX}"
  HOME="${FAKE_HOME}" APP_EXPORT_PROJECT_KEY=fixture ./bin/export.sh full --zip >/dev/null 2>&1
); then
  fail_test "dirty Git working tree unexpectedly produced a baseline export"
fi
[[ -f "${FIRST_ZIP}" ]] \
  || fail_test "failed dirty export changed the current export set"

(
  cd "${SANDBOX}"
  git add sample.txt
  git commit -qm 'fixture update'
)

SECOND_REL="$(run_export)"
SECOND_ZIP="${SANDBOX}/${SECOND_REL}"
[[ "${SECOND_ZIP}" != "${FIRST_ZIP}" ]] \
  || fail_test "second export reused the first filename"
assert_current_export_set "${SECOND_ZIP}"
[[ "$(cd "${SANDBOX}" && APP_EXPORT_PROJECT_KEY=fixture ./bin/export.sh --current)" == "${SECOND_REL}" ]] \
  || fail_test "--current did not resolve the second export"

FIRST_NAME="$(basename "${FIRST_ZIP}")"
[[ -f "${SANDBOX}/exports/text/Archiv/${FIRST_NAME}" ]] \
  || fail_test "previous ZIP was not moved to the archive directory"
[[ -f "${SANDBOX}/exports/text/Archiv/${FIRST_NAME}.sha256" ]] \
  || fail_test "previous checksum was not moved to the archive directory"

[[ -f "${SANDBOX}/exports/text/keep.txt" ]] \
  || fail_test "unrelated output-directory file was archived"
[[ "$(find "${FAKE_HOME}/Downloads" -maxdepth 1 -type f -printf '%f\n')" == "sentinel.txt" ]] \
  || fail_test "export wrote into HOME/Downloads"

printf 'temporary dirty export\n' >> "${SANDBOX}/sample.txt"
DIRTY_REL="$(cd "${SANDBOX}" && HOME="${FAKE_HOME}" APP_EXPORT_PROJECT_KEY=fixture ./bin/export.sh full --zip --allow-dirty)"
DIRTY_ZIP="${SANDBOX}/${DIRTY_REL}"
assert_current_export_set "${DIRTY_ZIP}"

CURRENT_META="$(unzip -Z1 "${DIRTY_ZIP}" | grep '/fixture_export_full.meta.json$')"
unzip -p "${DIRTY_ZIP}" "${CURRENT_META}" \
  | python3 -c 'import json,sys; data=json.load(sys.stdin); assert data["sourceGit"]["dirty"] is True'

echo "EXPORT_LIFECYCLE_IT=PASS"
