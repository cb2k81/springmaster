package de.cocondo.platform.demo.catalog;

import de.cocondo.system.dto.CountResponseDTO;
import de.cocondo.system.dto.PagedResponseDTO;
import de.cocondo.system.list.PagedQuerySupport;
import jakarta.persistence.EntityManager;
import jakarta.persistence.TypedQuery;
import jakarta.persistence.criteria.CriteriaBuilder;
import jakarta.persistence.criteria.CriteriaQuery;
import jakarta.persistence.criteria.Order;
import jakarta.persistence.criteria.Predicate;
import jakarta.persistence.criteria.Root;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import java.util.Objects;
import java.util.Set;
import org.springframework.data.domain.Sort;

/**
 * Persistent JPA reference for CatalogItem query operations.
 *
 * <p>This class is deliberately not wired into the current in-memory demo runtime.
 * It documents and compiles the durable repository-side query pattern that future
 * generated slices must use when List, /all and /count operate on persistent data.</p>
 */
public final class CatalogItemJpaQueryReference {

    private static final String ATTRIBUTE_ID = "id";
    private static final String ATTRIBUTE_SKU = "sku";
    private static final String ATTRIBUTE_NAME = "name";
    private static final String DEFAULT_SORT_BY = ATTRIBUTE_SKU;
    private static final Set<String> ALLOWED_SORT_FIELDS = Set.of(ATTRIBUTE_SKU, ATTRIBUTE_NAME);

    private final CatalogItemMapper mapper = new CatalogItemMapper();
    private final PagedQuerySupport pagedQuerySupport = new PagedQuerySupport();

    public PagedResponseDTO<CatalogItemListItemDTO> listPaged(
            EntityManager entityManager,
            CatalogItemPagedQuery query
    ) {
        Objects.requireNonNull(query, "query must not be null");
        pagedQuerySupport.validatePaging(query.page(), query.size());

        List<CatalogItem> rows = createDataQuery(
                entityManager,
                query.sortBy(),
                query.sortDir(),
                query.sku(),
                query.name()
        )
                .setFirstResult(query.page() * query.size())
                .setMaxResults(query.size())
                .getResultList();

        long totalElements = countRows(entityManager, query.sku(), query.name());

        PagedResponseDTO<CatalogItemListItemDTO> response = new PagedResponseDTO<>();
        response.setItems(rows.stream().map(mapper::toListItemDto).toList());
        response.setPage(query.page());
        response.setSize(query.size());
        response.setTotalElements(totalElements);
        response.setTotalPages(totalPages(totalElements, query.size()));
        return response;
    }

    public List<CatalogItemListItemDTO> listAll(
            EntityManager entityManager,
            CatalogItemAllQuery query
    ) {
        Objects.requireNonNull(query, "query must not be null");
        return createDataQuery(entityManager, query.sortBy(), query.sortDir(), query.sku(), query.name())
                .getResultList()
                .stream()
                .map(mapper::toListItemDto)
                .toList();
    }

    public CountResponseDTO count(
            EntityManager entityManager,
            CatalogItemCountQuery query
    ) {
        Objects.requireNonNull(query, "query must not be null");
        return CountResponseDTO.of(countRows(entityManager, query.sku(), query.name()));
    }

    private TypedQuery<CatalogItem> createDataQuery(
            EntityManager entityManager,
            String sortBy,
            String sortDir,
            String sku,
            String name
    ) {
        Objects.requireNonNull(entityManager, "entityManager must not be null");

        CriteriaBuilder cb = entityManager.getCriteriaBuilder();
        CriteriaQuery<CatalogItem> dataQuery = cb.createQuery(CatalogItem.class);
        Root<CatalogItem> root = dataQuery.from(CatalogItem.class);

        dataQuery.select(root);
        applyPredicates(dataQuery, root, cb, sku, name);
        dataQuery.orderBy(stableOrders(root, cb, sortBy, sortDir));
        return entityManager.createQuery(dataQuery);
    }

    private long countRows(
            EntityManager entityManager,
            String sku,
            String name
    ) {
        Objects.requireNonNull(entityManager, "entityManager must not be null");

        CriteriaBuilder cb = entityManager.getCriteriaBuilder();
        CriteriaQuery<Long> countQuery = cb.createQuery(Long.class);
        Root<CatalogItem> root = countQuery.from(CatalogItem.class);

        countQuery.select(cb.count(root));
        applyPredicates(countQuery, root, cb, sku, name);
        return entityManager.createQuery(countQuery).getSingleResult();
    }

    private void applyPredicates(
            CriteriaQuery<?> query,
            Root<CatalogItem> root,
            CriteriaBuilder cb,
            String sku,
            String name
    ) {
        List<Predicate> predicates = filterPredicates(root, cb, sku, name);
        if (!predicates.isEmpty()) {
            query.where(predicates.toArray(Predicate[]::new));
        }
    }

    private List<Predicate> filterPredicates(
            Root<CatalogItem> root,
            CriteriaBuilder cb,
            String sku,
            String name
    ) {
        List<Predicate> predicates = new ArrayList<>();
        if (sku != null && !sku.isBlank()) {
            predicates.add(cb.equal(
                    cb.upper(root.get(ATTRIBUTE_SKU)),
                    sku.trim().toUpperCase(Locale.ROOT)
            ));
        }
        if (name != null && !name.isBlank()) {
            predicates.add(cb.like(
                    cb.lower(root.get(ATTRIBUTE_NAME)),
                    "%" + name.trim().toLowerCase(Locale.ROOT) + "%"
            ));
        }
        return predicates;
    }

    private List<Order> stableOrders(
            Root<CatalogItem> root,
            CriteriaBuilder cb,
            String sortBy,
            String sortDir
    ) {
        String resolvedSortBy = pagedQuerySupport.resolveSortBy(sortBy, ALLOWED_SORT_FIELDS, DEFAULT_SORT_BY);
        Sort.Direction direction = pagedQuerySupport.resolveSortDirection(sortDir);
        List<Order> orders = new ArrayList<>();

        if (direction == Sort.Direction.DESC) {
            orders.add(cb.desc(cb.lower(root.get(resolvedSortBy))));
        } else {
            orders.add(cb.asc(cb.lower(root.get(resolvedSortBy))));
        }
        orders.add(cb.asc(root.get(ATTRIBUTE_ID)));
        return orders;
    }

    private int totalPages(long totalElements, int pageSize) {
        if (totalElements == 0) {
            return 0;
        }
        return (int) Math.ceil((double) totalElements / pageSize);
    }
}
