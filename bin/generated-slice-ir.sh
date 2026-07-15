#!/usr/bin/env bash
set -euo pipefail
set +H
export LC_ALL=C

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$SCRIPT_DIR/generated-slice-ir.py" "$@"
