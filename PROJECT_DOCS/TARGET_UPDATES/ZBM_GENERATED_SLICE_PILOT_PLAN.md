# ZBM Generated Slice Pilot Plan

Patch: `000127_springmaster_zbm_generated_slice_pilot_plan`

## 1. Zweck und Freigabegrenze

Dieses Dokument definiert den verbindlichen Vorbereitungs-, Qualifizierungs- und
Freigabepfad für den ersten fachlichen Generated-Slice-Piloten im Zielprojekt
`zbm`.

Der Patch `000127` ist ausschließlich ein Planungs- und Governance-Patch im
Springmaster-Repository. Er:

* analysiert oder verändert keine aktuelle ZBM-Datei;
* erzeugt keinen ZBM-Patch;
* rendert keinen Java-Quellcode;
* führt keinen ZBM-Dry-run und keinen ZBM-Apply aus;
* ändert den Springmaster-Target-Descriptor `platform/update/targets/zbm.env`
  nicht;
* erteilt keine Delivery- oder Apply-Freigabe.

Eine operative ZBM-Arbeit beginnt erst nach Lieferung einer aktuellen,
integritätsgeprüften ZBM-Full-Baseline und einer erneuten forensischen Analyse.
Ein echter Apply benötigt danach zusätzlich eine ausdrückliche Benutzerfreigabe.

## 2. Nachgewiesener Springmaster-Ausgangspunkt

Springmaster stellt mit dem Stand nach `000126` folgende nicht mutierende Kette
bereit:

```text
GeneratedServiceSlice YAML
-> strict fixture gate
-> springmaster.generated-service-slice-ir.v1
-> springmaster.generated-service-slice-patch-blueprint.v1
```

Nachgewiesen sind:

* ein neutraler Slice-Spec-Vertrag;
* ein fail-closed Fixture Gate;
* eine domänenneutrale Intermediate Representation;
* ein deterministischer, zielprojektneutraler Patch-Blueprint;
* ein Producer Artifact Preflight für fertige Patch-ZIPs;
* Rohbyte- und Closure-Evidence für Full-Exporte.

Noch nicht vorhanden sind:

* ein target-bound Source Renderer;
* eine ZBM-spezifisch gebundene, aber generisch implementierte
  Rendering-Konfiguration;
* ein Generated-Slice-Patch-Assembler;
* ein gegen die aktuelle ZBM-Baseline qualifiziertes Patch-ZIP.

Der Blueprint aus `000126` darf deshalb nicht als deploybarer ZBM-Patch
missverstanden werden.

## 3. Aktueller Springmaster-Target-Descriptor

Der in dieser Springmaster-Baseline vorhandene Descriptor enthält:

```env
TARGET_NAME=zbm
TARGET_STATUS=DELIVERY_ENABLED
TARGET_PATH=/opt/cocondo/zbm
TARGET_BASE_PACKAGE=de.cocondo.zbm
TARGET_LIFECYCLE=update-enabled
TARGET_INITIALIZATION_ALLOWED=false
TARGET_UPDATE_ALLOWED=true
TARGET_DELIVERY_ENABLED=true
TARGET_ALLOWED_PROFILES=tooling
```

Daraus folgt:

1. Die frühere Initialisierungsphase ist historisch abgeschlossen.
2. Der Descriptor erlaubt aktuell ausschließlich das Profil `tooling`.
3. Eine Generated-Slice-Lieferung ist dadurch **nicht** freigegeben.
4. `TARGET_DELIVERY_ENABLED=true` ist keine pauschale Erlaubnis für beliebige
   Profile oder fachliche Patches.
5. `000127` erweitert `TARGET_ALLOWED_PROFILES` nicht.

Für den ersten Piloten ist der bevorzugte Weg ein reviewtes, target-lokales
Patch-ZIP, das über das lokale ZBM-Patchsystem geprüft wird. Eine spätere
Delivery per Springmaster-`target-apply` benötigt einen eigenen, expliziten
Descriptor- und Profilentscheid und ist nicht Bestandteil dieses Plans.

