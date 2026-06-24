#!/usr/bin/env bash
# MariaDB command-line helpers for DBTool.

mariadb_client_command() {
  if command -v mariadb >/dev/null 2>&1; then
    printf 'mariadb'
    return 0
  fi
  if command -v mysql >/dev/null 2>&1; then
    printf 'mysql'
    return 0
  fi
  return 1
}

require_destructive_allowed() {
  if ! is_true "${APP_DBTOOL_ALLOW_DESTRUCTIVE}"; then
    fail "Destructive DB operation blocked. Set APP_DBTOOL_ALLOW_DESTRUCTIVE=true after verifying .env."
  fi
}

run_admin_sql() {
  local sql="$1"
  local client
  client="$(mariadb_client_command)" || fail "Neither mariadb nor mysql CLI was found."

  local args=(--host="${APP_DB_HOST}" --port="${APP_DB_PORT}" --user="${APP_DB_ADMIN_USER}" --protocol=tcp --execute="${sql}")
  if [[ -n "${APP_DB_ADMIN_PASS}" ]]; then
    MYSQL_PWD="${APP_DB_ADMIN_PASS}" "${client}" "${args[@]}"
  else
    "${client}" "${args[@]}"
  fi
}

recreate_database() {
  local db_name="$1"
  require_destructive_allowed
  [[ -n "${db_name}" ]] || fail "Database name must not be empty."
  case "${db_name}" in
    mysql|information_schema|performance_schema|sys)
      fail "Refusing to recreate protected database: ${db_name}"
      ;;
  esac

  run_admin_sql "DROP DATABASE IF EXISTS \`${db_name}\`; CREATE DATABASE \`${db_name}\` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
}
