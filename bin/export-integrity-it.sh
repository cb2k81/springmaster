#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
WORK_ROOT="${PROJECT_ROOT}/build/export-integrity-it"
RUN_DIR="${WORK_ROOT}/$(date +%Y%m%d_%H%M%S)_$$"
SOURCE_ROOT="${RUN_DIR}/source"
VALID_ZIP="${RUN_DIR}/valid-export.zip"
INVALID_ZIP="${RUN_DIR}/invalid-export.zip"
RUNTIME_PATH_ZIP="${RUN_DIR}/runtime-path-export.zip"
INVALID_EVIDENCE_ZIP="${RUN_DIR}/invalid-evidence-export.zip"
DELETED_EVIDENCE_ZIP="${RUN_DIR}/deleted-evidence-export.zip"
REAL_EXPORT=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --export)
      [[ $# -ge 2 ]] || { echo "ERROR: --export requires a ZIP path" >&2; exit 2; }
      REAL_EXPORT="$2"
      shift 2
      ;;
    -h|--help|help)
      echo "Usage: ./bin/export-integrity-it.sh [--export <full-export.zip>]"
      exit 0
      ;;
    *)
      echo "ERROR: unknown option $1" >&2
      exit 2
      ;;
  esac
done

mkdir -p "${SOURCE_ROOT}/patches/logs/validation"
printf 'fixture\n' > "${SOURCE_ROOT}/a.txt"
printf 'mutable\n' > "${SOURCE_ROOT}/patches/logs/validation/run.log"

python3 - "${SOURCE_ROOT}" "${VALID_ZIP}" "${INVALID_ZIP}" "${RUNTIME_PATH_ZIP}" "${INVALID_EVIDENCE_ZIP}" "${DELETED_EVIDENCE_ZIP}" <<'PY'
import hashlib
import json
import sys
import zipfile
from pathlib import Path

