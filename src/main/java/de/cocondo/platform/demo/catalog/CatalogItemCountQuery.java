package de.cocondo.platform.demo.catalog;

/**
 * Fachlicher Query-Typ fuer die CatalogItem-Count-only-Operation.
 */
public record CatalogItemCountQuery(
        String sku,
        String name
) {
}
