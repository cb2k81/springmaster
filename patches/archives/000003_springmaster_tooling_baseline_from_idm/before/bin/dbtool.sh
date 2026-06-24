#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
source "${SCRIPT_DIR}/init.env.sh"

usage() {
  cat <<'EOF'
Usage:
  ./bin/dbtool.sh env
  ./bin/dbtool.sh status
  ./bin/dbtool.sh validate-stage
  ./bin/dbtool.sh update-stage
  ./bin/dbtool.sh rebuild-dev
  ./bin/dbtool.sh rebuild-stage

Bootstrap status:
  This is a conservative starter implementation. Destructive operations require
  APP_DBTOOL_ALLOW_DESTRUCTIVE=true and the full DB tooling baseline patch will
  replace this with the IDM-derived implementation.
EOF
}

print_env() {
  cat <<EOF
APP_NAME=${APP_NAME}
APP_DB_HOST=${APP_DB_HOST}
APP_DB_PORT=${APP_DB_PORT}
APP_DEV_DB_NAME=${APP_DEV_DB_NAME}
APP_STAGE_DB_NAME=${APP_STAGE_DB_NAME}
APP_CHANGELOG_MASTER=${APP_CHANGELOG_MASTER}
APP_LIQUIBASE_CONTEXTS=${APP_LIQUIBASE_CONTEXTS}
EOF
}

require_project_changelog() {
  if [[ ! -f "${PROJECT_ROOT}/${APP_CHANGELOG_MASTER}" ]]; then
    fail "Liquibase master changelog not found: ${APP_CHANGELOG_MASTER}"
  fi
}

run_maven_liquibase() {
  local goal="$1"
  local db_name="$2"
  require_command mvn
  require_project_changelog
  (
    cd "${PROJECT_ROOT}"
    mvn -q "liquibase:${goal}" \
      -Dliquibase.changeLogFile="${APP_CHANGELOG_MASTER}" \
      -Dliquibase.url="jdbc:mariadb://${APP_DB_HOST}:${APP_DB_PORT}/${db_name}" \
      -Dliquibase.username="${APP_STAGE_DB_USER}" \
      -Dliquibase.password="${APP_STAGE_DB_PASS}"
  )
}

case "${1:-}" in
  env)
    print_env
    ;;
  status)
    print_env
    require_project_changelog
    log_info "Bootstrap DB status check completed. No database connection was opened."
    ;;
  validate-stage)
    run_maven_liquibase validate "${APP_STAGE_DB_NAME}"
    ;;
  update-stage)
    run_maven_liquibase update "${APP_STAGE_DB_NAME}"
    ;;
  rebuild-dev|rebuild-stage)
    if [[ "${APP_DBTOOL_ALLOW_DESTRUCTIVE:-false}" != "true" ]]; then
      fail "$1 is destructive and disabled in bootstrap. Set APP_DBTOOL_ALLOW_DESTRUCTIVE=true only after verifying .env."
    fi
    fail "$1 is reserved for the full IDM-derived DBTool baseline patch."
    ;;
  -h|--help|help|"")
    usage
    ;;
  *)
    usage >&2
    exit 2
    ;;
esac
