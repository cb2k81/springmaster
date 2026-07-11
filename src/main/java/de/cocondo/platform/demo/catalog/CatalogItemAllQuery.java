package de.cocondo.platform.demo.catalog;

/**
 * Fachlicher Query-Typ fuer die vollstaendige CatalogItem-Result-Set-Operation.
 */
public record CatalogItemAllQuery(
        String sortBy,
        String sortDir,
        String sku,
        String name
) {
}
