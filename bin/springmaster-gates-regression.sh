#!/usr/bin/env bash
set -euo pipefail

cd "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

RUN_ID="${1:-000069-regression}"
REPORT_DIR="target/springmaster-gates/${RUN_ID}"
LOG_DIR="target/springmaster-gates-regression"
mkdir -p "${LOG_DIR}"

bash -n ./bin/*.sh ./bin/lib/core/*.sh ./bin/lib/dbtool/*.sh
python3 -m py_compile ./bin/patch.py ./bin/springmaster-gates.py

./bin/springmaster-gates.sh report --run-id "${RUN_ID}" --clean > "${LOG_DIR}/${RUN_ID}.log"

for file in summary.txt summary.json findings.jsonl rule-sources.json input-manifest.json; do
  test -f "${REPORT_DIR}/${file}"
done

python3 -m json.tool "${REPORT_DIR}/summary.json" > "${LOG_DIR}/${RUN_ID}-summary.pretty.json"
python3 -m json.tool "${REPORT_DIR}/rule-sources.json" > "${LOG_DIR}/${RUN_ID}-rule-sources.pretty.json"
python3 -m json.tool "${REPORT_DIR}/input-manifest.json" > "${LOG_DIR}/${RUN_ID}-input-manifest.pretty.json"

printf '%s' "${RUN_ID}" > "${LOG_DIR}/current-run-id.txt"
python3 - <<'PY'
import json
from pathlib import Path

run_id = Path('target/springmaster-gates-regression/current-run-id.txt').read_text(encoding='utf-8')
report = Path('target/springmaster-gates') / run_id
schema = 'springmaster.report-only-report.v1'
seed = 'springmaster.report-only-gate-seed.v1'
required_report_files = ['summary.txt', 'summary.json', 'findings.jsonl', 'rule-sources.json', 'input-manifest.json']
allowed_severities = {'BLOCKER', 'ERROR', 'WARNING', 'INFO', 'MANUAL_REVIEW'}
required_finding_keys = {'gateId', 'ruleId', 'layer', 'mode', 'severity', 'ruleSource', 'subject', 'message'}

for name in required_report_files:
    if not (report / name).is_file():
        raise SystemExit(f'Missing report file: {name}')

summary = json.loads((report / 'summary.json').read_text(encoding='utf-8'))
if summary.get('reportSchemaVersion') != schema:
    raise SystemExit('Unexpected summary report schema version')
if summary.get('seedId') != seed:
    raise SystemExit('Unexpected seedId')
if summary.get('runId') != run_id:
    raise SystemExit('Unexpected runId')
if summary.get('mode') != 'report-only':
    raise SystemExit('Unexpected mode')
if summary.get('scope') != 'springmaster-reference-only':
    raise SystemExit('Unexpected scope')
if summary.get('status') != 'SUCCESS':
    raise SystemExit('Unexpected status')
if int(summary.get('findingCount', 0)) <= 0:
    raise SystemExit('Expected report-only findings')

rule_sources = json.loads((report / 'rule-sources.json').read_text(encoding='utf-8'))
if rule_sources.get('reportSchemaVersion') != schema:
    raise SystemExit('Unexpected rule-sources schema version')
required_sources = [entry for entry in rule_sources.get('ruleSources', []) if entry.get('required')]
if len(required_sources) < 6 or not all(entry.get('present') for entry in required_sources):
    raise SystemExit('Required rule source coverage incomplete')

manifest = json.loads((report / 'input-manifest.json').read_text(encoding='utf-8'))
if manifest.get('reportSchemaVersion') != schema:
    raise SystemExit('Unexpected input-manifest schema version')
if manifest.get('seedId') != seed:
    raise SystemExit('Unexpected input-manifest seedId')
if manifest.get('scope') != 'springmaster-reference-only':
    raise SystemExit('Unexpected input scope')
if not any(item.get('type') == 'target-projects' for item in manifest.get('unavailableInputs', [])):
    raise SystemExit('Expected target-projects to be listed as unavailable inputs')

rows = []
with (report / 'findings.jsonl').open(encoding='utf-8') as fh:
    for line in fh:
        if line.strip():
            row = json.loads(line)
            missing = required_finding_keys - set(row)
            if missing:
                raise SystemExit(f'Finding missing required keys: {sorted(missing)}')
            if row.get('mode') != 'report-only':
                raise SystemExit('Unexpected finding mode')
            if row.get('severity') not in allowed_severities:
                raise SystemExit('Unexpected finding severity')
            rows.append(row)
if len(rows) != summary.get('findingCount'):
    raise SystemExit('Finding count does not match summary')
if not any(row.get('gateId') == 'SM-G0-RULE-SOURCE-COVERAGE' for row in rows):
    raise SystemExit('Missing G0 rule source coverage finding')
if not any(str(row.get('gateId', '')).startswith('SM-G1-') for row in rows):
    raise SystemExit('Missing G1 diagnostic finding')
manifest_evidence = manifest.get('catalogDemoEvidence') or {}
if manifest_evidence.get('sliceState') != 'candidate-reference-slice':
    raise SystemExit('Expected Catalog-demo candidate evidence in input manifest')
if manifest_evidence.get('canonicalState') not in {'not-canonical', 'not canonical'}:
    raise SystemExit('Expected non-canonical Catalog-demo evidence in input manifest')
if any(row.get('gateId') == 'SM-G5-CATALOG-READINESS-EVIDENCE' and row.get('severity') == 'MANUAL_REVIEW' for row in rows):
    raise SystemExit('Unexpected G5 manual review after candidate evidence alignment')
PY

set +e
./bin/springmaster-gates.sh report --run-id "${RUN_ID}" > "${LOG_DIR}/${RUN_ID}-duplicate.log" 2>&1
DUPLICATE_RC=$?
set -e
if [[ "${DUPLICATE_RC}" -eq 0 ]]; then
  echo "[ERROR] Duplicate report run without --clean unexpectedly succeeded." >&2
  exit 1
fi
grep -Fq 'Report directory already exists' "${LOG_DIR}/${RUN_ID}-duplicate.log"

set +e
./bin/springmaster-gates.sh report --run-id "${RUN_ID}-target-rejected" --target /opt/cocondo/idm > "${LOG_DIR}/${RUN_ID}-target-rejected.log" 2>&1
TARGET_RC=$?
set -e
if [[ "${TARGET_RC}" -eq 0 ]]; then
  echo "[ERROR] Target-project input unexpectedly succeeded." >&2
  exit 1
fi
grep -Fq 'Target-project input is not supported' "${LOG_DIR}/${RUN_ID}-target-rejected.log"

CUSTOM_OUT="target/springmaster-gates-regression-custom"
./bin/springmaster-gates.sh report --run-id "${RUN_ID}-custom" --out-dir "${CUSTOM_OUT}" --clean > "${LOG_DIR}/${RUN_ID}-custom.log"
test -f "${CUSTOM_OUT}/${RUN_ID}-custom/summary.json"
python3 -m json.tool "${CUSTOM_OUT}/${RUN_ID}-custom/summary.json" > /dev/null

echo "[OK] Springmaster report-only gate regression passed: ${REPORT_DIR}"


