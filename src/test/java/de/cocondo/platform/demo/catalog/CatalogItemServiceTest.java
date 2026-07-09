package de.cocondo.platform.demo.catalog;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import de.cocondo.system.dto.PagedResponseDTO;
import de.cocondo.system.exception.EntityAlreadyExistsException;
import java.time.LocalDateTime;
import org.junit.jupiter.api.Test;

class CatalogItemServiceTest {

    private final CatalogItemService service = new CatalogItemService();

    @Test
    void createsListsAndFindsCatalogItemsByIdAndSku() {
        CatalogItemDTO created = service.create(new CatalogItemCreateDTO(" SKU-1 ", "Demo Item", null));

        assertThat(created.getId()).isNotBlank();
        assertThat(created.getSku()).isEqualTo("SKU-1");
        assertThat(service.size()).isEqualTo(1);
        assertThat(service.listPaged(0, 20, "sku", "ASC").getItems()).hasSize(1);
        assertThat(service.findById(created.getId()))
                .hasValueSatisfying(found -> assertThat(found.getSku()).isEqualTo("SKU-1"));
        assertThat(service.findBySku("sku-1"))
                .hasValueSatisfying(found -> assertThat(found.getId()).isEqualTo(created.getId()));
    }

    @Test
    void listsCatalogItemsPagedAndSorted() {
        service.create(new CatalogItemCreateDTO("SKU-2", "Beta", null));
        service.create(new CatalogItemCreateDTO("SKU-1", "Alpha", null));

        PagedResponseDTO<CatalogItemListItemDTO> response = service.listPaged(0, 1, "sku", "ASC");

        assertThat(response.getItems()).hasSize(1);
        assertThat(response.getItems().getFirst().getSku()).isEqualTo("SKU-1");
        assertThat(response.getPage()).isZero();
        assertThat(response.getSize()).isEqualTo(1);
        assertThat(response.getTotalElements()).isEqualTo(2);
        assertThat(response.getTotalPages()).isEqualTo(2);
    }

    @Test
    void appliesSameFiltersToPagedAndAllQueries() {
        service.create(new CatalogItemCreateDTO("SKU-2", "Beta", null));
        service.create(new CatalogItemCreateDTO("SKU-1", "Alpha", null));
        service.create(new CatalogItemCreateDTO("SKU-3", "Alpine", null));

        PagedResponseDTO<CatalogItemListItemDTO> paged = service.listPaged(0, 1, "sku", "ASC", null, "alp");
        var all = service.listAll("sku", "ASC", null, "alp");

        assertThat(paged.getItems()).hasSize(1);
        assertThat(paged.getItems().getFirst().getSku()).isEqualTo("SKU-1");
        assertThat(paged.getTotalElements()).isEqualTo(2);
        assertThat(paged.getTotalPages()).isEqualTo(2);
        assertThat(all).extracting(CatalogItemListItemDTO::getSku).containsExactly("SKU-1", "SKU-3");
    }

    @Test
    void returnsEmptyResultsForUnmatchedFilters() {
        service.create(new CatalogItemCreateDTO("SKU-1", "Alpha", null));

        PagedResponseDTO<CatalogItemListItemDTO> paged = service.listPaged(0, 20, "sku", "ASC", "SKU-X", null);

        assertThat(paged.getItems()).isEmpty();
        assertThat(paged.getTotalElements()).isZero();
        assertThat(paged.getTotalPages()).isZero();
        assertThat(service.listAll("sku", "ASC", "SKU-X", null)).isEmpty();
    }

    @Test
    void updatesCatalogItemWithoutChangingSku() {
        CatalogItemDTO created = service.create(new CatalogItemCreateDTO("SKU-1", "Demo Item", null));

        CatalogItemDTO updated = service.update(created.getId(), new CatalogItemUpdateDTO("Updated", "Description"));

        assertThat(updated.getId()).isEqualTo(created.getId());
        assertThat(updated.getSku()).isEqualTo("SKU-1");
        assertThat(updated.getName()).isEqualTo("Updated");
        assertThat(updated.getDescription()).isEqualTo("Description");
    }

    @Test
    void deletesCatalogItemById() {
        CatalogItemDTO created = service.create(new CatalogItemCreateDTO("SKU-1", "Demo Item", null));

        service.delete(created.getId());

        assertThat(service.findById(created.getId())).isEmpty();
        assertThat(service.findBySku("SKU-1")).isEmpty();
        assertThat(service.size()).isZero();
    }

    @Test
    void rejectsDuplicateSkuCaseInsensitively() {
        service.create(new CatalogItemCreateDTO("SKU-1", "Demo Item", null));

        assertThatThrownBy(() -> service.create(new CatalogItemCreateDTO("sku-1", "Other Item", null)))
                .isInstanceOf(EntityAlreadyExistsException.class)
                .hasMessageContaining("SKU");
    }

    @Test
    void rejectsUnsupportedSortBy() {
        assertThatThrownBy(() -> service.listPaged(0, 20, "createdAt", "ASC"))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessageContaining("sortBy");
    }

    @Test
    void rejectsInvalidAvailabilityOnUpdateAtServiceBoundary() {
        CatalogItemDTO created = service.create(new CatalogItemCreateDTO("SKU-1", "Demo Item", null));
        CatalogItemUpdateDTO payload = new CatalogItemUpdateDTO("Updated", null);
        payload.setAvailability(new CatalogItemAvailabilityDTO(
                LocalDateTime.of(2026, 12, 31, 0, 0),
                LocalDateTime.of(2026, 1, 1, 0, 0)
        ));

        assertThatThrownBy(() -> service.update(created.getId(), payload))
                .isInstanceOf(de.cocondo.system.entity.validation.ValidationException.class)
                .hasMessageContaining("availability");
    }

    @Test
    void rejectsUnknownIdForUpdateAndDelete() {
        assertThatThrownBy(() -> service.update("unknown", new CatalogItemUpdateDTO("Updated", null)))
                .isInstanceOf(CatalogItemNotFoundException.class)
                .hasMessageContaining("id");
        assertThatThrownBy(() -> service.delete("unknown"))
                .isInstanceOf(CatalogItemNotFoundException.class)
                .hasMessageContaining("id");
    }
}
