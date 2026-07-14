# CatalogItem Write API Contract Report

## Zweck

Dieser Bericht dokumentiert die CatalogItem-Evidence für den Springmaster Write API Contract Report.

Der CatalogItem-Slice bleibt `candidate-reference-slice`. Der Patch macht ihn nicht zu einer kanonisch vollständig persistenten Fachanwendung. Er belegt aber das einfache Write-Basismuster für Create, Update und Delete.

## Abgedeckte Endpunkte

```text
POST   /api/demo/catalog/items
PUT    /api/demo/catalog/items/{id}
DELETE /api/demo/catalog/items/{id}
```

## Evidence

| Operation | Evidence |
|---|---|
| Create | `CatalogItemController#create`, `CatalogItemService#create`, MockMvc-Test `createsCatalogItemWithOpaqueIdLocation` |
| Update | `CatalogItemController#update`, `CatalogItemService#update`, MockMvc-Test `updatesCatalogItemByOpaqueId` |
| Delete | `CatalogItemController#delete`, `CatalogItemService#delete`, MockMvc-Test `deletesCatalogItemByOpaqueIdBodylessly` |
| Duplicate Business Key | `EntityAlreadyExistsException`, MockMvc-Test `returnsConflictForDuplicateSkuWithStandardErrorBody` |
| Validation | `@Valid` request body, MockMvc-Tests für invalid create/update |
| Not Found | `ResourceNotFoundException`, globaler `RESOURCE_NOT_FOUND` Error Contract |
| OpenAPI | `CatalogItemOpenApiWriteContractTest` |
| Golden Fixture | `write-api-contract-report.catalogitem.golden.json` |

## Contract-Entscheidungen

### Create

Create nutzt die Collection Root:

```text
POST /api/demo/catalog/items
```

Der Endpoint gibt `201 Created` zurück und setzt einen `Location` Header auf den opaque-id Detail-Endpunkt.

Die `Location` darf nicht auf den fachlichen Business Key `sku` zeigen. Der bestehende MockMvc-Test prüft, dass der Location Header `/api/demo/catalog/items/` enthält und nicht `/api/demo/catalog/items/SKU-1` ist.

### Update

Update nutzt:

```text
PUT /api/demo/catalog/items/{id}
```

Der Endpoint gibt `200 OK` mit `CatalogItemDTO` zurück. Die ID kommt ausschließlich aus der Route. Das UpdateDTO enthält keine öffentliche ID-Semantik.

### Delete

Delete nutzt:

```text
DELETE /api/demo/catalog/items/{id}
```

Der Endpoint ist bodyless und gibt `204 No Content` zurück. Repeated strict delete beziehungsweise unbekannte ID wird über den globalen `RESOURCE_NOT_FOUND` Contract behandelt.

## Grenzen

Nicht Bestandteil dieser Evidence:

* Bulk Delete;
* State Commands;
* Relationship Commands;
* Command Precheck;
* Optimistic Locking;
* persistente Transaktionsgrenzen.

Diese Themen bleiben nachgelagert.

## Ergebnis

Der Write API Contract Report erzeugt für CatalogItem eine findings-freie Golden Fixture und bleibt report-only.
