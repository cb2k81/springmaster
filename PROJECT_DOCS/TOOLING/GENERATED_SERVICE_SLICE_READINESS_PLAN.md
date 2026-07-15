# Generated Service Slice Readiness Plan

Patch: `000077_springmaster_generated_service_slice_readiness_plan`

Marker-Ausrichtung: `000078_springmaster_generated_service_slice_readiness_marker_alignment`

## Zweck

Dieses Dokument definiert den nächsten Reifegrad nach der erfolgreichen Project-New-Instanziierung aus Patch `000076`.

`000076` hat bewiesen, dass Springmaster ein neues technisches Java-Backend-Skeleton erzeugen kann. `000077` legt fest, was zusätzlich erforderlich ist, damit aus diesem Skeleton ein fachlicher Backend-Service-Slice entsteht.

Der Plan ist bewusst documentation-only. Er erzeugt noch keinen Slice-Generator, kopiert keinen Core in Zielprojekte, führt keine Zielprojekt-Scans aus und aktiviert keine strict gates.

## Ausgangslage nach 000076

Springmaster ist aktuell als technische Skeleton-Factory validiert.

Für Acceptance- und Verify-Skripte wird diese Fähigkeit zusätzlich mit dem stabilen Kontrollbegriff `technical Backend-Skeleton` benannt. Der Begriff ist synonym zur deutschen Formulierung `technisches Java-Backend-Skeleton` und dient nur der Marker-Kompatibilität; er ändert keine fachliche oder technische Entscheidung.

Nachgewiesen ist:

| Fähigkeit | Stand |
|---|---|
| Neues Backend-Skeleton erzeugen | validiert durch `bin/project-new-acceptance.sh` |
| Generated-project Maven-Test | validiert |
| Patch-Bootstrap im generierten Projekt | validiert |
| Export im generierten Projekt | validiert |
| DBTool-Status ohne lokale `.env` | validiert |
| Sanitized DB defaults | validiert |
| Core-Scan-Ausrichtung auf `de.cocondo.system` | im Skeleton vorbereitet |
| Fachlicher Aggregate-Slice | noch nicht erzeugt |
| Core-Verteilung in neue Projekte | noch nicht entschieden |
| Zielprojekt-Delivery | weiterhin blockiert |

Damit ist Springmaster für den technischen Projektstart tauglich. Für einen neuen fachlichen Service fehlt noch ein definierter Übergang von Skeleton zu Service-Slice.

## Zielbild eines generated service slice

Ein generated service slice ist kein vollständiger produktiver Service. Er ist ein erster fachlicher, testbarer Aggregate-Slice, der in einem neu instanziierten Backend-Projekt dieselben Architekturentscheidungen wie der Springmaster CatalogItem Candidate-Slice nachvollziehbar anwendet.

Der erste Slice soll mindestens enthalten:

| Bereich | Mindestinhalt |
|---|---|
| Aggregate | eine kleine fachliche Resource mit fachneutralem Beispielnamen oder explizit übergebener Domain-/Aggregate-Namen |
| API | Controller mit Collection-, Detail-, Create-, Full-Update- und bodyless Delete-Kontrakt |
| DTOs | getrennte Create-, Update-, Read- und ListItem-DTOs |
| Validation | Bean Validation am Controller-Boundary und Service-Boundary-Validation für Create und Update |
| Mapping | expliziter Mapper zwischen Request-/Response-DTO und Domain-/Persistence-Modell |
| Service | Service als Application Boundary, kein Repository-Zugriff aus Controller |
| Error Contract | strukturierte Fehlerantwort mit `errorId`, Status, Typ und optionalen Violations |
| Tests | Controller-, Service-, Mapper- und Validator-Tests |
| Evidence | maschinenlesbare Slice-Evidence analog `CATALOGITEM_CANDIDATE_SLICE_EVIDENCE.json` |

Der Slice darf zunächst weiterhin `candidate-reference-slice` sein. Er darf nicht automatisch als `canonical-reference-slice` klassifiziert werden.

## Abgrenzung zu Project-New

