package de.cocondo.platform.demo.catalog;

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
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageImpl;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Sort;
import org.springframework.stereotype.Repository;

@Repository
public class CatalogItemJpaQueryRepository {

    private final EntityManager entityManager;

    public CatalogItemJpaQueryRepository(EntityManager entityManager) {
        this.entityManager = entityManager;
    }

    public Page<CatalogItem> findPage(CatalogItemPagedQuery query) {
        CatalogItemQuerySupport.validate(query);
        long totalElements = countRows(query.sku(), query.name());
        List<CatalogItem> rows = totalElements == 0
                ? List.of()
                : createDataQuery(query.sortBy(), query.sortDir(), query.sku(), query.name())
                        .setFirstResult(CatalogItemQuerySupport.validatedOffset(query.page(), query.size()))
                        .setMaxResults(query.size())
                        .getResultList();
        return new PageImpl<>(rows, PageRequest.of(query.page(), query.size()), totalElements);
    }

    public List<CatalogItem> findAll(CatalogItemAllQuery query) {
        CatalogItemQuerySupport.validate(query);
        return createDataQuery(query.sortBy(), query.sortDir(), query.sku(), query.name()).getResultList();
    }

    public long count(CatalogItemCountQuery query) {
        CatalogItemQuerySupport.validate(query);
        return countRows(query.sku(), query.name());
    }

    private TypedQuery<CatalogItem> createDataQuery(
            String sortBy,
            String sortDir,
            String sku,
            String name
    ) {
        CriteriaBuilder criteriaBuilder = entityManager.getCriteriaBuilder();
        CriteriaQuery<CatalogItem> dataQuery = criteriaBuilder.createQuery(CatalogItem.class);
        Root<CatalogItem> root = dataQuery.from(CatalogItem.class);

        dataQuery.select(root);
        applyPredicates(dataQuery, root, criteriaBuilder, sku, name);
        dataQuery.orderBy(stableOrders(root, criteriaBuilder, sortBy, sortDir));
        return entityManager.createQuery(dataQuery);
    }

    private long countRows(String sku, String name) {
        CriteriaBuilder criteriaBuilder = entityManager.getCriteriaBuilder();
        CriteriaQuery<Long> countQuery = criteriaBuilder.createQuery(Long.class);
        Root<CatalogItem> root = countQuery.from(CatalogItem.class);

        countQuery.select(criteriaBuilder.count(root));
        applyPredicates(countQuery, root, criteriaBuilder, sku, name);
        return entityManager.createQuery(countQuery).getSingleResult();
    }

    private void applyPredicates(
            CriteriaQuery<?> query,
            Root<CatalogItem> root,
            CriteriaBuilder criteriaBuilder,
            String sku,
            String name
    ) {
        List<Predicate> predicates = filterPredicates(root, criteriaBuilder, sku, name);
        if (!predicates.isEmpty()) {
            query.where(predicates.toArray(Predicate[]::new));
        }
    }

    private List<Predicate> filterPredicates(
            Root<CatalogItem> root,
            CriteriaBuilder criteriaBuilder,
            String sku,
            String name
    ) {
        List<Predicate> predicates = new ArrayList<>();
        if (sku != null && !sku.isBlank()) {
            predicates.add(criteriaBuilder.equal(
                    criteriaBuilder.upper(root.get(CatalogItemQuerySupport.ATTRIBUTE_SKU)),
                    sku.trim().toUpperCase(Locale.ROOT)
            ));
        }
        if (name != null && !name.isBlank()) {
            predicates.add(criteriaBuilder.like(
                    criteriaBuilder.lower(root.get(CatalogItemQuerySupport.ATTRIBUTE_NAME)),
                    "%" + name.trim().toLowerCase(Locale.ROOT) + "%"
            ));
        }
        return predicates;
    }

    private List<Order> stableOrders(
            Root<CatalogItem> root,
            CriteriaBuilder criteriaBuilder,
            String sortBy,
            String sortDir
    ) {
        String resolvedSortBy = CatalogItemQuerySupport.resolveSortBy(sortBy);
        Sort.Direction direction = CatalogItemQuerySupport.resolveSortDirection(sortDir);
        List<Order> orders = new ArrayList<>();
        if (direction == Sort.Direction.DESC) {
            orders.add(criteriaBuilder.desc(criteriaBuilder.lower(root.get(resolvedSortBy))));
        } else {
            orders.add(criteriaBuilder.asc(criteriaBuilder.lower(root.get(resolvedSortBy))));
        }
        orders.add(criteriaBuilder.asc(root.get(CatalogItemQuerySupport.ATTRIBUTE_ID)));
        return orders;
    }
}
