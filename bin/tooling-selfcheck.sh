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

if [[ -x "${PROJECT_ROOT}/bin/patch-agents-scope-it.sh" ]]; then
  log_info "Checking AGENTS.md patch scope fixture"
  "${PROJECT_ROOT}/bin/patch-agents-scope-it.sh" >/dev/null
else
  log_info "Skipping AGENTS.md patch scope fixture; capability is not installed in this project"
fi

run_optional_contract_check() {
  local label="$1"
  local entrypoint="$2"
  shift 2
  if [[ -x "${entrypoint}" || -f "${entrypoint}" ]]; then
    log_info "Checking ${label}"
    "$@"
  else
    log_info "Skipping ${label}; capability is not installed in this project"
  fi
}

run_optional_contract_check \
  "documentation governance" \
  "${PROJECT_ROOT}/bin/documentation-gate.sh" \
  bash -c '"$1" --check >/dev/null && "$2" >/dev/null' _ \
  "${PROJECT_ROOT}/bin/documentation-gate.sh" \
  "${PROJECT_ROOT}/bin/documentation-gate-it.sh"

run_optional_contract_check \
  "configuration contract" \
  "${PROJECT_ROOT}/bin/config-contract.sh" \
  bash -c '"$1" --check >/dev/null && "$2" >/dev/null' _ \
  "${PROJECT_ROOT}/bin/config-contract.sh" \
  "${PROJECT_ROOT}/bin/config-contract-it.sh"

run_optional_contract_check \
  "release manifest contract" \
  "${PROJECT_ROOT}/bin/release-manifest-it.sh" \
  "${PROJECT_ROOT}/bin/release-manifest-it.sh"

if [[ -f "${PROJECT_ROOT}/platform/update/tools/compatibility-matrix.py" \
   && -f "${PROJECT_ROOT}/platform/update/compatibility/platform-compatibility-matrix.json" \
   && -f "${PROJECT_ROOT}/platform/update/tools/profile-rules.py" \
   && -f "${PROJECT_ROOT}/platform/update/rules/profiles.json" \
   && -x "${PROJECT_ROOT}/platform/update/tests/platform-update-managed-state-it.sh" ]]; then
  log_info "Checking Platform-Update compatibility matrix"
  python3 "${PROJECT_ROOT}/platform/update/tools/compatibility-matrix.py" --matrix "${PROJECT_ROOT}/platform/update/compatibility/platform-compatibility-matrix.json" validate >/dev/null
  "${PROJECT_ROOT}/platform/update/tests/platform-update-compatibility-matrix-it.sh" >/dev/null

  log_info "Checking declarative Platform-Update profile rules"
  python3 "${PROJECT_ROOT}/platform/update/tools/profile-rules.py" --rules "${PROJECT_ROOT}/platform/update/rules/profiles.json" validate >/dev/null
  "${PROJECT_ROOT}/platform/update/tests/platform-update-profile-rules-it.sh" >/dev/null

  log_info "Checking managed target version and provenance state"
  "${PROJECT_ROOT}/platform/update/tests/platform-update-managed-state-it.sh" >/dev/null
else
  log_info "Skipping Springmaster-only Platform-Update source contracts"
fi

log_info "Checking export lifecycle, checksum and archive contract"
"${PROJECT_ROOT}/bin/export-lifecycle-it.sh" >/dev/null

if is_true "${RUN_EXPORT}"; then
  log_info "Checking one full export and its integrity manifest"
  EXPORT_REL="$("${PROJECT_ROOT}/bin/export.sh" full --zip)"
  "${PROJECT_ROOT}/bin/export-integrity-it.sh" --export "${EXPORT_REL}" >/dev/null
else
  log_info "Skipping live full export; checking synthetic export integrity fixtures"
  "${PROJECT_ROOT}/bin/export-integrity-it.sh" >/dev/null
fi

run_optional_contract_check \
  "observability contract" \
  "${PROJECT_ROOT}/bin/observability-contract.sh" \
  bash -c '"$1" --check >/dev/null && "$2" >/dev/null' _ \
  "${PROJECT_ROOT}/bin/observability-contract.sh" \
  "${PROJECT_ROOT}/bin/observability-contract-it.sh"

run_optional_contract_check \
  "database migration contract" \
  "${PROJECT_ROOT}/bin/db-migration-contract.sh" \
  bash -c '"$1" --check >/dev/null && "$2" >/dev/null' _ \
  "${PROJECT_ROOT}/bin/db-migration-contract.sh" \
  "${PROJECT_ROOT}/bin/db-migration-contract-it.sh"

log_info "Checking DBTool env/status"
"${PROJECT_ROOT}/bin/dbtool.sh" env >/dev/null
"${PROJECT_ROOT}/bin/dbtool.sh" status >/dev/null

"${SCRIPT_DIR}/patch-scope-least-privilege-it.sh" >/dev/null
log_info "Checking patch run API, idempotency and background lifecycle"
"${SCRIPT_DIR}/patch-run-api-it.sh" >/dev/null
"${SCRIPT_DIR}/patch-transactional-accept-it.sh" >/dev/null
"${SCRIPT_DIR}/core-persistence-newness-contract-it.sh" >/dev/null
"${SCRIPT_DIR}/patch-state-audit.sh" --check
log_info "Tooling selfcheck completed successfully."