source_root = Path(sys.argv[1])
valid_zip = Path(sys.argv[2])
invalid_zip = Path(sys.argv[3])
runtime_path_zip = Path(sys.argv[4])
invalid_evidence_zip = Path(sys.argv[5])
deleted_evidence_zip = Path(sys.argv[6])
data = (source_root / "a.txt").read_bytes()
entry = {"path": "a.txt", "sizeBytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
entries = [entry]
manifest_digest = hashlib.sha256(
    json.dumps(entries, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
).hexdigest()
source_evidence = {
    "status": "PRIOR_GATES_PASSED",
    "fixture": True,
    "changedPaths": ["a.txt"],
}
source_evidence_digest = hashlib.sha256(
    json.dumps(source_evidence, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
).hexdigest()
evidence = {
    "schemaVersion": "springmaster.export-closure-evidence.v1",
    "exportStatus": "COMPLETE",
    "generatedAt": "2026-07-14T00:00:00Z",
    "sourceEvidenceSha256": source_evidence_digest,
    "sourceEvidence": source_evidence,
}
meta = {
    "exportFormatVersion": 2,
    "exportStatus": "COMPLETE",
    "sourceHashPolicy": "sha256-raw-repository-bytes",
    "profile": "full",
    "outputFile": "fixture_export_full.txt",
    "fileCount": 1,
    "includedFiles": ["a.txt"],
    "fileManifest": entries,
    "fileManifestSha256": manifest_digest,
    "closureEvidenceFile": "closure-evidence.json",
}

def write(path, meta_payload, evidence_payload=evidence):
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("fixture_export_full/fixture_export_full.txt", "fixture export\n")
        archive.writestr(
            "fixture_export_full/fixture_export_full.meta.json",
            json.dumps(meta_payload, indent=2) + "\n",
        )
        archive.writestr(
            "fixture_export_full/closure-evidence.json",
            json.dumps(evidence_payload, indent=2) + "\n",
        )

write(valid_zip, meta)
invalid = json.loads(json.dumps(meta))
invalid["fileManifest"][0]["sha256"] = "0" * 64
write(invalid_zip, invalid)
runtime_data = (source_root / "patches/logs/validation/run.log").read_bytes()
runtime_entry = {
    "path": "patches/logs/validation/run.log",
    "sizeBytes": len(runtime_data),
    "sha256": hashlib.sha256(runtime_data).hexdigest(),
}
runtime_meta = json.loads(json.dumps(meta))
runtime_meta["includedFiles"] = [runtime_entry["path"]]
runtime_meta["fileManifest"] = [runtime_entry]
runtime_meta["fileManifestSha256"] = hashlib.sha256(
    json.dumps([runtime_entry], ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
).hexdigest()
write(runtime_path_zip, runtime_meta)

invalid_source_evidence = {
    "status": "PRIOR_GATES_PASSED",
    "fixture": True,
    "changedPaths": ["typo.txt"],
}
invalid_evidence = dict(evidence)
invalid_evidence["sourceEvidence"] = invalid_source_evidence
invalid_evidence["sourceEvidenceSha256"] = hashlib.sha256(
    json.dumps(
        invalid_source_evidence,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
).hexdigest()
write(invalid_evidence_zip, meta, invalid_evidence)

deleted_source_evidence = {
    "status": "PRIOR_GATES_PASSED",
    "fixture": True,
    "changedPaths": ["a.txt", "removed.txt"],
    "deletedPaths": ["removed.txt"],
}
deleted_evidence = dict(evidence)
deleted_evidence["sourceEvidence"] = deleted_source_evidence
deleted_evidence["sourceEvidenceSha256"] = hashlib.sha256(
    json.dumps(
        deleted_source_evidence,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
).hexdigest()
write(deleted_evidence_zip, meta, deleted_evidence)
PY

python3 "${SCRIPT_DIR}/export-integrity-check.py" \
  "${VALID_ZIP}" --source-root "${SOURCE_ROOT}" --require-evidence \
  > "${RUN_DIR}/valid.log" 2>&1

if python3 "${SCRIPT_DIR}/export-integrity-check.py" \
  "${INVALID_ZIP}" --source-root "${SOURCE_ROOT}" --require-evidence \
  > "${RUN_DIR}/invalid.log" 2>&1; then
  echo "ERROR: invalid export fixture unexpectedly passed" >&2
  exit 1
fi
grep -Eq 'source mismatch|fileManifestSha256 mismatch' "${RUN_DIR}/invalid.log"

if python3 "${SCRIPT_DIR}/export-integrity-check.py" \
  "${RUNTIME_PATH_ZIP}" --source-root "${SOURCE_ROOT}" --require-evidence \
  > "${RUN_DIR}/runtime-path.log" 2>&1; then
  echo "ERROR: mutable validation-log fixture unexpectedly passed" >&2
  exit 1
fi
grep -q 'mutable operational path is forbidden' "${RUN_DIR}/runtime-path.log"

if python3 "${SCRIPT_DIR}/export-integrity-check.py" \
  "${INVALID_EVIDENCE_ZIP}" --source-root "${SOURCE_ROOT}" --require-evidence \
  > "${RUN_DIR}/invalid-evidence.log" 2>&1; then
  echo "ERROR: invalid changedPaths evidence fixture unexpectedly passed" >&2
  exit 1
fi
grep -q 'changedPaths entry is neither present in the final manifest nor declared deleted' \
  "${RUN_DIR}/invalid-evidence.log"

python3 "${SCRIPT_DIR}/export-integrity-check.py" \
  "${DELETED_EVIDENCE_ZIP}" --source-root "${SOURCE_ROOT}" --require-evidence \
  > "${RUN_DIR}/deleted-evidence.log" 2>&1

if [[ -n "${REAL_EXPORT}" ]]; then
  if [[ "${REAL_EXPORT}" != /* ]]; then
    REAL_EXPORT="${PROJECT_ROOT}/${REAL_EXPORT}"
  fi
  python3 "${SCRIPT_DIR}/export-integrity-check.py" \
    "${REAL_EXPORT}" --source-root "${PROJECT_ROOT}" \
    > "${RUN_DIR}/real-export.log" 2>&1
fi

echo "EXPORT_INTEGRITY_IT=PASS"
echo "LOG_DIR=${RUN_DIR}"
