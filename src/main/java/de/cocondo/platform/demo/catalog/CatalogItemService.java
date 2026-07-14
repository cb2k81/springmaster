package de.cocondo.platform.demo.catalog;

import de.cocondo.system.dto.CountResponseDTO;
import de.cocondo.system.dto.PagedResponseDTO;
import de.cocondo.system.exception.EntityAlreadyExistsException;
import de.cocondo.system.exception.ResourceNotFoundException;
import de.cocondo.system.list.PagedQuerySupport;
import de.cocondo.system.query.ResultSetQueryOperations;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import org.springframework.stereotype.Service;

@Service
public class CatalogItemService implements ResultSetQueryOperations<
        CatalogItemPagedQuery,
        CatalogItemAllQuery,
        CatalogItemCountQuery,
        CatalogItemListItemDTO> {

    public static final int DEFAULT_PAGE_SIZE = 20;

    private static final String DEFAULT_SORT_BY = "sku";
    private static final Comparator<CatalogItem> TIE_BREAKER_COMPARATOR =
            Comparator.comparing(CatalogItem::getId);
    private static final Map<String, Comparator<CatalogItem>> SORT_COMPARATORS = Map.of(
            "sku", Comparator.comparing(CatalogItem::getSku, String.CASE_INSENSITIVE_ORDER),
            "name", Comparator.comparing(CatalogItem::getName, String.CASE_INSENSITIVE_ORDER)
    );

    private final CatalogItemValidator validator = new CatalogItemValidator();
    private final CatalogItemMapper mapper = new CatalogItemMapper();
    private final PagedQuerySupport pagedQuerySupport = new PagedQuerySupport();
    private final Map<String, CatalogItem> itemsById = new LinkedHashMap<>();
    private final Map<String, CatalogItem> itemsBySku = new LinkedHashMap<>();

    public synchronized CatalogItemDTO create(CatalogItemCreateDTO request) {
        validator.validate(request);
        String key = skuKey(request.getSku());
        if (itemsBySku.containsKey(key)) {
            throw new EntityAlreadyExistsException(
                    "Catalog item already exists: SKU=" + request.getSku().trim(),
                    "catalog.item.conflict");
        }
        CatalogItem item = mapper.toEntity(request);
        itemsById.put(item.getId(), item);
        itemsBySku.put(key, item);
        return mapper.toDto(item);
    }

    public synchronized CatalogItemDTO update(String id, CatalogItemUpdateDTO request) {
        CatalogItem item = findEntityById(id)
                .orElseThrow(() -> new ResourceNotFoundException(
                        "Catalog item not found: id=" + id,
                        "catalog.item.not-found"));
        validator.validate(request);
        mapper.updateEntity(item, request);
        return mapper.toDto(item);
    }

    public synchronized void delete(String id) {
        CatalogItem item = findEntityById(id)
                .orElseThrow(() -> new ResourceNotFoundException(
                        "Catalog item not found: id=" + id,
                        "catalog.item.not-found"));
        itemsById.remove(item.getId());
        itemsBySku.remove(skuKey(item.getSku()));
    }

    public synchronized Optional<CatalogItemDTO> findById(String id) {
        return findEntityById(id).map(mapper::toDto);
    }

    public synchronized Optional<CatalogItemDTO> findBySku(String sku) {
        if (sku == null || sku.isBlank()) {
            return Optional.empty();
        }
        return Optional.ofNullable(itemsBySku.get(skuKey(sku))).map(mapper::toDto);
    }

    public synchronized PagedResponseDTO<CatalogItemListItemDTO> listPaged(
            int page,
            int size,
            String sortBy,
            String sortDir
    ) {
        return listPaged(page, size, sortBy, sortDir, null, null);
    }

    public synchronized PagedResponseDTO<CatalogItemListItemDTO> listPaged(
            int page,
            int size,
            String sortBy,
            String sortDir,
            String sku,
            String name
    ) {
        return listPaged(new CatalogItemPagedQuery(page, size, sortBy, sortDir, sku, name));
    }

    @Override
    public synchronized PagedResponseDTO<CatalogItemListItemDTO> listPaged(CatalogItemPagedQuery query) {
        Objects.requireNonNull(query, "query must not be null");
        pagedQuerySupport.validatePaging(query.page(), query.size());

        List<CatalogItem> matching = matchingSortedItems(query.sortBy(), query.sortDir(), query.sku(), query.name());
        int fromIndex = Math.min(query.page() * query.size(), matching.size());
        int toIndex = Math.min(fromIndex + query.size(), matching.size());
        List<CatalogItemListItemDTO> items = matching.subList(fromIndex, toIndex).stream()
                .map(mapper::toListItemDto)
                .toList();

        PagedResponseDTO<CatalogItemListItemDTO> response = new PagedResponseDTO<>();
        response.setItems(items);
        response.setPage(query.page());
        response.setSize(query.size());
        response.setTotalElements(matching.size());
        response.setTotalPages(totalPages(matching.size(), query.size()));
        return response;
    }

    public synchronized List<CatalogItemListItemDTO> listAll(
            String sortBy,
            String sortDir,
            String sku,
            String name
    ) {
        return listAll(new CatalogItemAllQuery(sortBy, sortDir, sku, name));
    }

    @Override
    public synchronized List<CatalogItemListItemDTO> listAll(CatalogItemAllQuery query) {
        Objects.requireNonNull(query, "query must not be null");
        return matchingSortedItems(query.sortBy(), query.sortDir(), query.sku(), query.name()).stream()
                .map(mapper::toListItemDto)
                .toList();
    }

    public synchronized CountResponseDTO count(String sku, String name) {
        return count(new CatalogItemCountQuery(sku, name));
    }

    @Override
    public synchronized CountResponseDTO count(CatalogItemCountQuery query) {
        Objects.requireNonNull(query, "query must not be null");
        return CountResponseDTO.of(matchingItems(query.sku(), query.name()).size());
    }

    public synchronized void clear() {
        itemsById.clear();
        itemsBySku.clear();
    }

    public synchronized int size() {
        return itemsById.size();
    }

    private Optional<CatalogItem> findEntityById(String id) {
        if (id == null || id.isBlank()) {
            return Optional.empty();
        }
        return Optional.ofNullable(itemsById.get(id));
    }

    private String skuKey(String sku) {
        return sku.trim().toUpperCase(Locale.ROOT);
    }

    private List<CatalogItem> matchingSortedItems(String sortBy, String sortDir, String sku, String name) {
        Comparator<CatalogItem> comparator = pagedQuerySupport.stableComparator(
                sortBy,
                sortDir,
                SORT_COMPARATORS,
                DEFAULT_SORT_BY,
                TIE_BREAKER_COMPARATOR
        );

        return matchingItems(sku, name).stream()
                .sorted(comparator)
                .toList();
    }

    private List<CatalogItem> matchingItems(String sku, String name) {
        return new ArrayList<>(itemsById.values()).stream()
                .filter(item -> matchesSku(item, sku))
                .filter(item -> matchesName(item, name))
                .toList();
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
