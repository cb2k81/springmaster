#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path, PurePosixPath


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_manifest_digest(entries: list[dict]) -> str:
    encoded = json.dumps(entries, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return sha256_bytes(encoded)


def validate_checksum_sidecar(export_zip: Path, allow_missing: bool) -> tuple[Path | None, str]:
    checksum_file = Path(str(export_zip) + ".sha256")
    if not checksum_file.is_file():
        if allow_missing:
            return None, sha256_file(export_zip)
        fail(f"checksum sidecar not found: {checksum_file}")
    try:
        raw = checksum_file.read_text(encoding="utf-8")
    except Exception as exc:
        fail(f"cannot read checksum sidecar {checksum_file}: {exc}")
    match = re.fullmatch(r"([0-9a-f]{64})  ([^/\\\r\n]+)\n?", raw)
    if not match:
        fail(f"invalid checksum sidecar format: {checksum_file}")
    expected, filename = match.groups()
    if filename != export_zip.name:
        fail(
            f"checksum sidecar filename mismatch: expected {export_zip.name!r}, found {filename!r}"
        )
    actual = sha256_file(export_zip)
    if actual != expected:
        fail(
            f"checksum mismatch for {export_zip}: expected {expected}, actual {actual}"
        )
    return checksum_file, actual


def read_json(archive: zipfile.ZipFile, member: str) -> dict:
    try:
        value = json.loads(archive.read(member).decode("utf-8"))
    except Exception as exc:
        fail(f"cannot read JSON member {member}: {exc}")
    if not isinstance(value, dict):
        fail(f"JSON member {member} must contain an object")
    return value


def validate_meta(
    archive: zipfile.ZipFile,
    meta_member: str,
    source_root: Path | None,
    require_evidence: bool,
) -> tuple[int, str | None, set[str]]:
    meta = read_json(archive, meta_member)
    if meta.get("exportFormatVersion") != 2:
        fail(f"{meta_member}: exportFormatVersion must be 2")
    if meta.get("exportStatus") != "COMPLETE":
        fail(f"{meta_member}: exportStatus must be COMPLETE")
    if meta.get("sourceHashPolicy") != "sha256-raw-repository-bytes":
        fail(f"{meta_member}: unsupported sourceHashPolicy")

    included = meta.get("includedFiles")
    entries = meta.get("fileManifest")
    if not isinstance(included, list) or not all(isinstance(item, str) for item in included):
        fail(f"{meta_member}: includedFiles must be a list of paths")
    if not isinstance(entries, list) or not all(isinstance(item, dict) for item in entries):
        fail(f"{meta_member}: fileManifest must be a list of objects")

    paths: list[str] = []
    for entry in entries:
        path = entry.get("path")
        size = entry.get("sizeBytes")
        digest = entry.get("sha256")
        if not isinstance(path, str) or not path or path.startswith("/") or ".." in PurePosixPath(path).parts:
            fail(f"{meta_member}: invalid fileManifest path {path!r}")
        if path == "patches/logs/validation" or path.startswith("patches/logs/validation/"):
            fail(f"{meta_member}: mutable operational path is forbidden in export manifest: {path}")
        if not isinstance(size, int) or size < 0:
            fail(f"{meta_member}: invalid sizeBytes for {path}")
        if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
            fail(f"{meta_member}: invalid sha256 for {path}")
        paths.append(path)
        if source_root is not None:
            source = source_root / path
            if not source.is_file():
                fail(f"{meta_member}: source file missing: {path}")
            actual_size = source.stat().st_size
            actual_digest = sha256_file(source)
            if actual_size != size or actual_digest != digest:
                fail(
                    f"{meta_member}: source mismatch for {path}: "
                    f"expected size={size} sha256={digest}, actual size={actual_size} sha256={actual_digest}"
                )

    if paths != included:
        fail(f"{meta_member}: includedFiles and fileManifest path order/content differ")
    if len(paths) != len(set(paths)):
        fail(f"{meta_member}: duplicate fileManifest paths")
    if meta.get("fileCount") != len(entries):
        fail(f"{meta_member}: fileCount does not match fileManifest")
    expected_manifest_digest = canonical_manifest_digest(entries)
    if meta.get("fileManifestSha256") != expected_manifest_digest:
        fail(f"{meta_member}: fileManifestSha256 mismatch")

    output_file = meta.get("outputFile")
    if not isinstance(output_file, str) or not output_file or PurePosixPath(output_file).name != output_file:
        fail(f"{meta_member}: outputFile must be a plain member filename")
    text_member = str(PurePosixPath(meta_member).parent / output_file)
    if text_member not in archive.namelist():
        fail(f"{meta_member}: text export member missing: {text_member}")

    evidence_file = meta.get("closureEvidenceFile")
    if evidence_file is not None:
        if not isinstance(evidence_file, str) or not evidence_file or PurePosixPath(evidence_file).name != evidence_file:
            fail(f"{meta_member}: closureEvidenceFile must be a plain member filename or null")
    if require_evidence and not evidence_file:
        fail(f"{meta_member}: closure evidence is required")
    return len(entries), evidence_file, set(paths)


def validate_evidence(
    archive: zipfile.ZipFile,
    meta_member: str,
    evidence_file: str,
    manifest_paths: set[str],
) -> str:
    evidence_member = str(PurePosixPath(meta_member).parent / evidence_file)
    if evidence_member not in archive.namelist():
        fail(f"{meta_member}: closure evidence member missing: {evidence_member}")
    evidence = read_json(archive, evidence_member)
    if evidence.get("schemaVersion") != "springmaster.export-closure-evidence.v1":
        fail(f"{evidence_member}: invalid schemaVersion")
    if evidence.get("exportStatus") != "COMPLETE":
        fail(f"{evidence_member}: exportStatus must be COMPLETE")
    source_digest = evidence.get("sourceEvidenceSha256")
    source_evidence = evidence.get("sourceEvidence")
    if not isinstance(source_digest, str) or not re.fullmatch(r"[0-9a-f]{64}", source_digest):
        fail(f"{evidence_member}: invalid sourceEvidenceSha256")
    canonical_source = json.dumps(
        source_evidence,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    if sha256_bytes(canonical_source) != source_digest:
        fail(f"{evidence_member}: source evidence digest mismatch")

    if not isinstance(source_evidence, dict):
        fail(f"{evidence_member}: sourceEvidence must be an object")

    changed_paths = source_evidence.get("changedPaths")
    deleted_paths = source_evidence.get("deletedPaths", [])
    if changed_paths is not None:
        if not isinstance(changed_paths, list) or not all(isinstance(item, str) for item in changed_paths):
            fail(f"{evidence_member}: changedPaths must be a list of paths")
        if len(changed_paths) != len(set(changed_paths)):
            fail(f"{evidence_member}: changedPaths contains duplicates")
        if not isinstance(deleted_paths, list) or not all(isinstance(item, str) for item in deleted_paths):
            fail(f"{evidence_member}: deletedPaths must be a list of paths")
        if len(deleted_paths) != len(set(deleted_paths)):
            fail(f"{evidence_member}: deletedPaths contains duplicates")
        deleted_set = set(deleted_paths)
        if not deleted_set.issubset(set(changed_paths)):
            fail(f"{evidence_member}: deletedPaths must be a subset of changedPaths")
        for path in changed_paths:
            pure = PurePosixPath(path)
            if not path or path.startswith("/") or ".." in pure.parts:
                fail(f"{evidence_member}: invalid changedPaths entry: {path!r}")
            if path not in manifest_paths and path not in deleted_set:
                fail(
                    f"{evidence_member}: changedPaths entry is neither present in the final manifest "
                    f"nor declared deleted: {path}"
                )
    elif deleted_paths:
        fail(f"{evidence_member}: deletedPaths requires changedPaths")

    return evidence_member


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify Springmaster full/split ZIP export integrity.")
    parser.add_argument("export_zip", type=Path)
    parser.add_argument("--source-root", type=Path)
    parser.add_argument("--require-evidence", action="store_true")
    parser.add_argument(
        "--allow-missing-checksum",
        action="store_true",
        help="allow verification of legacy ZIP exports that predate the checksum sidecar contract",
    )
    args = parser.parse_args()

    export_zip = args.export_zip.expanduser().resolve()
    if not export_zip.is_file():
        fail(f"export ZIP not found: {export_zip}")
    source_root = args.source_root.expanduser().resolve() if args.source_root else None
    checksum_file, zip_sha256 = validate_checksum_sidecar(
        export_zip,
        args.allow_missing_checksum,
    )

    try:
        with zipfile.ZipFile(export_zip, "r") as archive:
            bad = archive.testzip()
            if bad:
                fail(f"ZIP CRC failure in {bad}")
            names = archive.namelist()
            if len(names) != len(set(names)):
                fail("duplicate ZIP members are forbidden")
            meta_members = sorted(name for name in names if name.endswith(".meta.json"))
            if not meta_members:
                fail("no export metadata member found")
            total_files = 0
            evidence_members: set[str] = set()
            for meta_member in meta_members:
                file_count, evidence_file, manifest_paths = validate_meta(
                    archive,
                    meta_member,
                    source_root,
                    args.require_evidence,
                )
                total_files += file_count
                if evidence_file:
                    evidence_members.add(
                        validate_evidence(archive, meta_member, evidence_file, manifest_paths)
                    )
    except zipfile.BadZipFile as exc:
        fail(f"invalid ZIP: {exc}")

    print("EXPORT_INTEGRITY=PASS")
    print(f"EXPORT_ZIP={export_zip}")
    print(f"EXPORT_SHA256={zip_sha256}")
    print(f"CHECKSUM_FILE={checksum_file or '-'}")
    print(f"META_FILES={len(meta_members)}")
    print(f"MANIFEST_ENTRIES={total_files}")
    print(f"CLOSURE_EVIDENCE_FILES={len(evidence_members)}")


if __name__ == "__main__":
    main()
