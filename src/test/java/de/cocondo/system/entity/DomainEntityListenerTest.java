package de.cocondo.system.entity;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.util.UUID;

import org.junit.jupiter.api.Test;

class DomainEntityListenerTest {

    private final DomainEntityListener listener = new DomainEntityListener();

    @Test
    void prePersistKeepsExistingIdentifier() {
        TestEntity entity = new TestEntity();
        String id = entity.getId();

        listener.prePersist(entity);

        assertDoesNotThrow(() -> UUID.fromString(entity.getId()));
        assertNotNull(id);
    }

    @Test
    void prePersistCreatesMissingIdentifier() {
        TestEntity entity = new TestEntity();
        entity.setId(" ");

        listener.prePersist(entity);

        assertNotNull(UUID.fromString(entity.getId()));
    }

    @Test
    void prePersistRejectsNullEntity() {
        assertThrows(IllegalArgumentException.class, () -> listener.prePersist(null));
    }

    private static final class TestEntity extends DomainEntity {
    }
}
