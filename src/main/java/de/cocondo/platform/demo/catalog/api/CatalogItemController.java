package de.cocondo.platform.demo.catalog.api;

import de.cocondo.platform.demo.catalog.CatalogItemAllQuery;
import de.cocondo.platform.demo.catalog.CatalogItemCountQuery;
import de.cocondo.platform.demo.catalog.CatalogItemCreateDTO;
import de.cocondo.platform.demo.catalog.CatalogItemDTO;
import de.cocondo.platform.demo.catalog.CatalogItemListItemDTO;
import de.cocondo.platform.demo.catalog.CatalogItemPagedQuery;
import de.cocondo.platform.demo.catalog.CatalogItemService;
import de.cocondo.platform.demo.catalog.CatalogItemUpdateDTO;
import de.cocondo.system.dto.CountResponseDTO;
import de.cocondo.system.dto.PagedResponseDTO;
import de.cocondo.system.exception.ResourceNotFoundException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.validation.Valid;
import java.net.URI;
import java.nio.charset.StandardCharsets;
import java.util.List;
import java.util.Set;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.util.UriUtils;

@RestController
@RequestMapping("/api/demo/catalog/items")
public class CatalogItemController {

    private static final int DEFAULT_PAGE_SIZE = CatalogItemService.DEFAULT_PAGE_SIZE;
    private static final Set<String> COUNT_QUERY_PARAMETERS = Set.of("sku", "name");

    private final CatalogItemService service;

    public CatalogItemController(CatalogItemService service) {
        this.service = service;
    }

    @GetMapping(produces = MediaType.APPLICATION_JSON_VALUE)
    public PagedResponseDTO<CatalogItemListItemDTO> list(
            @RequestParam(name = "page", defaultValue = "0") int page,
            @RequestParam(name = "size", defaultValue = "20") int size,
            @RequestParam(name = "sortBy", defaultValue = "sku") String sortBy,
            @RequestParam(name = "sortDir", defaultValue = "ASC") String sortDir,
            @RequestParam(name = "sku", required = false) String sku,
            @RequestParam(name = "name", required = false) String name
    ) {
        return service.listPaged(new CatalogItemPagedQuery(page, size, sortBy, sortDir, sku, name));
    }

    @GetMapping(path = "/all", produces = MediaType.APPLICATION_JSON_VALUE)
    public List<CatalogItemListItemDTO> listAll(
            @RequestParam(name = "sortBy", defaultValue = "sku") String sortBy,
            @RequestParam(name = "sortDir", defaultValue = "ASC") String sortDir,
            @RequestParam(name = "sku", required = false) String sku,
            @RequestParam(name = "name", required = false) String name
    ) {
        return service.listAll(new CatalogItemAllQuery(sortBy, sortDir, sku, name));
    }

    @GetMapping(path = "/count", produces = MediaType.APPLICATION_JSON_VALUE)
    public CountResponseDTO count(
            @RequestParam(name = "sku", required = false) String sku,
            @RequestParam(name = "name", required = false) String name,
            HttpServletRequest request
    ) {
        validateCountQueryParameters(request);
        return service.count(new CatalogItemCountQuery(sku, name));
    }

    @PostMapping
    public ResponseEntity<CatalogItemDTO> create(@Valid @RequestBody CatalogItemCreateDTO request) {
        CatalogItemDTO created = service.create(request);
        URI location = URI.create("/api/demo/catalog/items/" + UriUtils.encodePathSegment(
                created.getId(), StandardCharsets.UTF_8));
        return ResponseEntity.created(location).body(created);
    }

    @GetMapping("/{id}")
    public ResponseEntity<CatalogItemDTO> findById(@PathVariable("id") String id) {
        return service.findById(id)
                .map(ResponseEntity::ok)
                .orElseThrow(() -> new ResourceNotFoundException(
                        "Catalog item not found: id=" + id,
                        "catalog.item.not-found"));
    }

    @GetMapping("/by-sku/{sku}")
    public ResponseEntity<CatalogItemDTO> findBySku(@PathVariable("sku") String sku) {
        return service.findBySku(sku)
                .map(ResponseEntity::ok)
                .orElseThrow(() -> new ResourceNotFoundException(
                        "Catalog item not found: sku=" + sku,
                        "catalog.item.not-found"));
    }

    @PutMapping("/{id}")
    public CatalogItemDTO update(
            @PathVariable("id") String id,
            @Valid @RequestBody CatalogItemUpdateDTO request
    ) {
        return service.update(id, request);
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> delete(@PathVariable("id") String id) {
        service.delete(id);
        return ResponseEntity.noContent().build();
    }

    private void validateCountQueryParameters(HttpServletRequest request) {
        List<String> unsupported = request.getParameterMap().keySet().stream()
                .filter(parameter -> !COUNT_QUERY_PARAMETERS.contains(parameter))
                .sorted()
                .toList();
        if (!unsupported.isEmpty()) {
            throw new IllegalArgumentException(
                    "Unsupported count query parameter: " + unsupported.getFirst());
        }
    }
}
