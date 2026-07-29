#!/usr/bin/env bash
set -euo pipefail
MODE="${1:?mode required}"
ROOT="${COCONDO_PROJECT_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
PATHS_FILE="${COCONDO_PATCH_PATHS_FILE:-}"
cd "${ROOT}"

syntax_check() {
  if [[ -n "${PATHS_FILE}" && -f "${PATHS_FILE}" ]]; then
    ./bin/csource-check --project-root "${ROOT}" --paths-file "${PATHS_FILE}"
  fi
  git diff --check HEAD --
}

run_stage() {
  local name="$1"
  shift
  printf 'VALIDATION_SUBSTEP=%s\n' "${name}"
  if "$@"; then
    printf 'VALIDATION_SUBSTEP_RESULT=%s:PASS\n' "${name}"
  else
    local rc=$?
    printf 'VALIDATION_SUBSTEP_RESULT=%s:FAIL:%s\n' "${name}" "${rc}" >&2
    return "${rc}"
  fi
}

case "${MODE}" in
  syntax)
    run_stage syntax syntax_check
    ;;
  targeted)
    run_stage syntax syntax_check
    if [[ -x ./bin/tooling-selfcheck.sh && "${COCONDO_PATCH_SCOPES:-}" == *tooling* ]]; then
      run_stage tooling-selfcheck ./bin/tooling-selfcheck.sh --no-export
    else
      run_stage maven-test mvn -q test
    fi
    ;;
  full)
    run_stage maven-test mvn -q test
    if [[ -x ./bin/springmaster-gates.sh ]]; then
      run_stage maven-gates-report mvn -q -Pspringmaster-gates-report test
      run_stage springmaster-gates-report ./bin/springmaster-gates.sh report --clean
    fi
    ;;
  release)
    run_stage maven-clean-verify mvn -q clean verify
    ;;
  *) printf 'Unknown validation mode: %s\n' "${MODE}" >&2; exit 2 ;;
esac
