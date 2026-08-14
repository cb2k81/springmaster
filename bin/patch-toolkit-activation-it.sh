#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
WORK_ROOT="${PROJECT_ROOT}/target/patch-toolkit-activation-it"
FIXTURE="${WORK_ROOT}/repo"

rm -rf "${WORK_ROOT}"
mkdir -p "${FIXTURE}"

"${PROJECT_ROOT}/bin/patch-toolkit-activation.sh" \
  --check \
  --out "${WORK_ROOT}/positive.json" \
  >/dev/null

"${PROJECT_ROOT}/bin/cpatch" workspace --help >/dev/null

for path in \
  .cocondo/tooling/project.env \
  .cocondo/tooling/tooling.lock.json \
  .cocondo/tooling/cocondo-toolkit.pyz \
  .cocondo/tooling/cocondo-toolkit.pyz.sha256 \
  platform/versions/platform.env \
  contracts/governance/tooling/patch-toolkit-activation-contract.json \
  src/test/resources/tooling/patch-toolkit-activation-v1/activation-evidence.json \
  PROJECT_DOCS/TOOLING/COCONDO_PATCH_TOOLKIT_ACTIVATION_REPORT.md \
  AGENTS.md \
  pom.xml \
  bin/cpatch \
  bin/patch.sh \
  bin/patch.py \
  bin/patch-toolkit-activation.py \
  .cocondo/process.env \
  contracts/governance/tooling/process-operations-contract.json \
  bin/process-ops.sh \
  bin/process-ops.py \
  bin/process-ops-it.sh \
  bin/tooling-selfcheck.sh \
  bin/tooling-selfcheck-observability-it.sh \
  bin/lib/core/selfcheck-observability.sh
 do
  mkdir -p "${FIXTURE}/$(dirname "${path}")"
  cp "${PROJECT_ROOT}/${path}" "${FIXTURE}/${path}"
 done

python3 - "${FIXTURE}/.cocondo/tooling/project.env" <<'PY'
from pathlib import Path
import sys
path = Path(sys.argv[1])
text = path.read_text(encoding="utf-8")
text = text.replace("CPATCH_REQUIRE_WORKTREE=true", "CPATCH_REQUIRE_WORKTREE=false")
path.write_text(text, encoding="utf-8")
PY

if python3 "${FIXTURE}/bin/patch-toolkit-activation.py" \
  --root "${FIXTURE}" \
  --check \
  --out "${WORK_ROOT}/negative.json" \
  >/dev/null 2>&1
then
  echo "[ERROR] Activation check accepted disabled worktree enforcement" >&2
  exit 1
fi

grep -q 'PROJECT_ENV_MISMATCH' "${WORK_ROOT}/negative.json"

set +e
LEGACY_OUTPUT="$("${PROJECT_ROOT}/bin/patch.sh" accept /nonexistent/patch.zip 2>&1)"
LEGACY_STATUS=$?
set -e

test "${LEGACY_STATUS}" -eq 78
printf '%s\n' "${LEGACY_OUTPUT}" | grep -q 'LEGACY_PATCH_MUTATION_DISABLED'

# PATCH_TOOLKIT_SPLIT_STAGING_REGRESSION_V1
python3 - "${PROJECT_ROOT}/.cocondo/tooling/cocondo-toolkit.pyz" "${WORK_ROOT}/split-staging" <<'PY_STAGING'
from pathlib import Path
import json
import subprocess
import sys

runtime = Path(sys.argv[1])
root = Path(sys.argv[2])
sys.path.insert(0, str(runtime))
from cocondo_toolkit.gitops import GitRepository


def run(args, cwd, check=True):
    return subprocess.run(args, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=check)


def init_repo(path):
    path.mkdir(parents=True)
    run(["git", "init", "-q", "-b", "main"], path)
    run(["git", "config", "user.name", "Test"], path)
    run(["git", "config", "user.email", "test@example.invalid"], path)
    return path

mixed = init_repo(root / "mixed")
(mixed / ".gitignore").write_text("ignored/**\n", encoding="utf-8")
(mixed / "ignored").mkdir()
(mixed / "ignored/deleted file.txt").write_text("old\n", encoding="utf-8")
(mixed / "normal.txt").write_text("old\n", encoding="utf-8")
(mixed / "literal[abc].txt").write_text("old\n", encoding="utf-8")
run(["git", "add", "-f", ".gitignore", "ignored/deleted file.txt", "normal.txt", "literal[abc].txt"], mixed)
run(["git", "commit", "-qm", "baseline"], mixed)
(mixed / "ignored/deleted file.txt").unlink()
(mixed / "normal.txt").write_text("new\n", encoding="utf-8")
(mixed / "new file.txt").write_text("new\n", encoding="utf-8")
(mixed / "literal[abc].txt").write_text("new\n", encoding="utf-8")
repo = GitRepository(mixed)
expected = sorted(["ignored/deleted file.txt", "normal.txt", "new file.txt", "literal[abc].txt"])
repo.stage_paths(expected, mixed)
assert repo.staged_paths(mixed) == expected

