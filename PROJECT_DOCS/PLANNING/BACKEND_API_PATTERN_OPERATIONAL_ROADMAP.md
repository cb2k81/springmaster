# Springmaster Backend API Pattern Operational Roadmap

## 1. Zweck

Dieses Dokument persistiert die operative Aufgabenliste für die Weiterentwicklung von Springmaster als Master-/Template- und Validierungsbasis für Backend-Applikationen und API-Endpoints.

Der Query-/List-/All-/Count-Strang ist mit Patch `000114_springmaster_query_security_scope_parity_reference` auf Candidate-Reference-Reifegrad abgeschlossen. Seit `000116`/`000117` ist der globale API Error Contract im Core etabliert und im CatalogItem-Demo-Slice operativ genutzt. Seit `000118` ist Detail/Lookup report-only und golden-fixture-backed belegt. Seit `000119` ist Create/Update/Delete als Write API Contract report-only abgesichert. Seit `000120` ist Request Validation/OpenAPI-required-field alignment für CatalogItem belegt. Die nächsten Arbeiten dürfen diesen Query-Strang nicht unbegründet erweitern, sondern müssen die verbleibenden API- und Application-Patterns systematisch schließen.

## 2. Aktueller Reifegrad nach 000120

Erreicht ist:

```text
Query Contract Standard = executable report-backed,
CatalogItem-fixture-backed,
OpenAPI-evidence-backed,
persistent/JPA-reference-backed,
security/scope-parity-backed
```

Konkret vorhanden sind:

* dokumentierte Standards für paged list, `/all` und `/count`;
* `CountResponseDTO` und Query-Operations-Interfaces im Core;
* ausführbares Query-Contract-Report-Tooling;
* deterministische CatalogItem-Golden-Fixture;
* OpenAPI-Evidence für Query-Endpunkte;
* JPA-Count-Referenz ohne Listenmaterialisierung;
* Security-/Data-Scope-Paritätsreferenz für Query-Operationen;
* Full-Maven-Verifikation in den zugehörigen Runnern;
* Core-globaler API Error Contract mit CatalogItem-Migration;
* Detail/Lookup Contract Report mit CatalogItem-Golden-Evidence und OpenAPI-/MockMvc-Nachweis.

Nicht Ziel weiterer unmittelbarer Arbeit sind:

* erneute Query-Basisstandardisierung;
* weitere Query-Dokumentation ohne neue operative Verifikation;
* Strict-Gate-Promotion ohne vorherige Generated-Slice-Adoptionsentscheidung;
* Cursor-/Keyset-Pagination oder Async Export ohne konkrete Last-/SLA-Anforderung.

## 3. Priorisierte Aufgaben


Aktueller operativer Stand nach `000120`:

| Status | Patch | Ergebnis |
|---|---|---|
| abgeschlossen | `000116_springmaster_global_api_error_contract_core` | Core-globaler API Error Contract |
| abgeschlossen | `000117_springmaster_catalogitem_global_api_error_handler_migration` | CatalogItem nutzt globalen Error Handler |
| abgeschlossen | `000118_springmaster_detail_lookup_contract_report` | Detail/Lookup Report + Golden Fixture |
| abgeschlossen | `000119_springmaster_write_api_contract_report` | Create/Update/Delete Contract Report |
| abgeschlossen | `000120_springmaster_request_validation_openapi_gate` | Bean Validation ↔ OpenAPI required fields |
| aktueller Schritt | `000121_springmaster_generated_slice_api_pattern_adoption_plan` | Generator-/Template-Adoption planen |
| danach | `000122_springmaster_generated_slice_spec_contract` | Slice-Spec-Vertrag und Golden Spec definieren |


### Abgeschlossen – `000116_springmaster_global_api_error_contract_core` und `000117_springmaster_catalogitem_global_api_error_handler_migration`

**Ziel:** Wiederverwendbaren globalen API-Error-Contract im System-Core etablieren und CatalogItem vom lokalen Fehlerhandling auf den Core-Standard migrieren.

**Begründung:** Detail-, Write-, Command-, Security- und Validation-Patterns benötigen zuerst einen stabilen, zentralen Error Contract. Der aktuelle CatalogItem-Slice besitzt lokale `@ExceptionHandler` und lokale Error-DTOs. Das ist funktional, aber nicht als Master-/Template-Standard ausreichend.

