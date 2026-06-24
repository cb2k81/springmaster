#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
source "${SCRIPT_DIR}/init.env.sh"

BUILD_LOG="${BUILD_LOG:-${PROJECT_ROOT}/tmp/build.log}"
BUILD_SUMMARY="${BUILD_SUMMARY:-${PROJECT_ROOT}/tmp/build.summary}"
mkdir -p "$(dirname "${BUILD_LOG}")" "$(dirname "${BUILD_SUMMARY}")" "${PROJECT_ROOT}/target/dist"
: > "${BUILD_LOG}"
: > "${BUILD_SUMMARY}"

log_info "Build started for ${APP_NAME} at ${PROJECT_ROOT}"
require_command mvn

(
  cd "${PROJECT_ROOT}"
  mvn clean verify
) 2>&1 | tee -a "${BUILD_LOG}"

JAR_FILE="$(find "${PROJECT_ROOT}/target" -maxdepth 1 -type f -name "${APP_NAME}-*.jar" ! -name "*.original" | sort | tail -n 1 || true)"
if [[ -z "${JAR_FILE}" ]]; then
  fail "Build finished but no Spring Boot jar was found in target/."
fi

DIST_ZIP="${PROJECT_ROOT}/target/dist/${APP_NAME}.zip"
rm -f "${DIST_ZIP}"
(
  cd "${PROJECT_ROOT}"
  zip -q -r "${DIST_ZIP}" "${JAR_FILE#${PROJECT_ROOT}/}" README.md PROJECT_DOCS platform export.config.json .env.example
)

{
  echo "APP_NAME=${APP_NAME}"
  echo "JAR_FILE=${JAR_FILE#${PROJECT_ROOT}/}"
  echo "DIST_ZIP=${DIST_ZIP#${PROJECT_ROOT}/}"
  echo "REMOTE_DEPLOY_ENABLED=${APP_BUILD_REMOTE_DEPLOY_ENABLED}"
} > "${BUILD_SUMMARY}"

log_info "Build finished. ZIP: ${DIST_ZIP#${PROJECT_ROOT}/}"

if [[ "${APP_BUILD_REMOTE_DEPLOY_ENABLED}" == "true" ]]; then
  log_warn "Remote deployment hook is enabled but not implemented in bootstrap package. This will be added in the tooling baseline patch."
fi
