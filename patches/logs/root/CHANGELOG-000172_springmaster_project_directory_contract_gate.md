# 000172_springmaster_project_directory_contract_gate

## Ziel

Dieser Patch leitet die Project Directory Governance erstmals technisch als maschinenlesbaren Contract, versiegelte Directory Transition Baseline und read-only report-only Gate ab. Er bildet den realen Springmaster-Bestand ab, erkennt neue Strukturverstöße und nimmt keine automatische Strukturänderung vor.

## Baseline

- Git-HEAD: `402036fe7e74b975f5478449656f990b7285a9a5`
- Branch: `main`
- Full-Export: `springmaster_export_full_2026-07-23T07-22-47-588343Z.zip`
- Export-SHA-256: `05ea52a426c2cf288f1c45ff1d5baca861babfa5e35edc9c9910e880db363691`
- File-Manifest-SHA-256: `82685113f0d0ea251af8fe2e805c02bcad76b4d3d48e08146a4d432b9c7c7993`
- Raw-Byte-Rekonstruktion: `642/642`

## Neue technische Quellen

- `contracts/governance/project-structure/project-directory-contract.json`
- `contracts/governance/project-structure/directory-transition-baseline.json`
- `bin/project-directory-gate.py`
- `bin/project-directory-gate.sh`
- `bin/project-directory-gate-it.sh`
- `src/test/resources/tooling/project-directory-gate-v1/expected-cases.json`

## Contract und Profile

Der Contract modelliert getrennt:

- `springmaster-source`,
- `project-new-template-source` als eingebettete Quelle,
- `generated-project`,
- `managed-project` mit zukünftigem Deviation-Input.

Er registriert Root-Allowlist, Source-/Generated-/Runtime-Bereiche, Dateitypen, Transition-Klassen, Git-Commitregeln, Naming- und Case-Hygiene, Symlinkregeln sowie deklarierte Byte-Duplikate.

## Directory Transition Baseline

Die Baseline enthält 61 einzeln identifizierte Bestandsabweichungen:

- drei Dateien unter dem Root-Legacy-Bereich `docs/`,
- ein bestehendes Dokument unter `PROJECT_DOCS/OPERATIONAL/`,
- 57 historische nicht-Changelog-Dateien unter `patches/logs/platform-update/`.

Der kanonische Entry-Set-Hash ist im Contract versiegelt. Neue Instanzen derselben Klassen werden als neue Findings ausgewiesen und nicht automatisch in die Baseline aufgenommen.

## Gate-Verhalten

Das Gate unterstützt:

- `all`,
- `changed`,
- `report`,
- explizite Changed Paths,
- automatische Vollscan-Erweiterung bei Contract-, Baseline- oder Deviation-Änderungen,
- getrennte Transition Findings, neue Findings und Tool Errors,
- Root-, Area-, Dateityp-, Hygiene-, Case-, Symlink-, Duplicate- und Deviation-Prüfungen.

Das Gate ist read-only und standardmäßig report-only. Nur der explizite Schalter `--check` liefert Exit 1 bei neuen Findings; Tool Errors liefern immer Exit 2.

## Fixtures und Verifikation

17 positive und negative Fälle prüfen insbesondere:

- gültiges Generated-Project-Profil,
- unerlaubten Root-Pfad und gelöschte Pflichtdatei,
- falschen Dateityp und technische Datei unter Dokumentation,
- temporäre und Backup-Artefakte,
- Case-Kollision,
- defekten und externen Symlink,
- nicht deklarierte und deklarierte Byte-Duplikate,
- Bestandsfinding gegenüber neuem Finding,
- abgelaufene Deviation,
- Changed-to-All-Erweiterung,
- Baseline-Digest- und Missing-Contract-Tool-Errors.

Der reale Springmaster-Bestand ergibt 61 Transition Findings, 0 neue Findings und 0 Tool Errors. Ein frisch erzeugtes Project-New-Projekt besteht das `generated-project`-Profil bei externer Contract-Prüfung ohne Reparatur.

## Integration

- `tooling-selfcheck.sh` führt Gate und Fixtures optional aus.
- Python-Syntaxprüfung schreibt Cache ausschließlich unter `build/`.
- das Tooling-Exportprofil enthält Contract und Fixtures.
- die Documentation Scope Registry enthält Gate, Contract und Fixtures.
- die Project Directory Governance dokumentiert den report-only Umsetzungsstand und bleibt `draft`.

## Bewusst nicht enthalten

- keine Statuspromotion oder Strict-Promotion,
- keine Pfadverschiebung oder Legacy-Löschung,
- keine automatische Baseline-Erweiterung,
- keine Materialisierung des Gates in Project-New,
- kein Managed-Project-Deviation-Contract,
- keine Zielprojektmutation,
- keine Komponenten- oder Foundation-Versionserhöhung.

## SemVer

Der neue report-only Tooling- und Contract-Surface entspricht voraussichtlich einem kompatiblen `minor`-Impact für `PLATFORM_TOOLING_VERSION`. Gemäß aktiver Version Policy erfolgt die tatsächliche Erhöhung erst im Release-Closure-Schnitt; `platform/versions/platform.env` bleibt in diesem Zwischenpatch unverändert.
