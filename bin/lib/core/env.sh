#!/usr/bin/env bash
# Central environment loader for Springmaster-derived shell tooling.
#
# Loading order is intentionally project-local:
#   1. .env.example provides generated/project-local defaults.
#   2. .env overrides those defaults for the local runtime.
#
# Shared tooling must read these values. Tool updates from Springmaster must not
# hard-code target project names, database names, package roots or patch scopes.

if [[ -n "${SPRINGMASTER_CORE_ENV_SH_LOADED:-}" ]]; then
  return 0 2>/dev/null || exit 0
fi
SPRINGMASTER_CORE_ENV_SH_LOADED=1

if [[ -z "${PROJECT_DIR:-}" ]]; then
  PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
fi
export PROJECT_DIR

CORE_LOG_FILE="${PROJECT_DIR}/bin/lib/core/log.sh"
if [[ -f "${CORE_LOG_FILE}" ]]; then
  # shellcheck source=/dev/null
  source "${CORE_LOG_FILE}"
else
  fail() { printf '[ERROR] %s\n' "$*" >&2; exit 1; }
fi

ENV_DEFAULTS_FILE="${PROJECT_DIR}/.env.example"
ENV_FILE="${PROJECT_DIR}/.env"

if [[ -f "${ENV_DEFAULTS_FILE}" ]]; then
  # shellcheck source=/dev/null
  source "${ENV_DEFAULTS_FILE}"
fi

if [[ -f "${ENV_FILE}" ]]; then
  # shellcheck source=/dev/null
  source "${ENV_FILE}"
fi

APP_NAME="${APP_NAME:-springmaster}"
APP_EXPORT_PROJECT_KEY="${APP_EXPORT_PROJECT_KEY:-${APP_NAME}}"
APP_PORT="${APP_PORT:-8080}"
APP_PROFILE="${APP_PROFILE:-dev}"
APP_BASE_PACKAGE="${APP_BASE_PACKAGE:-de.cocondo.platform}"
APP_CORE_PACKAGE="${APP_CORE_PACKAGE:-de.cocondo.system}"

APP_DB_HOST="${APP_DB_HOST:-${DB_HOST:-localhost}}"
APP_DB_PORT="${APP_DB_PORT:-3306}"
DB_HOST="${DB_HOST:-${APP_DB_HOST}}"

APP_DEV_DB_NAME="${APP_DEV_DB_NAME:-springmaster}"
APP_DEV_DB_USER="${APP_DEV_DB_USER:-springmaster}"
APP_DEV_DB_PASS="${APP_DEV_DB_PASS:-springmaster}"

APP_STAGE_DB_NAME="${APP_STAGE_DB_NAME:-${APP_BUILD_DB_NAME:-springmaster_build}}"
APP_STAGE_DB_USER="${APP_STAGE_DB_USER:-${APP_BUILD_DB_USER:-${APP_DEV_DB_USER}}}"
APP_STAGE_DB_PASS="${APP_STAGE_DB_PASS:-${APP_BUILD_DB_PASS:-${APP_DEV_DB_PASS}}}"

APP_BUILD_DB_NAME="${APP_BUILD_DB_NAME:-${APP_STAGE_DB_NAME}}"
APP_BUILD_DB_USER="${APP_BUILD_DB_USER:-${APP_STAGE_DB_USER}}"
APP_BUILD_DB_PASS="${APP_BUILD_DB_PASS:-${APP_STAGE_DB_PASS}}"

APP_DB_ADMIN_USER="${APP_DB_ADMIN_USER:-root}"
APP_DB_ADMIN_PASS="${APP_DB_ADMIN_PASS:-}"

APP_CHANGELOG_DIR="${APP_CHANGELOG_DIR:-src/main/resources/db/changelog}"
APP_CHANGELOG_MASTER="${APP_CHANGELOG_MASTER:-${APP_CHANGELOG_DIR}/db.changelog-master.xml}"
APP_LIQUIBASE_CONTEXTS="${APP_LIQUIBASE_CONTEXTS:-}"

APP_OPENAPI_PATH="${APP_OPENAPI_PATH:-/api-docs}"
APP_EXPORT_CONFIG_FILE="${APP_EXPORT_CONFIG_FILE:-export.config.json}"
case "${APP_EXPORT_CONFIG_FILE}" in
  /*) ;;
  *) APP_EXPORT_CONFIG_FILE="${PROJECT_DIR}/${APP_EXPORT_CONFIG_FILE}" ;;
esac
APP_BUILD_REMOTE_DEPLOY_ENABLED="${APP_BUILD_REMOTE_DEPLOY_ENABLED:-false}"
APP_BUILD_CONSOLE_MODE="${APP_BUILD_CONSOLE_MODE:-compact}"
APP_DIST_DIR="${APP_DIST_DIR:-target/dist}"
APP_DBTOOL_ALLOW_DESTRUCTIVE="${APP_DBTOOL_ALLOW_DESTRUCTIVE:-false}"

LOG_LEVEL="${LOG_LEVEL:-INFO}"
BASE_URL="${BASE_URL:-http://localhost:${APP_PORT}}"

export \
  PROJECT_DIR ENV_DEFAULTS_FILE ENV_FILE \
  APP_NAME APP_EXPORT_PROJECT_KEY APP_PORT APP_PROFILE APP_BASE_PACKAGE APP_CORE_PACKAGE \
  APP_DB_HOST APP_DB_PORT DB_HOST \
  APP_DEV_DB_NAME APP_DEV_DB_USER APP_DEV_DB_PASS \
  APP_STAGE_DB_NAME APP_STAGE_DB_USER APP_STAGE_DB_PASS \
  APP_BUILD_DB_NAME APP_BUILD_DB_USER APP_BUILD_DB_PASS \
  APP_DB_ADMIN_USER APP_DB_ADMIN_PASS \
  APP_CHANGELOG_DIR APP_CHANGELOG_MASTER APP_LIQUIBASE_CONTEXTS \
  APP_OPENAPI_PATH APP_EXPORT_CONFIG_FILE APP_BUILD_REMOTE_DEPLOY_ENABLED \
  APP_BUILD_CONSOLE_MODE APP_DIST_DIR APP_DBTOOL_ALLOW_DESTRUCTIVE \
  LOG_LEVEL BASE_URL