**Mindestumfang:**

* Core-DTOs für `ApiErrorResponse` und `ApiViolationDTO`;
* kanonische Error-Typen, mindestens für Validation, Invalid Request, Not Found, Conflict, Unauthorized, Forbidden und Internal Error;
* zentraler `@ControllerAdvice` oder äquivalenter globaler Handler;
* sichere Fallback-Behandlung ohne Stacktrace-, SQL- oder Java-Klassennamen-Leakage;
* `errorId`-Erzeugung mit stabiler Form;
* CatalogItem-Migration weg von lokalen Error-DTOs;
* MockMvc-/Unit-Tests für `400`, `404`, `409` und sichere `500`-Antwort;
* OpenAPI-Basisnachweis für das Error-Schema, soweit mit dem bestehenden Setup deterministisch möglich.

**Nicht Bestandteil:**

* Detail-/Lookup-Report-Gate;
* Write-API-Report-Gate;
* vollständige Spring-Security-Integration;
* Observability-/MDC-Konzept.

**Pflichtverifikation:**

```bash
mvn -B -ntp test -Dtest='*Error*Test,CatalogItemControllerTest'
mvn -B -ntp test
git diff --check
./bin/export.sh full --zip
```

### Abgeschlossen – `000118_springmaster_detail_lookup_contract_report`

**Ziel:** Detail- und Alternate-Key-Lookup-Endpunkte analog zum Query-Strang als Contract absichern.

**Begründung:** Generierte Anwendungen benötigen ein standardisiertes Muster für Einzelobjektabfragen und eindeutige fachliche Schlüssel. CatalogItem enthält bereits `/{id}` und `/by-sku/{sku}`, aber noch kein eigenständiges Detail-/Lookup-Gate.

**Mindestumfang:**

* Contract-Dokumentation oder Erweiterung der bestehenden Endpoint-Standards für Detail/Lookup;
* CatalogItem-Golden-Evidence für `GET /api/demo/catalog/items/{id}` und `GET /api/demo/catalog/items/by-sku/{sku}`;
* OpenAPI- und MockMvc-Nachweis;
* `404` bei unbekannter ID oder unbekanntem Alternate Key;
* `409` als Standard für verletzte Eindeutigkeit bei Alternate-Key-Lookup, sofern runtimefähig demonstrierbar;
* Prüfung, dass Create-`Location` auf den Detail-Endpunkt verweist;
* keine öffentliche `findOne`-/`findFirst`-/`findAny`-Semantik als Contract-Sprache.

**Abhängigkeit:** P0 Error-Core muss abgeschlossen sein.

### P1 – `000119_springmaster_write_api_contract_report`

**Ziel:** Create, Full Update und Single Delete als schreibende API-Basismuster report- und testfähig absichern.

**Mindestumfang:**

* `POST /api/<domain>/<resources>` mit Request DTO;
* `PUT /api/<domain>/<resources>/{id}` mit Request DTO;
* bodyless `DELETE /api/<domain>/<resources>/{id}`;
* `201 Created` mit `Location` für Create;
* `200 OK` mit DTO für Update;
* `204 No Content` für Delete;
* standardisierte Error Responses für `400`, `404`, `409`;
* OpenAPI-Prüfung: `DELETE` darf kein `requestBody` besitzen;
* CatalogItem-Golden-Evidence.

**Nicht Bestandteil:**

* Bulk Delete;
* Relationship Commands;
* State Commands;
* Command Precheck.

**Abhängigkeiten:** P0 Error-Core und P1 Detail-/Lookup-Contract.

**Status nach Umsetzung:** `000119` ergänzt den report-only Write API Contract Report mit CatalogItem Golden Fixture, MockMvc-/OpenAPI-Evidence und bleibt ohne Bulk-/Command-/Relationship-Scope.

### P1 – `000120_springmaster_request_validation_openapi_gate`

**Ziel:** Bean-Validation-Regeln, Boundary-DTOs und OpenAPI-required-Felder konsistent prüfen.

**Mindestumfang:**

* Abgleich von `@NotNull`, `@NotBlank` und vergleichbaren Boundary-Validation-Regeln mit OpenAPI `required`;
* Nachweis, dass Entities nicht als öffentliche `@RequestBody` verwendet werden;
* Trennung von CreateDTO, UpdateDTO und ResponseDTO prüfen;
* standardisierte `400 VALIDATION_FAILED`-Antworten mit `violations`;
* Nested-Validation-Regeln für eingebettete DTOs dokumentieren und testen.

