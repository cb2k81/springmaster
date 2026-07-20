#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path

REQUIRED = ("documentType", "status", "scope", "owner", "validFrom", "supersedes")
ALLOWED_TYPES = {"governance", "adr", "concept", "guide", "requirements", "plan", "technical-debt", "sprint-summary"}


def front_matter(path: Path) -> dict[str, str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0] != "---":
        return {}
    result: dict[str, str] = {}
    for line in lines[1:]:
        if line == "---":
            return result
        if ":" in line:
            key, value = line.split(":", 1)
            result[key.strip()] = value.strip()
    return {}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=None)
    parser.add_argument("--out", default="target/documentation-gate-report.json")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    root = Path(args.root).resolve() if args.root else Path(__file__).resolve().parents[1]
    docs = root / "PROJECT_DOCS"
    baseline_path = docs / "TOOLING/documentation-transition-baseline.json"
    index_path = docs / "index.md"
    baseline = set(json.loads(baseline_path.read_text(encoding="utf-8"))["paths"])
    current = sorted(p.relative_to(root).as_posix() for p in docs.rglob("*.md"))
    indexed = set(re.findall(r"`(PROJECT_DOCS/[^`]+\.md)`", index_path.read_text(encoding="utf-8")))
    findings = []
    legacy = []
    for rel in current:
        metadata = front_matter(root / rel)
        missing = [key for key in REQUIRED if not metadata.get(key)]
        invalid_type = metadata.get("documentType") not in ALLOWED_TYPES if metadata else True
        if rel in baseline:
            if missing or invalid_type:
                legacy.append({"path": rel, "missing": missing, "invalidType": invalid_type})
        elif missing or invalid_type:
            findings.append({"code": "NEW_DOCUMENT_METADATA_INVALID", "path": rel, "missing": missing, "invalidType": invalid_type})
    expected_index = set(current) - {"PROJECT_DOCS/index.md"}
    for rel in sorted(expected_index - indexed):
        findings.append({"code": "INDEX_ENTRY_MISSING", "path": rel})
    for rel in sorted(indexed - expected_index):
        findings.append({"code": "INDEX_ENTRY_STALE", "path": rel})
    report = {
        "schema": "springmaster.documentation-gate-report.v1",
        "status": "PASS" if not findings else "FAIL",
        "mode": "transition-report-only-for-legacy",
        "documentCount": len(current),
        "baselineCount": len(baseline),
        "legacyMetadataFindingCount": len(legacy),
        "blockingFindingCount": len(findings),
        "blockingFindings": findings,
        "legacyFindings": legacy,
    }
    out = Path(args.out)
    if not out.is_absolute():
        out = root / out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"DOCUMENTATION_GATE={report['status']}")
    print(f"REPORT={out}")
    return 1 if args.check and findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
