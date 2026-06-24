#!/usr/bin/env bash
# Liquibase/Maven integration for DBTool.

run_maven_liquibase() {
  local goal="$1"
  local db_name="$2"
  local db_user="$3"
  local db_pass="$4"

  require_command mvn
  require_project_changelog

  local contexts_arg=()
  if [[ -n "${APP_LIQUIBASE_CONTEXTS}" ]]; then
    contexts_arg=(-Dliquibase.contexts="${APP_LIQUIBASE_CONTEXTS}")
  fi

  (
    cd "${PROJECT_DIR}"
    mvn -q "liquibase:${goal}" \
      -Dliquibase.changeLogFile="${APP_CHANGELOG_MASTER}" \
      -Dliquibase.url="$(jdbc_url_for_db "${db_name}")" \
      -Dliquibase.username="${db_user}" \
      -Dliquibase.password="${db_pass}" \
      "${contexts_arg[@]}"
  )
}
