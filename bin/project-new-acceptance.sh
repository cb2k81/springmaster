#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
PROJECT_DIR="${PROJECT_ROOT}"
export PROJECT_DIR

RUN_GENERATED_MAVEN_TEST=false
WORK_ROOT="${PROJECT_ROOT}/target/project-new-acceptance"
SAMPLE_NAME="sample-backend"
SAMPLE_DIR="${WORK_ROOT}/${SAMPLE_NAME}"
LOG_DIR="${WORK_ROOT}/logs"

usage() {
  cat <<'USAGE'
Usage:
  ./bin/project-new-acceptance.sh [--generated-maven-test|--skip-generated-maven-test] [--work-root <path>]

Purpose:
  Validates that Springmaster can instantiate a new Java backend skeleton without
  writing outside a disposable work directory.

Checks:
  * project-new dry-run and create
  * token rendering for package, Maven coordinates and DB defaults
  * patch registry bootstrap in the generated project
  * export full ZIP and export-integrity verification in the generated project
  * patch artifact preflight tooling is complete in the generated project
  * dbtool status in the generated project without opening a DB connection
  * optional mvn test in the generated project
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --generated-maven-test)
      RUN_GENERATED_MAVEN_TEST=true
      shift
      ;;
    --skip-generated-maven-test)
      RUN_GENERATED_MAVEN_TEST=false
      shift
      ;;
    --work-root)
      [[ $# -ge 2 ]] || { echo "[ERROR] --work-root requires a path" >&2; exit 1; }
      WORK_ROOT="$2"
      SAMPLE_DIR="${WORK_ROOT}/${SAMPLE_NAME}"
      LOG_DIR="${WORK_ROOT}/logs"
      shift 2
      ;;
    -h|--help|help)
      usage
      exit 0
      ;;
    *)
      echo "[ERROR] Unknown option: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

require_file() {
  local path="$1"
  if [[ ! -f "${path}" ]]; then
    echo "[ERROR] Required file missing: ${path}" >&2
    exit 1
  fi
  echo "[OK] ${path}"
}

require_marker() {
  local marker="$1"
  local file="$2"
  if ! grep -Fq -- "${marker}" "${file}"; then
    echo "[ERROR] Marker not found in ${file}: ${marker}" >&2
    exit 1
  fi
  echo "[OK] Marker '${marker}' in ${file}"
}

reject_marker() {
  local marker="$1"
  local file="$2"
  if grep -Fq -- "${marker}" "${file}"; then
    echo "[ERROR] Forbidden marker found in ${file}: ${marker}" >&2
    exit 1
  fi
  echo "[OK] Marker '${marker}' absent in ${file}"
}

mkdir -p "${LOG_DIR}"
rm -rf "${SAMPLE_DIR}"

cd "${PROJECT_ROOT}"

echo "Project-New Acceptance: dry-run"
./bin/project-new.sh create \
  --dry-run \
  --name "${SAMPLE_NAME}" \
  --path "${SAMPLE_DIR}" \
  --port 8091 \
  --group-id de.cocondo.acceptance \
  --base-package de.cocondo.acceptance.sample \
  > "${LOG_DIR}/01_project_new_dry_run.log"
require_marker "Modus:        DRY-RUN" "${LOG_DIR}/01_project_new_dry_run.log"
require_marker "Zusammenfassung:" "${LOG_DIR}/01_project_new_dry_run.log"

echo "Project-New Acceptance: create"
./bin/project-new.sh create \
  --name "${SAMPLE_NAME}" \
  --path "${SAMPLE_DIR}" \
  --port 8091 \
  --group-id de.cocondo.acceptance \
  --base-package de.cocondo.acceptance.sample \
  > "${LOG_DIR}/02_project_new_create.log"
require_marker "Projektanlage abgeschlossen." "${LOG_DIR}/02_project_new_create.log"

cd "${SAMPLE_DIR}"

require_file "pom.xml"
require_file "README.md"
require_file ".env.example"
require_file "export.config.json"
require_file "platform/versions/platform.env"
require_file "PROJECT_DOCS/BOOTSTRAP/PROJECT_NEW_BOOTSTRAP.md"
require_file "PROJECT_DOCS/CONFIG/ENV_TEMPLATE.env"
require_file "contracts/configuration/environment-contract.json"
require_file "contracts/database/migration-contract.json"
require_file "patches/archives/000001_project_new_bootstrap/manifest.json"
require_file "patches/archives/000001_project_new_bootstrap/patch-log.json"
python3 - <<'PY_BOOTSTRAP_IDENTITY'
import json
import uuid
from pathlib import Path

