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

case "${MODE}" in
  syntax) syntax_check ;;
  targeted)
    syntax_check
    if [[ -x ./bin/tooling-selfcheck.sh && "${COCONDO_PATCH_SCOPES:-}" == *tooling* ]]; then
      ./bin/tooling-selfcheck.sh --no-export
    else
      mvn -q test
    fi
    ;;
  full)
    mvn -q test
    if [[ -x ./bin/springmaster-gates.sh ]]; then
      mvn -q -Pspringmaster-gates-report test
      ./bin/springmaster-gates.sh report --clean
    fi
    ;;
  release) mvn -q clean verify ;;
  *) printf 'Unknown validation mode: %s\n' "${MODE}" >&2; exit 2 ;;
esac