**Abhängigkeiten:** P0 Error-Core und Write-API-Basismuster.

### P2 – `000121_springmaster_generated_slice_api_pattern_adoption_plan`

**Ziel:** Die erreichten API-Patterns in die Generator-/Template-Schicht überführen, ohne sofort Zielprojekte zu verändern.

**Mindestumfang:**

* Plan für Generated-Service-Slice Blueprint mit Query, Detail, Write und Error Contract;
* Definition, welche Bestandteile aus CatalogItem nur Referenz sind und welche generierbar sind;
* Akzeptanzkriterien für generierte Projekte;
* Gate-Anforderungen für generierte Slices;
* keine direkte Target-Delivery.

**Abhängigkeiten:** P0 bis P1 müssen abgeschlossen sein.

**Status nach Umsetzung:** `000121` persistiert den Adoptionsplan unter `PROJECT_DOCS/TOOLING/GENERATED_SLICE_API_PATTERN_ADOPTION_PLAN.md`. Die nächsten Schritte sind Spec Contract, Intermediate Model und Patch-Blueprint-Dry-run. Zielprojekt-Delivery bleibt weiterhin gesperrt.

## 4. Nachgelagerte Themen

Diese Themen sind relevant, aber aktuell nicht Teil der nächsten unmittelbaren Patch-Reihe:

| Thema | Einordnung | Startbedingung |
|---|---|---|
| Command Result DTO / Bulk Delete | später | Write-Basismuster stabil |
| State Commands | später | Command-Foundation vorhanden |
| Relationship Commands | später | mindestens zweites Demo-Aggregat oder Beziehungsslice vorhanden |
| Security Runtime Integration | später | Error-Core und Scope-Pattern stabil |
| Persistence/Liquibase Reference Slice | später | echter persistenter Demo-/Generated-Slice geplant |
| Report-Gate-Konsolidierung | später | Query, Detail, Write und Error Reports vorhanden |
| Strict Gate Promotion | später | Report-only Gates stabil und Golden Fixtures vorhanden |
| Cursor-/Keyset-Pagination | später | konkrete große Datenmenge oder SLA-Anforderung |
| Async Export | später | konkrete Laufzeit-/Timeout-Anforderung |
| Observability / Correlation / Audit | später | Error-Core und Command-Basismuster stabil |

## 5. Operative Regeln für die Abarbeitung

### 5.1 Patch-Schnitt

* Ein Patch darf nur ein Pattern oder eine klar abgegrenzte Reparatur betreffen.
* Fehlerbehandlung, Detail, Write und Validation dürfen nicht in einem Sammelpatch vermischt werden.
* Tooling-Parser-Änderungen müssen durch Golden Fixtures oder gezielte Regressionstests abgesichert werden.
* Dokumentationspatches dürfen keine Runtime-Versprechen enthalten, die nicht durch Tests oder Gates belegt sind.

### 5.2 Vorprüfung vor Auslieferung

Für jeden Patch muss vor Auslieferung explizit unterschieden werden zwischen:

```text
lokal/verbindlich ausgeführt
strukturell geprüft
nur im Runner auf Zielhost verifizierbar
```

Code-, Test- und Tooling-Patches dürfen nicht als vollständig geprüft bezeichnet werden, wenn kein echter Targeted Test und kein Full-Maven-Lauf ausgeführt wurde. Wenn Maven lokal nicht verfügbar ist, muss die Auslieferung ausdrücklich als strukturell geprüft mit verbindlicher Host-Runner-Verifikation bezeichnet werden.

### 5.3 Baseline-Regel

Patches werden nur gegen den zuletzt bestätigten sauberen Stand erstellt:

```text
git status --short  -> leer
HEAD                -> bekannt
Latest Patch         -> bekannt
Full Export          -> aktuell
```

Die Manifest-Hashes müssen aus genau diesem Stand berechnet werden. Der Live-Baseline-Guard ist Pflicht und darf nicht durch manuelle Annahmen ersetzt werden.

### 5.4 Abschlusskriterium pro Patch

Ein Patch gilt erst als abgeschlossen, wenn alle Punkte erfüllt sind:

