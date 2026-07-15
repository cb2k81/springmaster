# Generated Slice API Pattern Adoption Plan

Patch: `000121_springmaster_generated_slice_api_pattern_adoption_plan`
Status: documentation-only adoption plan

## 1. Zweck

Dieses Dokument definiert, wie die seit `000114` bis `000120` etablierten API-Pattern-Nachweise in die spätere Generated-Service-Slice-Schicht übernommen werden.

Der Patch erzeugt noch keinen Generator-Code, verändert keine Zielprojekte und aktiviert keine strict Gates. Er schließt die operative Planungsphase ab, damit die nächste Implementierungsstufe nicht mehr aus einzelnen Demo-Beobachtungen, sondern aus einem konsolidierten API-Pattern-Zielbild abgeleitet wird.

## 2. Ausgangslage nach 000120

Springmaster besitzt jetzt für den CatalogItem Candidate Reference Slice folgende belegte API-Pattern-Familien:

| Pattern-Familie | Referenzstand |
|---|---|
| Query/List/All/Count | report-only Tooling, Golden Fixture, OpenAPI Evidence, JPA Count Reference, Security/Data-Scope Parity |
| Global Error Contract | Core-owned Error DTOs, `GlobalApiExceptionHandler`, CatalogItem Migration |
| Detail/Lookup | Detail/Lookup Contract Report, Golden Fixture, OpenAPI Evidence |
| Write API | Create/Update/Delete Contract Report, Golden Fixture, OpenAPI Evidence |
| Request Validation/OpenAPI | DTO Boundary, Bean Validation Required Fields, OpenAPI `required` Evidence |

Damit ist die Grundlage für eine Generated-Slice-Adoption vorhanden. Die Adoption darf aber nicht durch Copy-and-Paste aus dem Demo-Slice erfolgen. Der Generator muss explizite Contracts, Inputs, Outputs, Evidence und Akzeptanzprüfungen besitzen.

## 3. Nicht-Ziele

`000121` ist kein Implementierungspatch für einen produktiven Slice-Generator.

Nicht enthalten sind:

* Generator-Code;
* Template-Renderer;
* Änderungen an `project-new` oder `platform-update`;
* Zielprojekt-Delivery;
* ZBM-, IDM-, Personnel- oder sonstige Target-Mutation;
* strict Gate Promotion;
* Bulk Delete, State Commands oder Relationship Commands;
* Persistenz-/Liquibase-Canonical-Promotion;
* Maven-Artefakt-Publishing für den Core.

## 4. Adoptionsprinzipien

### 4.1 Contract zuerst, Generator danach

Ein Generated Slice wird erst erzeugt, wenn seine Eingabe-Spec, Zielstruktur, API-Fläche, DTO-Regeln, Tests und Evidence-Verträge dokumentiert und reviewbar sind.

Die Reihenfolge lautet:

```text
API Pattern Contract
-> Slice Spec Contract
-> Generator Intermediate Model
-> Renderer / Patch Writer
-> Generated Target Patch
-> Target-local Patch Apply
-> Target Acceptance Evidence
```

### 4.2 Generate != Apply

Springmaster darf Zielprojekte nicht direkt mutieren. Der Generator erzeugt reviewbare Patch-ZIPs für das lokale Patchsystem des Zielprojekts.

Pflichtregeln:

* kein direkter Schreibzugriff in ein Zielprojekt außerhalb eines explizit erzeugten Patch-Artefakts;
* kein automatisches Apply ohne Zielprojektfreigabe;
* `TARGET_DELIVERY_ENABLED=false` bleibt Default;
* Zielprojekt-spezifische Scopes bleiben in der Zielprojekt-Konfiguration, nicht hart codiert in Springmaster.

### 4.3 CatalogItem ist Referenz, nicht Template-Kopie

CatalogItem ist die belegte Candidate Reference. Daraus dürfen Patterns abgeleitet werden, aber kein unkritisches Text- oder Code-Copying.

Generierbar sind:

* API-Endpoint-Familien;
* DTO-Boundary-Struktur;
* Report-/Evidence-Artefakte;
* Testklassenmuster;
* Service-/Mapper-/Validator-Schichtung.

Nicht automatisch generierbar sind:

* CatalogItem-Fachbegriffe;
* Catalog-spezifische Message Keys;
* in-memory Demo-Store als produktiver Persistence-Standard;
* Demo-spezifische Fixture-Daten;
* Scope- oder Permission-Namen ohne Slice-Spec.

## 5. Generated-Service-Slice Zielbild

Ein generierter fachlicher Service-Slice muss mindestens folgende Artefaktfamilien enthalten.

### 5.1 API Surface

