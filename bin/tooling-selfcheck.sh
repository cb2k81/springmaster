#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
PROJECT_DIR="${PROJECT_ROOT}"
export PROJECT_DIR

# shellcheck source=/dev/null
source "${SCRIPT_DIR}/init.env.sh"

RUN_EXPORT=true

print_usage() {
  cat <<'EOF'
Usage:
  ./bin/tooling-selfcheck.sh [--export|--no-export]

Options:
  --export      run one full ZIP export and verify its raw-byte hash manifest (default)
  --no-export   skip the live full ZIP export; synthetic export-integrity fixtures still run
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --export)
      RUN_EXPORT=true
      shift
      ;;
    --no-export|--skip-export)
      RUN_EXPORT=false
      shift
      ;;
    -h|--help|help)
      print_usage
      exit 0
      ;;
    *)
      fail "Unknown tooling-selfcheck option: $1"
      ;;
  esac
done

log_info "Checking shell syntax"
while IFS= read -r script; do
  bash -n "${script}"
done < <(find "${PROJECT_ROOT}/bin" -type f -name '*.sh' | sort)

log_info "Checking Python syntax"
while IFS= read -r script; do
  python3 -m py_compile "${script}"
done < <(find "${PROJECT_ROOT}/bin" -maxdepth 1 -type f -name '*.py' | sort)

log_info "Checking patch registry"
"${PROJECT_ROOT}/bin/patch.sh" list >/dev/null

log_info "Checking patch artifact preflight fixtures"
"${PROJECT_ROOT}/bin/patch-artifact-preflight-it.sh" >/dev/null

log_info "Checking AGENTS.md patch scope fixture"
"${PROJECT_ROOT}/bin/patch-agents-scope-it.sh" >/dev/null

log_info "Checking documentation governance"
"${PROJECT_ROOT}/bin/documentation-gate.sh" --check >/dev/null
"${PROJECT_ROOT}/bin/documentation-gate-it.sh" >/dev/null

log_info "Checking configuration contract"
"${PROJECT_ROOT}/bin/config-contract.sh" --check >/dev/null
"${PROJECT_ROOT}/bin/config-contract-it.sh" >/dev/null

log_info "Checking release manifest contract"
"${PROJECT_ROOT}/bin/release-manifest-it.sh" >/dev/null

log_info "Checking managed target version and provenance state"
"${PROJECT_ROOT}/platform/update/tests/platform-update-managed-state-it.sh" >/dev/null

if is_true "${RUN_EXPORT}"; then
  log_info "Checking one full export and its integrity manifest"
  EXPORT_REL="$("${PROJECT_ROOT}/bin/export.sh" full --zip)"
  "${PROJECT_ROOT}/bin/export-integrity-it.sh" --export "${EXPORT_REL}" >/dev/null
else
  log_info "Skipping live full export; checking synthetic export integrity fixtures"
  "${PROJECT_ROOT}/bin/export-integrity-it.sh" >/dev/null
fi

log_info "Checking observability contract"
"${PROJECT_ROOT}/bin/observability-contract.sh" --check >/dev/null
"${PROJECT_ROOT}/bin/observability-contract-it.sh" >/dev/null

log_info "Checking database migration contract"
"${PROJECT_ROOT}/bin/db-migration-contract.sh" --check >/dev/null
"${PROJECT_ROOT}/bin/db-migration-contract-it.sh" >/dev/null

log_info "Checking DBTool env/status"
"${PROJECT_ROOT}/bin/dbtool.sh" env >/dev/null
"${PROJECT_ROOT}/bin/dbtool.sh" status >/dev/null

log_info "Tooling selfcheck completed successfully."
