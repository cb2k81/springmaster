package de.cocondo.system.exception;

import static org.assertj.core.api.Assertions.assertThat;

import org.junit.jupiter.api.Test;

class CoreExceptionTypesTest {

    @Test
    void entityAlreadyExistsExceptionCarriesMessage() {
        EntityAlreadyExistsException exception = new EntityAlreadyExistsException("entity already exists");

        assertThat(exception).isInstanceOf(RuntimeException.class);
        assertThat(exception).hasMessage("entity already exists");
    }
}
