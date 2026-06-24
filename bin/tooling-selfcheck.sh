#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
PROJECT_DIR="${PROJECT_ROOT}"
export PROJECT_DIR

# shellcheck source=/dev/null
source "${SCRIPT_DIR}/init.env.sh"

log_info "Checking shell syntax"
while IFS= read -r script; do
  bash -n "${script}"
done < <(find "${PROJECT_ROOT}/bin" -type f -name '*.sh' | sort)

log_info "Checking Python syntax"
python3 -m py_compile "${PROJECT_ROOT}/bin/patch.py"

log_info "Checking patch registry"
"${PROJECT_ROOT}/bin/patch.sh" list >/dev/null

log_info "Checking single export"
"${PROJECT_ROOT}/bin/export.sh" full --zip >/dev/null

log_info "Checking split export"
"${PROJECT_ROOT}/bin/export.sh" --full-parts baseline --zip >/dev/null

log_info "Checking DBTool env/status"
"${PROJECT_ROOT}/bin/dbtool.sh" env >/dev/null
"${PROJECT_ROOT}/bin/dbtool.sh" status >/dev/null

log_info "Tooling selfcheck completed successfully."
