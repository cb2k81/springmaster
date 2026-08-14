#!/usr/bin/env bash
set -euo pipefail

TOOL="${1:?tool namespace required}"
shift
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_MIN_MAJOR=3
PYTHON_MIN_MINOR=10
PYTHON_BIN="$(command -v python3 || true)"
[[ -n "${PYTHON_BIN}" && -x "${PYTHON_BIN}" ]] || { printf 'Python 3 runtime not found in PATH\n' >&2; exit 9; }
if ! "${PYTHON_BIN}" - "${PYTHON_MIN_MAJOR}" "${PYTHON_MIN_MINOR}" <<'PY_VERSION_CHECK'
import sys
major,minor=map(int,sys.argv[1:])
raise SystemExit(0 if sys.version_info >= (major,minor) else 1)
PY_VERSION_CHECK
then
  printf 'Cocondo Toolkit requires Python >= %s.%s; resolved %s (%s)\n' \
    "${PYTHON_MIN_MAJOR}" "${PYTHON_MIN_MINOR}" "${PYTHON_BIN}" "$("${PYTHON_BIN}" --version 2>&1 || true)" >&2
  exit 9
fi

if [[ -f "${ROOT}/.cocondo/tooling/cocondo-toolkit.pyz" ]]; then
  TOOLING_DIR="${ROOT}/.cocondo/tooling"
elif [[ -f "${ROOT}/dist/cocondo-toolkit.pyz" ]]; then
  TOOLING_DIR="${ROOT}/dist"
else
  printf 'Cocondo Toolkit runtime not found below %s\n' "${ROOT}" >&2
  exit 9
fi
RUNTIME="${TOOLING_DIR}/cocondo-toolkit.pyz"
LOCK_FILE="${TOOLING_DIR}/tooling.lock.json"
[[ -f "${LOCK_FILE}" ]] || { printf 'Toolkit lock file missing: %s\n' "${LOCK_FILE}" >&2; exit 9; }

readarray -t LOCK_VALUES < <("${PYTHON_BIN}" - "${LOCK_FILE}" <<'PY_LOCK'
import json, pathlib, sys
p=pathlib.Path(sys.argv[1])
try:
    data=json.loads(p.read_text(encoding='utf-8'))
    assert data.get('schemaVersion') == 'cocondo.tooling-lock.v1'
    for key in ('toolkitVersion','runtimeFile','sha256'):
        assert isinstance(data.get(key), str) and data[key]
except Exception as exc:
    print(f'INVALID:{exc}')
    raise SystemExit(0)
print(data['toolkitVersion'])
print(data['runtimeFile'])
print(data['sha256'])
PY_LOCK
)
[[ "${LOCK_VALUES[0]:-}" != INVALID:* && ${#LOCK_VALUES[@]} -eq 3 ]] || { printf 'Invalid toolkit lock file: %s\n' "${LOCK_FILE}" >&2; exit 9; }
LOCK_VERSION="${LOCK_VALUES[0]}"
LOCK_RUNTIME="${LOCK_VALUES[1]}"
LOCK_SHA="${LOCK_VALUES[2]}"
[[ "${LOCK_RUNTIME}" == "$(basename "${RUNTIME}")" ]] || { printf 'Toolkit runtime name mismatch: lock=%s actual=%s\n' "${LOCK_RUNTIME}" "$(basename "${RUNTIME}")" >&2; exit 9; }
ACTUAL_SHA="$(sha256sum "${RUNTIME}" | awk '{print $1}')"
[[ "${ACTUAL_SHA}" == "${LOCK_SHA}" ]] || { printf 'Toolkit runtime checksum mismatch: %s\n' "${RUNTIME}" >&2; exit 9; }

ENV_CONFIG="${ROOT}/.cocondo/tooling/project.env"
JSON_CONFIG="${ROOT}/.cocondo/tooling/project.json"
CONFIG_VERSION=""
if [[ -f "${ENV_CONFIG}" ]]; then
  CONFIG_VERSION="$("${PYTHON_BIN}" - "${ENV_CONFIG}" <<'PY_ENV'
import pathlib, sys
value=''
for raw in pathlib.Path(sys.argv[1]).read_text(encoding='utf-8').splitlines():
    line=raw.strip()
    if line.startswith('CPATCH_TOOLKIT_VERSION='):
        value=line.split('=',1)[1].strip()
        break
print(value)
PY_ENV
)"
elif [[ -f "${JSON_CONFIG}" ]]; then
  CONFIG_VERSION="$("${PYTHON_BIN}" - "${JSON_CONFIG}" <<'PY_JSON'
import json, pathlib, sys
try:
    value=json.loads(pathlib.Path(sys.argv[1]).read_text(encoding='utf-8')).get('toolingVersion')
    print(value if isinstance(value,str) else '')
except Exception:
    print('')
PY_JSON
)"
fi
if [[ -n "${CONFIG_VERSION}" ]]; then
  [[ "${CONFIG_VERSION}" == "${LOCK_VERSION}" ]] || { printf 'Project config/runtime version mismatch: config=%s runtime=%s\n' "${CONFIG_VERSION:-missing}" "${LOCK_VERSION}" >&2; exit 2; }
fi

cd "${ROOT}"
exec "${PYTHON_BIN}" "${RUNTIME}" "${TOOL}" "$@"
