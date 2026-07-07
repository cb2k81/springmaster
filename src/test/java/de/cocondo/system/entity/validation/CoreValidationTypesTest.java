package de.cocondo.system.entity.validation;

import static org.assertj.core.api.Assertions.assertThatThrownBy;

import org.junit.jupiter.api.Test;

class CoreValidationTypesTest {

    @Test
    void validatorCanSignalValidationException() {
        Validator<String> validator = value -> {
            if (value == null || value.isBlank()) {
                throw new ValidationException("value must not be blank");
            }
        };

        assertThatThrownBy(() -> validator.validate(""))
                .isInstanceOf(ValidationException.class)
                .hasMessage("value must not be blank");
    }
}
