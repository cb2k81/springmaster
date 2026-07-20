#!/usr/bin/env bash
set -euo pipefail
umask 0002

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
RUN_DIR="${PROJECT_ROOT}/build/patch-artifact-preflight-it/$(date +%Y%m%d_%H%M%S)_$$"
FIXTURE="${RUN_DIR}/fixture"
PATCH_DIR="${RUN_DIR}/patches"
LOG_DIR="${RUN_DIR}/logs"
mkdir -p "${FIXTURE}/bin" "${FIXTURE}/custom" "${PATCH_DIR}" "${LOG_DIR}"

cp "${SCRIPT_DIR}/patch.py" "${FIXTURE}/bin/patch.py"
cp "${SCRIPT_DIR}/patch.sh" "${FIXTURE}/bin/patch.sh"
cp "${SCRIPT_DIR}/patch-artifact-preflight.py" "${FIXTURE}/bin/patch-artifact-preflight.py"
chmod +x "${FIXTURE}/bin/patch.py" "${FIXTURE}/bin/patch.sh" "${FIXTURE}/bin/patch-artifact-preflight.py"

cat > "${FIXTURE}/.gitignore" <<'EOF'
build/
exports/
patches/archives/
patches/runtime/
EOF
cat > "${FIXTURE}/.env" <<'EOF'
PATCH_LOCAL_SCOPES=custom
PATCH_SCOPE_CUSTOM_PATHS=custom/**
PATCH_SCOPE_CUSTOM_LOG_DIR=custom
PATCH_EXPORT_COMMAND=none
EOF
printf 'original\n' > "${FIXTURE}/custom/existing.txt"
printf '#!/usr/bin/env bash\nprintf tool-original\\n\n' > "${FIXTURE}/custom/tool.bash"
chmod 775 "${FIXTURE}/custom/tool.bash"
printf '#!/usr/bin/env bash\nprintf mode-only\\n\n' > "${FIXTURE}/custom/mode-only.bash"
chmod 664 "${FIXTURE}/custom/mode-only.bash"

(
  cd "${FIXTURE}"
  git init -q
  git config user.email "artifact-preflight@example.invalid"
  git config user.name "Artifact Preflight Fixture"
  git config core.sharedRepository group
  git add .
  git commit -qm "fixture baseline"
)

test "$(stat -c '%a' "${FIXTURE}/custom/existing.txt")" = "664"
test "$(stat -c '%a' "${FIXTURE}/custom/tool.bash")" = "775"
test "$(stat -c '%a' "${FIXTURE}/custom/mode-only.bash")" = "664"

mkdir -p "${FIXTURE}/patches/archives/000000_existing_artifact"
cat > "${FIXTURE}/patches/archives/000000_existing_artifact/manifest.json" <<'JSON'
{
  "schemaVersion": "springmaster.patch-manifest.v2",
  "artifactId": "urn:uuid:11111111-1111-4111-8111-111111111111",
  "id": "000000_existing_artifact",
  "patchId": "000000_existing_artifact",
  "name": "existing_artifact",
  "scope": "custom"
}
JSON

python3 - "${FIXTURE}" "${PATCH_DIR}" <<'PY'
import hashlib
import json
import sys
import uuid
import zipfile
from pathlib import Path

fixture = Path(sys.argv[1])
patch_dir = Path(sys.argv[2])
existing_sha = hashlib.sha256((fixture / "custom/existing.txt").read_bytes()).hexdigest()
tool_sha = hashlib.sha256((fixture / "custom/tool.bash").read_bytes()).hexdigest()
mode_only_sha = hashlib.sha256((fixture / "custom/mode-only.bash").read_bytes()).hexdigest()

def write_patch(patch_id, body, baseline_existing=existing_sha, baseline_format="map", artifact_id=None):
    name = patch_id.split("_", 1)[1]
    target = f"custom/{name}.txt"
    baseline_map = {
        "custom/existing.txt": baseline_existing,
        "custom/tool.bash": tool_sha,
        target: None,
        f"patches/logs/custom/CHANGELOG-{patch_id}.md": None,
    }
    baseline = {"expectedBeforeSha256": baseline_map}
    if baseline_format == "list":
        baseline = {
            "expectedBefore": [
                {"path": path, "sha256": value} if value is not None else {"path": path, "exists": False}
                for path, value in baseline_map.items()
            ]
        }
    manifest = {
        "schemaVersion": "springmaster.patch-manifest.v2",
        "artifactId": artifact_id or f"urn:uuid:{uuid.uuid5(uuid.NAMESPACE_URL, 'springmaster-test:' + patch_id)}",
        "id": patch_id,
        "patchId": patch_id,
        "scope": "custom",
        "name": name,
        "baseline": baseline,
    }
    with zipfile.ZipFile(patch_dir / f"{patch_id}.zip", "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("manifest.json", json.dumps(manifest, indent=2) + "\n")
        archive.writestr("files/custom/existing.txt", "changed\n")
        tool_info = zipfile.ZipInfo("files/custom/tool.bash")
        tool_info.external_attr = (0o100755 << 16)
        archive.writestr(tool_info, "#!/usr/bin/env bash\nprintf tool-changed\\n\n")
        archive.writestr(f"files/{target}", body)
        archive.writestr(f"logs/CHANGELOG-{patch_id}.md", f"# {patch_id}\n")


def write_mode_only_patch():
    patch_id = "000007_fixture_mode_only"
    manifest = {
        "schemaVersion": "springmaster.patch-manifest.v2",
        "artifactId": f"urn:uuid:{uuid.uuid5(uuid.NAMESPACE_URL, 'springmaster-test:' + patch_id)}",
        "id": patch_id,
        "patchId": patch_id,
        "scope": "custom",
        "name": "fixture_mode_only",
        "baseline": {
            "expectedBeforeSha256": {
                "custom/mode-only.bash": mode_only_sha,
                f"patches/logs/custom/CHANGELOG-{patch_id}.md": None,
            }
        },
    }
    with zipfile.ZipFile(patch_dir / f"{patch_id}.zip", "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("manifest.json", json.dumps(manifest, indent=2) + "\n")
        mode_info = zipfile.ZipInfo("files/custom/mode-only.bash")
        mode_info.external_attr = (0o100755 << 16)
        archive.writestr(mode_info, (fixture / "custom/mode-only.bash").read_bytes())
        archive.writestr(f"logs/CHANGELOG-{patch_id}.md", f"# {patch_id}\n")

write_patch("000001_fixture_valid", "valid\n")
write_patch("000002_fixture_hash_mismatch", "hash\n", "0" * 64)
write_patch("000003_fixture_trailing_whitespace", "bad  \n")
write_patch("000004_fixture_eof_blank_line", "bad\n\n")
write_patch("000005_fixture_missing_newline", "bad")
write_patch("000006_fixture_list_baseline", "list-valid\n", baseline_format="list")
write_mode_only_patch()
write_patch(
    "000010_fixture_duplicate_artifact",
    "duplicate-artifact\n",
    artifact_id="urn:uuid:11111111-1111-4111-8111-111111111111",
)


def rewrite_manifest(source_name, target_name, transform):
    source = patch_dir / source_name
    target = patch_dir / target_name
    with zipfile.ZipFile(source) as src, zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as dst:
        for info in src.infolist():
            data = src.read(info.filename)
            if info.filename == "manifest.json":
                manifest = json.loads(data)
                transform(manifest)
                data = (json.dumps(manifest, indent=2) + "\n").encode()
            dst.writestr(info, data)

rewrite_manifest(
    "000001_fixture_valid.zip",
    "000008_fixture_missing_artifact.zip",
    lambda manifest: manifest.pop("artifactId"),
)
rewrite_manifest(
    "000001_fixture_valid.zip",
    "000009_fixture_invalid_artifact.zip",
    lambda manifest: manifest.__setitem__("artifactId", "not-a-uuid"),
)
PY

run_expect_pass() {
  local name="$1"
  shift
  (
    cd "${FIXTURE}"
    "$@"
  ) > "${LOG_DIR}/${name}.log" 2>&1
}

run_expect_fail() {
  local name="$1"
  local expected="$2"
  shift 2
  if (
    cd "${FIXTURE}"
    "$@"
  ) > "${LOG_DIR}/${name}.log" 2>&1; then
    echo "ERROR: ${name} unexpectedly passed" >&2
    exit 1
  fi
  grep -q "${expected}" "${LOG_DIR}/${name}.log"
}

python3 - "${FIXTURE}/bin/patch-artifact-preflight.py" "${FIXTURE}" <<'PY' \
  > "${LOG_DIR}/atomic-output-allocation.log" 2>&1
import importlib.util
import shutil
import sys
from pathlib import Path

sys.dont_write_bytecode = True
script = Path(sys.argv[1])
fixture = Path(sys.argv[2])
spec = importlib.util.spec_from_file_location("patch_artifact_preflight", script)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)
module.timestamp = lambda: "20260101_000000"
first = module.allocate_output_directory(fixture, None, "000001_fixture_valid")
second = module.allocate_output_directory(fixture, None, "000001_fixture_valid")
if first == second or not first.is_dir() or not second.is_dir():
    raise SystemExit(f"atomic output allocation failed: first={first} second={second}")
print(f"FIRST_OUTPUT={first}")
print(f"SECOND_OUTPUT={second}")
print("OUTPUT_DIRECTORY_ATOMIC_ALLOCATION=PASS")
shutil.rmtree(first)
shutil.rmtree(second)
shutil.rmtree(script.parent / "__pycache__", ignore_errors=True)
PY
grep -Fxq 'OUTPUT_DIRECTORY_ATOMIC_ALLOCATION=PASS' \
  "${LOG_DIR}/atomic-output-allocation.log"

run_expect_fail missing-artifact PATCH_ARTIFACT_IDENTITY_INVALID \
  ./bin/patch.sh artifact-preflight "${PATCH_DIR}/000008_fixture_missing_artifact.zip" --no-export
run_expect_fail invalid-artifact PATCH_ARTIFACT_IDENTITY_INVALID \
  ./bin/patch.sh artifact-preflight "${PATCH_DIR}/000009_fixture_invalid_artifact.zip" --no-export
run_expect_fail duplicate-artifact PATCH_ARTIFACT_IDENTITY_CONFLICT \
  ./bin/patch.sh artifact-preflight "${PATCH_DIR}/000010_fixture_duplicate_artifact.zip" --no-export

run_expect_pass valid-first \
  ./bin/patch.sh artifact-preflight "${PATCH_DIR}/000001_fixture_valid.zip" --no-export
run_expect_pass valid-second \
  ./bin/patch.sh artifact-preflight "${PATCH_DIR}/000001_fixture_valid.zip" --no-export
run_expect_pass list-baseline \
  ./bin/patch.sh artifact-preflight "${PATCH_DIR}/000006_fixture_list_baseline.zip" --no-export
run_expect_pass mode-only \
  ./bin/patch.sh artifact-preflight "${PATCH_DIR}/000007_fixture_mode_only.zip" --no-export

grep -q 'ARTIFACT_PREFLIGHT=PASS' "${LOG_DIR}/valid-first.log"
grep -q 'ARTIFACT_PREFLIGHT=PASS' "${LOG_DIR}/valid-second.log"
grep -q 'ARTIFACT_PREFLIGHT=PASS' "${LOG_DIR}/list-baseline.log"
grep -q 'ARTIFACT_PREFLIGHT=PASS' "${LOG_DIR}/mode-only.log"
FIRST_REPORT="$(sed -n 's/^REPORT=//p' "${LOG_DIR}/valid-first.log" | tail -n 1)"
SECOND_REPORT="$(sed -n 's/^REPORT=//p' "${LOG_DIR}/valid-second.log" | tail -n 1)"
test -n "${FIRST_REPORT}"
test -n "${SECOND_REPORT}"
test "${FIRST_REPORT}" != "${SECOND_REPORT}"
test -f "${FIRST_REPORT}"
test -f "${SECOND_REPORT}"
echo "OUTPUT_COLLISION_REGRESSION=PASS first=${FIRST_REPORT} second=${SECOND_REPORT}"
test -z "$(cd "${FIXTURE}" && git status --porcelain=v1 --untracked-files=all)"

run_expect_fail hash-mismatch PATCH_ARTIFACT_LIVE_BASELINE_MISMATCH \
  ./bin/patch.sh artifact-preflight "${PATCH_DIR}/000002_fixture_hash_mismatch.zip" --no-export
run_expect_fail trailing-whitespace PATCH_PAYLOAD_TRAILING_WHITESPACE \
  ./bin/patch.sh artifact-preflight "${PATCH_DIR}/000003_fixture_trailing_whitespace.zip" --no-export
run_expect_fail eof-blank-line PATCH_PAYLOAD_EOF_BLANK_LINE \
  ./bin/patch.sh artifact-preflight "${PATCH_DIR}/000004_fixture_eof_blank_line.zip" --no-export
run_expect_fail missing-newline PATCH_PAYLOAD_FINAL_NEWLINE_MISSING \
  ./bin/patch.sh artifact-preflight "${PATCH_DIR}/000005_fixture_missing_newline.zip" --no-export

printf 'dirty\n' > "${FIXTURE}/dirty.txt"
run_expect_fail dirty-worktree PATCH_ARTIFACT_WORKTREE_DIRTY \
  ./bin/patch.sh artifact-preflight "${PATCH_DIR}/000001_fixture_valid.zip" --no-export
rm -f "${FIXTURE}/dirty.txt"

test -z "$(cd "${FIXTURE}" && git status --porcelain=v1 --untracked-files=all)"

(
  cd "${FIXTURE}"
  ./bin/patch.sh apply "${PATCH_DIR}/000001_fixture_valid.zip" > "${LOG_DIR}/direct-apply-mode.log" 2>&1
)
test "$(stat -c '%a' "${FIXTURE}/custom/existing.txt")" = "664"
test "$(stat -c '%a' "${FIXTURE}/custom/tool.bash")" = "775"
test "$(stat -c '%a' "${FIXTURE}/custom/fixture_valid.txt")" = "664"
test "$(stat -c '%a' "${FIXTURE}/patches/logs/custom/CHANGELOG-000001_fixture_valid.md")" = "664"
echo "GIT_MODE_CONTRACT=PASS nonexec=100644 executable=100755 hostModes=664,775"

echo "PATCH_ARTIFACT_PREFLIGHT_IT=PASS"
echo "LOG_DIR=${LOG_DIR}"