## 4. Verbindliche Eingaben aus der aktuellen ZBM-Baseline

Vor jeder weiteren Generator- oder Pilotimplementierung müssen mindestens
folgende Nachweise aus `/opt/cocondo/zbm` vorliegen:

```text
Git HEAD und Branch
sauberer Working Tree
letzte acht Commits
Latest Patch inklusive Scope und Status
AGENTS.md und projektlokale Governance
platform/versions/platform.env
.env.example und patchrelevante .env-Konfiguration ohne Secrets
pom.xml und Abhängigkeitsmodell
src/main/** und src/test/**
OpenAPI-/API-Dokumentation
Liquibase-/Persistenzstruktur
Security-/Permission-Verträge
lokale Patch-Scope-Konfiguration
Patch-, Export- und Tooling-Selfcheck-Fähigkeit
aktueller Full-ZIP-Export mit Integritätsmanifest
```

Minimaler Erfassungsblock:

```bash
cd /opt/cocondo/zbm
set +e
set +H

git status --short
git log --oneline -8
./bin/patch.sh show latest
./bin/tooling-selfcheck.sh --no-export
./bin/export.sh full --zip
```

Falls `tooling-selfcheck.sh` in der Zielbaseline nicht vorhanden oder nicht
kompatibel ist, wird dies als Befund dokumentiert. Es wird nicht durch eine
unreviewte direkte Dateiänderung repariert.

## 5. Forensische Zielqualifizierung

Die aktuelle ZBM-Baseline ist vor einer Pilotentscheidung gegen mindestens
folgende Aspekte zu analysieren:

### 5.1 Architektur und Governance

* geltende `AGENTS.md`, ADRs und Projektregeln;
* Package-, Controller-, Service-, Repository-, Mapper- und DTO-Grenzen;
* Core-Nutzung unter `de.cocondo.system`;
* vorhandene lokale Patch-Scope- und Changelog-Konventionen;
* bestehende Test- und Export-Gates.

### 5.2 API- und Laufzeitbestand

* vorhandene fachliche Services und Aggregate;
* bestehende Endpunkte, Operation IDs und DTOs;
* Query-, Detail-, Lookup-, Write-, Validation- und Error-Verträge;
* Rückwärtskompatibilität und mögliche Routenkollisionen;
* bestehende OpenAPI- und Runtime-Evidence.

### 5.3 Persistence

* Entity-, Repository- und Tabellenmodell;
* Liquibase-Changelogs und Datenmigrationen;
* Business-Key-, Unique- und Referenzintegrität;
* Transaktionsgrenzen;
* Verhalten bei Create, Update und Delete.

Ein In-Memory-Store oder eine nur kompilierbare Dummy-Persistenz ist für einen
operativen ZBM-Piloten nicht zulässig. Eine solche Variante wäre höchstens eine
separat benannte Generator-Fixture und keine ZBM-Delivery.

### 5.4 Security

* bestehende Authentifizierungs- und Autorisierungsgrenze;
* Permission Vocabulary und Rollenbezug;
* Controller-, Service- oder Method-Security-Konvention;
* erwartete `401`-/`403`-Verträge;
* Testprincipal- und Security-Testmuster.

Ungeklärte Security darf nicht stillschweigend als "offen" in einen
anwendbaren Fachservice übernommen werden. Solange die Security-Disposition
nicht aufgelöst ist, bleibt der Pilot für Apply blockiert.

## 6. Auswahl des Pilot-Aggregats

Die Golden Spec `administration.business-partner` ist eine neutrale
Generator-Referenz. Sie ist **nicht automatisch** das fachliche Zielmodell von
ZBM.

Das Pilot-Aggregat wird erst nach Baselineanalyse ausgewählt. Es soll:

