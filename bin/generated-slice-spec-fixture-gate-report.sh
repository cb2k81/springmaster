#!/usr/bin/env bash
set -euo pipefail
set +H

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${PROJECT_ROOT}"
exec python3 "${SCRIPT_DIR}/generated-slice-spec-fixture-gate-report.py" "$@"
