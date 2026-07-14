#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

if [[ "${1:-}" == "artifact-preflight" ]]; then
  shift
  exec python3 "${SCRIPT_DIR}/patch-artifact-preflight.py" "${PROJECT_ROOT}" "$@"
fi

exec python3 "${SCRIPT_DIR}/patch.py" "${PROJECT_ROOT}" "$@"
