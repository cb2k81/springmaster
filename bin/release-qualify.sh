#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${PROJECT_ROOT}"

RELEASE_VERSION=""
RUN_MAVEN=true
RUN_TOOLING=true
RUN_EXPORT=true

usage() {
  cat <<'EOF'
Usage: ./bin/release-qualify.sh [--release-version X.Y.Z] [--skip-maven] [--skip-tooling] [--no-export]
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --release-version) RELEASE_VERSION="${2:?missing release version}"; shift 2 ;;
    --skip-maven) RUN_MAVEN=false; shift ;;
    --skip-tooling) RUN_TOOLING=false; shift ;;
    --no-export) RUN_EXPORT=false; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage >&2; exit 2 ;;
  esac
done

if [[ -n "$(git status --porcelain)" ]]; then
  echo "RELEASE_QUALIFICATION_ERROR: working tree is not clean" >&2
  exit 3
fi

# shellcheck source=/dev/null
source "${PROJECT_ROOT}/platform/versions/platform.env"
if [[ -z "${RELEASE_VERSION}" ]]; then
  RELEASE_VERSION="${PLATFORM_VERSION%%-*}"
fi

DOC_STATUS=PASS
MAVEN_STATUS=SKIPPED
TOOLING_STATUS=SKIPPED
EXPORT_STATUS=SKIPPED
EXPORT_PATH=""

./bin/documentation-gate.sh --check

if [[ "${RUN_MAVEN}" == true ]]; then
  mvn -q test
  MAVEN_STATUS=PASS
fi
if [[ "${RUN_TOOLING}" == true ]]; then
  ./bin/tooling-selfcheck.sh --no-export
  TOOLING_STATUS=PASS
fi
if [[ "${RUN_EXPORT}" == true ]]; then
  EXPORT_PATH="$(./bin/export.sh full --zip)"
  ./bin/export-integrity-it.sh --export "${EXPORT_PATH}" >/dev/null
  EXPORT_STATUS=PASS
fi

python3 ./bin/release-manifest.py \
  --root "${PROJECT_ROOT}" \
  --release-version "${RELEASE_VERSION}" \
  --documentation-gate "${DOC_STATUS}" \
  --maven-test "${MAVEN_STATUS}" \
  --tooling-selfcheck "${TOOLING_STATUS}" \
  --export-integrity "${EXPORT_STATUS}" \
  --export-path "${EXPORT_PATH}"