`project-new.sh` bleibt konservativ. Es erzeugt ein technisches Backend-Skeleton, keine fachliche Domäne.

Der generated service slice ist eine zweite Stufe:

1. `project-new.sh` erzeugt das technische Projekt.
2. Ein späteres Slice-Tool oder ein deterministischer Patch erzeugt den fachlichen Aggregate-Slice.
3. Die Slice-Evidence dokumentiert, welche Architekturstandards erfüllt, teilweise erfüllt oder bewusst deferred sind.

Diese Trennung verhindert, dass jedes neue Projekt automatisch fachlichen Beispielcode enthält, der später wieder entfernt werden muss.

## Core-Verteilungsentscheidung

Der wiederverwendbare Springmaster Core liegt aktuell unter:

```text
src/main/java/de/cocondo/system/**
src/test/java/de/cocondo/system/**
```

Das Skeleton scannt bereits `de.cocondo.system`, enthält den Core-Code aber noch nicht automatisch.

Für die erste generated-service-slice-Stufe gilt folgende Arbeitsentscheidung:

| Option | Bewertung |
|---|---|
| Maven-Artefakt | Zielbild, aber noch nicht validiert |
| Git-Submodule / separates Repository | aktuell nicht eingeführt |
| Source-Core-Kopie per deterministischem Patch | kurzfristig passend für Springmaster-Workflow |
| gar kein Core im Zielprojekt | nur für Minimal-Skeleton ausreichend, nicht für echte Slice-Referenz |

Der nächste Umsetzungsschritt soll daher einen konservativen `source-core-copy`-Pfad planen oder implementieren, bevor ein Slice im generierten Projekt Core-Typen voraussetzt.

Dabei gelten Schutzregeln:

* Core-Code bleibt unter `de.cocondo.system`.
* Es wird kein Springmaster-App-Code aus `de.cocondo.platform.*` in Zielprojekte übertragen.
* Core-Tests gehören zum übertragenen Core-Slice.
* Zielprojekt-spezifische Scopes und Zusatzpfade dürfen nicht in Springmaster hart codiert werden.
* Bestehende Zielprojekte werden weiterhin nicht ohne explizite Freigabe gescannt oder verändert.

## Slice-Blueprint-Anforderungen

Der spätere Slice-Blueprint muss aus den Standards ableitbar sein, nicht aus zufälligem Demo-Code.

Pflichtreferenzen:

| Thema | Referenz |
|---|---|
| API Endpoint Contract | `PROJECT_DOCS/STANDARDS/API/API_ENDPOINT_CONTRACT_STANDARD.md` |
| Query/Paging/Sorting | `PROJECT_DOCS/STANDARDS/API/API_QUERY_REFERENCE_DATA_CONSISTENCY_STANDARD.md` |
| DTO Boundary | `PROJECT_DOCS/STANDARDS/API/DTO_BOUNDARY_AND_VALIDATION_STANDARD.md` |
| Error Contract | `PROJECT_DOCS/STANDARDS/API/API_ERROR_CONTRACT_STANDARD.md` und `API_ERROR_IDENTITY_STATUSCODE_CONSISTENCY_STANDARD.md` |
| Application Boundary | `PROJECT_DOCS/STANDARDS/CONTROLLER_SERVICE_USECASE_TRANSACTION_STANDARD.md` |
| Persistence Identity | `PROJECT_DOCS/STANDARDS/DOMAIN_ENTITY_PERSISTENCE_STANDARD.md` |
| Mapping | `PROJECT_DOCS/STANDARDS/MAPPING_STANDARD.md` |
| Security | `PROJECT_DOCS/STANDARDS/SECURITY_PERMISSION_BOUNDARY_STANDARD.md` |
| Candidate Evidence | `PROJECT_DOCS/DEMO/CATALOGITEM_CANDIDATE_SLICE_EVIDENCE.json` |

Der CatalogItem-Slice darf als Implementation Reference dienen, bleibt aber ein Candidate. Für generierte Services darf aus ihm kein unkritischer Copy-and-Paste-Standard entstehen.

## Minimaler Contract für den ersten generated slice

