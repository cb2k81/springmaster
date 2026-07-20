#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"
TOOL="${PROJECT_ROOT}/platform/update/tools/profile-rules.py"
RULES="${PROJECT_ROOT}/platform/update/rules/profiles.json"
python3 "${TOOL}" --rules "${RULES}" validate >/dev/null
[[ "$(python3 "${TOOL}" --rules "${RULES}" get --profile core --field scope)" == core ]]
[[ "$(python3 "${TOOL}" --rules "${RULES}" get --profile tooling-cutover --field synthesizeToolingCutoverConfig)" == true ]]
[[ "$(python3 "${TOOL}" --rules "${RULES}" get --profile core-docs --field fullTest)" == false ]]
python3 "${TOOL}" --rules "${RULES}" paths --profile core | grep -Fxq 'src/test/java/de/cocondo/system'
WORK_ROOT="$(mktemp -d)"
trap 'rm -rf "${WORK_ROOT}"' EXIT
python3 - "${RULES}" "${WORK_ROOT}/bad.json" <<'PY'
import json,sys
src=json.load(open(sys.argv[1],encoding='utf-8'))
src['profiles']['core']['payloadPaths'].append('../escape')
json.dump(src,open(sys.argv[2],'w',encoding='utf-8'))
PY
if python3 "${TOOL}" --rules "${WORK_ROOT}/bad.json" validate >/dev/null 2>&1; then
  echo '[FAIL] unsafe profile rule was accepted' >&2
  exit 1
fi
echo 'PLATFORM_UPDATE_PROFILE_RULES_IT=PASS'
