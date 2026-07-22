# 000168_springmaster_documentation_governance_bootstrap_v2

## Ziel

Dieser Patch schafft den regelkonformen Bootstrap fuer die weitere Governance-Persistenz. Er aktiviert die konsolidierte Documentation Governance V2, friert den aktuellen Dokumentbestand als einmalige V2-Transition-Baseline ein und stellt maschinenlesbare Dokumenttypen-, Metadaten- und Scope-Vertraege bereit.

## Baseline

- Git-HEAD: `6f72a152892331c79ac483961dd64aa6f362b8e4`
- Branch: `main`
- Full-Export: `springmaster_export_full_2026-07-22T15-40-32-733975Z.zip`
- Export-SHA-256: `2b0dd248cfe271541a4f4d261c4ff9f6cf782a2378c02252a6a7c1c39228bc25`
- File-Manifest-SHA-256: `1e7b38a09d27964802d08bd18ed840ed6d886036bc9b7996cf664b96ea5829fb`

## Inhalt

- `PROJECT_DOCS/DOCUMENTATION_GOVERNANCE.md` wird am bestehenden kanonischen Pfad konsolidiert und bleibt `active`.
- `PROJECT_DOCS/index.md` erhaelt V2-Metadaten und Eintraege fuer die Bootstrap-Templates.
- Die Documentation Transition Baseline wird einmalig gegen den vollstaendigen Markdown- und technischen Bestandsstand des Baseline-Commits eingefroren; danach kann sie nur reduziert werden.
- Unter `contracts/governance/documentation/` werden Dokumenttypen, Status, Pflichtmetadaten, Rule IDs und die initiale Scope Registry definiert.
- Unter `PROJECT_DOCS/_TEMPLATES/` werden allgemeine, Governance-, Standard-, ADR- und Report-Templates bereitgestellt.
- `bin/documentation-gate.py` wird auf Report Schema V2 erweitert. Findings, Transition-Findings und Tool Errors werden getrennt ausgewiesen.
- `bin/documentation-gate-it.sh` qualifiziert positive, negative, Legacy-, Baseline- und Tool-Error-Szenarien.

## Gate-Wirkung

- Neue oder migrierte Dokumente muessen V2-Front-Matter unmittelbar erfuellen.
- Der unveraenderte Bestand bleibt ueber die eingefrorene Transition-Baseline report-only sichtbar.
- Neue technische Dateien unter `PROJECT_DOCS/` blockieren.
- Unbekannte Dokumenttypen, ungueltige Status, doppelte Document IDs, ungueltige Supersession, Indexdrift und Baseline-Lock-Abweichungen blockieren.
- Kein bestehendes Quality Gate ausserhalb der Documentation Governance wird zu `strict` promoviert.

## Bewusst nicht enthalten

- keine Persistierung der weiteren Governance- und Standardentwuerfe,
- keine Java-, Coverage-, PMD-, Checkstyle-, SpotBugs- oder ArchUnit-Einfuehrung,
- keine Project-New- oder Managed-Project-Aenderung,
- keine Verschiebung bestehender Dokument- oder Contract-Pfade,
- keine Komponenten- oder Releaseversionserhoehung.

## Verifikation vor Artefakterstellung

- `git diff --check`
- `python3 -m py_compile bin/documentation-gate.py`
- `bash -n bin/documentation-gate.sh`
- `bash -n bin/documentation-gate-it.sh`
- `./bin/documentation-gate-it.sh` mit 10 Szenarien
- `./bin/documentation-gate.sh --check-all`
- relevante Contract-, Release-, Export-, Observability-, DB-Migration- und Scope-Selfchecks

Ergebnis des V2-Gates auf dem gepatchten Exportbestand:

- Status: `PASS`
- Blocking Findings: `0`
- V2-Dokumente: `7`
- baselinete Legacy-Markdown-Dokumente: `149`
- baselinete technische Uebergangsartefakte: `20`

## SemVer

Der Patch fuehrt einen Governance- und Tooling-Bootstrap innerhalb des laufenden Foundation-Sprints ein. Entsprechend der aktuellen Version Policy erfolgt in diesem Zwischenpatch keine Komponenten- oder Releaseversionserhoehung.
