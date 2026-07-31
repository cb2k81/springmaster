#!/usr/bin/env bash

selfcheck_run_substep() {
  if [[ "$#" -lt 2 ]]; then
    printf 'SELF_CHECK_OBSERVABILITY_ERROR=missing-substep-command\n' >&2
    return 64
  fi

  local substep="$1"
  shift

  if [[ ! "${substep}" =~ ^[A-Za-z0-9][A-Za-z0-9._-]*$ ]]; then
    printf 'SELF_CHECK_OBSERVABILITY_ERROR=invalid-substep-id:%s\n' "${substep}" >&2
    return 64
  fi

  local project_root="${PROJECT_ROOT:?PROJECT_ROOT must be set before sourcing selfcheck observability}"
  local log_root="${SELF_CHECK_SUBSTEP_LOG_ROOT:-${project_root}/target/tooling-selfcheck/substeps}"
  local log_path="${log_root}/${substep}.log"
  local display_path="${log_path}"
  local rc

  mkdir -p -- "${log_root}"
  if [[ "${log_path}" == "${project_root}/"* ]]; then
    display_path="${log_path#"${project_root}/"}"
  fi

  printf 'SELF_CHECK_SUBSTEP_START=%s\n' "${substep}"
  printf 'SELF_CHECK_SUBSTEP_LOG=%s\n' "${display_path}"

  if "$@" >"${log_path}" 2>&1; then
    rc=0
  else
    rc=$?
  fi

  printf 'SELF_CHECK_SUBSTEP_RESULT=%s:%s\n' "${substep}" "${rc}"
  if [[ "${rc}" -ne 0 ]]; then
    printf 'SELF_CHECK_FAILED_SUBSTEP=%s\n' "${substep}" >&2
    cat -- "${log_path}" >&2
    return "${rc}"
  fi
}
