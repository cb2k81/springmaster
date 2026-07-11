package de.cocondo.platform.demo.catalog;

/**
 * Fachlicher Query-Typ fuer die paginierte CatalogItem-Listenoperation.
 */
public record CatalogItemPagedQuery(
        int page,
        int size,
        String sortBy,
        String sortDir,
        String sku,
        String name
) {
}
