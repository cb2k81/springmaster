# CHANGELOG 000127 – ZBM Generated Slice Pilot Plan

Patch-ID: `000127_springmaster_zbm_generated_slice_pilot_plan`

Scope: `docs`

## Ziel

Den ersten fachlichen Generated-Slice-Piloten für ZBM baseline-relativ,
patchsystemkonform und ohne Zielmutation vorbereiten.

## Änderungen

* neues verbindliches ZBM-Pilotplandokument;
* Korrektur der Target-Registry-Dokumentation auf den bereits vorhandenen
  ZBM-Descriptorzustand;
* Einordnung älterer ZBM-Initialisierungs-/Core-Copy-Dokumente als historische
  Evidence;
* Definition der erforderlichen ZBM-Baseline, forensischen Qualifizierung und
  Target Bindings;
* explizite Persistence-, Security-, Compatibility- und Scope-Entscheidungen;
* deterministischer Sandbox-, Test-, Freigabe-, Apply- und Exportpfad;
* Alignment von Roadmap, Implementation Plan, Adoption Plan, Blueprint und
  Version Policy.

## Nicht enthalten

* keine Änderung an `platform/update/targets/zbm.env`;
* keine Versionserhöhung;
* kein Renderer oder Patch-Assembler;
* kein ZBM-Quellcode;
* kein ZBM-Patch-ZIP;
* kein ZBM-Dry-run oder Apply;
* keine Maven-Pflicht für diesen documentation-only Patch.
