#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
SPRINGMASTER_EXPECTED='PATCH_SCOPE_ROOT_EXTRA_PATHS="AGENTS.md;contracts/**;src/main/java/de/cocondo/platform/demo/**;src/main/java/de/cocondo/system/entity/**"'
TARGET_EXPECTED='PATCH_SCOPE_ROOT_EXTRA_PATHS="AGENTS.md;contracts/**"'

for file in \
  "${PROJECT_ROOT}/.env.example" \
  "${PROJECT_ROOT}/PROJECT_DOCS/CONFIG/SPRINGMASTER_ENV_TEMPLATE.env"; do
  grep -Fxq "${SPRINGMASTER_EXPECTED}" "${file}"
  if grep -Eq 'de/cocondo/system/(http|observability|security)' "${file}"; then
    echo "Springmaster root scope contains a stale HTTP/Observability/Security exception: ${file}" >&2
    exit 1
  fi
done

grep -Fxq "${TARGET_EXPECTED}" \
  "${PROJECT_ROOT}/PROJECT_DOCS/TEMPLATES/project-skeleton/files/.env.example.tpl"
grep -Fq 'PATCH_SCOPE_ROOT_EXTRA_PATHS=\"AGENTS.md;contracts/**\"' \
  "${PROJECT_ROOT}/bin/project-new.sh"

for file in \
  "${PROJECT_ROOT}/PROJECT_DOCS/TEMPLATES/project-skeleton/files/.env.example.tpl" \
  "${PROJECT_ROOT}/bin/project-new.sh"; do
  if grep -Eq 'de/cocondo/(platform/demo|system/(entity|http|observability|security))' "${file}"; then
    echo "Generated project scope leaks Springmaster-specific source paths: ${file}" >&2
    exit 1
  fi
done

echo "PATCH_SCOPE_LEAST_PRIVILEGE_IT=PASS"
