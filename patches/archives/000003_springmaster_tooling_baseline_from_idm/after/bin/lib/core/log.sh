#!/usr/bin/env bash
# Shared logging and guard helpers for springmaster shell tooling.

if [[ -n "${SPRINGMASTER_CORE_LOG_SH_LOADED:-}" ]]; then
  return 0 2>/dev/null || exit 0
fi
SPRINGMASTER_CORE_LOG_SH_LOADED=1

LOG_LEVEL="${LOG_LEVEL:-INFO}"

_timestamp() {
  date '+%Y-%m-%dT%H:%M:%S%z'
}

_log_line() {
  local level="$1"
  shift
  printf '[%s] [%s] %s\n' "$(_timestamp)" "$level" "$*" >&2
}

log_debug() {
  if [[ "${LOG_LEVEL}" == "DEBUG" ]]; then
    _log_line "DEBUG" "$@"
  fi
}

log_info() {
  _log_line "INFO" "$@"
}

log_warn() {
  _log_line "WARN" "$@"
}

log_error() {
  _log_line "ERROR" "$@"
}

fail() {
  log_error "$*"
  exit 1
}

require_command() {
  local command_name="$1"
  if ! command -v "${command_name}" >/dev/null 2>&1; then
    fail "Required command not found: ${command_name}"
  fi
}

is_true() {
  case "${1:-}" in
    true|TRUE|yes|YES|1|on|ON) return 0 ;;
    *) return 1 ;;
  esac
}
