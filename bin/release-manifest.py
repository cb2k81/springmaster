#!/usr/bin/env python3
"""Generate a machine-readable Springmaster release qualification manifest."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SEMVER = re.compile(r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$")
REQUIRED_VERSION_KEYS = (
    "PLATFORM_NAME",
    "PLATFORM_VERSION",
    "PLATFORM_CORE_VERSION",
    "PLATFORM_TOOLING_VERSION",
    "PLATFORM_TEMPLATE_VERSION",
    "PLATFORM_DEMO_VERSION",
    "PLATFORM_UPDATE_VERSION",
    "PLATFORM_STATE_PATCH",
)


def fail(message: str) -> "NoReturn":
    print(f"RELEASE_MANIFEST_ERROR: {message}", file=sys.stderr)
    raise SystemExit(2)


def parse_env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            fail(f"invalid version line in {path}: {raw!r}")
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    missing = [key for key in REQUIRED_VERSION_KEYS if not values.get(key)]
    if missing:
        fail("missing version keys: " + ", ".join(missing))
    return values


def git_output(root: Path, *args: str) -> str:
    result = subprocess.run(["git", *args], cwd=root, text=True, capture_output=True)
    if result.returncode != 0:
        fail(result.stderr.strip() or f"git {' '.join(args)} failed")
    return result.stdout.strip()


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--release-version", required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--documentation-gate", choices=("PASS", "SKIPPED", "FAIL"), required=True)
    parser.add_argument("--maven-test", choices=("PASS", "SKIPPED", "FAIL"), required=True)
    parser.add_argument("--tooling-selfcheck", choices=("PASS", "SKIPPED", "FAIL"), required=True)
    parser.add_argument("--export-integrity", choices=("PASS", "SKIPPED", "FAIL"), required=True)
    parser.add_argument("--export-path", default="")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    root = args.root.resolve()
    if not SEMVER.fullmatch(args.release_version):
        fail("--release-version must be numeric SemVer X.Y.Z")
    versions = parse_env(root / "platform/versions/platform.env")
    if versions["PLATFORM_VERSION"].split("-", 1)[0] != args.release_version:
        fail("release version does not match PLATFORM_VERSION numeric prefix")
    dirty = git_output(root, "status", "--porcelain")
    if dirty:
        fail("working tree is not clean")
    commit = git_output(root, "rev-parse", "HEAD")
    tag = f"springmaster-v{args.release_version}"
    checks = {
        "documentationGate": args.documentation_gate,
        "mavenTest": args.maven_test,
        "toolingSelfcheck": args.tooling_selfcheck,
        "exportIntegrity": args.export_integrity,
    }
    status = "QUALIFIED" if all(value == "PASS" for value in checks.values()) else "INCOMPLETE"
    payload = {
        "schemaVersion": "springmaster.release-manifest.v1",
        "status": status,
        "releaseVersion": args.release_version,
        "foundationVersion": versions["PLATFORM_VERSION"],
        "gitCommit": commit,
        "gitTag": tag,
        "components": {
            "core": versions["PLATFORM_CORE_VERSION"],
            "tooling": versions["PLATFORM_TOOLING_VERSION"],
            "template": versions["PLATFORM_TEMPLATE_VERSION"],
            "demo": versions["PLATFORM_DEMO_VERSION"],
            "update": versions["PLATFORM_UPDATE_VERSION"],
        },
        "statePatch": versions["PLATFORM_STATE_PATCH"],
        "contracts": {
            "patchManifest": "springmaster.patch-manifest.v2",
            "releaseManifest": "springmaster.release-manifest.v1",
        },
        "qualification": checks,
        "exportPath": args.export_path or None,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
    }
    output = args.output or root / "build/releases" / args.release_version / "release-manifest.json"
    if not output.is_absolute():
        output = root / output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"RELEASE_QUALIFICATION={status}")
    print(f"RELEASE_VERSION={args.release_version}")
    print(f"GIT_TAG={tag}")
    print(f"MANIFEST={output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
