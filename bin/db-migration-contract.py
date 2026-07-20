#!/usr/bin/env python3
import argparse
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

SCHEMA = "springmaster.database-migration-contract.v1"


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def parse_xml(path: Path):
    try:
        return ET.parse(path).getroot(), None
    except (ET.ParseError, OSError) as exc:
        return None, str(exc)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root")
    parser.add_argument("--contract", default="contracts/database/migration-contract.json")
    parser.add_argument("--out", default="target/db-migration-contract-report.json")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    root = Path(args.root).resolve() if args.root else Path(__file__).resolve().parents[1]
    contract = json.loads((root / args.contract).read_text(encoding="utf-8"))
    findings: list[dict[str, object]] = []
    if contract.get("schema") != SCHEMA:
        findings.append({"code": "CONTRACT_SCHEMA_INVALID", "actual": contract.get("schema")})
    master_rel = contract.get("master")
    changes_rel = contract.get("changesDirectory")
    master = root / str(master_rel)
    changes = root / str(changes_rel)
    file_pattern = re.compile(str(contract.get("filePattern", "")))
    id_pattern = re.compile(str(contract.get("changeSetIdPattern", "")))
    author_pattern = re.compile(str(contract.get("requiredAuthorPattern", "")))
    if not master.is_file():
        findings.append({"code": "MASTER_CHANGELOG_MISSING", "path": master_rel})
    if not changes.is_dir():
        findings.append({"code": "CHANGES_DIRECTORY_MISSING", "path": changes_rel})
    included: list[str] = []
    if master.is_file():
        master_root, error = parse_xml(master)
        if error:
            findings.append({"code": "MASTER_XML_INVALID", "detail": error})
        else:
            for child in master_root:
                if local_name(child.tag) == "include":
                    file_value = child.attrib.get("file", "")
                    included.append(file_value)
            if included != sorted(included):
                findings.append({"code": "MASTER_INCLUDE_ORDER_INVALID", "includes": included})
    files = sorted(changes.glob("*.xml")) if changes.is_dir() else []
    expected_includes = [f"db/changelog/changes/{path.name}" for path in files]
    for path in files:
        if not file_pattern.fullmatch(path.name):
            findings.append({"code": "CHANGELOG_FILENAME_INVALID", "path": path.relative_to(root).as_posix()})
    for value in sorted(set(expected_includes) - set(included)):
        findings.append({"code": "CHANGELOG_NOT_INCLUDED", "path": value})
    for value in sorted(set(included) - set(expected_includes)):
        findings.append({"code": "INCLUDE_TARGET_MISSING", "path": value})
    seen: set[tuple[str, str]] = set()
    destructive = set(contract.get("destructiveElementsRequireRollback", []))
    change_set_count = 0
    for path in files:
        xml_root, error = parse_xml(path)
        if error:
            findings.append({"code": "CHANGELOG_XML_INVALID", "path": path.relative_to(root).as_posix(), "detail": error})
            continue
        for element in xml_root.iter():
            if local_name(element.tag) != "changeSet":
                continue
            change_set_count += 1
            change_id = element.attrib.get("id", "")
            author = element.attrib.get("author", "")
            identity = (change_id, author)
            if not id_pattern.fullmatch(change_id):
                findings.append({"code": "CHANGESET_ID_INVALID", "path": path.relative_to(root).as_posix(), "id": change_id})
            if not author_pattern.fullmatch(author):
                findings.append({"code": "CHANGESET_AUTHOR_INVALID", "path": path.relative_to(root).as_posix(), "author": author})
            if identity in seen:
                findings.append({"code": "CHANGESET_IDENTITY_DUPLICATE", "id": change_id, "author": author})
            seen.add(identity)
            if contract.get("forbidRunAlways") and element.attrib.get("runAlways", "false").lower() == "true":
                findings.append({"code": "RUN_ALWAYS_FORBIDDEN", "id": change_id})
            if contract.get("forbidRunOnChange") and element.attrib.get("runOnChange", "false").lower() == "true":
                findings.append({"code": "RUN_ON_CHANGE_FORBIDDEN", "id": change_id})
            child_names = {local_name(child.tag) for child in element}
            used_destructive = sorted(child_names & destructive)
            if used_destructive and "rollback" not in child_names:
                findings.append({"code": "DESTRUCTIVE_ROLLBACK_MISSING", "id": change_id, "elements": used_destructive})
    if not files:
        findings.append({"code": "NO_CHANGELOG_FILES"})
    if not change_set_count:
        findings.append({"code": "NO_CHANGESETS"})
    report = {
        "schema": "springmaster.database-migration-contract-report.v1",
        "status": "PASS" if not findings else "FAIL",
        "master": master_rel,
        "includedFileCount": len(included),
        "changeSetCount": change_set_count,
        "findings": findings,
    }
    out = Path(args.out)
    if not out.is_absolute():
        out = root / out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"DB_MIGRATION_CONTRACT={report['status']}")
    print(f"REPORT={out}")
    return 1 if args.check and findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
