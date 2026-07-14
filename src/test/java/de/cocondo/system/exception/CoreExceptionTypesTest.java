package de.cocondo.system.exception;

import static org.assertj.core.api.Assertions.assertThat;

import org.junit.jupiter.api.Test;

class CoreExceptionTypesTest {

    @Test
    void entityAlreadyExistsExceptionCarriesMessageAndDefaultMessageKey() {
        EntityAlreadyExistsException exception = new EntityAlreadyExistsException("entity already exists");

        assertThat(exception).isInstanceOf(RuntimeException.class);
        assertThat(exception).hasMessage("entity already exists");
        assertThat(exception.getMessageKey()).isEqualTo("springmaster.resource.conflict");
    }

    @Test
    void resourceNotFoundExceptionCarriesMessageAndMessageKey() {
        ResourceNotFoundException exception = new ResourceNotFoundException(
                "resource not found",
                "demo.resource.not-found"
        );

        assertThat(exception).isInstanceOf(RuntimeException.class);
        assertThat(exception).hasMessage("resource not found");
        assertThat(exception.getMessageKey()).isEqualTo("demo.resource.not-found");
    }
}
