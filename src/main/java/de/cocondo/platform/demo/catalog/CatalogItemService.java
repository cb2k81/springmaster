package de.cocondo.platform.demo.catalog;

import de.cocondo.system.dto.PagedResponseDTO;
import de.cocondo.system.exception.EntityAlreadyExistsException;
import de.cocondo.system.list.PagedQuerySupport;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Optional;
import org.springframework.data.domain.Sort;
import org.springframework.stereotype.Service;

@Service
public class CatalogItemService {

    public static final int DEFAULT_PAGE_SIZE = 20;

    private final CatalogItemValidator validator = new CatalogItemValidator();
    private final CatalogItemMapper mapper = new CatalogItemMapper();
    private final PagedQuerySupport pagedQuerySupport = new PagedQuerySupport();
    private final Map<String, CatalogItem> itemsById = new LinkedHashMap<>();
    private final Map<String, CatalogItem> itemsBySku = new LinkedHashMap<>();

    public synchronized CatalogItemDTO create(CatalogItemCreateDTO request) {
        validator.validate(request);
        String key = skuKey(request.getSku());
        if (itemsBySku.containsKey(key)) {
            throw new EntityAlreadyExistsException("Catalog item already exists: SKU=" + request.getSku().trim());
        }
        CatalogItem item = mapper.toEntity(request);
        itemsById.put(item.getId(), item);
        itemsBySku.put(key, item);
        return mapper.toDto(item);
    }

    public synchronized CatalogItemDTO update(String id, CatalogItemUpdateDTO request) {
        CatalogItem item = findEntityById(id)
                .orElseThrow(() -> new CatalogItemNotFoundException("Catalog item not found: id=" + id));
        validator.validate(request);
        mapper.updateEntity(item, request);
        return mapper.toDto(item);
    }

    public synchronized void delete(String id) {
        CatalogItem item = findEntityById(id)
                .orElseThrow(() -> new CatalogItemNotFoundException("Catalog item not found: id=" + id));
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
        pagedQuerySupport.validatePaging(page, size);

        List<CatalogItem> matching = matchingSortedItems(sortBy, sortDir, sku, name);
        int fromIndex = Math.min(page * size, matching.size());
        int toIndex = Math.min(fromIndex + size, matching.size());
        List<CatalogItemListItemDTO> items = matching.subList(fromIndex, toIndex).stream()
                .map(mapper::toListItemDto)
                .toList();

        PagedResponseDTO<CatalogItemListItemDTO> response = new PagedResponseDTO<>();
        response.setItems(items);
        response.setPage(page);
        response.setSize(size);
        response.setTotalElements(matching.size());
        response.setTotalPages(totalPages(matching.size(), size));
        return response;
    }

    public synchronized List<CatalogItemListItemDTO> listAll(
            String sortBy,
            String sortDir,
            String sku,
            String name
    ) {
        return matchingSortedItems(sortBy, sortDir, sku, name).stream()
                .map(mapper::toListItemDto)
                .toList();
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
        String resolvedSortBy = resolveSortBy(sortBy);
        Sort.Direction resolvedSortDirection = pagedQuerySupport.resolveSortDirection(sortDir);
        Comparator<CatalogItem> comparator = comparator(resolvedSortBy);
        if (resolvedSortDirection == Sort.Direction.DESC) {
            comparator = comparator.reversed();
        }

        List<CatalogItem> matching = new ArrayList<>(itemsById.values()).stream()
                .filter(item -> matchesSku(item, sku))
                .filter(item -> matchesName(item, name))
                .toList();
        return matching.stream()
                .sorted(comparator.thenComparing(CatalogItem::getId))
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

    private String resolveSortBy(String sortBy) {
        if (sortBy == null || sortBy.isBlank()) {
            return "sku";
        }
        String normalized = sortBy.trim();
        if ("sku".equals(normalized) || "name".equals(normalized)) {
            return normalized;
        }
        throw new IllegalArgumentException("Unsupported sortBy: " + sortBy);
    }

    private Comparator<CatalogItem> comparator(String sortBy) {
        return switch (sortBy) {
            case "sku" -> Comparator.comparing(CatalogItem::getSku, String.CASE_INSENSITIVE_ORDER);
            case "name" -> Comparator.comparing(CatalogItem::getName, String.CASE_INSENSITIVE_ORDER);
            default -> throw new IllegalArgumentException("Unsupported sortBy: " + sortBy);
        };
    }

    private int totalPages(int totalElements, int pageSize) {
        if (totalElements == 0) {
            return 0;
        }
        return (int) Math.ceil((double) totalElements / pageSize);
    }
}
