# 000176_springmaster_engineering_contract_foundation

## Ziel

Dieser Tooling Patch implementiert `SPRINGMASTER-SPRINT-001`, Slice S-01 beziehungsweise Teilziel M-001. Er materialisiert die maschinenlesbare Brücke von Änderungsklassifikation und Risiko über deterministische Engineering-Profile bis zu Engineering-Evidence und Engineering-Completion.

## Baseline

- Git-HEAD: `f23b994412569f8e95e6f9f82285f6ec1d18916d`
- Branch: `main`
- Full-Export: `springmaster_export_full_2026-07-23T09-56-57-024519Z.zip`
- Export-SHA-256: `94c89ade307fbd3da1f31ea114e060581218d8c2f61f86a79297e34367ad3dc6`
- File-Manifest-SHA-256: `04e04c4440b6b3951f13efa603a531f6dee56831653a4f461710052aa36fea4c`
- Raw-Byte-Rekonstruktion: `666/666`

## Sprintbezug

- Sprint-ID: `SPRINGMASTER-SPRINT-001`
- Slice: `S-01`
- Teilziel: `M-001`
- Anforderungen: `EQP-REQ-001`, `EQP-REQ-002`
- Drift-Ergebnis: `none`

## Neue Contracts

Unter `contracts/governance/engineering/`:

- `change-classification-contract.json`
- `engineering-profile-contract.json`
- `engineering-evidence-contract.json`
- `engineering-completion-contract.json`

Die Contracts sind `report-only` und besitzen stabile V1-Schema-IDs. Sie konkretisieren ausschließlich bereits in der Engineering Governance festgelegte Begriffe und führen keine neue normative Prozessregel ein.

## Contract-Semantik

- 21 Änderungsklassen aus der Engineering Governance.
- vier geordnete Risikostufen und zwölf explizite Risikoindikatoren.
- Profile `fast`, `qualification`, `audit` und `release`.
- `qualification` ist für Engineering Completion immer erforderlich.
- Audit und Release werden deterministisch aus expliziten Flags oder Release-Klasse gewählt.
- vollständige Evidence-Struktur für Baseline, Scope, Klassen, Profile, Ausführungen, Findings, Deferrals, Schulden, Auswirkungen und technischen Status.
- vierzehn Completion-Kriterien mit den Statuswerten `qualified`, `qualified-with-findings`, `blocked`, `incomplete` und `cancelled`.

## Validator und Fixtures

`bin/engineering-contracts.py` bietet vier read-only Operationen:

- `contracts`
- `profiles`
- `evidence`
- `completion`

Exit-Semantik:

- `0`: technisch erfolgreich, keine Findings oder report-only-Ausführung ohne `--check`.
- `1`: Validierungsfindings bei `--check`.
- `2`: Tool Error oder nicht verlässlich lesbarer Contract/Input.

`bin/engineering-contracts-it.sh` prüft 18 positive, negative und Tool-Error-Szenarien, darunter:

- eindeutige Contract-IDs und Referenzen,
- Low-, High- und Release-Profilwahl,
- unbekannte Klassen,
- Evidence-Profile-Mismatch,
- Tool Error in qualifizierter Evidence,
- doppelte Execution IDs,
- gültige `qualified`- und `qualified-with-findings`-Completion,
- unzulässige Blocker- und Statuskombinationen,
- fehlenden Contract-Root.

## Dokumentations- und Sprintfortschreibung

- Engineering Governance verweist auf die vier realen Contractpfade und grenzt den Validator vom späteren Engineering-Qualification-Gate ab.
- `STATUS.md` wechselt in Phase `execution`, markiert M-001 als `completed` und S-02 als nächsten kontrollierten Schritt.
- `COMPLETION_REPORT.md` nimmt S-01 als akzeptierten Slice auf, ohne den Sprint vorzeitig zu schließen.
- Scope Registry und Tooling-Exportprofil werden um Contract-, Validator- und Fixturepfade ergänzt.
- der Tooling-Selfcheck führt Contractprüfung und 18 Fixtures aus.

## Sicherheits- und Scopegrenzen

Nicht enthalten sind:

- kein Engineering-Qualification-Gate; dieses bleibt S-04 vorbehalten,
- keine Strict-Promotion,
- keine neue externe Dependency,
- keine Coverage-, Komplexitäts-, Lizenz- oder Vulnerability-Schwelle,
- keine Project-New-Materialisierung der Engineering-Contracts,
- keine Mutation eines gemanagten Projekts,
- keine Produkt-, Core-, Demo- oder Maven-Änderung,
- keine Versionserhöhung oder Releasefreigabe.

## Qualifikation

- Contract-Semantik: `PASS`.
- Engineering-Contract-Fixtures: `18/18 PASS`.
- Documentation Gate und Fixtures: `PASS`, `10/10`.
- Project Directory Gate und Fixtures: `PASS`, `0` neue Findings, `61` Transition Findings, `17/17`.
- Sprint Gate und Fixtures: `PASS`, `21/21`.
- Bash- und Python-Syntax: `PASS`.
- JSON-Lesbarkeit und Schema-Referenzen: `PASS`.
- Payload-Parität und Diff-Hygiene: `PASS`.

## Nächster kontrollierter Schritt

Nach Annahme wird ein frischer Full Export erzeugt. Darauf beginnt Slice S-02 beziehungsweise M-002 mit Quality Rule Catalog und Gate Registry als eigener begrenzter Patch.
