#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
RUN_DIR="${PROJECT_ROOT}/build/project-directory-gate-it/$(date +%Y%m%d_%H%M%S)_$$"
mkdir -p "${RUN_DIR}"

python3 - "${PROJECT_ROOT}" "${RUN_DIR}" <<'PY'
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

project_root = Path(sys.argv[1])
run_dir = Path(sys.argv[2])
expectations = json.loads((project_root / "src/test/resources/tooling/project-directory-gate-v1/expected-cases.json").read_text(encoding="utf-8"))


def digest(entries):
    raw = json.dumps(entries, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def write_json(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def base_fixture(case_id: str) -> Path:
    root = run_dir / case_id
    for directory in (
        "PROJECT_DOCS",
        "bin",
        "contracts/governance/project-structure",
        "patches",
        "platform/versions",
        "src/main/java/example",
        "src/test/resources",
    ):
        (root / directory).mkdir(parents=True, exist_ok=True)
    for name, content in {
        ".env.example": "APP_NAME=fixture\n",
        ".gitignore": "target/\nbuild/\ntmp/\nexports/\npatches/archives/\npatches/runtime/\npatches/logs/accept/\npatches/logs/validation/\npatches/work/\nplatform/update/generated/\nplatform/update/manifests/\n.env\n.env.*\n!.env.example\n.idea/\n*.iml\n__pycache__/\n*.pyc\n",
        "AGENTS.md": "# Fixture Agents\n",
        "README.md": "# Fixture\n",
        "export.config.json": '{"project": "fixture"}\n',
        "pom.xml": "<project/>\n",
        "PROJECT_DOCS/README.md": "# Project Docs\n",
        "bin/tool.sh": "#!/usr/bin/env bash\nset -euo pipefail\n",
        "contracts/fixture.json": '{"contract": "fixture"}\n',
        "patches/bootstrap.json": '{"patch": "fixture"}\n',
        "platform/versions/platform.env": "PLATFORM_NAME=fixture\n",
        "src/main/java/example/App.java": "package example; final class App {}\n",
        "src/test/resources/fixture.json": '{"test": "fixture"}\n',
    }.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    shutil.copy2(project_root / "bin/project-directory-gate.py", root / "bin/project-directory-gate.py")
    shutil.copy2(
        project_root / "contracts/governance/project-structure/project-directory-contract.json",
        root / "contracts/governance/project-structure/project-directory-contract.json",
    )
    shutil.copy2(
        project_root / "contracts/governance/project-structure/directory-transition-baseline.json",
        root / "contracts/governance/project-structure/directory-transition-baseline.json",
    )
    return root


def init_git(root: Path):
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    subprocess.run(["git", "-C", str(root), "config", "user.email", "fixture@example.invalid"], check=True)
    subprocess.run(["git", "-C", str(root), "config", "user.name", "Directory Gate Fixture"], check=True)
    subprocess.run(["git", "-C", str(root), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(root), "commit", "-qm", "fixture baseline"], check=True)


def prepare_springmaster_fixture(root: Path):
    (root / "docs").mkdir(parents=True, exist_ok=True)
    (root / "patches/bootstrap.json").unlink(missing_ok=True)
    for name, content in {
        ".cocondo/process.env": "CPROCESS_CONFIG_VERSION=2\n",
        ".cocondo/tooling/project.env": "CPATCH_CONFIG_VERSION=1\n",
        ".cocondo/tooling/scopes/tooling.env": "CPATCH_SCOPE_ID=tooling\n",
        ".cocondo/tooling/validators/full.env": "CPATCH_VALIDATOR_ID=full\n",
        ".cocondo/tooling/tooling.lock.json": "{\"toolingVersion\": \"fixture\"}\n",
        ".cocondo/tooling/cocondo-toolkit.pyz.sha256": "fixture  cocondo-toolkit.pyz\n",
    }.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    (root / ".cocondo/tooling/cocondo-toolkit.pyz").write_bytes(b"fixture-toolkit")
    for name in ("cpatch", "crun", "cartifact", "cmanifest", "cgit-tx", "csource-check", "ctool-doctor"):
        path = root / "bin" / name
        path.write_text(f"#!/usr/bin/env bash\nset -euo pipefail\nprintf '%s\\n' {name!r}\n", encoding="utf-8")
        path.chmod(0o755)
    init_git(root)


def load_contract(root: Path):
    path = root / "contracts/governance/project-structure/project-directory-contract.json"
    return path, json.loads(path.read_text(encoding="utf-8"))


def load_baseline(root: Path):
    path = root / "contracts/governance/project-structure/directory-transition-baseline.json"
    return path, json.loads(path.read_text(encoding="utf-8"))


def sync_baseline(root: Path, entries):
    baseline_path, baseline = load_baseline(root)
    value = digest(entries)
    baseline["entries"] = entries
    baseline["entryCount"] = len(entries)
    baseline["entrySetSha256"] = value
    write_json(baseline_path, baseline)
    contract_path, contract = load_contract(root)
    contract["transitionBaseline"]["entrySetSha256"] = value
    write_json(contract_path, contract)


def prepare(case_id: str):
    root = base_fixture(case_id)
    changed_paths: list[str] = []
    deviations = None
    profile = "generated-project"

    if case_id == "valid-patch-work-runtime":
        (root / "patches/work").mkdir(parents=True, exist_ok=True)
        (root / "patches/work/current-diagnostics.zip").write_bytes(b"fixture")
    elif case_id == "unexpected-root":
        (root / "rogue").mkdir()
        (root / "rogue/file.txt").write_text("rogue\n", encoding="utf-8")
        changed_paths = ["rogue/file.txt"]
    elif case_id == "required-root-deleted":
        (root / "README.md").unlink()
        changed_paths = ["README.md"]
    elif case_id == "wrong-file-type":
        (root / "contracts/bad.yaml").write_text("bad: true\n", encoding="utf-8")
    elif case_id == "technical-file-under-docs":
        (root / "PROJECT_DOCS/new-contract.json").write_text("{}\n", encoding="utf-8")
    elif case_id == "temporary-source-file":
        (root / "src/main/java/example/Service.java.tmp").write_text("temporary\n", encoding="utf-8")
    elif case_id == "backup-artifact":
        (root / "README.md.bak").write_text("backup\n", encoding="utf-8")
    elif case_id == "case-collision":
        (root / "contracts/alpha.json").write_text('{"a": 1}\n', encoding="utf-8")
        (root / "contracts/Alpha.json").write_text('{"a": 2}\n', encoding="utf-8")
    elif case_id == "broken-symlink":
        os.symlink("missing.java", root / "src/main/java/example/Broken.java")
    elif case_id == "external-symlink":
        os.symlink("/etc/passwd", root / "src/main/java/example/External.java")
    elif case_id == "unapproved-duplicate":
        payload = '{"same": true}\n'
        (root / "contracts/a.json").write_text(payload, encoding="utf-8")
        (root / "contracts/b.json").write_text(payload, encoding="utf-8")
        changed_paths = ["contracts/a.json"]
    elif case_id == "approved-derivation":
        payload = '{"same": true}\n'
        (root / "contracts/a.json").write_text(payload, encoding="utf-8")
        (root / "contracts/b.json").write_text(payload, encoding="utf-8")
        contract_path, contract = load_contract(root)
        contract["duplicatePolicy"]["allowedPairs"].append({
            "left": "contracts/a.json",
            "right": "contracts/b.json",
            "kind": "fixture-qualified-derivation",
        })
        write_json(contract_path, contract)
    elif case_id == "baseline-existing-vs-new":
        legacy = root / "PROJECT_DOCS/LEGACY"
        legacy.mkdir()
        (legacy / "existing.md").write_text("# Existing\n", encoding="utf-8")
        (legacy / "new.md").write_text("# New\n", encoding="utf-8")
        contract_path, contract = load_contract(root)
        contract["areas"].insert(0, {
            "id": "fixture-legacy",
            "patterns": ["PROJECT_DOCS/LEGACY/**"],
            "profiles": ["generated-project"],
            "pathClass": "legacy-accepted",
            "sourceKind": "source",
            "commitPolicy": "allowed",
            "allowedSuffixes": [".md"],
            "newPathPolicy": "baseline-only",
        })
        write_json(contract_path, contract)
        entries = [{
            "path": "PROJECT_DOCS/LEGACY/existing.md",
            "findingCodes": ["LEGACY_PATH_PRESENT"],
            "classification": "legacy-accepted",
            "owner": "fixture",
            "reason": "Fixture baseline entry",
        }]
        sync_baseline(root, entries)
    elif case_id == "valid-springmaster-toolkit-layout":
        profile = "springmaster-source"
        prepare_springmaster_fixture(root)
    elif case_id == "ignored-local-artifacts":
        profile = "springmaster-source"
        prepare_springmaster_fixture(root)
        for name, content in {
            ".env": "SECRET=local\n",
            ".idea/workspace.xml": "<workspace/>\n",
            "springmaster.iml": "<module/>\n",
            "bin/__pycache__/fixture.cpython-312.pyc": "local-cache\n",
        }.items():
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
    elif case_id == "tracked-patch-runtime":
        profile = "springmaster-source"
        prepare_springmaster_fixture(root)
        runtime = root / "patches/logs/validation/fixture/result.log"
        runtime.parent.mkdir(parents=True, exist_ok=True)
        runtime.write_text("runtime\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(root), "add", "-f", runtime.relative_to(root).as_posix()], check=True)
        subprocess.run(["git", "-C", str(root), "commit", "-qm", "track forbidden runtime"], check=True)
    elif case_id == "non-executable-extensionless-tool":
        profile = "springmaster-source"
        prepare_springmaster_fixture(root)
        path = root / "bin/non-executable"
        path.write_text("not executable\n", encoding="utf-8")
        path.chmod(0o644)
        subprocess.run(["git", "-C", str(root), "add", path.relative_to(root).as_posix()], check=True)
        subprocess.run(["git", "-C", str(root), "commit", "-qm", "add non executable tool"], check=True)
    elif case_id == "expired-deviation":
        deviations = root / "contracts/deviations.json"
        write_json(deviations, {
            "schemaVersion": "springmaster.managed-project-deviations.v1",
            "deviations": [{
                "path": "PROJECT_DOCS/LOCAL",
                "status": "approved",
                "expiresAt": "2020-01-01",
            }],
        })
    elif case_id == "contract-change-expands-all":
        changed_paths = ["contracts/governance/project-structure/project-directory-contract.json"]
    elif case_id == "invalid-baseline-extension":
        baseline_path, baseline = load_baseline(root)
        baseline["entries"].append({
            "path": "docs/unapproved.md",
            "findingCodes": ["LEGACY_PATH_PRESENT"],
            "classification": "legacy-accepted",
            "owner": "fixture",
            "reason": "Unsealed extension",
        })
        baseline["entryCount"] = len(baseline["entries"])
        baseline["entrySetSha256"] = digest(baseline["entries"])
        write_json(baseline_path, baseline)
    elif case_id == "tool-error-missing-contract":
        (root / "contracts/governance/project-structure/project-directory-contract.json").unlink()

    return root, changed_paths, deviations, profile


for case in expectations["cases"]:
    case_id = case["id"]
    root, changed_paths, deviations, profile = prepare(case_id)
    report = run_dir / f"{case_id}.json"
    mode = case.get("mode", "all")
    command = [
        sys.executable,
        str(root / "bin/project-directory-gate.py"),
        "--root", str(root),
        "--profile", profile,
        "--mode", mode,
        "--out", str(report),
        "--check",
    ]
    for changed in changed_paths:
        command.extend(["--changed-path", changed])
    if deviations is not None:
        command.extend(["--deviations", str(deviations)])
    completed = subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    if completed.returncode != case["expectedExit"]:
        raise SystemExit(f"{case_id}: expected exit {case['expectedExit']}, got {completed.returncode}: {completed.stdout}")
    payload = json.loads(report.read_text(encoding="utf-8"))
    if payload.get("status") != case["expectedStatus"]:
        raise SystemExit(f"{case_id}: expected status {case['expectedStatus']}, got {payload.get('status')}")
    codes = {item.get("code") for item in payload.get("newFindings", [])}
    transition_codes = {item.get("code") for item in payload.get("transitionFindings", [])}
    tool_codes = {item.get("code") for item in payload.get("toolErrors", [])}
    expected_code = case.get("expectedCode")
    if expected_code is not None and expected_code not in codes:
        raise SystemExit(f"{case_id}: expected finding code {expected_code}, got {sorted(codes)}")
    expected_transition = case.get("expectedTransitionCode")
    if expected_transition is not None and expected_transition not in transition_codes:
        raise SystemExit(f"{case_id}: expected transition code {expected_transition}, got {sorted(transition_codes)}")
    expected_tool = case.get("expectedToolErrorCode")
    if expected_tool is not None and expected_tool not in tool_codes:
        raise SystemExit(f"{case_id}: expected tool error {expected_tool}, got {sorted(tool_codes)}")
    if "expectedExpandedToAll" in case and payload.get("expandedToAll") is not case["expectedExpandedToAll"]:
        raise SystemExit(f"{case_id}: expected expandedToAll={case['expectedExpandedToAll']}, got {payload.get('expandedToAll')}")
    expected_ignored_min = case.get("expectedIgnoredPathCountMin")
    if expected_ignored_min is not None and payload.get("summary", {}).get("ignoredPathCount", 0) < expected_ignored_min:
        raise SystemExit(
            f"{case_id}: expected ignoredPathCount >= {expected_ignored_min}, "
            f"got {payload.get('summary', {}).get('ignoredPathCount')}"
        )
    expected_detail = case.get("expectedDetail")
    if expected_detail:
        candidates = [item for item in payload.get("newFindings", []) if item.get("code") == expected_code]
        if not candidates or not any(all(item.get("details", {}).get(k) == v for k, v in expected_detail.items()) for item in candidates):
            raise SystemExit(f"{case_id}: expected details {expected_detail}, got {candidates}")

print("PROJECT_DIRECTORY_GATE_IT=PASS")
print(f"CASES={len(expectations['cases'])}")
print(f"REPORT_DIR={run_dir}")
PY
