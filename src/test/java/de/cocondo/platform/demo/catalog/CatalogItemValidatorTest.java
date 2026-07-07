package de.cocondo.platform.demo.catalog;

import static org.assertj.core.api.Assertions.assertThatCode;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import de.cocondo.system.entity.validation.ValidationException;
import java.time.LocalDateTime;
import org.junit.jupiter.api.Test;

class CatalogItemValidatorTest {

    private final CatalogItemValidator validator = new CatalogItemValidator();

    @Test
    void acceptsValidCreatePayload() {
        CatalogItemCreateDTO payload = new CatalogItemCreateDTO("SKU-1", "Demo Item", "Description");

        assertThatCode(() -> validator.validate(payload)).doesNotThrowAnyException();
    }

    @Test
    void acceptsValidUpdatePayload() {
        CatalogItemUpdateDTO payload = new CatalogItemUpdateDTO("Demo Item", "Description");

        assertThatCode(() -> validator.validate(payload)).doesNotThrowAnyException();
    }

    @Test
    void rejectsMissingSku() {
        CatalogItemCreateDTO payload = new CatalogItemCreateDTO(" ", "Demo Item", null);

        assertThatThrownBy(() -> validator.validate(payload))
                .isInstanceOf(ValidationException.class)
                .hasMessageContaining("sku");
    }

    @Test
    void rejectsMissingCreateName() {
        CatalogItemCreateDTO payload = new CatalogItemCreateDTO("SKU-1", " ", null);

        assertThatThrownBy(() -> validator.validate(payload))
                .isInstanceOf(ValidationException.class)
                .hasMessageContaining("name");
    }

    @Test
    void rejectsMissingUpdateName() {
        CatalogItemUpdateDTO payload = new CatalogItemUpdateDTO(" ", null);

        assertThatThrownBy(() -> validator.validate(payload))
                .isInstanceOf(ValidationException.class)
                .hasMessageContaining("name");
    }

    @Test
    void rejectsInvalidAvailabilityRange() {
        CatalogItemUpdateDTO payload = new CatalogItemUpdateDTO("Demo Item", null);
        payload.setAvailability(new CatalogItemAvailabilityDTO(
                LocalDateTime.of(2026, 12, 31, 0, 0),
                LocalDateTime.of(2026, 1, 1, 0, 0)
        ));

        assertThatThrownBy(() -> validator.validate(payload))
                .isInstanceOf(ValidationException.class)
                .hasMessageContaining("availability");
    }
}
