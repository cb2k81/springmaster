#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
source "${SCRIPT_DIR}/init.env.sh"

cat <<'EOF'
platform-update.sh bootstrap placeholder

Status:
  The target registry structure exists under platform/update/targets/.
  Update-patch generation is intentionally not implemented in the bootstrap package.
  It will be introduced by a dedicated platform-update patch after the tooling baseline is stable.
EOF
