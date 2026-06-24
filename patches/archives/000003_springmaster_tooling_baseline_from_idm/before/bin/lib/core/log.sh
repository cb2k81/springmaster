#!/usr/bin/env bash

: "${LOG_LEVEL:=INFO}"

_log_level_num() {
  case "${1^^}" in
    DEBUG) echo 0 ;;
    INFO)  echo 1 ;;
    WARN)  echo 2 ;;
    ERROR) echo 3 ;;
    *)     echo 1 ;;
  esac
}

_log() {
  local level="$1"
  shift
  local configured current timestamp
  configured="$(_log_level_num "${LOG_LEVEL}")"
  current="$(_log_level_num "${level}")"
  if (( current < configured )); then
    return 0
  fi
  timestamp="$(date +"%Y-%m-%dT%H:%M:%S%z")"
  if [[ "${level}" == "WARN" || "${level}" == "ERROR" ]]; then
    echo "[${timestamp}] [${level}] $*" >&2
  else
    echo "[${timestamp}] [${level}] $*"
  fi
}

log_debug() { _log DEBUG "$@"; }
log_info()  { _log INFO  "$@"; }
log_warn()  { _log WARN  "$@"; }
log_error() { _log ERROR "$@"; }

fail() {
  log_error "$@"
  exit 1
}

require_command() {
  local command="$1"
  if ! command -v "${command}" >/dev/null 2>&1; then
    fail "Required command not found: ${command}"
  fi
}
