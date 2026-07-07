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
  --export      run the full ZIP export check (default)
  --no-export   skip the full ZIP export check, useful when patch accept/verify performs export separately
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
python3 -m py_compile "${PROJECT_ROOT}/bin/patch.py"

log_info "Checking patch registry"
"${PROJECT_ROOT}/bin/patch.sh" list >/dev/null

if is_true "${RUN_EXPORT}"; then
  log_info "Checking full export"
  "${PROJECT_ROOT}/bin/export.sh" full --zip >/dev/null
else
  log_info "Skipping full export check"
fi

log_info "Checking DBTool env/status"
"${PROJECT_ROOT}/bin/dbtool.sh" env >/dev/null
"${PROJECT_ROOT}/bin/dbtool.sh" status >/dev/null

log_info "Tooling selfcheck completed successfully."
