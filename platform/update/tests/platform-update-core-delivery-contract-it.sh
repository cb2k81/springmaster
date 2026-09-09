#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"
WORK_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/springmaster-s01-artifact-model.XXXXXX")"
trap 'rm -rf "${WORK_ROOT}"' EXIT
TARGET_ROOT="${WORK_ROOT}/target"
STAGING_ROOT="${WORK_ROOT}/staging"
OUTPUT_ROOT="${WORK_ROOT}/artifacts"
PATCH_ID="000001_s01_model_fixture"
ARTIFACT_ID="urn:uuid:11111111-2222-4333-8444-555555555555"

mkdir -p "${TARGET_ROOT}/bin" "${TARGET_ROOT}/custom" \
  "${TARGET_ROOT}/patches/logs/custom" "${STAGING_ROOT}/files/custom" \
  "${STAGING_ROOT}/delete/custom" "${STAGING_ROOT}/logs" "${OUTPUT_ROOT}"
cp "${PROJECT_ROOT}/bin/patch.py" "${TARGET_ROOT}/bin/patch.py"
cp "${PROJECT_ROOT}/bin/patch.sh" "${TARGET_ROOT}/bin/patch.sh"
chmod +x "${TARGET_ROOT}/bin/patch.py" "${TARGET_ROOT}/bin/patch.sh"
printf '%s\n' 'build/' 'exports/' 'patches/archives/' 'patches/runtime/' > "${TARGET_ROOT}/.gitignore"
python3 - "${TARGET_ROOT}/bin/patch.py" <<'PY'
from pathlib import Path
import sys
path=Path(sys.argv[1])
text=path.read_text(encoding="utf-8").replace(
    'PATCH_MANIFEST_SCHEMA = "springmaster.patch-manifest.v2"',
    'PATCH_MANIFEST_SCHEMA = "fixture.patch-manifest.v2"',
)
path.write_text(text,encoding="utf-8")
PY
printf '%s\n' 'PATCH_LOCAL_SCOPES=custom' 'PATCH_SCOPE_CUSTOM_PATHS=custom/**;platform/**;patches/logs/custom/**' \
  'PATCH_SCOPE_CUSTOM_LOG_DIR=custom' > "${TARGET_ROOT}/.env"
printf 'before\n' > "${TARGET_ROOT}/custom/modify.txt"
printf 'delete-me\n' > "${TARGET_ROOT}/custom/delete.txt"
printf 'mode-only\n' > "${TARGET_ROOT}/custom/mode.sh"
chmod 0644 "${TARGET_ROOT}/custom/mode.sh"
(
  cd "${TARGET_ROOT}"
  git init -q -b main
  git config user.name 'S01 Disposable Fixture'
  git config user.email 's01@example.invalid'
  git add .
  git commit -qm baseline
)

printf 'added\n' > "${STAGING_ROOT}/files/custom/add.txt"
printf 'after\n' > "${STAGING_ROOT}/files/custom/modify.txt"
printf 'mode-only\n' > "${STAGING_ROOT}/files/custom/mode.sh"
chmod 0755 "${STAGING_ROOT}/files/custom/mode.sh"
printf 'delete marker\n' > "${STAGING_ROOT}/delete/custom/delete.txt"
printf '# S01 model fixture\n' > "${STAGING_ROOT}/logs/CHANGELOG-${PATCH_ID}.md"
mkdir -p "${STAGING_ROOT}/files/platform/update" "${STAGING_ROOT}/files/platform/versions"
python3 - "${STAGING_ROOT}/files/platform/update/managed-state.json" \
  "${STAGING_ROOT}/files/platform/update/compatibility-decision.json" \
  "${ARTIFACT_ID}" "${PATCH_ID}" <<'PY'
from pathlib import Path
import json,sys
decision={"schemaVersion":"springmaster.platform-update-compatibility-decision.v1","status":"PASS","profile":"fixture"}
Path(sys.argv[1]).write_text(json.dumps({
  "schemaVersion":"springmaster.managed-target-state.v1",
  "target":"fixture",
  "artifactId":sys.argv[3],
  "patchId":sys.argv[4],
  "profile":"fixture",
  "installedVersions":{},
  "compatibility":decision,
},sort_keys=True)+"\n",encoding="utf-8")
Path(sys.argv[2]).write_text(json.dumps(decision,sort_keys=True)+"\n",encoding="utf-8")
PY
printf 'PLATFORM_VERSION=fixture\n' > "${STAGING_ROOT}/files/platform/versions/platform.env"

