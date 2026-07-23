# 000171_springmaster_governance_audit02_reconciliation

## Ziel

Dieser Patch persistiert die vier nach Gesamtaudit 02 verbleibenden Governance- und Standard-Drafts und übernimmt ausschließlich die im Audit bestätigten Reconciliation-Korrekturen. Er vervollständigt die normative Volltextbasis, ohne Drafts zu aktivieren, Gates oder Tooling-Verhalten zu ändern oder Legacy-Dokumente abzulösen.

## Baseline

- Git-HEAD: `0ab0b967584078d07b03db24c76f6815e7beeb97`
- Branch: `main`
- Full-Export: `springmaster_export_full_2026-07-23T05-34-28-796609Z.zip`
- Export-SHA-256: `b42e16e3be79c370514696789add7cae23341cd10616b147860cdf630994197a`
- File-Manifest-SHA-256: `5f92a8b740a3c2e3a7b397a81c46ffa266b01fa9d3da4cc882a5a4fca341e52b`

## Neue Drafts

- `PROJECT_DOCS/GOVERNANCE/SPRINT_GOVERNANCE.md`
- `PROJECT_DOCS/GOVERNANCE/MANAGED_PROJECT_GOVERNANCE.md`
- `PROJECT_DOCS/GOVERNANCE/RELEASE_AND_VERSION_GOVERNANCE.md`
- `PROJECT_DOCS/STANDARDS/BUILD_AND_TOOLING_STANDARD.md`

Alle vier Dokumente bleiben `status: draft` und erhalten durch diesen Patch keine Aktivierungswirkung.

## Audit-02-Reconciliation

- Documentation Governance erlaubt kontrolliert `SOLUTION_PLAN.md` und `STATUS.md` am Root eines aktiven Sprintordners und führt den Solution Plan als Dokumentrolle.
- Project Directory Governance verwendet den eindeutigen Begriff `Directory Transition Baseline` und trennt `Tool Error` von Findings.
- Engineering Governance verwendet den kanonischen Begriff `Tool Error`.
- Java Architecture und Java Coding verwenden `Findings-Baseline` statt einer generischen Transition-Baseline.
- Index und Scope Registry registrieren die vier neuen Dokumente und ihre logischen Scopes.
- Die informative Target Registry führt den bereits vorhandenen ZDM-Descriptor als Initialisierungskandidaten auf.

## Statuswirkung

- Documentation Governance bleibt `active`; die Änderung ist eine qualifizierte, rückwärtskompatible Präzisierung des Sprint-Dokument-Lifecycles.
- Alle übrigen neuen und geänderten Governance-/Standard-Dokumente bleiben `draft`.
- Bestehende akzeptierte ADRs, aktive Fachstandards, `SPRINT_RELEASE_GOVERNANCE.md` und `SPRINGMASTER_VERSION_POLICY.md` behalten ihre bisherige Autorität.
- Es erfolgt keine Strict-Promotion und keine Erweiterung der Documentation Transition Baseline.

## Bewusst nicht enthalten

- keine neuen Contracts, Gates, Fixtures oder Register,
- keine Maven-, Bash-, Python- oder Release-Tooling-Änderung,
- keine Verzeichnis- oder Sprintmigration,
- keine Project-New-Materialisierung,
- keine Zielprojektmutation,
- keine Supersession aktiver Legacy-Dokumente,
- keine Komponenten-, Foundation- oder Releaseversionserhöhung.

## Verifikation

- vollständige Raw-Byte-Baseline gegen den Full-Export,
- V2-Metadaten und registrierte Scope-Pfade,
- eindeutige Document IDs und 399 eindeutige Standard-Rule-IDs,
- Terminologie-, Index- und ZDM-Registry-Konsistenz,
- `./bin/documentation-gate.sh --check-all`,
- `./bin/documentation-gate-it.sh`,
- `git diff --check`,
- Live-Baseline-, Dry-run- und Artifact-Preflight des Patchartefakts.

## SemVer

Der Patch persistiert ausschließlich Draft-Dokumente und rückwärtskompatible Dokumentations-Reconciliation. Es erfolgt keine Versionsänderung.
