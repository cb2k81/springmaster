#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

VALIDATION_EXCLUDE = "patches/logs/validation/**"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Synthesize target-safe export configuration for a tooling cutover."
    )
    parser.add_argument("--target-root", required=True, type=Path)
    parser.add_argument("--output-root", required=True, type=Path)
    parser.add_argument("--target-name", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    target_root = args.target_root.resolve()
    output_root = args.output_root.resolve()
    source = target_root / "export.config.json"
    if not source.is_file():
        raise SystemExit(f"target export.config.json missing: {source}")
    try:
        config = json.loads(source.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"cannot read target export.config.json: {exc}") from exc
    if not isinstance(config, dict):
        raise SystemExit("target export.config.json must contain an object")
    project_key = config.get("projectKey")
    if not isinstance(project_key, str) or not project_key.strip():
        raise SystemExit("target export.config.json requires a non-empty projectKey")
    if project_key != args.target_name:
        raise SystemExit(
            f"target projectKey mismatch: expected {args.target_name!r}, got {project_key!r}"
        )
    global_exclude = config.get("globalExclude")
    if not isinstance(global_exclude, list) or not all(
        isinstance(item, str) for item in global_exclude
    ):
        raise SystemExit("target globalExclude must be a list of strings")
    if VALIDATION_EXCLUDE not in global_exclude:
        global_exclude.append(VALIDATION_EXCLUDE)
    if len(global_exclude) != len(set(global_exclude)):
        raise SystemExit("target globalExclude contains duplicate entries")
    destination = output_root / "export.config.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(config, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": "PASS",
                "projectKey": project_key,
                "validationLogExclude": VALIDATION_EXCLUDE,
                "output": str(destination),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
