# 000169_springmaster_core_governance_drafts

## Ziel

Dieser Patch persistiert die im Cross-Document Consistency Audit 01 validierten Kern-Governance-Dokumente als kontrollierte V2-Drafts. Er schafft damit fruehzeitig Git-Historie fuer den weiteren Governance-Aufbau, ohne Entwurfsregeln bereits zu aktivieren oder technisch strict durchzusetzen.

## Baseline

- Git-HEAD: `597af73a42290c0bf1eb3ebefce9dd4d7c927ef7`
- Branch: `main`
- Full-Export: `springmaster_export_full_2026-07-22T16-10-45-576847Z.zip`
- Export-SHA-256: `192ef307ba17bfd2eb17f641f6d2fbdd18611313355072c1d8016c9ce7eff59b`
- File-Manifest-SHA-256: `48b9a7b4e5b6fccbbc3274263fca35b79c7803c1621a629cf7e4955e16890daa`

## Inhalt

Folgende normative Dokumente werden mit `status: draft` aufgenommen:

- `PROJECT_DOCS/GOVERNANCE/PROJECT_DIRECTORY_GOVERNANCE.md`
- `PROJECT_DOCS/GOVERNANCE/ENGINEERING_GOVERNANCE.md`
- `PROJECT_DOCS/GOVERNANCE/QUALITY_GATE_GOVERNANCE.md`
- `PROJECT_DOCS/GOVERNANCE/TEST_GOVERNANCE.md`
- `PROJECT_DOCS/GOVERNANCE/DEPENDENCY_GOVERNANCE.md`

Zusaetzlich werden:

- die neuen Dokumente in `PROJECT_DOCS/index.md` aufgenommen,
- ihre logischen Scope-Pfade in `contracts/governance/documentation/scope-registry.json` registriert.

## Statuswirkung

- Die neuen Dokumente sind normative Entwuerfe, aber noch nicht `active`.
- Sie erzeugen noch keine automatische Strict-Promotion technischer Regeln.
- Bestehender Code und bestehende Projekte werden durch diesen Patch nicht migriert.
- Die Documentation Transition Baseline wird nicht erweitert.

## Bewusst nicht enthalten

- keine Java- oder Testing-Standards,
- keine Quality-Tool-Konfiguration,
- keine Directory-, Test-, Dependency- oder Quality-Gate-Contracts ausser der Scope-Registrierung,
- keine Project-New- oder Managed-Project-Aenderung,
- keine Pfadverschiebung,
- keine Komponenten- oder Releaseversionserhoehung.

## Verifikation

- V2-Metadaten und Scope-Pfade der fuenf Dokumente
- vollstaendige Indexabdeckung
- `./bin/documentation-gate.sh --check-all`
- `./bin/documentation-gate-it.sh` mit 10 Szenarien
- `git diff --check`
- Live-Baseline-, Dry-run- und Artifact-Preflight des Patchartefakts

## SemVer

Der Patch persistiert ausschliesslich normative Draft-Dokumente und erweitert die bestehende Scope Registry. Es erfolgt keine Komponenten- oder Releaseversionserhoehung.