* fachlich klar abgegrenzt sein;
* eine überschaubare CRUD-/Management-Surface besitzen;
* List, `/all`, `/count`, Detail und höchstens einen eindeutigen Alternate
  Lookup sinnvoll unterstützen;
* keine komplexe Zustandsmaschine voraussetzen;
* keine Bulk-, Relationship- oder Workflow-Commands als Voraussetzung haben;
* vorhandene ZBM-Architektur- und Persistenzmuster repräsentieren;
* ausreichend Tests und fachliche Evidenz ermöglichen;
* ein kontrollierbares Migrations- und Rollback-Risiko besitzen.

Ein bestehender ZBM-Service ist für Standardisierung grundsätzlich vorzuziehen,
wenn seine Migration ohne Parallel-API, Datenverlust oder verdeckte
Kompatibilitätsbrüche möglich ist. `BusinessPartner` darf nur gewählt werden,
wenn die aktuelle ZBM-Fachlichkeit und Baseline diese Zuordnung bestätigen.

## 7. Verbindlicher Target-Binding-Datensatz

Vor Source Rendering muss ein reviewbarer Binding-Datensatz mindestens
folgende Werte enthalten:

| Binding | Regel |
|---|---|
| `targetName` | exakt `zbm` |
| `targetRoot` | aus verifizierter Zielbaseline, erwartet `/opt/cocondo/zbm` |
| `targetGitHead` | vollständiger Commit-Hash der qualifizierten Baseline |
| `targetLatestPatch` | Patch-ID und Status aus dem lokalen ZBM-Patchsystem |
| `targetBasePackage` | aus ZBM-Konfiguration und Source verifiziert, nicht nur aus Springmaster-Descriptor übernommen |
| `targetBasePackagePath` | deterministisch aus dem verifizierten Basispaket |
| `targetCorePackage` | tatsächliche Core-Grenze der ZBM-Baseline |
| `targetPatchScope` | kleinster vorhandener lokaler Scope; niemals ungeprüft `root` |
| `targetPatchLogDir` | zum Scope passendes ZBM-Changelog-Verzeichnis |
| `sliceId` | fachlich bestätigter, kollisionsfreier Slice-Identifier |
| `modulePackage` | ZBM-konform und außerhalb verbotener Demo-Packages |
| `basePath` | kollisionsfrei und rückwärtskompatibel entschieden |
| `persistenceDisposition` | bestehendes Modell wiederverwenden, migrieren oder explizit neu einführen |
| `securityDisposition` | bestehende ZBM-Policy implementieren; kein stilles Default |
| `compatibilityDisposition` | preserve, migrate oder ausdrücklich deprecate |
| `testSelectors` | konkrete targeted Tests plus Full-Test-Verpflichtung |
| `exportCommand` | genau ein abschließender Full-ZIP-Export |

Unbekannte Pflichtbindings werden nicht durch Namenskonventionen oder
Springmaster-Demo-Werte ersetzt. Der Renderer muss fail-closed abbrechen.

## 8. Patch-Scope und Änderungsgrenze im Zielprojekt

Der Zielpatch verwendet den kleinsten ZBM-lokalen Scope, der Source, Tests,
Resources, Dokumentation und Changelog des Piloten regelkonform abdeckt.
Zusätzliche Scopes oder Pfade gehören in die projektlokale ZBM-Konfiguration,
nicht als ZBM-Sonderfall in das zentrale Springmaster-Patchsystem.

Vor der Patch-Erzeugung sind Kollisionen zu klassifizieren:

```text
new       Zielpfad existiert nicht
modify    Zielpfad existiert und wird bewusst standardisiert
unchanged gerenderte Bytes entsprechen bereits dem Ziel
conflict  Zielpfad existiert, aber Eigentum oder Migration ist ungeklärt
```

`conflict` ist ein Stop-Zustand. Es erfolgt kein Überschreiben durch
"last writer wins".

