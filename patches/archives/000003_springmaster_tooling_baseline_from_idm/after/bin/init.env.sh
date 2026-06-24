#!/usr/bin/env bash
# Loads project-local environment configuration and shared shell helpers.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="${PROJECT_DIR:-$(cd "${SCRIPT_DIR}/.." && pwd)}"
export PROJECT_DIR

# shellcheck source=/dev/null
source "${PROJECT_DIR}/bin/lib/core/env.sh"
