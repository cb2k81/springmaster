package de.cocondo.system.core.id;

import static org.assertj.core.api.Assertions.assertThat;

import java.util.UUID;

import org.junit.jupiter.api.Test;
import org.springframework.stereotype.Service;

class UuidIdGeneratorServiceTest {

    private final UuidIdGeneratorService generator = new UuidIdGeneratorService();

    @Test
    void implementsIdGeneratorServiceContract() {
        assertThat(generator).isInstanceOf(IdGeneratorService.class);
    }

    @Test
    void generatesValidUuidString() {
        String id = generator.generateId();

        assertThat(id).isNotBlank();
        assertThat(UUID.fromString(id).toString()).isEqualTo(id);
    }

    @Test
    void generatesDifferentIdsForSeparateCalls() {
        String firstId = generator.generateId();
        String secondId = generator.generateId();

        assertThat(firstId).isNotEqualTo(secondId);
    }

    @Test
    void isRegisteredAsSpringServiceCandidate() {
        assertThat(UuidIdGeneratorService.class).hasAnnotation(Service.class);
    }
}
