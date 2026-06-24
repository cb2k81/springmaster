#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
PROJECT_DIR="${PROJECT_ROOT}"
export PROJECT_DIR

# shellcheck source=/dev/null
source "${SCRIPT_DIR}/init.env.sh"
# shellcheck source=/dev/null
source "${SCRIPT_DIR}/lib/dbtool/config.sh"
# shellcheck source=/dev/null
source "${SCRIPT_DIR}/lib/dbtool/mariadb.sh"
# shellcheck source=/dev/null
source "${SCRIPT_DIR}/lib/dbtool/liquibase.sh"
# shellcheck source=/dev/null
source "${SCRIPT_DIR}/lib/dbtool/changelog.sh"
# shellcheck source=/dev/null
source "${SCRIPT_DIR}/lib/dbtool/commands.sh"

dbtool_main "$@"