* Runner `DONE`;
* relevante Targeted Tests grün;
* bei Code/Tooling Full-Maven-Test grün;
* `git diff --check` grün;
* Full-ZIP-Export erzeugt;
* Commit erstellt;
* Push nach `origin/main` erfolgreich;
* `git status --short` leer;
* `./bin/patch.sh show latest` zeigt den erwarteten Patch.

## 6. Abschlusskriterium der nächsten Roadmap-Etappe

Die nächste Roadmap-Etappe ist erreicht, wenn P0 bis P2 abgeschlossen sind und Springmaster als Master-/Template-Basis folgende Pattern-Familien operativ belegt:

```text
Query/List/All/Count
Global Error Contract
Detail/Lookup
Create/Update/Delete
Request Validation / DTO Boundary
Generated Slice Adoption Plan
```

Erst danach sollen nachgelagerte Themen wie Command-Bulk, Relationship Commands, Strict-Gate-Promotion oder Cursor-/Keyset-Pagination neu priorisiert werden.

## 7. Fortschreibung nach Patch 000120

Patch `000120_springmaster_request_validation_openapi_gate` schließt die P1-Basisfamilie Request Validation / DTO Boundary auf Candidate-Reference-Niveau ab.

Erreicht:

```text
Query/List/All/Count                  abgeschlossen
Global Error Contract                 abgeschlossen
Detail/Lookup                         abgeschlossen
Create/Update/Delete                  abgeschlossen
Request Validation / DTO Boundary     abgeschlossen
```

Der nächste priorisierte Schritt ist jetzt:

```text
000121_springmaster_generated_slice_api_pattern_adoption_plan
```

Ziel dieses Folgepatches ist keine neue Runtime-Funktion, sondern die Überführung der belegten API-Pattern-Familien in Generator-/Template-Anforderungen, damit spätere Zielprojekte die Standards deterministisch übernehmen können.


## Status nach Patch 000122

Patch `000122_springmaster_generated_slice_spec_contract` konkretisiert den in `000121` geplanten Übergang in einen expliziten Slice-Spec-Vertrag.

Erreicht:

```text
GeneratedServiceSlice YAML contract       dokumentiert
Neutral golden slice spec                 vorhanden
API surface families                      Query, Detail, Write, Validation, Error
Target delivery boundary                  patch-zip only
Demo package reuse                        explizit verboten
```

Der nächste priorisierte Schritt ist jetzt:

```text
000123_springmaster_generated_slice_spec_fixture_gate
```

Ziel dieses Folgepatches ist ein ausführbares Fixture-/Report-Gate für den Slice-Spec-Vertrag, bevor Intermediate Model oder Patch-Blueprint-Generator implementiert werden.


## Status after Patch 000123

Patch `000123_springmaster_generated_slice_spec_fixture_gate` closes the executable Slice-Spec fixture gate.

```text
GeneratedServiceSlice YAML parse       PASS
Required top-level contract fields     PASS
List/All/Count surface                 PASS
Detail/alternate lookup surface        PASS
Create/Update/Delete surface           PASS
DTO and validation boundary            PASS
Global 400/404/409 error families       PASS
Required report families               PASS
Patch-only delivery boundary            PASS
Demo package reuse prohibition          PASS
Golden report findings                  0
```

The gate is strict for the neutral BusinessPartner golden fixture and is protected by positive golden comparison and negative fail-closed tests. It does not generate Java code or mutate a target project.

The remaining ordered work is:

```text
P1  000125_springmaster_generated_slice_intermediate_representation
P1  000126_springmaster_generated_slice_patch_blueprint_dry_run
P1  000127_springmaster_zbm_generated_slice_pilot_plan
```

No ZBM apply or generated target delivery may occur without the current ZBM baseline and an explicit user instruction.

## Status after Patch 000124

Patch `000124_springmaster_patch_artifact_preflight_hardening` closes the remaining P0 process gap. Patch artifacts can now be qualified against a clean committed baseline, exact live hashes, strict payload hygiene and an isolated worktree apply. Full exports expose authoritative raw-byte file manifests and optional embedded closure evidence.

The ordered remaining work is:

```text
P1  000125_springmaster_generated_slice_intermediate_representation
P1  000126_springmaster_generated_slice_patch_blueprint_dry_run
P1  000127_springmaster_zbm_generated_slice_pilot_plan
```
