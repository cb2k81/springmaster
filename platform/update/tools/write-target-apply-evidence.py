#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path

SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Write canonical source evidence for one platform-update target apply."
    )
    parser.add_argument("--patch-zip", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--target-name", required=True)
    parser.add_argument("--generated-profile", required=True)
    parser.add_argument("--accept-profile", required=True)
    parser.add_argument("--full-test", required=True, choices=("True", "False"))
    parser.add_argument("--source-target-git-head", required=True)
    parser.add_argument("--target-root", required=True, type=Path)
    return parser.parse_args()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    args = parse_args()
    patch_zip = args.patch_zip.resolve()
    if not patch_zip.is_file():
        raise SystemExit(f"patch ZIP missing: {patch_zip}")
    with zipfile.ZipFile(patch_zip) as archive:
        try:
            manifest = json.loads(archive.read("manifest.json"))
        except (KeyError, json.JSONDecodeError) as exc:
            raise SystemExit(f"invalid patch manifest: {exc}") from exc
    artifact_id = manifest.get("artifactId")
    patch_id = manifest.get("patchId")
    scope = manifest.get("scope")
    requires = manifest.get("requires") or {}
    expected = (manifest.get("baseline") or {}).get("expectedBeforeSha256")
    if manifest.get("schemaVersion") != "springmaster.patch-manifest.v2":
        raise SystemExit("manifest.schemaVersion is not springmaster.patch-manifest.v2")
    if not isinstance(artifact_id, str) or not artifact_id.startswith("urn:uuid:"):
        raise SystemExit("manifest.artifactId missing or invalid")
    if not isinstance(patch_id, str) or not patch_id:
        raise SystemExit("manifest.patchId missing")
    if manifest.get("id") != patch_id:
        raise SystemExit("manifest.id and manifest.patchId differ")
    if not isinstance(scope, str) or not scope:
        raise SystemExit("manifest.scope missing")
    if requires.get("target") != args.target_name:
        raise SystemExit("manifest target does not match requested target")
    if requires.get("profile") != args.generated_profile:
        raise SystemExit("manifest profile does not match generated profile")
    if not isinstance(expected, dict) or not expected:
        raise SystemExit("manifest baseline.expectedBeforeSha256 missing")
    changed_paths = sorted(expected)
    target_root = args.target_root.resolve()
    state_path = target_root / "platform/update/managed-state.json"
    version_path = target_root / "platform/versions/platform.env"
    if not state_path.is_file() or not version_path.is_file():
        raise SystemExit("managed target state or version file missing after apply")
    managed_state = json.loads(state_path.read_text(encoding="utf-8"))
    required_state = (requires.get("managedState") or {})
    for key in ("schemaVersion", "target", "artifactId", "patchId", "profile", "installedVersions"):
        if managed_state.get(key) != required_state.get(key):
            raise SystemExit(f"applied managed state mismatch for {key}")
    evidence = {
        "schemaVersion": "springmaster.platform-update-target-apply-evidence.v1",
        "status": "PRIOR_GATES_PASSED",
        "target": args.target_name,
        "artifactId": artifact_id,
        "patchId": patch_id,
        "patchSha256": sha256_file(patch_zip),
        "patchScope": scope,
        "generatedProfile": args.generated_profile,
        "acceptProfile": args.accept_profile,
        "fullTest": args.full_test == "True",
        "acceptExport": False,
        "producerArtifactPreflight": "PASS",
        "targetDryRun": "PASS",
        "targetAccept": "SUCCESS",
        "sourceTargetGitHead": args.source_target_git_head,
        "changedPaths": changed_paths,
        "deletedPaths": [],
        "managedState": managed_state,
        "managedStateSha256": sha256_file(state_path),
        "platformVersionStateSha256": sha256_file(version_path),
    }
    if not SHA256_RE.fullmatch(evidence["patchSha256"]):
        raise SystemExit("invalid patch SHA-256")
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(evidence, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
