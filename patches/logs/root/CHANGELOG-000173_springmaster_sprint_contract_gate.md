# 000173_springmaster_sprint_contract_gate

## Ziel

Dieser Patch leitet die Sprint Governance technisch als maschinenlesbaren Sprint Contract, Drift Contract, vier spezialisierte Sprint-Templates und read-only report-only Sprint Gate ab. Er führt noch keinen realen Sprint ein, aktiviert keine Strict-Prüfung und verändert keine Produktiv- oder Zielprojektquellen.

## Baseline

- Git-HEAD: `62b013764be8aa61bebf1afd7e15119799a9e291`
- Branch: `main`
- Full-Export: `springmaster_export_full_2026-07-23T08-20-23-669334Z.zip`
- Export-SHA-256: `00a333b331291702da7e3eee97c92ec7ef445ba728eb2dea72536b815623d1b6`
- File-Manifest-SHA-256: `c9ad0ecb812322cb1b40f5b7f6ce49918e3898b0547debebf9e84c7248a3a266`
- Raw-Byte-Rekonstruktion: `649/649`

## Neue technische Quellen

- `contracts/governance/sprint/sprint-contract.json`
- `contracts/governance/sprint/sprint-drift-contract.json`
- `bin/sprint-gate.py`
- `bin/sprint-gate.sh`
- `bin/sprint-gate-it.sh`
- `src/test/resources/tooling/sprint-gate-v1/expected-cases.json`

## Neue Sprint-Templates

- `PROJECT_DOCS/_TEMPLATES/SPRINT_BRIEF_TEMPLATE.md`
- `PROJECT_DOCS/_TEMPLATES/SPRINT_SOLUTION_PLAN_TEMPLATE.md`
- `PROJECT_DOCS/_TEMPLATES/SPRINT_STATUS_TEMPLATE.md`
- `PROJECT_DOCS/_TEMPLATES/SPRINT_COMPLETION_REPORT_TEMPLATE.md`

Die Templates erhalten eigenständige V2-Metadaten und stellen die ausfüllbaren Sprintdokumente innerhalb eines dokumentierten Vorlagenblocks bereit.

## Sprint Contract

Der Contract konkretisiert:

- aktive und archivierte Sprintpfade,
- Sprint-ID- und Dokument-ID-Muster,
- vier Pflichtdokumentrollen,
- Phasen, Gesamtstatus, Teilzielstatus, Qualification und Closure,
- Pflichtüberschriften,
- Problem-/Lösungsraum-Trennung,
- DoR- und DoD-Checklisten,
- messbare Teilzieltabellen,
- WORK-Verzeichnisse und temporäre Metadaten,
- Index- und Archivanforderungen.

## Drift Contract

Der Drift Contract konkretisiert:

- Prüfevents und Driftkategorien,
- kontrollierte Ergebnisse,
- Amendment-pflichtige Kategorien,
- Amendment-ID und Pflichtfelder,
- Review nach überschrittenem Zielabschluss.

## Gate-Verhalten

Das Gate unterstützt:

- `all`, `changed` und `report`,
- explizite Changed Paths,
- automatische Vollscan-Erweiterung bei Contract-, Template-, Governance-, Gate- oder Indexänderungen,
- aktive und archivierte Sprintprüfung,
- getrennte Findings und Tool Errors,
- report-only als Standard und `--check` für CI-kompatible Exit-Semantik.

Der aktuelle Springmaster-Bestand besitzt noch keinen Sprint unter `PROJECT_DOCS/SPRINTS/`. Der Baseline-Scan besteht deshalb ohne Transition-Ausnahme mit 0 Findings. Neue Sprintinstanzen müssen den Contract unmittelbar vollständig erfüllen.

## Fixtures und Verifikation

21 positive, negative und Tool-Error-Fälle prüfen insbesondere:

- leeren Bestand, gültigen aktiven und gültigen archivierten Sprint,
- ungültige Sprint- und Dokumentidentität,
- fehlende Pflichtdokumente und Überschriften,
- Vermischung von Problem- und Lösungsraum,
- unvollständige DoR,
- ungültige Teilziele und Statusparität,
- mehr als eine Statusquelle,
- ungültige Phase,
- akzeptierte Drift ohne Amendment und unvollständige Amendments,
- veraltete Driftprüfung nach Zieltermin,
- ungültige WORK-Metadaten,
- fehlende temporäre Abschlussentscheidungen,
- temporäre Inhalte im Archiv,
- Changed-to-All-Erweiterung,
- fehlenden Contract als Tool Error.

## Integration

- `tooling-selfcheck.sh` führt Sprint Gate und Fixtures optional aus.
- das Tooling-Exportprofil enthält Sprint Contracts und Fixtures.
- die Documentation Scope Registry registriert Sprint Contracts und Gate.
- `PROJECT_DOCS/index.md` indexiert die vier Templates.
- die Sprint Governance dokumentiert den report-only Umsetzungsstand und bleibt `draft`.

## Qualifikation

- Sprint Gate: `PASS`, 0 Findings, 0 Tool Errors
- Sprint Gate Fixtures: `21/21 PASS`
- Documentation Gate V2: `PASS`
- Documentation Gate Fixtures: `10/10 PASS`
- Project Directory Gate: `PASS`, 61 Transition Findings, 0 neue Findings
- Project Directory Fixtures: `17/17 PASS`
- Bash- und Python-Syntax: `PASS`
- Diff-Hygiene: `PASS`

## Bewusst nicht enthalten

- kein realer Springmaster-Sprint,
- keine Materialisierung in Project-New,
- keine Managed-Project-Adoption,
- keine Status- oder Strict-Promotion,
- keine Legacy-Sprintmigration oder Löschung,
- keine Release- oder Versionsänderung,
- keine Zielprojektmutation.

## SemVer

Der neue report-only Contract- und Tooling-Surface entspricht voraussichtlich einem kompatiblen `minor`-Impact für `PLATFORM_TOOLING_VERSION`. Die tatsächliche Versionserhöhung bleibt der Release Closure vorbehalten; `platform/versions/platform.env` wird in diesem Patch nicht verändert.
