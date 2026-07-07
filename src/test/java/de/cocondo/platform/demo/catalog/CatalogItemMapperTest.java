package de.cocondo.platform.demo.catalog;

import static org.assertj.core.api.Assertions.assertThat;

import java.time.LocalDateTime;
import java.util.LinkedHashSet;
import java.util.Set;
import org.junit.jupiter.api.Test;

class CatalogItemMapperTest {

    private final CatalogItemMapper mapper = new CatalogItemMapper();

    @Test
    void mapsCreatePayloadToEntityDetailDtoAndListItemDto() {
        LocalDateTime validFrom = LocalDateTime.of(2026, 1, 1, 0, 0);
        LocalDateTime validTo = LocalDateTime.of(2026, 12, 31, 23, 59);
        CatalogItemAvailabilityDTO availability = new CatalogItemAvailabilityDTO(validFrom, validTo);

        CatalogItemCreateDTO payload = new CatalogItemCreateDTO(" SKU-1 ", " Demo Item ", " Description ");
        payload.setTags(new LinkedHashSet<>(Set.of("demo", "catalog")));
        payload.setAvailability(availability);

        CatalogItem entity = mapper.toEntity(payload);
        CatalogItemDTO dto = mapper.toDto(entity);
        CatalogItemListItemDTO listItem = mapper.toListItemDto(entity);

        assertThat(entity.getSku()).isEqualTo("SKU-1");
        assertThat(entity.getName()).isEqualTo("Demo Item");
        assertThat(entity.getDescription()).isEqualTo("Description");
        assertThat(entity.getTags()).containsExactlyInAnyOrder("demo", "catalog");
        assertThat(entity.getAvailability()).isNotNull();
        assertThat(entity.getAvailability().getValidFrom()).isEqualTo(validFrom);
        assertThat(entity.getAvailability().getValidTo()).isEqualTo(validTo);
        assertThat(dto.getId()).isEqualTo(entity.getId());
        assertThat(dto.getSku()).isEqualTo("SKU-1");
        assertThat(dto.getValidFrom()).isEqualTo(validFrom);
        assertThat(dto.getValidTo()).isEqualTo(validTo);
        assertThat(dto.getPersistenceVersion()).isZero();
        assertThat(listItem.getId()).isEqualTo(entity.getId());
        assertThat(listItem.getSku()).isEqualTo("SKU-1");
        assertThat(listItem.getName()).isEqualTo("Demo Item");
    }

    @Test
    void updatesEntityWithoutChangingSkuOrId() {
        CatalogItem entity = mapper.toEntity(new CatalogItemCreateDTO("SKU-1", "Demo Item", null));
        String id = entity.getId();
        LocalDateTime validFrom = LocalDateTime.of(2026, 2, 1, 0, 0);
        CatalogItemUpdateDTO payload = new CatalogItemUpdateDTO(" Updated ", " Description ");
        payload.setTags(new LinkedHashSet<>(Set.of("updated")));
        payload.setAvailability(new CatalogItemAvailabilityDTO(validFrom, null));

        mapper.updateEntity(entity, payload);

        assertThat(entity.getId()).isEqualTo(id);
        assertThat(entity.getSku()).isEqualTo("SKU-1");
        assertThat(entity.getName()).isEqualTo("Updated");
        assertThat(entity.getDescription()).isEqualTo("Description");
        assertThat(entity.getTags()).containsExactly("updated");
        assertThat(entity.getAvailability().getValidFrom()).isEqualTo(validFrom);
    }
}