Core-Änderungen, globale Tooling-Änderungen und fachlicher Slice-Code werden
nicht in einem untrennbaren ZBM-Pilotpatch vermischt. Ein notwendiger Core- oder
Generatorfix wird zuerst separat im zuständigen Projekt qualifiziert.

## 9. Operative Phasen nach `000127`

### Phase A – Baseline Intake

1. aktuelle ZBM-Baseline und Hostnachweise entgegennehmen;
2. Exportintegrität prüfen;
3. Git-, Patch- und Governance-Stand bestätigen;
4. keine Zielmutation durchführen.

### Phase B – Forensische Pilotentscheidung

1. Runtime Gap und bestehende Service-Slices erfassen;
2. Pilot-Aggregat begründet auswählen;
3. Persistence, Security und Compatibility entscheiden;
4. Target-Binding-Datensatz reviewen;
5. Stop-Befunde vor Generatorarbeit schließen oder ausdrücklich blockieren.

### Phase C – Generische Renderer-/Assembler-Qualifizierung

1. target-bound Renderer und Patch-Assembler im Springmaster implementieren;
2. keine ZBM-Fachlogik im generischen Tooling hardcodieren;
3. BusinessPartner nur als Golden Reference verwenden;
4. mindestens eine zweite abweichende Projektion testen;
5. deterministische Bytes, Pfade, Manifest und Scope nachweisen;
6. Producer Artifact Preflight gegen eine exakte Ziel-Testkopie ausführen.

### Phase D – ZBM-Sandbox-Dry-run

1. target-lokales Patch-ZIP erzeugen;
2. vollständige Ziel-Baseline-Hashes in `manifest.json` verankern;
3. ZIP- und Scope-Preflight ausführen;
4. lokales ZBM-`patch.sh apply --dry-run` ausführen;
5. Patch in einer isolierten exakten ZBM-Testkopie anwenden;
6. targeted Tests, vollständigen Maven-Test und `git diff --check` dort
   ausführen;
7. noch keinen Live-Apply durchführen.

### Phase E – Explizite Apply-Freigabe

Dem Benutzer werden vor dem Live-Apply mindestens vorgelegt:

* ausgewähltes Aggregat und fachliche Begründung;
* Target HEAD und Latest Patch;
* vollständige Dateiliste und Scope;
* New/Modify/Delete-/Conflict-Klassifikation;
* Persistence-, Security- und Compatibility-Entscheid;
* Dry-run-, Testkopie-, Test- und Preflight-Nachweise;
* Patch-ZIP und SHA-256;
* verbleibende Risiken und Rollback-Pfad.

Ohne ausdrückliches Benutzer-OK endet der Prozess hier.

### Phase F – Kontrollierter Live-Apply

Nach ausdrücklicher Freigabe:

1. Clean-Tree- und Baseline-Preflight im ZBM-Live-Repository;
2. lokaler ZBM-Patch-Apply;
3. targeted Tests;
4. vollständiger Maven-Test;
5. API-/OpenAPI-/Report-Gates;
6. `git diff --check`;
7. exakte Changed-Path-Prüfung;
8. genau ein abschließender ZBM-Full-ZIP-Export;
9. Exportintegritätsprüfung;
10. Commit und Push erst nach separater Abschlussprüfung.

## 10. Pflichtgates

| Gate | Dry-run erforderlich | Apply erforderlich |
|---|---:|---:|
| aktuelle ZBM-Baseline integer | ja | ja |
| Clean Working Tree | ja | ja |
| AGENTS-/ADR-/Governance-Review | ja | ja |
| fachliches Pilot-Aggregat bestätigt | ja | ja |
| Target Bindings vollständig | ja | ja |
| Persistence entschieden und getestet | ja | ja |
| Security entschieden und getestet | ja | ja |
| Route-/Package-/Schema-Kollisionen ausgeschlossen | ja | ja |
| Spec Gate, IR und Blueprint grün | ja | ja |
| Renderer-/Patch-Assembler-Golden und Neutralität grün | ja | ja |
| Artifact Preflight | ja | ja |
| ZBM Patch Dry-run | ja | ja |
| isolierter Apply und Tests | ja | ja |
| ausdrückliche Benutzerfreigabe | nein | ja |
| Live targeted/full tests | nein | ja |
| ein finaler Full-Export | nein | ja |

