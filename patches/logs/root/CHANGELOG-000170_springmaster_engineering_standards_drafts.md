# 000170_springmaster_engineering_standards_drafts

## Ziel

Dieser Patch persistiert die im Cross-Document Consistency Audit 01 validierten Java- und Testing-Standards als kontrollierte V2-Drafts. Er schafft Git-Historie fuer die technischen Detailregeln, ohne bestehende Standards abzuloesen, neue Quality Tools einzufuehren oder Regeln bereits strict durchzusetzen.

## Baseline

- Git-HEAD: `c7ba0b4ab5958e522513debc177aa20e6cce34a8`
- Branch: `main`
- Full-Export: `springmaster_export_full_2026-07-22T18-48-33-677541Z.zip`
- Export-SHA-256: `c5aaaa6148738a252486eb82dd4437b147f5e2b1026b138b3854f6ebc1cc2320`
- File-Manifest-SHA-256: `d0059932bb9cfec13c1c5ce65a241117a0f9f00497f77b42e876f05980d65cf5`

## Inhalt

Folgende normativen Dokumente werden mit `status: draft` aufgenommen:

- `PROJECT_DOCS/STANDARDS/ARCHITECTURE/JAVA_ARCHITECTURE_STANDARD.md`
- `PROJECT_DOCS/STANDARDS/JAVA/JAVA_CODING_STANDARD.md`
- `PROJECT_DOCS/STANDARDS/TESTING/TESTING_STANDARD.md`

Zusaetzlich werden:

- die neuen Dokumente in `PROJECT_DOCS/index.md` aufgenommen,
- ihre logischen Scope-Pfade in `contracts/governance/documentation/scope-registry.json` registriert.

## Statuswirkung

- Die neuen Standards sind normative Entwuerfe, aber noch nicht `active`.
- Bestehende aktive Fachstandards und akzeptierte ADRs behalten ihre Autoritaet.
- Ueberlappende Regeln werden vor einer spaeteren Aktivierung durch eine Standard-Reconciliation bereinigt.
- Es werden keine Quality Rules strict geschaltet.
- Die Documentation Transition Baseline wird nicht erweitert.

## Bewusst nicht enthalten

- kein Build and Tooling Standard,
- keine Checkstyle-, PMD-, SpotBugs-, ArchUnit- oder Coverage-Konfiguration,
- keine Rule-Catalog- oder Quality-Contract-Implementierung,
- keine Source- oder Package-Umsortierung,
- keine Project-New- oder Managed-Project-Aenderung,
- keine Komponenten- oder Releaseversionserhoehung.

## Verifikation

- V2-Metadaten und registrierte Scope-Pfade der drei Standards
- eindeutige Document IDs und Rule IDs
- vollstaendige Indexabdeckung
- `./bin/documentation-gate.sh --check-all`
- `./bin/documentation-gate-it.sh`
- `git diff --check`
- Live-Baseline-, Dry-run- und Artifact-Preflight des Patchartefakts

## SemVer

Der Patch persistiert ausschliesslich normative Draft-Dokumente und erweitert die Documentation Scope Registry. Es erfolgt keine Komponenten- oder Releaseversionserhoehung.
