package de.cocondo.platform.demo.catalog;

import de.cocondo.system.dto.CountResponseDTO;
import de.cocondo.system.dto.PagedResponseDTO;
import de.cocondo.system.exception.EntityAlreadyExistsException;
import de.cocondo.system.exception.ResourceNotFoundException;
import de.cocondo.system.query.ResultSetQueryOperations;
import java.util.List;
import java.util.Optional;
import org.springframework.data.domain.Page;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class CatalogItemService implements ResultSetQueryOperations<
        CatalogItemPagedQuery,
        CatalogItemAllQuery,
        CatalogItemCountQuery,
        CatalogItemListItemDTO> {

    public static final int DEFAULT_PAGE_SIZE = 20;

    private final CatalogItemRepository repository;
    private final CatalogItemJpaQueryRepository queryRepository;
    private final CatalogItemValidator validator = new CatalogItemValidator();
    private final CatalogItemMapper mapper = new CatalogItemMapper();

    public CatalogItemService(
            CatalogItemRepository repository,
            CatalogItemJpaQueryRepository queryRepository
    ) {
        this.repository = repository;
        this.queryRepository = queryRepository;
    }

    @Transactional
    public CatalogItemDTO create(CatalogItemCreateDTO request) {
        validator.validate(request);
        String normalizedSku = request.getSku().trim();
        if (repository.existsBySkuIgnoreCase(normalizedSku)) {
            throw duplicateSku(normalizedSku);
        }

        CatalogItem item = mapper.toEntity(request);
        CatalogItem persisted = repository.saveAndFlush(item);
        return mapper.toDto(persisted);
    }

    @Transactional
    public CatalogItemDTO update(String id, CatalogItemUpdateDTO request) {
        CatalogItem item = requireById(id);
        validator.validate(request);
        mapper.updateEntity(item, request);
        CatalogItem persisted = repository.saveAndFlush(item);
        return mapper.toDto(persisted);
    }

    @Transactional
    public void delete(String id) {
        CatalogItem item = requireById(id);
        repository.delete(item);
        repository.flush();
    }

    @Transactional(readOnly = true)
    public Optional<CatalogItemDTO> findById(String id) {
        if (id == null || id.isBlank()) {
            return Optional.empty();
        }
        return repository.findById(id).map(mapper::toDto);
    }

    @Transactional(readOnly = true)
    public Optional<CatalogItemDTO> findBySku(String sku) {
        if (sku == null || sku.isBlank()) {
            return Optional.empty();
        }
        return repository.findBySkuIgnoreCase(sku.trim()).map(mapper::toDto);
    }

    @Transactional(readOnly = true)
    public PagedResponseDTO<CatalogItemListItemDTO> listPaged(
            int page,
            int size,
            String sortBy,
            String sortDir
    ) {
        return listPaged(page, size, sortBy, sortDir, null, null);
    }

    @Transactional(readOnly = true)
    public PagedResponseDTO<CatalogItemListItemDTO> listPaged(
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
    @Transactional(readOnly = true)
    public PagedResponseDTO<CatalogItemListItemDTO> listPaged(CatalogItemPagedQuery query) {
        CatalogItemQuerySupport.validate(query);
        Page<CatalogItem> result = queryRepository.findPage(query);

        PagedResponseDTO<CatalogItemListItemDTO> response = new PagedResponseDTO<>();
        response.setItems(result.getContent().stream().map(mapper::toListItemDto).toList());
        response.setPage(result.getNumber());
        response.setSize(result.getSize());
        response.setTotalElements(result.getTotalElements());
        response.setTotalPages(result.getTotalPages());
        return response;
    }

    @Transactional(readOnly = true)
    public List<CatalogItemListItemDTO> listAll(
            String sortBy,
            String sortDir,
            String sku,
            String name
    ) {
        return listAll(new CatalogItemAllQuery(sortBy, sortDir, sku, name));
    }

    @Override
    @Transactional(readOnly = true)
    public List<CatalogItemListItemDTO> listAll(CatalogItemAllQuery query) {
        CatalogItemQuerySupport.validate(query);
        return queryRepository.findAll(query).stream()
                .map(mapper::toListItemDto)
                .toList();
    }

    @Transactional(readOnly = true)
    public CountResponseDTO count(String sku, String name) {
        return count(new CatalogItemCountQuery(sku, name));
    }

    @Override
    @Transactional(readOnly = true)
    public CountResponseDTO count(CatalogItemCountQuery query) {
        CatalogItemQuerySupport.validate(query);
        return CountResponseDTO.of(queryRepository.count(query));
    }

    private CatalogItem requireById(String id) {
        if (id == null || id.isBlank()) {
            throw notFound(id);
        }
        return repository.findById(id).orElseThrow(() -> notFound(id));
    }

    private ResourceNotFoundException notFound(String id) {
        return new ResourceNotFoundException(
                "Catalog item not found: id=" + id,
                "catalog.item.not-found"
        );
    }

    private EntityAlreadyExistsException duplicateSku(String sku) {
        return new EntityAlreadyExistsException(
                "Catalog item already exists: SKU=" + sku,
                "catalog.item.conflict"
        );
    }
}
