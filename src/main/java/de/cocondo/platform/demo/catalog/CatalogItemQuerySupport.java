package de.cocondo.platform.demo.catalog;

import de.cocondo.system.list.PagedQuerySupport;
import java.util.Set;
import org.springframework.data.domain.Sort;

final class CatalogItemQuerySupport {

    static final String ATTRIBUTE_ID = "id";
    static final String ATTRIBUTE_SKU = "sku";
    static final String ATTRIBUTE_NAME = "name";
    static final String DEFAULT_SORT_BY = ATTRIBUTE_SKU;
    static final Set<String> ALLOWED_SORT_FIELDS = Set.of(ATTRIBUTE_SKU, ATTRIBUTE_NAME);

    private static final PagedQuerySupport PAGED_QUERY_SUPPORT = new PagedQuerySupport();

    private CatalogItemQuerySupport() {
    }

    static void validate(CatalogItemPagedQuery query) {
        if (query == null) {
            throw new IllegalArgumentException("query must not be null");
        }
        PAGED_QUERY_SUPPORT.validatePaging(query.page(), query.size());
        validatedOffset(query.page(), query.size());
        resolveSortBy(query.sortBy());
        resolveSortDirection(query.sortDir());
    }

    static void validate(CatalogItemAllQuery query) {
        if (query == null) {
            throw new IllegalArgumentException("query must not be null");
        }
        resolveSortBy(query.sortBy());
        resolveSortDirection(query.sortDir());
    }

    static void validate(CatalogItemCountQuery query) {
        if (query == null) {
            throw new IllegalArgumentException("query must not be null");
        }
    }

    static int validatedOffset(int page, int size) {
        try {
            return Math.multiplyExact(page, size);
        } catch (ArithmeticException exception) {
            throw new IllegalArgumentException("page and size exceed the supported result offset", exception);
        }
    }

    static String resolveSortBy(String sortBy) {
        return PAGED_QUERY_SUPPORT.resolveSortBy(sortBy, ALLOWED_SORT_FIELDS, DEFAULT_SORT_BY);
    }

    static Sort.Direction resolveSortDirection(String sortDir) {
        return PAGED_QUERY_SUPPORT.resolveSortDirection(sortDir);
    }
}
