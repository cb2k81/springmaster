#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
RUN_DIR="${PROJECT_ROOT}/build/patch-agents-scope-it/$(date +%Y%m%d_%H%M%S)_$$"
FIXTURE="${RUN_DIR}/fixture"
PATCH_ZIP="${RUN_DIR}/000001_fixture_agents.zip"
mkdir -p "${FIXTURE}/bin" "${RUN_DIR}"
cp "${SCRIPT_DIR}/patch.py" "${FIXTURE}/bin/patch.py"
chmod +x "${FIXTURE}/bin/patch.py"
printf 'build/\npatches/archives/\npatches/runtime/\n' > "${FIXTURE}/.gitignore"
(
  cd "${FIXTURE}"
  git init -q
  git config user.email "agents-scope@example.invalid"
  git config user.name "Agents Scope Fixture"
  git add .
  git commit -qm "fixture baseline"
)
python3 - "${PATCH_ZIP}" <<'PY'
import json
import sys
import zipfile
from pathlib import Path

zip_path = Path(sys.argv[1])
patch_id = zip_path.stem
manifest = {
    "id": patch_id,
    "patchId": patch_id,
    "scope": "docs",
    "name": "fixture_agents",
    "baseline": {
        "expectedBeforeSha256": {
            "AGENTS.md": None,
            "patches/logs/docs/CHANGELOG-000001_fixture_agents.md": None,
        }
    },
}
with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
    archive.writestr("manifest.json", json.dumps(manifest, indent=2) + "\n")
    archive.writestr("files/AGENTS.md", "# Fixture agents\n")
    archive.writestr("logs/CHANGELOG-000001_fixture_agents.md", "# Fixture agents\n")
PY
python3 "${FIXTURE}/bin/patch.py" "${FIXTURE}" apply --dry-run "${PATCH_ZIP}" >/dev/null
python3 "${FIXTURE}/bin/patch.py" "${FIXTURE}" apply "${PATCH_ZIP}" >/dev/null
test -f "${FIXTURE}/AGENTS.md"
grep -Fxq '# Fixture agents' "${FIXTURE}/AGENTS.md"
printf 'PATCH_AGENTS_SCOPE_IT=PASS\n'
