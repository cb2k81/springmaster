#!/usr/bin/env bash
# DBTool configuration helpers.

print_dbtool_env() {
  cat <<EOF
APP_NAME=${APP_NAME}
APP_DB_HOST=${APP_DB_HOST}
APP_DB_PORT=${APP_DB_PORT}
APP_DEV_DB_NAME=${APP_DEV_DB_NAME}
APP_DEV_DB_USER=${APP_DEV_DB_USER}
APP_STAGE_DB_NAME=${APP_STAGE_DB_NAME}
APP_STAGE_DB_USER=${APP_STAGE_DB_USER}
APP_CHANGELOG_MASTER=${APP_CHANGELOG_MASTER}
APP_LIQUIBASE_CONTEXTS=${APP_LIQUIBASE_CONTEXTS}
APP_DBTOOL_ALLOW_DESTRUCTIVE=${APP_DBTOOL_ALLOW_DESTRUCTIVE}
EOF
}

require_project_changelog() {
  if [[ ! -f "${PROJECT_DIR}/${APP_CHANGELOG_MASTER}" ]]; then
    fail "Liquibase master changelog not found: ${APP_CHANGELOG_MASTER}"
  fi
}

jdbc_url_for_db() {
  local db_name="$1"
  printf 'jdbc:mariadb://%s:%s/%s' "${APP_DB_HOST}" "${APP_DB_PORT}" "${db_name}"
}
