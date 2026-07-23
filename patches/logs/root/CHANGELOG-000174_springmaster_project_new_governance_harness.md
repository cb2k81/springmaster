# 000174_springmaster_project_new_governance_harness

## Ziel

Dieser Patch materialisiert den minimalen report-only Governance-Harness in Project-New. Ein frisch erzeugtes Projekt erhält lokal ausführbare Documentation-, Project-Directory- und Sprint-Contracts samt Gates, Fixtures, Templates, Adoption und leeren Deviation-/Risikoausgangsständen. Die vollständige Springmaster-Governance wird nicht kopiert.

## Baseline

- Git-HEAD: `da7596d94a3331265393eeadc62f962ea0cc35c4`
- Branch: `main`
- Full-Export: `springmaster_export_full_2026-07-23T08-44-18-984255Z.zip`
- Export-SHA-256: `b3cfc87dab1ae34919ac29547b2a37a98df3349b152e997ef1dfcfca51475680`
- File-Manifest-SHA-256: `bb385db6cc5db24668f4386e95d7b050b07d19b6f5eae4fee2aae545c8477a46`
- Raw-Byte-Rekonstruktion: `660/660`

## Project-New-Materialisierung

Project-New erzeugt zusätzlich:

- ein projektlokales `AGENTS.md`,
- einen V2-Dokumentationsindex,
- Bootstrap- und Governance-Adoption-Dokumente,
- einen maschinenlesbaren Adoption Record,
- leere Deviation- und Risikoregister,
- einen initialen Generated-Project-Managed-State,
- Documentation-, Directory- und Sprint-Contracts,
- report-only Gates und vollständige Fixture-Sätze,
- allgemeine Governance- und Sprint-Templates,
- einen projektlokalen Tooling-Selfcheck.

Kanonische Schema-IDs bleiben unverändert `springmaster.*`. Projektbezogene Tokens werden nur an dafür vorgesehenen Scope-, Identitäts- und Provenienzstellen ersetzt.

## Generated-Project-Profil

Der Directory Contract erlaubt die lokal erforderlichen Bereiche `PROJECT_DOCS/TOOLING/**` und `PROJECT_DOCS/_TEMPLATES/**` für `generated-project` und `managed-project`. Das erzeugte Projekt erhält eine leere, versiegelte Directory Transition Baseline und besteht das Profil `generated-project` mit null Findings.

## Provenienz und Git-Baseline

Project-New benötigt fail-closed einen verifizierbaren 40-stelligen Springmaster-Git-HEAD für den Adoption Record. Die Fresh-Project-Acceptance erzeugt das Ziel außerhalb des Springmaster-Working-Trees, initialisiert dort eine eigenständige lokale Git-Baseline und prüft dadurch Patch-, Gate- und Exportfähigkeit ohne verdeckte Parent-Repository-Kopplung.

Relative `--work-root`-Pfade der Acceptance werden vor dem Verzeichniswechsel kanonisch auf den Springmaster-Projektroot bezogen. Der absichtlich dirty ausgeführte Export-Config-Prioritätstest verwendet explizit `--allow-dirty`.

## Fresh-Project-Acceptance

Die Acceptance prüft unter anderem:

- Dry-run und sichere Projektanlage,
- vollständige Materialisierung aller Harness-Dateien,
- Token- und Schema-ID-Integrität,
- eigenständige lokale Git-Baseline,
- Patch-Registry und Bootstrap-Provenienz,
- Documentation Gate sowie 10 Fixtures,
- Project Directory Gate sowie 17 Fixtures,
- Sprint Gate sowie 21 Fixtures,
- projektlokalen Tooling-Selfcheck,
- Config- und Migration-Contracts,
- DBTool-Status ohne Datenbankverbindung,
- vollständigen Full-ZIP-Export und Raw-Byte-Integrität,
- projektlokalen Export-Key trotz bewusst abweichender `export.config.json`,
- optional den Maven-Test des erzeugten Projekts.

## Dokumentation

Aktualisiert werden:

- Project-New-Betriebsdokumentation,
- Project-Skeleton-README und Manifest,
- Managed Project Governance,
- Project Directory Governance.

Die Governance-Dokumente bleiben `draft`; die Gates bleiben `report-only`.

## Qualifikation

- Source Tooling Selfcheck `--no-export`: `PASS`
- Source Documentation Gate und Fixtures: `PASS`, `10/10`
- Source Project Directory Gate und Fixtures: `PASS`, `17/17`, `61` Transition Findings, `0` neue Findings
- Source Sprint Gate und Fixtures: `PASS`, `21/21`
- Fresh-Project-Acceptance ohne Maven: `PASS`
- Generated Documentation Gate: `PASS`
- Generated Directory Gate: `PASS`, `0` Findings
- Generated Sprint Gate: `PASS`
- Generated Tooling Selfcheck `--no-export`: `PASS`
- Generated Full Export und Integritätscheck: `PASS`
- Provenienz-Fail-Closed-Test: `PASS`
- Bash-, Python- und JSON-Syntax: `PASS`
- Diff-Hygiene: `PASS`

Der gezielte Maven-Test konnte in der Qualifikationsumgebung nicht ausgeführt werden, weil dort kein `mvn` installiert ist. Die vorhandene Java-Acceptance wurde auf die neuen Artefakte erweitert; der reale Tooling-/Maven-Kontext bleibt Bestandteil der Repository-Acceptance.

## Bewusst nicht enthalten

- kein realer Springmaster-Pilotsprint,
- keine vollständige Kopie der Springmaster-Governance oder Standards,
- keine Strict- oder Statuspromotion,
- keine automatische Target-Registry-Aufnahme,
- kein Managed-Project-Apply,
- keine Platform-, Core-, Tooling- oder Release-Versionserhöhung.

## SemVer

Die additive Project-New- und Tooling-Funktionalität entspricht voraussichtlich einem kompatiblen `minor`-Impact für Template und Tooling. `PLATFORM_TEMPLATE_VERSION` bleibt in diesem Patch konsistent bei `0.3.1`; die tatsächliche Komponenten- oder Release-Versionierung erfolgt erst in der Release Closure.
