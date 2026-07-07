package de.cocondo.platform.demo.catalog;

import de.cocondo.system.entity.validation.ValidationException;
import de.cocondo.system.entity.validation.Validator;
import java.util.Set;

public class CatalogItemValidator implements Validator<CatalogItemCreateDTO> {

    private static final int MAX_SKU_LENGTH = 128;
    private static final int MAX_NAME_LENGTH = 255;
    private static final int MAX_DESCRIPTION_LENGTH = 1000;
    private static final int MAX_TAG_LENGTH = 128;

    @Override
    public void validate(CatalogItemCreateDTO entity) throws ValidationException {
        if (entity == null) {
            throw new ValidationException("Catalog item create payload must not be null");
        }
        requireText(entity.getSku(), "sku", MAX_SKU_LENGTH);
        validateMutableFields(entity.getName(), entity.getDescription(), entity.getTags(), entity.getAvailability());
    }

    public void validate(CatalogItemUpdateDTO entity) throws ValidationException {
        if (entity == null) {
            throw new ValidationException("Catalog item update payload must not be null");
        }
        validateMutableFields(entity.getName(), entity.getDescription(), entity.getTags(), entity.getAvailability());
    }

    private void validateMutableFields(
            String name,
            String description,
            Set<String> tags,
            CatalogItemAvailabilityDTO availability
    ) {
        requireText(name, "name", MAX_NAME_LENGTH);
        requireOptionalLength(description, "description", MAX_DESCRIPTION_LENGTH);
        validateTags(tags);
        validateAvailability(availability);
    }

    private void requireText(String value, String fieldName, int maxLength) {
        if (value == null || value.isBlank()) {
            throw new ValidationException("Catalog item " + fieldName + " must not be blank");
        }
        if (value.trim().length() > maxLength) {
            throw new ValidationException("Catalog item " + fieldName + " must not exceed " + maxLength + " characters");
        }
    }

    private void requireOptionalLength(String value, String fieldName, int maxLength) {
        if (value != null && value.trim().length() > maxLength) {
            throw new ValidationException("Catalog item " + fieldName + " must not exceed " + maxLength + " characters");
        }
    }

    private void validateTags(Set<String> tags) {
        if (tags == null) {
            return;
        }
        for (String tag : tags) {
            requireText(tag, "tag", MAX_TAG_LENGTH);
        }
    }

    private void validateAvailability(CatalogItemAvailabilityDTO availability) {
        if (availability == null) {
            return;
        }
        if (!availability.isChronological()) {
            throw new ValidationException("Catalog item availability validFrom must not be after validTo");
        }
    }
}
