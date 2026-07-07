package de.cocondo.system.core.id;

import static org.assertj.core.api.Assertions.assertThat;

import org.junit.jupiter.api.Test;

class IdGeneratorServiceTest {

    @Test
    void idGeneratorServiceDefinesStringIdContract() {
        IdGeneratorService generator = () -> "generated-id";

        assertThat(generator.generateId()).isEqualTo("generated-id");
    }
}