archive = Path("patches/archives/000001_project_new_bootstrap")
manifest = json.loads((archive / "manifest.json").read_text(encoding="utf-8"))
patch_log = json.loads((archive / "patch-log.json").read_text(encoding="utf-8"))
assert manifest["schemaVersion"] == "springmaster.patch-manifest.v2"
assert manifest["id"] == manifest["patchId"] == "000001_project_new_bootstrap"
assert patch_log["artifactId"] == manifest["artifactId"]
assert str(uuid.UUID(manifest["artifactId"].removeprefix("urn:uuid:"))) in manifest["artifactId"]
PY_BOOTSTRAP_IDENTITY
require_file "src/main/java/de/cocondo/acceptance/sample/app/SampleBackendApplication.java"
require_file "src/main/java/de/cocondo/acceptance/sample/app/api/PlatformInfoController.java"
require_file "src/test/java/de/cocondo/acceptance/sample/app/SampleBackendApplicationTests.java"
require_file "bin/patch.sh"
require_file "bin/patch-artifact-preflight.py"
require_file "bin/patch-artifact-preflight-it.sh"
require_file "bin/export.sh"
require_file "bin/export-integrity-check.py"
require_file "bin/export-integrity-it.sh"
require_file "bin/dbtool.sh"
require_file "bin/db-migration-contract.py"
require_file "bin/db-migration-contract.sh"
require_file "bin/build.sh"
require_file "bin/config-contract.py"
require_file "bin/config-contract.sh"
require_file "bin/tooling-selfcheck.sh"
require_file "bin/lib/core/env.sh"

if [[ -f ".env" ]]; then
  echo "[ERROR] project-new must not create a local .env" >&2
  exit 1
fi
echo "[OK] No .env generated"

require_marker "<artifactId>sample-backend</artifactId>" "pom.xml"
require_marker "<groupId>de.cocondo.acceptance</groupId>" "pom.xml"
require_marker "package de.cocondo.acceptance.sample.app;" "src/main/java/de/cocondo/acceptance/sample/app/SampleBackendApplication.java"
require_marker "package de.cocondo.acceptance.sample.app.api;" "src/main/java/de/cocondo/acceptance/sample/app/api/PlatformInfoController.java"
require_marker "APP_EXPORT_PROJECT_KEY=sample-backend" ".env.example"
require_marker "APP_CORE_PACKAGE=de.cocondo.system" ".env.example"
require_marker "APP_DEV_DB_NAME=sample_backend" ".env.example"
require_marker "APP_STAGE_DB_NAME=sample_backend_build" ".env.example"
require_marker 'PATCH_LOCAL_SCOPES="domain;sample-backend"' ".env.example"
require_marker 'PATCH_SCOPE_SAMPLE_BACKEND_PATHS="src/main/java/de/cocondo/acceptance/sample/**' ".env.example"
require_marker 'APP_DEV_DB_NAME="${APP_DEV_DB_NAME:-sample_backend}"' "bin/lib/core/env.sh"
require_marker 'APP_DEV_DB_USER="${APP_DEV_DB_USER:-sample_backend}"' "bin/lib/core/env.sh"
require_marker 'APP_STAGE_DB_NAME="${APP_STAGE_DB_NAME:-${APP_BUILD_DB_NAME:-sample_backend_build}}"' "bin/lib/core/env.sh"
reject_marker "__PROJECT_NAME__" "README.md"
reject_marker "__BASE_PACKAGE__" "src/main/java/de/cocondo/acceptance/sample/app/SampleBackendApplication.java"
require_marker "include-stacktrace: never" "src/main/resources/application.yml"
require_marker "show-details: never" "src/main/resources/application.yml"
require_marker 'springmaster.export-closure-evidence.v1' "bin/export.sh"
require_marker 'springmaster.export-closure-evidence.v1' "bin/export-integrity-check.py"
require_marker 'springmaster.patch-artifact-preflight.v1' "bin/patch-artifact-preflight.py"
require_marker 'springmaster.patch-export-evidence.v1' "bin/patch-artifact-preflight.py"
reject_marker 'sample-backend.export-closure-evidence.v1' "bin/export.sh"