ignored = init_repo(root / "ignored-addition")
(ignored / ".gitignore").write_text("ignored/**\n", encoding="utf-8")
run(["git", "add", ".gitignore"], ignored)
run(["git", "commit", "-qm", "baseline"], ignored)
(ignored / "ignored").mkdir()
(ignored / "ignored/new.txt").write_text("new\n", encoding="utf-8")
repo = GitRepository(ignored)
try:
    repo.stage_paths(["ignored/new.txt"], ignored)
except Exception as exc:
    assert getattr(exc, "code", None) == "GIT_COMMAND_FAILED", repr(exc)
else:
    raise AssertionError("new ignored file was staged")
assert repo.staged_paths(ignored) == []

large = init_repo(root / "large")
paths = []
for index in range(1024):
    path = large / f"files/f{index:04d}.txt"
    path.parent.mkdir(exist_ok=True)
    path.write_text("old\n", encoding="utf-8")
run(["git", "add", "."], large)
run(["git", "commit", "-qm", "baseline"], large)
for index in range(1024):
    path = large / f"files/f{index:04d}.txt"
    if index % 3 == 0:
        path.unlink()
    else:
        path.write_text("new\n", encoding="utf-8")
    paths.append(f"files/f{index:04d}.txt")
for index in range(64):
    path = large / f"additions/n{index:04d}.txt"
    path.parent.mkdir(exist_ok=True)
    path.write_text("new\n", encoding="utf-8")
    paths.append(f"additions/n{index:04d}.txt")
repo = GitRepository(large)
repo.stage_paths(paths, large)
assert repo.staged_paths(large) == sorted(paths)
print(json.dumps({"mixed": "PASS", "ignoredAddition": "REJECTED", "largePathCount": len(paths)}, sort_keys=True))
PY_STAGING

# PATCH_TOOLKIT_ACCEPT_QUALIFICATION_COMPATIBILITY_REGRESSION_V1
python3 - "${PROJECT_ROOT}/.cocondo/tooling/cocondo-toolkit.pyz" "${WORK_ROOT}/qualification-commit" <<'PY_ACCEPT_QUALIFICATION'
from pathlib import Path
import subprocess
import sys
import zipfile

runtime=Path(sys.argv[1])
root=Path(sys.argv[2])
member="cocondo_toolkit/gitops.py"
bad='self.run(["show", "--check", "--oneline", "--no-patch", commit], cwd=cwd)'
good='self.run(["show", "--check", "--oneline", commit], cwd=cwd)'
with zipfile.ZipFile(runtime) as archive:
    source=archive.read(member).decode("utf-8")
