#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
FIXTURE="${PROJECT_ROOT}/build/release-manifest-it/fixture"
rm -rf "${FIXTURE}"
mkdir -p "${FIXTURE}/platform/versions"
cat > "${FIXTURE}/platform/versions/platform.env" <<'EOF'
PLATFORM_NAME=springmaster
PLATFORM_VERSION=0.15.0-foundation
PLATFORM_CORE_VERSION=0.3.6
PLATFORM_TOOLING_VERSION=0.5.0
PLATFORM_TEMPLATE_VERSION=0.2.0
PLATFORM_DEMO_VERSION=0.2.8
PLATFORM_UPDATE_VERSION=0.9.0
PLATFORM_STATE_PATCH=000141_springmaster_sprint_release_governance
EOF
(
  cd "${FIXTURE}"
  git init -q
  git config user.email release-fixture@example.invalid
  git config user.name 'Release Fixture'
  git add platform/versions/platform.env
  git commit -qm baseline
)
python3 "${PROJECT_ROOT}/bin/release-manifest.py" \
  --root "${FIXTURE}" \
  --release-version 0.15.0 \
  --documentation-gate PASS \
  --maven-test PASS \
  --tooling-selfcheck PASS \
  --export-integrity PASS \
  --export-path exports/text/fixture.zip \
  --output build/releases/0.15.0/release-manifest.json >/dev/null
python3 - "${FIXTURE}/build/releases/0.15.0/release-manifest.json" <<'PY'
import json, sys
p=json.load(open(sys.argv[1]))
assert p['schemaVersion']=='springmaster.release-manifest.v1'
assert p['status']=='QUALIFIED'
assert p['releaseVersion']=='0.15.0'
assert p['foundationVersion']=='0.15.0-foundation'
assert p['gitTag']=='springmaster-v0.15.0'
assert p['components']['tooling']=='0.5.0'
assert p['contracts']['patchManifest']=='springmaster.patch-manifest.v2'
assert set(p['qualification'].values())=={'PASS'}
PY
if python3 "${PROJECT_ROOT}/bin/release-manifest.py" \
  --root "${FIXTURE}" --release-version 0.14.9 \
  --documentation-gate PASS --maven-test PASS --tooling-selfcheck PASS --export-integrity PASS >/dev/null 2>&1; then
  echo "release version mismatch unexpectedly accepted" >&2
  exit 1
fi
echo RELEASE_MANIFEST_IT=PASS