HEAD_BEFORE="$(git -C "${TARGET_ROOT}" rev-parse HEAD)"
TREE_BEFORE="$(git -C "${TARGET_ROOT}" rev-parse HEAD^{tree})"
STATUS_BEFORE="$(git -C "${TARGET_ROOT}" status --porcelain=v1 --untracked-files=all)"
SUMMARY="$(python3 "${PROJECT_ROOT}/platform/update/tools/finalize-target-patch.py" \
  --root "${STAGING_ROOT}" --target-root "${TARGET_ROOT}" \
  --output "${OUTPUT_ROOT}/${PATCH_ID}.zip" --patch-id "${PATCH_ID}" \
  --artifact-id "${ARTIFACT_ID}" --name s01_model_fixture --scope custom \
  --target-name fixture --profile fixture --description 'S01 artifact model fixture')"

python3 - "${OUTPUT_ROOT}/${PATCH_ID}.zip" "${SUMMARY}" <<'PY'
import json,sys,zipfile
summary=json.loads(sys.argv[2])
assert summary["canonicalSchemaVersion"]=="cocondo.patch-manifest.v5",summary
assert summary["targetSchemaVersion"]=="fixture.patch-manifest.v2",summary
assert summary["adapterId"]=="springmaster.platform-update.legacy-v2-target-adapter.v1",summary
assert (summary["new"],summary["modified"],summary["deleted"],summary["modeOnly"])==(5,2,1,1),summary
with zipfile.ZipFile(sys.argv[1]) as archive:
    manifest=json.loads(archive.read("manifest.json"))
    projection=manifest["canonicalArtifactModel"]
    canonical=projection["manifest"]
    ops={item["path"]:item for item in canonical["operations"]}
    assert manifest["artifactId"]==canonical["artifactId"]
    assert manifest["patchId"]==canonical["patchId"]
    assert manifest["requires"]["target"]==canonical["target"]["requiredProjectId"]=="fixture"
    assert manifest["scope"]==canonical["target"]["allowedScopes"][0]=="custom"
    assert ops["custom/add.txt"]["type"]=="add"
    assert ops["custom/modify.txt"]["type"]=="modify"
    assert ops["custom/delete.txt"]["type"]=="delete"
    assert ops["custom/mode.sh"]["beforeSha256"]==ops["custom/mode.sh"]["afterSha256"]
    assert ops["custom/mode.sh"]["beforeMode"]=="0644" and ops["custom/mode.sh"]["afterMode"]=="0755"
    assert "delete/custom/delete.txt" in archive.namelist()
PY

python3 "${PROJECT_ROOT}/bin/patch-artifact-preflight.py" "${TARGET_ROOT}" \
  "${OUTPUT_ROOT}/${PATCH_ID}.zip" --output "${WORK_ROOT}/preflight" --no-export \
  --engine "${TARGET_ROOT}/bin/patch.py" >/dev/null

EVIDENCE_ROOT="${WORK_ROOT}/evidence-target"
git clone -q --no-hardlinks "${TARGET_ROOT}" "${EVIDENCE_ROOT}"
mkdir -p "${EVIDENCE_ROOT}/platform/update" "${EVIDENCE_ROOT}/platform/versions"
cp "${STAGING_ROOT}/files/platform/update/managed-state.json" "${EVIDENCE_ROOT}/platform/update/managed-state.json"
cp "${STAGING_ROOT}/files/platform/update/compatibility-decision.json" "${EVIDENCE_ROOT}/platform/update/compatibility-decision.json"
cp "${STAGING_ROOT}/files/platform/versions/platform.env" "${EVIDENCE_ROOT}/platform/versions/platform.env"
python3 "${PROJECT_ROOT}/platform/update/tools/write-target-apply-evidence.py" \
  --patch-zip "${OUTPUT_ROOT}/${PATCH_ID}.zip" --output "${WORK_ROOT}/apply-evidence.json" \
  --target-name fixture --generated-profile fixture --accept-profile fixture \
  --full-test False --source-target-git-head "${HEAD_BEFORE}" --target-root "${EVIDENCE_ROOT}" >/dev/null
python3 - "${WORK_ROOT}/apply-evidence.json" "${ARTIFACT_ID}" "${PATCH_ID}" <<'PY'
import json,sys
evidence=json.load(open(sys.argv[1],encoding="utf-8"))
assert evidence["artifactId"]==sys.argv[2]
assert evidence["patchId"]==sys.argv[3]
assert evidence["target"]==evidence["managedState"]["target"]=="fixture"
assert evidence["managedState"]["artifactId"]==sys.argv[2]
assert evidence["managedState"]["patchId"]==sys.argv[3]
assert evidence["managedState"]["compatibility"]==evidence["compatibilityDecision"]
assert evidence["canonicalArtifactModelSchema"]=="cocondo.patch-manifest.v5"
assert evidence["legacyTargetAdapter"]=="springmaster.platform-update.legacy-v2-target-adapter.v1"
assert evidence["deletedPaths"]==["custom/delete.txt"]
PY