## 11. Stop-Bedingungen

Der Pilot wird ohne Zielmutation gestoppt, wenn mindestens einer dieser Fälle
vorliegt:

* ZBM-Working-Tree ist nicht sauber;
* Export und Live-HEAD gehören nicht zur selben Baseline;
* `AGENTS.md` oder verbindliche Governance ist nicht ausgewertet;
* Patchsystem oder Scope ist unklar;
* bestehende Zielpfade kollidieren ohne Migrationsentscheid;
* Persistence oder Security ist ungelöst;
* ein benötigter Core- oder Toolingfix wird in den Fachpatch hineingemischt;
* Baseline-Hashes, Payload, Dateimodi oder Exportintegrität weichen ab;
* targeted oder vollständige Tests sind rot;
* API-/OpenAPI-/Report-Verträge sind nicht belegt;
* die ausdrückliche Apply-Freigabe fehlt.

## 12. Evidence-Artefakte für den Piloten

Die operative Pilot-Delivery muss mindestens folgende Evidence erzeugen:

```text
ZBM baseline intake report
forensic runtime-gap report
pilot aggregate decision
resolved target-binding record
validated Slice-Spec
canonical IR
canonical target-bound blueprint
rendered file manifest
patch manifest with target live hashes
target artifact-preflight report
ZBM dry-run log
isolated apply and test logs
live apply and test logs, falls freigegeben
API report-family evidence
single final ZBM Full-ZIP export
export-integrity and closure evidence
```

Laufzeitlogs bleiben Validation-Evidence und werden nicht pauschal committed.
Das fachliche Changelog und ausdrücklich versionierte Review-Dokumente bleiben
Teil des Zielpatches.

## 13. Definition of Done

### DoD `000127` – Pilotplanung

```text
ZBM-Eingaben sind vollständig definiert.
Aktueller Springmaster-Descriptor ist korrekt eingeordnet.
BusinessPartner ist als Reference, nicht als automatische ZBM-Fachlichkeit markiert.
Persistence, Security, Compatibility und Scope sind explizite Decisions.
Dry-run-, Test-, Apply-, Export- und Freigabepfad sind deterministisch beschrieben.
Keine ZBM-Datei wurde gelesen, erzeugt oder verändert.
Kein ZBM-Patch wurde erzeugt oder angewendet.
```

### DoD P1.4 – Sandbox-Dry-run-Bereitschaft

```text
Aktuelle ZBM-Baseline ist integer und forensisch analysiert.
Pilot-Aggregat und Target Bindings sind bestätigt.
Generischer Renderer und Patch-Assembler sind qualifiziert.
Target-lokales Patch-ZIP besteht Artifact Preflight und ZBM-Dry-run.
Isolierter Apply sowie targeted und vollständige Tests sind grün.
Live-ZBM bleibt unverändert.
```

### DoD P1.4 – Operative Pilot-Delivery

```text
Benutzer hat den konkreten Live-Apply ausdrücklich freigegeben.
ZBM Live-Baseline entspricht weiterhin den erwarteten Hashes.
Apply, targeted Tests, Full Maven, API-Gates und diff check sind grün.
Genau ein finaler integritätsgeprüfter ZBM-Full-Export liegt vor.
Commit und Push sind nach Abschlussreview erfolgt.
```

Nach Erreichen der jeweiligen DoD werden keine spekulativen Folgepatches
abgeleitet. Weitere Arbeiten beginnen nur aus einem konkreten Befund oder einem
neuen Benutzerauftrag.
