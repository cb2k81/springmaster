package de.cocondo.platform.demo.catalog;

import de.cocondo.system.dto.CountResponseDTO;
import de.cocondo.system.dto.PagedResponseDTO;
import de.cocondo.system.list.PagedQuerySupport;
import java.util.Collection;
import java.util.Comparator;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Objects;

/**
 * Security/data-scope parity reference for CatalogItem query operations.
 *
 * <p>This class is deliberately not wired into the current demo runtime. It
 * demonstrates the non-negotiable query rule for secured reference slices:
 * paged list, complete-result-set and count-only operations must use the same
 * permission gate and data-scope predicate family before operation-specific
 * paging, sorting or DTO mapping is applied.</p>
 */
public final class CatalogItemScopedQueryReference {

    private static final String DEFAULT_SORT_BY = "sku";
    private static final Comparator<CatalogItem> TIE_BREAKER_COMPARATOR =
            Comparator.comparing(CatalogItem::getId);
    private static final Map<String, Comparator<CatalogItem>> SORT_COMPARATORS = Map.of(
            "sku", Comparator.comparing(CatalogItem::getSku, String.CASE_INSENSITIVE_ORDER),
            "name", Comparator.comparing(CatalogItem::getName, String.CASE_INSENSITIVE_ORDER)
    );

    private final CatalogItemMapper mapper = new CatalogItemMapper();
    private final PagedQuerySupport pagedQuerySupport = new PagedQuerySupport();

    public PagedResponseDTO<CatalogItemListItemDTO> listPaged(
            Collection<CatalogItem> source,
            CatalogItemPagedQuery query,
            CatalogItemQueryScope scope
    ) {
        Objects.requireNonNull(query, "query must not be null");
        pagedQuerySupport.validatePaging(query.page(), query.size());

        List<CatalogItem> matching = matchingScopedItems(source, query.sku(), query.name(), scope).stream()
                .sorted(stableComparator(query.sortBy(), query.sortDir()))
                .toList();
        int fromIndex = Math.min(query.page() * query.size(), matching.size());
        int toIndex = Math.min(fromIndex + query.size(), matching.size());

        PagedResponseDTO<CatalogItemListItemDTO> response = new PagedResponseDTO<>();
        response.setItems(matching.subList(fromIndex, toIndex).stream().map(mapper::toListItemDto).toList());
        response.setPage(query.page());
        response.setSize(query.size());
        response.setTotalElements(matching.size());
        response.setTotalPages(totalPages(matching.size(), query.size()));
        return response;
    }

    public List<CatalogItemListItemDTO> listAll(
            Collection<CatalogItem> source,
            CatalogItemAllQuery query,
            CatalogItemQueryScope scope
    ) {
        Objects.requireNonNull(query, "query must not be null");
        return matchingScopedItems(source, query.sku(), query.name(), scope).stream()
                .sorted(stableComparator(query.sortBy(), query.sortDir()))
                .map(mapper::toListItemDto)
                .toList();
    }

    public CountResponseDTO count(
            Collection<CatalogItem> source,
            CatalogItemCountQuery query,
            CatalogItemQueryScope scope
    ) {
        Objects.requireNonNull(query, "query must not be null");
        return CountResponseDTO.of(matchingScopedItems(source, query.sku(), query.name(), scope).size());
    }

    private List<CatalogItem> matchingScopedItems(
            Collection<CatalogItem> source,
            String sku,
            String name,
            CatalogItemQueryScope scope
    ) {
        requireReadPermission(scope);
        Objects.requireNonNull(source, "source must not be null");
        return source.stream()
                .filter(scope::canSee)
                .filter(item -> matchesSku(item, sku))
                .filter(item -> matchesName(item, name))
                .toList();
    }

    private void requireReadPermission(CatalogItemQueryScope scope) {
        Objects.requireNonNull(scope, "scope must not be null");
        if (!scope.readAllowed()) {
            throw new SecurityException("Missing permission: " + CatalogItemQueryScope.READ_PERMISSION);
        }
    }

    private Comparator<CatalogItem> stableComparator(String sortBy, String sortDir) {
        return pagedQuerySupport.stableComparator(
                sortBy,
                sortDir,
                SORT_COMPARATORS,
                DEFAULT_SORT_BY,
                TIE_BREAKER_COMPARATOR
        );
    }

    private boolean matchesSku(CatalogItem item, String sku) {
        if (sku == null || sku.isBlank()) {
            return true;
        }
        return item.getSku() != null && item.getSku().equalsIgnoreCase(sku.trim());
    }

    private boolean matchesName(CatalogItem item, String name) {
        if (name == null || name.isBlank()) {
            return true;
        }
        return item.getName() != null
                && item.getName().toLowerCase(Locale.ROOT).contains(name.trim().toLowerCase(Locale.ROOT));
    }

    private int totalPages(int totalElements, int pageSize) {
        if (totalElements == 0) {
            return 0;
        }
        return (int) Math.ceil((double) totalElements / pageSize);
    }
}