Der erste erzeugbare fachliche Slice soll mit einem neutralen Beispiel-Aggregate validiert werden, beispielsweise `SampleRecord` oder `TaskItem` im generierten Acceptance-Projekt.

Mindest-Endpunkte:

```text
GET    /api/<domain>/<resources>?page=&size=&sortBy=&sortDir=
GET    /api/<domain>/<resources>/{id}
POST   /api/<domain>/<resources>
PUT    /api/<domain>/<resources>/{id}
DELETE /api/<domain>/<resources>/{id}
```

Optionale Endpunkte wie `/options`, `/search`, Relationship-Endpunkte oder Commands bleiben out of scope, bis der Minimal-Slice stabil ist.

## Readiness-Kriterien

Ein generated service slice gilt erst als readiness-bestätigt, wenn die folgende Matrix erfüllt ist:

| Kriterium | Erwartung |
|---|---|
| Projektinstanziierung | `project-new-acceptance.sh --generated-maven-test` bleibt grün |
| Core-Verfügbarkeit | der benötigte Core ist im generierten Projekt vorhanden oder bewusst nicht benötigt |
| Slice-Erzeugung | der Slice wird deterministisch erzeugt oder als Patch angewendet |
| Tests | generiertes Projekt besteht `mvn test` |
| Patchsystem | generierter Slice ist im Projekt als Patch nachvollziehbar |
| Export | generiertes Projekt erzeugt Full-ZIP-Export |
| Evidence | Slice-Evidence ist maschinenlesbar und klassifiziert Candidate/Canonical/Deferred-Status |
| Security | mindestens `documented-deferred-security`; produktiv erst mit implementierter Security |
| Persistence | In-memory oder einfache Store-Mechanik darf nur als Candidate-Foundation gelten |
| Gates | Springmaster report-only Gates bleiben grün und nicht strict |

## Risiken

| Risiko | Bewertung | Gegenmaßnahme |
|---|---|---|
| Core-Verteilung unklar | hoch | source-copy-Plan oder Maven-Artefakt-Strategie separat entscheiden |
| Demo-Candidate wird vorschnell canonical | mittel | Evidence muss `candidate-reference-slice` und `not-canonical` explizit führen |
| Generator erzeugt zu viel Fachcode | mittel | Project-New und Slice-Generation getrennt halten |
| Security bleibt zu lange deferred | hoch für produktive Nutzung | Security-Implementation als späteren Canonical-Blocker behandeln |
| Persistence/Liquibase fehlen | hoch für produktive Nutzung | Durable-Persistence-Slice vor Canonical-Promotion verlangen |
| Zielprojekt-Delivery wird zu früh aktiviert | hoch | Target comparison/delivery bleiben blocked bis explizite Freigabe |

## Entscheidung nach 000077

Springmaster bleibt nach `000077` eine validierte technische Skeleton-Factory mit einem Candidate-Slice-Blueprint.

Die nächste Reifestufe ist nicht die automatische Zielprojekt-Auslieferung. Die nächste Reifestufe ist die definierte Erzeugung oder Anwendung eines ersten fachlichen Slice in einem frisch generierten Projekt.

## Stand nach 000080

Patch `000080_springmaster_generated_service_slice_blueprint_spec` konkretisiert den Blueprint für spätere fachliche Service-Slices und definiert den ersten operativen Konzepttest am Zielprojekt `zbm`.

Festgelegt wird:

* `project-new` bleibt die technische Initialisierungsschicht;
* `platform-update` bleibt die spätere Update-/Delivery-Mechanik;
* ein Service-Slice-Generator erzeugt später Zielprojekt-Patches statt direkter Mutationen;
* `zbm` ist der erste Initialisierungskandidat;
* IDM und Personnel bleiben deferred und werden nicht beliefert;
* Core-Verteilung startet kurzfristig als kontrollierter `source-core-copy`-Pfad;
* fachliche Slice-Erzeugung bleibt ein eigener Folgepatch.

Der nächste operative Schritt ist der `ZBM Initialization Concept Test` gegen `/opt/cocondo/zbm`.