assert bad not in source
assert source.count(good) == 1
root.mkdir(parents=True)
subprocess.run(["git","init","-q","-b","main"],cwd=root,check=True)
subprocess.run(["git","config","user.name","Qualification Fixture"],cwd=root,check=True)
subprocess.run(["git","config","user.email","qualification@example.invalid"],cwd=root,check=True)
(root/"value.txt").write_text("value\n",encoding="utf-8")
subprocess.run(["git","add","value.txt"],cwd=root,check=True)
subprocess.run(["git","commit","-qm","qualification fixture"],cwd=root,check=True)
commit=subprocess.run(["git","rev-parse","HEAD"],cwd=root,check=True,text=True,stdout=subprocess.PIPE).stdout.strip()
subprocess.run(["git","show","--check","--oneline",commit],cwd=root,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
print("PATCH_TOOLKIT_ACCEPT_QUALIFICATION_COMPATIBILITY=PASS")
PY_ACCEPT_QUALIFICATION

# PATCH_TOOLKIT_CUTOVER_HISTORY_ISOLATION_REGRESSION_V1
cp "${PROJECT_ROOT}/.cocondo/tooling/project.env" "${FIXTURE}/.cocondo/tooling/project.env"
python3 - "${FIXTURE}/contracts/governance/tooling/patch-toolkit-activation-contract.json" <<'PY_CUTOVER_HISTORY'
from pathlib import Path
import json
import sys

path=Path(sys.argv[1])
data=json.loads(path.read_text(encoding="utf-8"))
history=data["codexCutoverFoundationAcceptance"]
assert history["toolingVersion"] == "0.13.0"
history["toolingVersion"] = "0.14.0"
path.write_text(json.dumps(data,indent=2)+"\n",encoding="utf-8")
PY_CUTOVER_HISTORY

if python3 "${FIXTURE}/bin/patch-toolkit-activation.py" \
  --root "${FIXTURE}" \
  --check \
  --out "${WORK_ROOT}/historical-cutover-negative.json" \
  >/dev/null 2>&1
then
  echo "[ERROR] Activation check accepted drift in immutable 000203 cutover acceptance" >&2
  exit 1
fi

python3 - "${WORK_ROOT}/historical-cutover-negative.json" <<'PY_CUTOVER_RESULT'
import json
import sys

data=json.load(open(sys.argv[1],encoding="utf-8"))
matches=[
    item for item in data.get("findings",[])
    if item.get("code") == "CODEX_CUTOVER_FOUNDATION_EVIDENCE_MISMATCH"
    and item.get("key") == "toolingVersion"
    and item.get("expected") == "0.14.0"
    and item.get("actual") == "0.13.0"
]
assert len(matches) == 1, data.get("findings")
PY_CUTOVER_RESULT

# PATCH_TOOLKIT_PYTHON310_RUNTIME_COMPATIBILITY_REGRESSION_V1
python3 - "${PROJECT_ROOT}/.cocondo/tooling/cocondo-toolkit.pyz" "${PROJECT_ROOT}/bin/cocondo-toolkit-launcher.sh" <<'PY_PYTHON_RUNTIME'
import sys,zipfile
from pathlib import Path
runtime=Path(sys.argv[1]); launcher=Path(sys.argv[2]).read_text(encoding='utf-8')
assert 'PYTHON_MIN_MAJOR=3' in launcher and 'PYTHON_MIN_MINOR=10' in launcher, launcher
assert 'exec "${PYTHON_BIN}" "${RUNTIME}" "${TOOL}" "$@"' in launcher, launcher
failures=[]
with zipfile.ZipFile(runtime) as archive:
    source=archive.read('cocondo_toolkit/patching.py').decode('utf-8')
    assert source.count('artifact.split(":")') == 0, source
    assert source.count("artifact.split(':')") == 2, source
    for info in archive.infolist():
        if info.is_dir() or not info.filename.endswith('.py'):
            continue
        text=archive.read(info).decode('utf-8')
        try:
            compile(text,info.filename,'exec')
        except SyntaxError as exc:
            failures.append((info.filename,exc.lineno,exc.msg))
assert not failures, failures
print(f'PATCH_TOOLKIT_PYTHON_RUNTIME_COMPILE=PASS python={sys.version_info.major}.{sys.version_info.minor}')
PY_PYTHON_RUNTIME

PY_WORKSPACE_ROOT="${WORK_ROOT}/python-runtime-workspace"
PY_WORKSPACE_BASE="${PY_WORKSPACE_ROOT}/base"
PY_WORKSPACE_CANDIDATE="${PY_WORKSPACE_ROOT}/candidate"
rm -rf "${PY_WORKSPACE_ROOT}"
mkdir -p "${PY_WORKSPACE_BASE}/bin" "${PY_WORKSPACE_BASE}/.cocondo"
cp "${PROJECT_ROOT}/bin/cpatch" "${PROJECT_ROOT}/bin/cocondo-toolkit-launcher.sh" "${PY_WORKSPACE_BASE}/bin/"
cp -a "${PROJECT_ROOT}/.cocondo/tooling" "${PY_WORKSPACE_BASE}/.cocondo/tooling"
git -C "${PY_WORKSPACE_BASE}" init -q -b main
git -C "${PY_WORKSPACE_BASE}" config user.name "Toolkit Python Runtime Fixture"
git -C "${PY_WORKSPACE_BASE}" config user.email "toolkit-python-runtime@example.invalid"
git -C "${PY_WORKSPACE_BASE}" add bin .cocondo/tooling
git -C "${PY_WORKSPACE_BASE}" commit -qm "fixture baseline"
git -C "${PY_WORKSPACE_BASE}" worktree add -q -b change/python-runtime-smoke "${PY_WORKSPACE_CANDIDATE}" main
(
  cd "${PY_WORKSPACE_CANDIDATE}"
  ./bin/cpatch workspace init --name python-runtime-smoke --scope tooling --format json >"${PY_WORKSPACE_ROOT}/workspace-init.json"
)
python3 - "${PY_WORKSPACE_ROOT}/workspace-init.json" <<'PY_WORKSPACE_RESULT'
import json,sys
v=json.load(open(sys.argv[1],encoding='utf-8'))
assert isinstance(v,dict) and v,v
print('PATCH_TOOLKIT_PYTHON_RUNTIME_WORKSPACE_JSON=PASS')
PY_WORKSPACE_RESULT
test -z "$(git -C "${PY_WORKSPACE_CANDIDATE}" status --porcelain=v1 --untracked-files=all)"
printf '%s\n' 'PATCH_TOOLKIT_PYTHON_RUNTIME_WORKSPACE=PASS'
git -C "${PY_WORKSPACE_BASE}" worktree remove "${PY_WORKSPACE_CANDIDATE}"

echo "PATCH_TOOLKIT_ACTIVATION_IT=PASS"
