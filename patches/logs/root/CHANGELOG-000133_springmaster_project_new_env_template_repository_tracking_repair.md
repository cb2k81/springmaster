# CHANGELOG 000133 – Project-New Env-Template Repository Tracking Repair

## Ursache

Der vollständige Maven-Test in einer frischen isolierten Git-Kopie scheiterte ausschließlich in `ProjectNewInstantiationAcceptanceTest`, weil das erzeugte Projekt keine `.env.example` enthielt.

Die Quelldatei `PROJECT_DOCS/TEMPLATES/project-skeleton/files/.env.example.tpl` war im lokalen Full-v2-Export vorhanden, wurde jedoch durch `.env.*` ignoriert und deshalb nicht in frische Git-Clones übernommen.

## Änderung

- `.gitignore` erhält eine präzise Ausnahme für die Project-New-Template-Quelldatei.
- Die Acceptance-Dokumentation beschreibt Ursache, Tracking-Vertrag und Fresh-Clone-Nachweis.
- Der Inhalt der Template-Datei bleibt bytegenau unverändert und wird im Resume-Runner über SHA-256 gebunden.

## Qualifikation

Verpflichtend sind:

- Artifact-Preflight, Live-Baseline und Dry-run für `000133` in isolierter Kopie;
- Sichtbarkeit der zuvor ignorierten Template-Datei als exakter Closure-Pfad;
- synthetischer Commit der Patches `000131`, `000132` und `000133` einschließlich Template-Datei;
- neuer frischer Clone aus diesem Commit;
- Project-New-Acceptance im frischen Clone;
- gezielte Maven-Tests für Artifact-Preflight und Project-New;
- vollständiger Springmaster-Maven-Test;
- reale ZBM-Core-Delivery-Integration mit Maven;
- Tooling-Selfcheck, ZBM-Live-Nichtmutation und genau ein finaler Full-v2-Export.