Pflichtendpunkte für managementfähige Aggregate:

```text
GET    /api/<domain>/<resources>
GET    /api/<domain>/<resources>/all
GET    /api/<domain>/<resources>/count
GET    /api/<domain>/<resources>/{id}
POST   /api/<domain>/<resources>
PUT    /api/<domain>/<resources>/{id}
DELETE /api/<domain>/<resources>/{id}
```

Optionale Endpunkte:

```text
GET    /api/<domain>/<resources>/by-<key>/{value}
POST   /api/<domain>/<resources>/search
POST   /api/<domain>/<resources>/search/all
POST   /api/<domain>/<resources>/search/count
```

Optionale Endpunkte dürfen nur erzeugt werden, wenn die Slice-Spec ihre fachliche Eindeutigkeit, Filtersemantik oder Such-DTOs explizit definiert.

### 5.2 DTO Boundary

Pflicht-DTOs:

| DTO | Zweck |
|---|---|
| `<Aggregate>CreateDTO` | `POST` Request Body |
| `<Aggregate>UpdateDTO` | `PUT` Request Body |
| `<Aggregate>DTO` oder `<Aggregate>ResponseDTO` | Detail-/Write-Response |
| `<Aggregate>ListItemDTO` | Listen-Response |
| `<Aggregate>PagedQuery` | typed paged query input |
| `<Aggregate>AllQuery` | typed complete-result query input |
| `<Aggregate>CountQuery` | typed count query input |

Regeln:

* Domain Entities dürfen nicht als `@RequestBody` exponiert werden.
* Controller verwenden `@Valid @RequestBody` für Create und Update.
* Bean Validation Required Fields müssen mit OpenAPI `required` übereinstimmen.
* Response DTOs dürfen keine Persistence- oder Repository-Typen exponieren.

### 5.3 Error Contract

Generierte Slices verwenden ausschließlich den Core-globalen API Error Contract.

Pflicht:

* `ResourceNotFoundException` oder fachlich äquivalente Core-kompatible Not-Found-Exception;
* `EntityAlreadyExistsException` oder fachlich äquivalente Conflict-Exception;
* `VALIDATION_FAILED` bei Bean-Validation-Verstößen;
* keine controller-lokalen Error DTOs;
* keine controller-lokalen `@ExceptionHandler` für Standardfälle;
* Error-Body enthält `errorId`, `status`, `errorType`, `message`, `path`, `method` und bei Validation `violations`.

### 5.4 Query Operations

Generierte Slices müssen `ResultSetQueryOperations` oder ein kompatibles typed-query Muster verwenden.

Pflicht:

* paged list, `/all` und `/count` nutzen dieselbe Filterfamilie;
* `/count` materialisiert keine Listen und mappt keine DTOs;
* Sort-Felder sind allowlisted;
* stabile Tiebreaker-Sortierung wird definiert;
* `/all` besitzt keine Paging-Parameter;
* `/count` besitzt keine Paging- und Sortierparameter.

### 5.5 Detail und Alternate-Key Lookup

Pflicht:

* `GET /{id}` nutzt eine opaque externe ID;
* unbekannte IDs erzeugen `404 RESOURCE_NOT_FOUND`;
* `POST` `Location` zeigt auf den Detail-Endpunkt;
* keine öffentliche `findOne`, `findFirst`, `getById` oder `findAny` Contract-Sprache.

Optional:

* `GET /by-<key>/{value}` nur bei eindeutigem fachlichem Schlüssel;
* verletzte Eindeutigkeit muss als `409 CONFLICT` eingeordnet werden, sobald runtimefähig nachweisbar.

### 5.6 Write API

Pflicht:

* `POST` erzeugt `201 Created` und `Location`;
* `PUT` erzeugt `200 OK` mit Response Body;
* bodyless `DELETE` erzeugt `204 No Content`;
* duplicate business key oder äquivalenter Konflikt erzeugt `409 CONFLICT`;
* unbekanntes Update/Delete-Ziel erzeugt `404 RESOURCE_NOT_FOUND`;
* `DELETE` hat in OpenAPI keinen `requestBody`.

Nicht Teil des ersten generated slice:

* Bulk Delete;
* State Commands;
* Relationship Commands;
* Command Precheck;
* Optimistic Locking als Pflichtfeature.

### 5.7 Persistence und JPA Count

Für den ersten Generated-Slice-Reifegrad sind zwei Modi zulässig:

| Modus | Zulässigkeit | Bedingung |
|---|---|---|
| `candidate-in-memory` | nur Candidate | explizite Evidence, keine Canonical-Promotion |
| `liquibase-jpa` | bevorzugt | Repository-/Criteria-Level Count, ChangeSet, Tests |

