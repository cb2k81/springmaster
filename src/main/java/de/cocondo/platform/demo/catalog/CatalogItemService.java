package de.cocondo.platform.demo.catalog;

import de.cocondo.system.dto.PagedResponseDTO;
import de.cocondo.system.exception.EntityAlreadyExistsException;
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
    public static final int MAX_PAGE_SIZE = 200;

    private final CatalogItemValidator validator = new CatalogItemValidator();
    private final CatalogItemMapper mapper = new CatalogItemMapper();
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

    public synchronized PagedResponseDTO<CatalogItemListItemDTO> listPaged(int page, int size, String sortBy, String sortDir) {
        validatePage(page);
        int resolvedSize = resolveSize(size);
        Comparator<CatalogItem> comparator = comparator(resolveSortBy(sortBy));
        if (resolveSortDirection(sortDir) == Sort.Direction.DESC) {
            comparator = comparator.reversed();
        }

        List<CatalogItem> sorted = new ArrayList<>(itemsById.values());
        sorted.sort(comparator.thenComparing(CatalogItem::getId));

        int fromIndex = Math.min(page * resolvedSize, sorted.size());
        int toIndex = Math.min(fromIndex + resolvedSize, sorted.size());
        List<CatalogItemListItemDTO> items = sorted.subList(fromIndex, toIndex).stream()
                .map(mapper::toListItemDto)
                .toList();

        PagedResponseDTO<CatalogItemListItemDTO> response = new PagedResponseDTO<>();
        response.setItems(items);
        response.setPage(page);
        response.setSize(resolvedSize);
        response.setTotalElements(sorted.size());
        response.setTotalPages(totalPages(sorted.size(), resolvedSize));
        return response;
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

    private void validatePage(int page) {
        if (page < 0) {
            throw new IllegalArgumentException("page must be >= 0");
        }
    }

    private int resolveSize(int size) {
        if (size <= 0) {
            throw new IllegalArgumentException("size must be > 0");
        }
        if (size > MAX_PAGE_SIZE) {
            throw new IllegalArgumentException("size must be <= " + MAX_PAGE_SIZE);
        }
        return size;
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

    private Sort.Direction resolveSortDirection(String sortDir) {
        if (sortDir == null || sortDir.isBlank()) {
            return Sort.Direction.ASC;
        }
        return switch (sortDir.toLowerCase(Locale.ROOT)) {
            case "asc" -> Sort.Direction.ASC;
            case "desc" -> Sort.Direction.DESC;
            default -> throw new IllegalArgumentException("Unsupported sortDir: " + sortDir);
        };
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


