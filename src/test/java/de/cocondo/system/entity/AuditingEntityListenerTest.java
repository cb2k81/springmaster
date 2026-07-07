package de.cocondo.system.entity;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;

import java.time.LocalDateTime;

import org.junit.jupiter.api.Test;

class AuditingEntityListenerTest {

    private final AuditingEntityListener listener = new AuditingEntityListener();

    @Test
    void prePersistInitializesAuditFields() {
        TestAuditable entity = new TestAuditable();

        listener.prePersist(entity);

        assertEquals("SYSTEM", entity.getCreatedBy());
        assertNotNull(entity.getCreatedAt());
        assertEquals(entity.getCreatedBy(), entity.getLastModifiedBy());
        assertEquals(entity.getCreatedAt(), entity.getLastModifiedAt());
    }

    @Test
    void prePersistKeepsExistingCreationValues() {
        TestAuditable entity = new TestAuditable();
        LocalDateTime timestamp = LocalDateTime.of(2026, 1, 2, 3, 4);
        entity.setCreatedBy("tester");
        entity.setCreatedAt(timestamp);

        listener.prePersist(entity);

        assertEquals("tester", entity.getCreatedBy());
        assertEquals(timestamp, entity.getCreatedAt());
        assertEquals("tester", entity.getLastModifiedBy());
        assertEquals(timestamp, entity.getLastModifiedAt());
    }

    @Test
    void preUpdateOnlyUpdatesLastModifiedValues() {
        TestAuditable entity = new TestAuditable();
        LocalDateTime created = LocalDateTime.of(2026, 1, 2, 3, 4);
        entity.setCreatedBy("tester");
        entity.setCreatedAt(created);

        listener.preUpdate(entity);

        assertEquals("tester", entity.getCreatedBy());
        assertEquals(created, entity.getCreatedAt());
        assertEquals("SYSTEM", entity.getLastModifiedBy());
        assertNotNull(entity.getLastModifiedAt());
    }

    private static final class TestAuditable extends DomainEntity {
    }
}