Bei `liquibase-jpa` ist ein dedizierter Count-Query-Pfad Pflicht. `findAll().size()`, Stream-Count nach Materialisierung oder DTO-Mapping im Count-Pfad sind nicht zulässig.

### 5.8 Security/Data-Scope

Der erste generated slice darf `documented-deferred-security` sein, sofern dies in Evidence und Akzeptanz klar markiert wird.

Für eine spätere Canonical-Promotion ist erforderlich:

* Permission Vocabulary in der Slice-Spec;
* Query-/Detail-/Write-Operationen nutzen konsistente Permission- und Data-Scope-Regeln;
* `401` und `403` werden über den globalen Error Contract geprüft;
* OpenAPI Security Requirements sind dokumentiert.

## 6. Slice-Spec Mindestmodell

Eine Generated-Slice-Spec muss mindestens folgende Informationsgruppen enthalten:

```yaml
slice:
  boundedContext: administration
  aggregate: BusinessPartner
  resourcePath: business-partners
  basePackage: de.cocondo.zbm.administration.businesspartner

api:
  collectionPath: /api/administration/business-partners
  operations:
    query: true
    all: true
    count: true
    detail: true
    create: true
    update: true
    delete: true
    alternateLookups: []

fields:
  - name: name
    type: string
    requiredOnCreate: true
    requiredOnUpdate: true
    maxLength: 255
    sortable: true
    filterable: true

persistence:
  mode: liquibase-jpa
  tableName: adm_business_partner

security:
  mode: documented-deferred-security
  permissions:
    read: administration.business-partner.read
    write: administration.business-partner.write
    delete: administration.business-partner.delete

evidence:
  candidateReference: true
  canonicalPromotion: blocked
```

Die Spec darf keine impliziten Defaults nutzen, die API-, Security-, Persistence- oder Validation-Verhalten unklar machen.

## 7. Generated Evidence

Jeder generierte Slice muss eine maschinenlesbare Evidence-Datei liefern.

Mindestfelder:

```json
{
  "schema": "springmaster.generated-service-slice-evidence.v1",
  "slice": {
    "boundedContext": "administration",
    "aggregate": "BusinessPartner",
    "resourcePath": "business-partners"
  },
  "apiPatterns": {
    "query": "implemented",
    "detailLookup": "implemented",
    "writeApi": "implemented",
    "requestValidationOpenApi": "implemented",
    "globalErrorContract": "implemented"
  },
  "classification": "candidate-reference-slice",
  "canonicalPromotion": "blocked"
}
```

Evidence darf keine erfolgreiche Canonical-Promotion behaupten, solange Security, durable persistence, strict gates und Zielprojekt-Acceptance nicht nachgewiesen sind.

## 8. Report- und Testpflichten

Ein generated slice muss folgende Nachweise liefern oder bewusst deferred markieren:

| Nachweis | Candidate Pflicht | Canonical Pflicht |
|---|---:|---:|
| Query Contract Report | ja | ja |
| Detail/Lookup Contract Report | ja | ja |
| Write API Contract Report | ja | ja |
| Request Validation/OpenAPI Report | ja | ja |
| Global Error Contract Tests | ja | ja |
| OpenAPI Query/Detail/Write/Validation Tests | ja | ja |
| Full Maven Test im Zielprojekt | ja | ja |
| Full-ZIP-Export im Zielprojekt | ja | ja |
| Security 401/403 Tests | deferred erlaubt | ja |
| Durable Persistence/Liquibase Tests | deferred bei Candidate | ja |
| Strict Gate Promotion | nein | ja |

## 9. Implementierungsreihenfolge nach 000121

Empfohlene nächste Schritte:

| Priorität | Patch-Kandidat | Ziel |
|---:|---|---|
| 1 | `000122_springmaster_generated_slice_spec_contract` | YAML/JSON-Spec-Vertrag und Golden Spec für einen neutralen Slice definieren |
| 2 | `000123_springmaster_generated_slice_spec_fixture_gate` | Golden Slice-Spec strikt parsen und API/DTO/Error/Report/Delivery-Verträge ausführbar validieren |
| 3 | `000124_springmaster_patch_artifact_preflight_hardening` | Patch-Artefakte vor Auslieferung gegen exakte Baseline, ZIP-Identität und EOF-/Diff-Hygiene prüfen |
| 4 | `000125_springmaster_generated_slice_intermediate_representation` | Validierte Spec in ein neutrales internes Slice-Modell überführen |
| 5 | `000126_springmaster_generated_slice_patch_blueprint_dry_run` | Patch-Blueprint deterministisch erzeugen, ohne Target-Dateien zu mutieren |
| 6 | `000127_springmaster_zbm_generated_slice_pilot_plan` | ZBM-Pilotinputs, Scope und Zielprojekt-Gates dokumentieren |
| 7 | später | ZBM oder anderes frisches Zielprojekt mit lokalem Patchsystem als Acceptance Target nutzen |

