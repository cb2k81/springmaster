#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

ACTIVATION_CONTRACT="${PROJECT_ROOT}/contracts/governance/tooling/patch-toolkit-activation-contract.json"
COMMAND="${1:-}"

if [[ -f "${ACTIVATION_CONTRACT}" ]]; then
  legacy_mutation=false
  case "${COMMAND}" in
    accept)
      legacy_mutation=true
      ;;
    apply|rollback)
      dry_run=false
      for argument in "$@"; do
        if [[ "${argument}" == "--dry-run" ]]; then
          dry_run=true
          break
        fi
      done
      if [[ "${dry_run}" != "true" ]]; then
        legacy_mutation=true
      fi
      ;;
  esac

  if [[ "${legacy_mutation}" == "true" ]]; then
    echo "LEGACY_PATCH_MUTATION_DISABLED: use ./bin/cpatch for mutating patch operations" >&2
    exit 78
  fi
fi

if [[ "${1:-}" == "artifact-preflight" ]]; then
  shift
  exec python3 "${SCRIPT_DIR}/patch-artifact-preflight.py" "${PROJECT_ROOT}" "$@"
fi

exec python3 "${SCRIPT_DIR}/patch.py" "${PROJECT_ROOT}" "$@"
