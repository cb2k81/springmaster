#!/usr/bin/env bash
set -euo pipefail

cd "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

RUN_ID="000068-selfcheck"
REPORT_DIR="target/springmaster-gates/${RUN_ID}"

python3 -m py_compile ./bin/springmaster-gates.py
mkdir -p target
./bin/springmaster-gates.sh report --run-id "${RUN_ID}" --clean > "target/springmaster-gates-${RUN_ID}.log"

test -d "${REPORT_DIR}"
for file in summary.txt summary.json findings.jsonl rule-sources.json input-manifest.json; do
  test -f "${REPORT_DIR}/${file}"
done

python3 -m json.tool "${REPORT_DIR}/summary.json" >/dev/null
python3 -m json.tool "${REPORT_DIR}/rule-sources.json" >/dev/null
python3 -m json.tool "${REPORT_DIR}/input-manifest.json" >/dev/null
python3 - <<'PY'
import json
from pathlib import Path
report = Path('target/springmaster-gates/000068-selfcheck')
summary = json.loads((report / 'summary.json').read_text(encoding='utf-8'))
if summary.get('reportSchemaVersion') != 'springmaster.report-only-report.v1':
    raise SystemExit('Unexpected reportSchemaVersion')
if summary.get('seedId') != 'springmaster.report-only-gate-seed.v1':
    raise SystemExit('Unexpected seedId')
if summary.get('mode') != 'report-only':
    raise SystemExit('Unexpected mode')
if summary.get('scope') != 'springmaster-reference-only':
    raise SystemExit('Unexpected scope')
if summary.get('status') != 'SUCCESS':
    raise SystemExit('Unexpected status')
if int(summary.get('findingCount', 0)) <= 0:
    raise SystemExit('Expected at least one report-only finding')
rule_sources = json.loads((report / 'rule-sources.json').read_text(encoding='utf-8'))
if rule_sources.get('reportSchemaVersion') != 'springmaster.report-only-report.v1':
    raise SystemExit('Unexpected rule-sources reportSchemaVersion')
manifest = json.loads((report / 'input-manifest.json').read_text(encoding='utf-8'))
if manifest.get('reportSchemaVersion') != 'springmaster.report-only-report.v1':
    raise SystemExit('Unexpected input-manifest reportSchemaVersion')
required = [entry for entry in rule_sources.get('ruleSources', []) if entry.get('required')]
if len(required) < 6 or not all(entry.get('present') for entry in required):
    raise SystemExit('Required rule source coverage incomplete')
if manifest.get('scope') != 'springmaster-reference-only':
    raise SystemExit('Unexpected input scope')
jsonl = report / 'findings.jsonl'
rows = []
with jsonl.open(encoding='utf-8') as fh:
    for line in fh:
        if line.strip():
            rows.append(json.loads(line))
if not rows:
    raise SystemExit('findings.jsonl must not be empty')
if not any(row.get('gateId') == 'SM-G0-RULE-SOURCE-COVERAGE' for row in rows):
    raise SystemExit('Missing G0 rule source coverage finding')
if not any(str(row.get('gateId','')).startswith('SM-G1-') for row in rows):
    raise SystemExit('Missing G1 diagnostic finding')
evidence = manifest.get('catalogDemoEvidence') or {}
if evidence.get('sliceState') != 'candidate-reference-slice':
    raise SystemExit('Expected Catalog-demo candidate evidence in input manifest')
if any(row.get('gateId') == 'SM-G5-CATALOG-READINESS-EVIDENCE' and row.get('severity') == 'MANUAL_REVIEW' for row in rows):
    raise SystemExit('Unexpected G5 manual review after candidate evidence alignment')
PY

echo "[OK] Springmaster report-only gate selfcheck passed: ${REPORT_DIR}"