Diese Reihenfolge ist bewusst konservativ. Ein Zielprojekt wird erst verwendet, wenn Spec Contract, Intermediate Model und Patch Blueprint stabil sind.

## 10. Akzeptanzkriterien für den ersten Generated Slice

Ein erster generated slice ist erst akzeptiert, wenn alle folgenden Punkte erfüllt sind:

* der Slice wird als Patch-ZIP erzeugt, nicht direkt in ein Zielprojekt geschrieben;
* `manifest.json` enthält korrekte Scope- und Baseline-Informationen für das Zielprojekt;
* Zielprojekt-Patch-Dry-run ist erfolgreich;
* Zielprojekt-Patch-Apply ist erfolgreich;
* Zielprojekt-`mvn test` ist grün;
* Zielprojekt-`git diff --check` ist grün;
* Zielprojekt-Full-ZIP-Export wird erzeugt;
* Evidence-Datei klassifiziert den Slice als Candidate oder Canonical ohne Übertreibung;
* Query, Detail, Write, Validation und Error Contract sind durch Tests oder Report-Fixtures belegt;
* keine Springmaster-Demo-Pakete oder `de.cocondo.platform.demo`-Artefakte werden in das Zielprojekt übernommen.

## 11. Abschlussbewertung

Mit `000121` ist der API-Pattern-Reifegrad in eine konkrete Generator-Adoptionsplanung überführt.

Die nächste Arbeit darf daher nicht erneut die API-Basismuster dokumentieren, sondern muss den Übergang in ein explizites Generated-Slice-Spec-Modell vorbereiten.

Nächster fachlich sinnvoller Schritt:

```text
000122_springmaster_generated_slice_spec_contract
```


## Contract concretization after 000122

Patch `000122_springmaster_generated_slice_spec_contract` resolves the first implementation step named by this adoption plan.

The generated-slice target is now represented by:

* `PROJECT_DOCS/TOOLING/GENERATED_SLICE_SPEC_CONTRACT.md`
* `PROJECT_DOCS/TOOLING/GENERATED_SLICE_SPEC_GOLDEN_BUSINESS_PARTNER.yaml`

This moves the work from a planning-only adoption model to an explicit Slice-Spec contract. The next step is executable fixture validation, not target-project delivery.

Nächster fachlich sinnvoller Schritt:

```text
000123_springmaster_generated_slice_spec_fixture_gate
```


## Executable fixture validation after 000123

Patch `000123_springmaster_generated_slice_spec_fixture_gate` closes the executable-input-contract step before the Intermediate Representation.

The BusinessPartner golden YAML now proves:

* strict dependency-free YAML parsing;
* the complete list/all/count/detail/alternate-lookup/create/update/delete surface;
* distinct CreateDTO and UpdateDTO boundaries;
* explicit `400`, `404` and `409` global error families;
* all four required report families;
* patch-ZIP delivery without direct target-project mutation;
* explicit prohibition of Demo package reuse.

The gate is not an IR parser and does not generate a target patch. Patch `000124_springmaster_patch_artifact_preflight_hardening` closes the P0 delivery-process boundary. The next step is `000125_springmaster_generated_slice_intermediate_representation`.

## P0 closure after 000124

Generated-slice patch artifacts now have a deterministic producer-side qualification boundary. The export raw-byte manifest prevents baseline hashes from being inferred from presentation separators, and the isolated worktree preflight verifies exact payload, scope, diff and export integrity before delivery.

The next ordered patch is:

```text
000125_springmaster_generated_slice_intermediate_representation
```

## Intermediate Representation after 000125

Patch `000125_springmaster_generated_slice_intermediate_representation` transforms a contract-v1 Slice-Spec into the canonical `springmaster.generated-service-slice-ir.v1` model.

The IR now carries:

* package and resource identity without active Demo packages;
* shared Query filter, sorting and pagination semantics;
* list, `/all`, `/count`, detail and alternate-lookup operations;
* create, update and bodyless delete operations;
* entity, DTO and field capability metadata;
* validation, global error status families and required report evidence;
* patch-only target delivery duties.

The committed BusinessPartner golden output is supplemented by a synthetic Supplier test. This proves that the transformer is domain-neutral and does not treat CatalogItem implementation files as generator input.

The next ordered patch is:

```text
000126_springmaster_generated_slice_patch_blueprint_dry_run
```
