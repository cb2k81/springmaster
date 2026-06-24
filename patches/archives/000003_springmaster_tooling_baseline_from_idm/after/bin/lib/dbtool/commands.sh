#!/usr/bin/env bash
# DBTool command dispatcher.

usage() {
  cat <<'EOF'
Usage:
  ./bin/dbtool.sh env
  ./bin/dbtool.sh status
  ./bin/dbtool.sh changelogs
  ./bin/dbtool.sh validate-stage
  ./bin/dbtool.sh update-stage
  ./bin/dbtool.sh rebuild-dev
  ./bin/dbtool.sh rebuild-stage

Safety:
  rebuild-dev and rebuild-stage are destructive and require:
    APP_DBTOOL_ALLOW_DESTRUCTIVE=true
  Admin access is read from:
    APP_DB_ADMIN_USER
    APP_DB_ADMIN_PASS
EOF
}

dbtool_status() {
  print_dbtool_env
  require_project_changelog
  log_info "DBTool configuration is valid. No database connection was opened for status."
}

dbtool_rebuild_dev() {
  recreate_database "${APP_DEV_DB_NAME}"
  run_maven_liquibase update "${APP_DEV_DB_NAME}" "${APP_DEV_DB_USER}" "${APP_DEV_DB_PASS}"
}

dbtool_rebuild_stage() {
  recreate_database "${APP_STAGE_DB_NAME}"
  run_maven_liquibase update "${APP_STAGE_DB_NAME}" "${APP_STAGE_DB_USER}" "${APP_STAGE_DB_PASS}"
}

dbtool_main() {
  case "${1:-}" in
    env)
      print_dbtool_env
      ;;
    status)
      dbtool_status
      ;;
    changelogs)
      list_changelog_files
      ;;
    validate-stage)
      run_maven_liquibase validate "${APP_STAGE_DB_NAME}" "${APP_STAGE_DB_USER}" "${APP_STAGE_DB_PASS}"
      ;;
    update-stage)
      run_maven_liquibase update "${APP_STAGE_DB_NAME}" "${APP_STAGE_DB_USER}" "${APP_STAGE_DB_PASS}"
      ;;
    rebuild-dev)
      dbtool_rebuild_dev
      ;;
    rebuild-stage)
      dbtool_rebuild_stage
      ;;
    -h|--help|help|"")
      usage
      ;;
    *)
      usage >&2
      exit 2
      ;;
  esac
}