NEGATIVE_ROOT="${WORK_ROOT}/negative"
git clone -q --no-hardlinks "${TARGET_ROOT}" "${NEGATIVE_ROOT}"
printf 'baseline drift\n' > "${NEGATIVE_ROOT}/custom/modify.txt"
git -C "${NEGATIVE_ROOT}" add custom/modify.txt
git -C "${NEGATIVE_ROOT}" -c user.name=Fixture -c user.email=fixture@example.invalid commit -qm drift
if python3 "${PROJECT_ROOT}/bin/patch-artifact-preflight.py" "${NEGATIVE_ROOT}" \
  "${OUTPUT_ROOT}/${PATCH_ID}.zip" --output "${WORK_ROOT}/mismatch" --no-export \
  --engine "${NEGATIVE_ROOT}/bin/patch.py" >"${WORK_ROOT}/mismatch.log" 2>&1; then
  echo 'baseline/hash mismatch was accepted' >&2
  exit 1
fi
grep -q PATCH_ARTIFACT_LIVE_BASELINE_MISMATCH "${WORK_ROOT}/mismatch.log"

DUPLICATE_ROOT="${WORK_ROOT}/duplicate"
mkdir -p "${DUPLICATE_ROOT}/files/custom" "${DUPLICATE_ROOT}/delete/custom" "${DUPLICATE_ROOT}/logs"
printf 'value\n' > "${DUPLICATE_ROOT}/files/custom/same.txt"
printf 'marker\n' > "${DUPLICATE_ROOT}/delete/custom/same.txt"
printf '# duplicate\n' > "${DUPLICATE_ROOT}/logs/CHANGELOG-000002_duplicate.md"
if python3 "${PROJECT_ROOT}/platform/update/tools/finalize-target-patch.py" \
  --root "${DUPLICATE_ROOT}" --target-root "${TARGET_ROOT}" --output "${OUTPUT_ROOT}/000002_duplicate.zip" \
  --patch-id 000002_duplicate --name duplicate --scope custom --target-name fixture \
  --kind platform-update-compatibility >"${WORK_ROOT}/duplicate.log" 2>&1; then
  echo 'duplicate path was accepted' >&2
  exit 1
fi
grep -q 'duplicate target operation' "${WORK_ROOT}/duplicate.log"

EMPTY_ROOT="${WORK_ROOT}/empty"
mkdir -p "${EMPTY_ROOT}/files/custom" "${EMPTY_ROOT}/logs"
cp "${TARGET_ROOT}/custom/modify.txt" "${EMPTY_ROOT}/files/custom/modify.txt"
printf '# existing\n' > "${TARGET_ROOT}/patches/logs/custom/CHANGELOG-000003_empty.md"
cp "${TARGET_ROOT}/patches/logs/custom/CHANGELOG-000003_empty.md" "${EMPTY_ROOT}/logs/CHANGELOG-000003_empty.md"
if python3 "${PROJECT_ROOT}/platform/update/tools/finalize-target-patch.py" \
  --root "${EMPTY_ROOT}" --target-root "${TARGET_ROOT}" --output "${OUTPUT_ROOT}/000003_empty.zip" \
  --patch-id 000003_empty --name empty --scope custom --target-name fixture \
  --kind platform-update-compatibility >"${WORK_ROOT}/empty.log" 2>&1; then
  echo 'empty effective payload was accepted' >&2
  exit 1
fi
grep -q 'empty effective payload' "${WORK_ROOT}/empty.log"
rm "${TARGET_ROOT}/patches/logs/custom/CHANGELOG-000003_empty.md"

test "$(git -C "${TARGET_ROOT}" rev-parse HEAD)" = "${HEAD_BEFORE}"
test "$(git -C "${TARGET_ROOT}" rev-parse HEAD^{tree})" = "${TREE_BEFORE}"
test "$(git -C "${TARGET_ROOT}" status --porcelain=v1 --untracked-files=all)" = "${STATUS_BEFORE}"
echo 'PLATFORM_UPDATE_CORE_DELIVERY_CONTRACT=PASS'
echo 'DISPOSABLE_TARGET_ONLY=true'
echo 'TARGET_APPLY_INVOKED=false'