chmod +x bin/*.sh

echo "Project-New Acceptance: patch registry"
./bin/patch.sh list > "${LOG_DIR}/03_generated_patch_list.log"
require_marker "000001" "${LOG_DIR}/03_generated_patch_list.log"
require_marker "project_new_bootstrap" "${LOG_DIR}/03_generated_patch_list.log"

echo "Project-New Acceptance: configuration contract"
./bin/config-contract.sh --check > "${LOG_DIR}/04_generated_config_contract.log" 2>&1
require_marker "CONFIG_CONTRACT=PASS" "${LOG_DIR}/04_generated_config_contract.log"

echo "Project-New Acceptance: migration contract"
./bin/db-migration-contract.sh --check > "${LOG_DIR}/04b_generated_db_migration_contract.log" 2>&1
require_marker "DB_MIGRATION_CONTRACT=PASS" "${LOG_DIR}/04b_generated_db_migration_contract.log"

echo "Project-New Acceptance: DBTool status"
./bin/dbtool.sh status > "${LOG_DIR}/04_generated_dbtool_status.log" 2>&1
require_marker "APP_DEV_DB_NAME=sample_backend" "${LOG_DIR}/04_generated_dbtool_status.log"
require_marker "APP_STAGE_DB_NAME=sample_backend_build" "${LOG_DIR}/04_generated_dbtool_status.log"
require_marker "DBTool configuration and migration contract are valid" "${LOG_DIR}/04_generated_dbtool_status.log"

echo "Project-New Acceptance: export"
./bin/export.sh full --zip > "${LOG_DIR}/05_generated_export.log" 2>&1
GENERATED_EXPORT="$(tail -n 1 "${LOG_DIR}/05_generated_export.log")"
if [[ ! -f "${GENERATED_EXPORT}" ]]; then
  echo "[ERROR] Generated export ZIP missing: ${GENERATED_EXPORT}" >&2
  exit 1
fi
unzip -t "${GENERATED_EXPORT}" > "${LOG_DIR}/06_generated_export_zip_test.log"
python3 bin/export-integrity-check.py "${GENERATED_EXPORT}" --source-root . > "${LOG_DIR}/07_generated_export_integrity.log"
require_marker "EXPORT_INTEGRITY=PASS" "${LOG_DIR}/07_generated_export_integrity.log"
python3 - "${GENERATED_EXPORT}" > "${LOG_DIR}/08_generated_export_meta.log" <<'PY'
import json
import sys
import zipfile
from pathlib import Path
zip_path = Path(sys.argv[1])
with zipfile.ZipFile(zip_path) as archive:
    meta_name = next(name for name in archive.namelist() if name.endswith('.meta.json'))
    meta = json.loads(archive.read(meta_name).decode('utf-8'))
print(f"profile={meta.get('profile')}")
print(f"fileCount={meta.get('fileCount')}")
if meta.get('profile') != 'full':
    raise SystemExit('Unexpected export profile')
if int(meta.get('fileCount') or 0) < 25:
    raise SystemExit('Generated export contains too few files')
if meta.get('projectKey') != 'sample-backend':
    raise SystemExit(f"Unexpected export projectKey: {meta.get('projectKey')}")
PY

echo "Project-New Acceptance: export project key wins over stale export.config.json"
python3 - <<'PY'
import json
from pathlib import Path
path = Path('export.config.json')
data = json.loads(path.read_text())
data['projectKey'] = 'springmaster'
path.write_text(json.dumps(data, indent=2) + "\n")
PY
./bin/export.sh full --zip > "${LOG_DIR}/09_generated_export_stale_config.log" 2>&1
STALE_CONFIG_EXPORT="$(tail -n 1 "${LOG_DIR}/09_generated_export_stale_config.log")"
case "${STALE_CONFIG_EXPORT}" in
  exports/text/sample-backend_export_full_*.zip) echo "[OK] export key remains sample-backend" ;;
  *) echo "[ERROR] export ZIP name not project-local: ${STALE_CONFIG_EXPORT}" >&2; exit 1 ;;
esac

echo "Project-New Acceptance: generated Maven test"
if [[ "${RUN_GENERATED_MAVEN_TEST}" == "true" ]]; then
  mvn -q test > "${LOG_DIR}/10_generated_mvn_test.log" 2>&1
  echo "[OK] Generated project mvn test successful"
else
  echo "[SKIP] Generated project mvn test skipped"
fi

echo "[OK] Project-New instantiation acceptance passed"
echo "Generated project: ${SAMPLE_DIR}"
echo "Logs: ${LOG_DIR}"
