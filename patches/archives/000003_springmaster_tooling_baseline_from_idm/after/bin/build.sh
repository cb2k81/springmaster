#!/usr/bin/env bash
set -euo pipefail
# Local-first build tool for springmaster.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
PROJECT_DIR="${PROJECT_ROOT}"
export PROJECT_DIR

# shellcheck source=/dev/null
source "${SCRIPT_DIR}/init.env.sh"

BUILD_LOG="${BUILD_LOG:-${PROJECT_ROOT}/tmp/build.log}"
BUILD_SUMMARY="${BUILD_SUMMARY:-${PROJECT_ROOT}/tmp/build.summary}"
BUILD_CONSOLE_MODE="${BUILD_CONSOLE_MODE:-${APP_BUILD_CONSOLE_MODE:-compact}}"
DIST_DIR="${PROJECT_ROOT}/${APP_DIST_DIR}"

case "${BUILD_CONSOLE_MODE}" in
  compact|tee|silent) ;;
  *) fail "Invalid BUILD_CONSOLE_MODE=${BUILD_CONSOLE_MODE}. Allowed values: compact, tee, silent." ;;
esac

mkdir -p "$(dirname "${BUILD_LOG}")" "$(dirname "${BUILD_SUMMARY}")" "${DIST_DIR}"
: > "${BUILD_LOG}"
: > "${BUILD_SUMMARY}"

append_build_log() {
  local level="$1"
  shift
  printf '[%s] [%s] %s\n' "$(date '+%Y-%m-%dT%H:%M:%S%z')" "$level" "$*" >> "${BUILD_LOG}"
}

console_info() {
  if [[ "${BUILD_CONSOLE_MODE}" != "silent" ]]; then log_info "$*"; fi
  append_build_log "INFO" "$*"
}

run_logged() {
  local description="$1"
  shift
  console_info "${description}"
  local exit_code=0
  if [[ "${BUILD_CONSOLE_MODE}" == "tee" ]]; then
    set +e
    "$@" 2>&1 | tee -a "${BUILD_LOG}"
    exit_code=${PIPESTATUS[0]}
    set -e
  else
    set +e
    "$@" >> "${BUILD_LOG}" 2>&1
    exit_code=$?
    set -e
  fi
  if [[ ${exit_code} -ne 0 ]]; then
    log_error "Failed: ${description}. See ${BUILD_LOG}"
    exit "${exit_code}"
  fi
}

require_command mvn
require_command zip

run_logged "Running Maven clean verify" bash -lc "cd '${PROJECT_ROOT}' && mvn clean verify"

JAR_FILE="$(find "${PROJECT_ROOT}/target" -maxdepth 1 -type f -name "${APP_NAME}-*.jar" ! -name "*.original" | sort | tail -n 1 || true)"
if [[ -z "${JAR_FILE}" ]]; then
  fail "Build finished but no Spring Boot jar was found for APP_NAME=${APP_NAME}."
fi

DIST_ZIP="${DIST_DIR}/${APP_NAME}.zip"
rm -f "${DIST_ZIP}"
run_logged "Creating runtime distribution ZIP" bash -lc "cd '${PROJECT_ROOT}' && zip -q -r '${DIST_ZIP}' '${JAR_FILE#${PROJECT_ROOT}/}' README.md PROJECT_DOCS platform export.config.json .env.example"

BOM_FILE="$(find "${PROJECT_ROOT}/target" -maxdepth 2 -type f \( -name 'bom.json' -o -name '*cyclonedx*.json' -o -name '*.spdx.json' \) | sort | head -n 1 || true)"

{
  echo "APP_NAME=${APP_NAME}"
  echo "JAR_FILE=${JAR_FILE#${PROJECT_ROOT}/}"
  echo "DIST_ZIP=${DIST_ZIP#${PROJECT_ROOT}/}"
  echo "BOM_FILE=${BOM_FILE#${PROJECT_ROOT}/}"
  echo "BUILD_LOG=${BUILD_LOG#${PROJECT_ROOT}/}"
  echo "REMOTE_DEPLOY_ENABLED=${APP_BUILD_REMOTE_DEPLOY_ENABLED}"
} > "${BUILD_SUMMARY}"

log_info "Build finished. ZIP: ${DIST_ZIP#${PROJECT_ROOT}/}"
if is_true "${APP_BUILD_REMOTE_DEPLOY_ENABLED}"; then
  log_warn "Remote deployment is intentionally not implemented in springmaster tooling baseline 000003."
fi
